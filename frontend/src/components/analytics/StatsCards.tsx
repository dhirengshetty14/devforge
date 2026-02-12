import { Card } from "@/components/ui/card";

type Props = {
  counts: Record<string, number>;
};

export function StatsCards({ counts }: Props) {
  const items = [
    { label: "Views", value: counts.view || 0 },
    { label: "Clicks", value: counts.click || 0 },
    { label: "Shares", value: counts.share || 0 },
  ];

  return (
    <div className="grid sm:grid-cols-3 gap-4">
      {items.map((item) => (
        <Card key={item.label}>
          <p className="text-sm text-slate-500">{item.label}</p>
          <p className="text-2xl font-semibold mt-1">{item.value}</p>
        </Card>
      ))}
    </div>
  );
}
