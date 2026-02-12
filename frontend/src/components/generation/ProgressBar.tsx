type Props = {
  value: number;
};

export function ProgressBar({ value }: Props) {
  return (
    <div className="w-full rounded-full bg-slate-200 h-2 overflow-hidden">
      <div
        className="h-full bg-slate-900 transition-all duration-500"
        style={{ width: `${Math.max(0, Math.min(100, value))}%` }}
      />
    </div>
  );
}
