"use client";

import { motion } from "framer-motion";
import { useState } from "react";

import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";

type PublicGenerateResponse = {
  username: string;
  portfolio_path: string;
  portfolio_url: string;
  projects_analyzed: number;
  summary: string;
};

export default function HomePage() {
  const [githubUrl, setGithubUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<PublicGenerateResponse | null>(null);

  const handleGenerate = async () => {
    try {
      setLoading(true);
      setError(null);
      setResult(null);
      const response = await api.post<PublicGenerateResponse>(
        "/api/public/generate",
        { github_url: githubUrl, template_id: "minimal" },
        false,
      );
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to generate portfolio");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container py-16 sm:py-24">
      <motion.section
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.55 }}
        className="glass rounded-3xl p-8 sm:p-12"
      >
        <p className="inline-flex rounded-full bg-slate-900 text-white text-xs px-3 py-1 mb-5">
          Production-grade portfolio generation
        </p>
        <h1 className="text-4xl sm:text-6xl font-semibold tracking-tight max-w-4xl" style={{ fontFamily: "var(--font-display)" }}>
          Turn GitHub activity into a senior-level portfolio with realtime AI insights.
        </h1>
        <p className="mt-5 text-slate-600 max-w-2xl">
          Paste any public GitHub profile URL and DevForge generates a portfolio automatically.
        </p>

        <div className="mt-8 grid gap-3 max-w-2xl">
          <input
            value={githubUrl}
            onChange={(event) => setGithubUrl(event.target.value)}
            placeholder="https://github.com/username"
            className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm"
          />
          <div className="flex flex-wrap gap-3">
            <Button onClick={handleGenerate} disabled={loading || !githubUrl.trim()}>
              {loading ? "Generating..." : "Generate Portfolio"}
            </Button>
            <Button asChild variant="outline">
              <a href="/dashboard">Advanced Dashboard</a>
            </Button>
          </div>
        </div>

        {error ? <p className="mt-3 text-sm text-red-600">{error}</p> : null}

        {result ? (
          <div className="mt-6 rounded-2xl border border-emerald-200 bg-emerald-50 p-4">
            <p className="text-sm text-emerald-900">
              Portfolio ready for <strong>@{result.username}</strong>. Projects analyzed: {result.projects_analyzed}
            </p>
            <p className="mt-2 text-sm text-slate-700">{result.summary}</p>
            <a className="mt-3 inline-block text-sm font-medium text-emerald-800 underline" href={result.portfolio_url} target="_blank" rel="noreferrer">
              Open generated portfolio
            </a>
            <iframe
              title="Generated portfolio preview"
              src={result.portfolio_url}
              className="mt-4 h-[500px] w-full rounded-xl border border-slate-300 bg-white"
            />
          </div>
        ) : null}
      </motion.section>
    </div>
  );
}
