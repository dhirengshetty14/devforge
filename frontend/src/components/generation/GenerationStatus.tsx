import { Card } from "@/components/ui/card";
import { ProgressBar } from "@/components/generation/ProgressBar";
import { LiveLog } from "@/components/generation/LiveLog";
import { GenerationProgressEvent } from "@/types/portfolio";

type Props = {
  progress: number;
  step?: string;
  status?: string;
  events: GenerationProgressEvent[];
};

export function GenerationStatus({ progress, step, status, events }: Props) {
  return (
    <Card>
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Generation Status</h3>
        <span className="text-xs uppercase tracking-wide text-slate-500">{status || "idle"}</span>
      </div>
      <div className="mt-3 space-y-2">
        <ProgressBar value={progress} />
        <p className="text-sm text-slate-600">{step || "Waiting to start..."}</p>
      </div>
      <div className="mt-4">
        <LiveLog events={events} />
      </div>
    </Card>
  );
}
