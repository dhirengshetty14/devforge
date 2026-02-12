"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

type AnalyticsResponse = {
  portfolio_id: string;
  counts: Record<string, number>;
  recent: Array<{
    id: string;
    event_type: string;
    event_data: Record<string, unknown>;
    created_at: string;
  }>;
};

export function useAnalytics(portfolioId?: string) {
  return useQuery({
    queryKey: ["analytics", portfolioId],
    queryFn: () => api.get<AnalyticsResponse>(`/api/analytics/${portfolioId}`),
    enabled: Boolean(portfolioId),
  });
}
