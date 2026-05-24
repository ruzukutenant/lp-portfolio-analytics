interface StatProps {
  label: string;
  value: string;
  hint?: string;
  tone?: "default" | "positive" | "negative";
}

export function Stat({ label, value, hint, tone = "default" }: StatProps) {
  const toneClass =
    tone === "positive"
      ? "text-emerald-700"
      : tone === "negative"
      ? "text-red-700"
      : "text-gray-900";
  return (
    <div className="flex flex-col gap-1 border border-gray-200 rounded-lg bg-white p-4">
      <div className="text-xs text-gray-500 uppercase tracking-wide">{label}</div>
      <div className={`text-2xl font-semibold tabular-nums ${toneClass}`}>{value}</div>
      {hint && <div className="text-xs text-gray-500">{hint}</div>}
    </div>
  );
}
