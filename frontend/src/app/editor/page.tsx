"use client";

import { useEffect, useMemo, useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { TemplateSelector } from "@/components/portfolio/TemplateSelector";
import { CustomizationPanel } from "@/components/portfolio/CustomizationPanel";
import { PortfolioPreview } from "@/components/portfolio/PortfolioPreview";
import { GenerationStatus } from "@/components/generation/GenerationStatus";
import { useGeneration } from "@/hooks/useGeneration";
import { usePortfolios } from "@/hooks/usePortfolio";
import { api } from "@/lib/api";
import { useUIStore } from "@/stores/uiStore";
import { TemplateDefinition } from "@/types/portfolio";

type PreviewResponse = {
  portfolio_id: string;
  html: string;
};

const defaultTemplates: TemplateDefinition[] = [
  {
    id: "minimal",
    name: "Minimal Pro",
    description: "Clean engineering-forward portfolio style.",
    defaults: { accent: "#0f766e", font: "Sora" },
  },
  {
    id: "modern",
    name: "Modern Grid",
    description: "Structured showcase for system projects.",
    defaults: { accent: "#1d4ed8", font: "Space Grotesk" },
  },
  {
    id: "creative",
    name: "Creative Systems",
    description: "Bold storytelling for senior SDE branding.",
    defaults: { accent: "#ea580c", font: "Sora" },
  },
];

export default function EditorPage() {
  const { data: portfolios = [] } = usePortfolios();
  const selectedTemplate = useUIStore((state) => state.selectedTemplate);
  const setSelectedTemplate = useUIStore((state) => state.setSelectedTemplate);
  const activePortfolio = portfolios[0];
  const [previewHtml, setPreviewHtml] = useState<string>("");

  const generation = useGeneration(activePortfolio?.id);

  const templates = useMemo(() => defaultTemplates, []);

  useEffect(() => {
    if (!activePortfolio?.id) return;
    api
      .get<PreviewResponse>(`/api/portfolios/${activePortfolio.id}/preview`)
      .then((res) => setPreviewHtml(res.html))
      .catch(() => null);
  }, [activePortfolio?.id, generation.latest?.status]);

  const applyTheme = async (theme: Record<string, unknown>) => {
    if (!activePortfolio?.id) return;
    await api.patch(`/api/portfolios/${activePortfolio.id}`, {
      template_id: selectedTemplate,
      theme_config: theme,
    });
  };

  return (
    <div className="container py-8 grid lg:grid-cols-[260px,1fr] gap-6">
      <Sidebar />
      <div className="space-y-6">
        <Card>
          <div className="flex items-center justify-between gap-3">
            <div>
              <h1 className="text-2xl font-semibold">Portfolio Editor</h1>
              <p className="text-sm text-slate-600 mt-1">Select templates, customize theme, and generate portfolio.</p>
            </div>
            <Button disabled={!activePortfolio} onClick={() => generation.triggerGeneration()}>
              Generate Portfolio
            </Button>
          </div>
        </Card>

        <TemplateSelector templates={templates} selected={selectedTemplate} onSelect={setSelectedTemplate} />

        <div className="grid xl:grid-cols-[320px,1fr] gap-4">
          <CustomizationPanel onApply={applyTheme} />
          <GenerationStatus
            progress={generation.progress}
            step={generation.latest?.step}
            status={generation.latest?.status}
            events={generation.events}
          />
        </div>

        <PortfolioPreview html={previewHtml} />
      </div>
    </div>
  );
}
