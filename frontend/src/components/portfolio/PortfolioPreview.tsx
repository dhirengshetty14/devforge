import { Card } from "@/components/ui/card";

type Props = {
  html?: string;
};

export function PortfolioPreview({ html }: Props) {
  return (
    <Card className="overflow-hidden">
      <h3 className="text-lg font-semibold mb-3">Live Preview</h3>
      {html ? (
        <iframe title="Portfolio preview" className="w-full h-[540px] rounded-xl border border-slate-300" srcDoc={html} />
      ) : (
        <p className="text-sm text-slate-600">Generate your portfolio to see preview.</p>
      )}
    </Card>
  );
}
