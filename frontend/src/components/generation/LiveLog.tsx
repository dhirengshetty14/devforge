import { GenerationProgressEvent } from "@/types/portfolio";

type Props = {
  events: GenerationProgressEvent[];
};

export function LiveLog({ events }: Props) {
  return (
    <div className="rounded-xl border border-slate-300 bg-white h-56 overflow-y-auto p-3 text-xs font-mono">
      {events.length === 0 ? (
        <div className="text-slate-500">No events yet</div>
      ) : (
        <ul className="space-y-1">
          {events.map((event, idx) => (
            <li key={`${event.job_id}-${idx}`} className="text-slate-700">
              [{event.status}] {event.progress}% - {event.step}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
