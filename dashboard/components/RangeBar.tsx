import { fmtUsd } from "@/lib/data";

interface RangeBarProps {
  p10: number;
  p50: number;
  p90: number;
  paidIn: number;
}

export function RangeBar({ p10, p50, p90, paidIn }: RangeBarProps) {
  // Scale so paid-in sits at ~25% and p90 sits near the right
  const max = Math.max(p90 * 1.05, paidIn * 1.5);
  const pct = (n: number) => (n / max) * 100;

  return (
    <div className="space-y-2">
      <div className="relative h-12 bg-gray-100 rounded-md overflow-hidden">
        {/* Range bar p10 to p90 */}
        <div
          className="absolute top-0 h-full bg-blue-100 border-l-2 border-r-2 border-blue-300"
          style={{ left: `${pct(p10)}%`, width: `${pct(p90) - pct(p10)}%` }}
        />
        {/* P50 marker */}
        <div
          className="absolute top-0 h-full w-0.5 bg-blue-700"
          style={{ left: `${pct(p50)}%` }}
        />
        {/* Paid-in marker */}
        <div
          className="absolute top-0 h-full w-0.5 bg-gray-700 border-l border-dashed"
          style={{ left: `${pct(paidIn)}%` }}
        />
      </div>
      <div className="relative h-5 text-xs text-gray-600 tabular-nums">
        <span className="absolute" style={{ left: `${pct(p10)}%`, transform: "translateX(-50%)" }}>
          P10 {fmtUsd(p10, { compact: true })}
        </span>
        <span
          className="absolute font-semibold text-blue-700"
          style={{ left: `${pct(p50)}%`, transform: "translateX(-50%)" }}
        >
          P50 {fmtUsd(p50, { compact: true })}
        </span>
        <span className="absolute" style={{ left: `${pct(p90)}%`, transform: "translateX(-50%)" }}>
          P90 {fmtUsd(p90, { compact: true })}
        </span>
      </div>
      <div className="relative h-5 text-xs text-gray-500">
        <span
          className="absolute italic"
          style={{ left: `${pct(paidIn)}%`, transform: "translateX(-50%)" }}
        >
          Paid-in {fmtUsd(paidIn, { compact: true })}
        </span>
      </div>
    </div>
  );
}
