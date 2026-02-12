"use client";

import { TemplateDefinition } from "@/types/portfolio";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

type Props = {
  templates: TemplateDefinition[];
  selected: string;
  onSelect: (id: string) => void;
};

export function TemplateSelector({ templates, selected, onSelect }: Props) {
  return (
    <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-4">
      {templates.map((template) => {
        const active = selected === template.id;
        return (
          <Card key={template.id} className={active ? "ring-2 ring-slate-900" : ""}>
            <h3 className="text-lg font-semibold">{template.name}</h3>
            <p className="text-sm text-slate-600 mt-1">{template.description}</p>
            <div className="mt-4">
              <Button variant={active ? "default" : "outline"} onClick={() => onSelect(template.id)}>
                {active ? "Selected" : "Select"}
              </Button>
            </div>
          </Card>
        );
      })}
    </div>
  );
}
