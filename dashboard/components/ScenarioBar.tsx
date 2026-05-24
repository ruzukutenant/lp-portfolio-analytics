import type { Scenario } from "@/lib/types";

interface ScenarioBarProps {
  scenarios: Scenario[];
}

const COLORS = ["bg-emerald-500", "bg-blue-500", "bg-amber-500", "bg-red-500"];

export function ScenarioBar({ scenarios }: ScenarioBarProps) {
  return (
    <div className="space-y-2">
      <div className="flex h-6 rounded-md overflow-hidden bg-gray-100">
        {scenarios.map((s, i) => (
          <div
            key={s.label}
            className={`${COLORS[i % COLORS.length]} flex items-center justify-center text-xs text-white font-medium`}
            style={{ width: `${s.prob * 100}%` }}
            title={`${s.label}: ${(s.prob * 100).toFixed(0)}% at ${s.mult}× mark${s._anchor ? ` — ${s._anchor}` : ""}`}
          >
            {s.prob >= 0.15 && `${s.label} ${s.mult}×`}
          </div>
        ))}
      </div>
      <div className="text-xs text-gray-500 space-y-0.5">
        {scenarios.map((s) => (
          <div key={s.label}>
            <span className="font-medium text-gray-700">
              {(s.prob * 100).toFixed(0)}% {s.label}
            </span>
            {" at "}
            <span className="tabular-nums">{s.mult}×</span>
            {s._anchor && <span className="text-gray-500"> — {s._anchor}</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
