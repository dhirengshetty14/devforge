"use client";

import { useMemo } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Card } from "@/components/ui/card";
import { usePortfolios } from "@/hooks/usePortfolio";
import { useAnalytics } from "@/hooks/useAnalytics";
import { StatsCards } from "@/components/analytics/StatsCards";
import { VisitorChart } from "@/components/analytics/VisitorChart";

export default function AnalyticsPage() {
  const portfoliosQuery = usePortfolios();
  const firstPortfolio = portfoliosQuery.data?.[0];
  const analyticsQuery = useAnalytics(firstPortfolio?.id);

  const chartData = useMemo(() => {
    const recent = analyticsQuery.data?.recent || [];
    const grouped = new Map<string, number>();
    for (const item of recent) {
      const date = new Date(item.created_at).toISOString().slice(0, 10);
      grouped.set(date, (grouped.get(date) || 0) + 1);
    }
    return [...grouped.entries()].map(([date, count]) => ({ date, count })).slice(-14);
  }, [analyticsQuery.data?.recent]);

  return (
    <div className="container py-8 grid lg:grid-cols-[260px,1fr] gap-6">
      <Sidebar />
      <div className="space-y-6">
        <Card>
          <h1 className="text-2xl font-semibold">Analytics</h1>
          <p className="text-sm text-slate-600 mt-1">
            Track views, interactions, and engagement for your portfolio.
          </p>
        </Card>

        {!firstPortfolio ? (
          <Card>
            <p className="text-sm text-slate-600">Create a portfolio first to view analytics.</p>
          </Card>
        ) : analyticsQuery.isLoading ? (
          <Card>
            <p className="text-sm text-slate-600">Loading analytics...</p>
          </Card>
        ) : (
          <>
            <StatsCards counts={analyticsQuery.data?.counts || {}} />
            <VisitorChart data={chartData} />
          </>
        )}
      </div>
    </div>
  );
}
