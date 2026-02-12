"use client";

import { useMemo, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { GenerationJob } from "@/types/api";
import { GenerationProgressEvent } from "@/types/portfolio";

const WS_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function useGeneration(portfolioId?: string) {
  const [events, setEvents] = useState<GenerationProgressEvent[]>([]);
  const [latest, setLatest] = useState<GenerationProgressEvent | null>(null);
  const [activeJob, setActiveJob] = useState<GenerationJob | null>(null);

  const triggerMutation = useMutation({
    mutationFn: async () => {
      if (!portfolioId) {
        throw new Error("Portfolio is required");
      }
      return api.post<GenerationJob>(`/api/portfolios/${portfolioId}/generate`, {});
    },
    onSuccess: (job) => {
      setActiveJob(job);
      connectWebSocket(job.id);
    },
  });

  const connectWebSocket = (jobId: string) => {
    const wsUrl = WS_BASE.replace("http", "ws");
    const socket = new WebSocket(`${wsUrl}/ws/generation/${jobId}`);
    socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data) as GenerationProgressEvent;
        setLatest(payload);
        setEvents((prev) => [...prev.slice(-100), payload]);
      } catch {
        // ignore malformed events
      }
    };
    socket.onerror = () => {
      setLatest({
        job_id: jobId,
        status: "failed",
        progress: 100,
        step: "WebSocket disconnected",
      });
    };
  };

  const progress = useMemo(() => latest?.progress ?? activeJob?.progress_percentage ?? 0, [activeJob, latest]);

  return {
    triggerGeneration: triggerMutation.mutate,
    isGenerating: triggerMutation.isPending || (latest?.status === "processing"),
    events,
    latest,
    progress,
    activeJob,
    error: triggerMutation.error,
  };
}
