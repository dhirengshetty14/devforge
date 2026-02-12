"use client";

import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

type Props = {
  onApply: (theme: Record<string, unknown>) => void;
};

export function CustomizationPanel({ onApply }: Props) {
  const [accent, setAccent] = useState("#0f766e");
  const [font, setFont] = useState("Sora");

  return (
    <Card>
      <h3 className="text-lg font-semibold">Theme</h3>
      <div className="mt-4 space-y-4">
        <label className="block">
          <span className="text-sm text-slate-600">Accent</span>
          <input
            type="color"
            value={accent}
            onChange={(e) => setAccent(e.target.value)}
            className="mt-1 h-10 w-16 rounded border border-slate-300"
          />
        </label>
        <label className="block">
          <span className="text-sm text-slate-600">Font</span>
          <input
            value={font}
            onChange={(e) => setFont(e.target.value)}
            className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
          />
        </label>
        <Button onClick={() => onApply({ accent, font })}>Apply</Button>
      </div>
    </Card>
  );
}
