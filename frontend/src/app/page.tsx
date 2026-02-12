"use client";

import { motion } from "framer-motion";
import { useState } from "react";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";

type GitHubAuthStart = {
  authorization_url: string;
  state: string;
};

export default function HomePage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGitHubLogin = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.post<GitHubAuthStart>("/api/auth/github", {}, false);
      window.location.href = response.authorization_url;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to start GitHub OAuth");
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
          DevForge analyzes repositories and commits with distributed workers, then builds a polished portfolio website you can deploy quickly.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Button onClick={handleGitHubLogin} disabled={loading}>
            {loading ? "Connecting..." : "Continue with GitHub"}
          </Button>
          <Button asChild variant="outline">
            <a href="/dashboard">Open Dashboard</a>
          </Button>
        </div>
        {error ? <p className="mt-3 text-sm text-red-600">{error}</p> : null}
      </motion.section>
    </div>
  );
}
