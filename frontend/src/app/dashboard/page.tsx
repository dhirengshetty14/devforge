"use client";

import { useMemo, useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { usePortfolios, useCreatePortfolio } from "@/hooks/usePortfolio";
import { api } from "@/lib/api";

export default function DashboardPage() {
  const portfoliosQuery = usePortfolios();
  const createPortfolio = useCreatePortfolio();
  const [subdomain, setSubdomain] = useState("");
  const [syncing, setSyncing] = useState(false);
  const [syncMessage, setSyncMessage] = useState("");

  const portfolios = useMemo(() => portfoliosQuery.data || [], [portfoliosQuery.data]);

  const handleCreate = () => {
    if (!subdomain.trim()) return;
    createPortfolio.mutate({
      subdomain: subdomain.trim().toLowerCase(),
      template_id: "minimal",
      theme_config: { accent: "#0f766e", font: "Sora" },
    });
    setSubdomain("");
  };

  const handleSync = async () => {
    try {
      setSyncing(true);
      setSyncMessage("");
      const res = await api.post<{ detail: string }>("/api/github/sync", {});
      setSyncMessage(res.detail);
    } catch (err) {
      setSyncMessage(err instanceof Error ? err.message : "Sync failed");
    } finally {
      setSyncing(false);
    }
  };

  return (
    <div className="container py-8 grid lg:grid-cols-[260px,1fr] gap-6">
      <Sidebar />
      <div className="space-y-6">
        <Card>
          <h1 className="text-2xl font-semibold">Dashboard</h1>
          <p className="text-slate-600 mt-1">Sync GitHub data and manage generated portfolios.</p>
          <div className="mt-4 flex flex-wrap gap-2">
            <Button onClick={handleSync} disabled={syncing}>
              {syncing ? "Syncing..." : "Sync GitHub"}
            </Button>
            {syncMessage ? <span className="text-sm text-slate-600 self-center">{syncMessage}</span> : null}
          </div>
        </Card>

        <Card>
          <h2 className="text-lg font-semibold">Create Portfolio</h2>
          <div className="mt-3 flex gap-2">
            <input
              value={subdomain}
              onChange={(e) => setSubdomain(e.target.value)}
              placeholder="yourname"
              className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
            />
            <Button onClick={handleCreate} disabled={createPortfolio.isPending}>
              Create
            </Button>
          </div>
        </Card>

        <Card>
          <h2 className="text-lg font-semibold">Your Portfolios</h2>
          {portfoliosQuery.isLoading ? (
            <p className="text-sm text-slate-600 mt-3">Loading portfolios...</p>
          ) : portfolios.length === 0 ? (
            <p className="text-sm text-slate-600 mt-3">No portfolios created yet.</p>
          ) : (
            <ul className="mt-3 space-y-3">
              {portfolios.map((portfolio) => (
                <li key={portfolio.id} className="rounded-xl border border-slate-300 p-3">
                  <p className="font-medium">{portfolio.subdomain}.devforge.dev</p>
                  <p className="text-sm text-slate-600">
                    Template: {portfolio.template_id} • Published: {portfolio.is_published ? "Yes" : "No"}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  );
}
