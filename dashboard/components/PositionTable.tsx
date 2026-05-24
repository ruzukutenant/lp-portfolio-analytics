import { fmtUsd, fmtMultiple } from "@/lib/data";
import type { Position } from "@/lib/types";

interface PositionTableProps {
  positions: Position[];
}

export function PositionTable({ positions }: PositionTableProps) {
  const sorted = [...positions].sort(
    (a, b) => (b.expected_exit_usd ?? 0) - (a.expected_exit_usd ?? 0),
  );

  return (
    <div className="overflow-x-auto border border-gray-200 rounded-lg bg-white">
      <table className="w-full text-sm">
        <thead className="bg-gray-50 text-xs text-gray-600 uppercase tracking-wide">
          <tr>
            <th className="text-left px-4 py-2 font-semibold">Company</th>
            <th className="text-left px-2 py-2 font-semibold">Cohort</th>
            <th className="text-right px-2 py-2 font-semibold">Cost</th>
            <th className="text-right px-2 py-2 font-semibold">GP mark</th>
            <th className="text-right px-2 py-2 font-semibold">Dil-adj mark</th>
            <th className="text-right px-2 py-2 font-semibold">Δ vs GP</th>
            <th className="text-right px-2 py-2 font-semibold">P50 exit</th>
            <th className="text-right px-2 py-2 font-semibold">× cost</th>
            <th className="text-center px-2 py-2 font-semibold">QSBS</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((p) => {
            const delta =
              p.dilution_adjusted_mark_usd !== null && p.gp_current_mark_usd > 0
                ? ((p.dilution_adjusted_mark_usd - p.gp_current_mark_usd) /
                    p.gp_current_mark_usd) *
                  100
                : null;
            const deltaClass =
              delta === null
                ? "text-gray-400"
                : delta > 5
                ? "text-emerald-700"
                : delta < -5
                ? "text-red-700"
                : "text-gray-600";

            return (
              <tr key={p.company} className="border-t border-gray-100 hover:bg-gray-50">
                <td className="px-4 py-2 font-medium text-gray-900">
                  {p.company}
                  {p.realized && (
                    <span className="ml-2 text-xs text-red-700 bg-red-50 px-1.5 py-0.5 rounded">
                      realized
                    </span>
                  )}
                </td>
                <td className="px-2 py-2 text-xs text-gray-600">{p.cohort ?? "—"}</td>
                <td className="px-2 py-2 text-right tabular-nums">{fmtUsd(p.cost_usd)}</td>
                <td className="px-2 py-2 text-right tabular-nums text-gray-500">
                  {fmtUsd(p.gp_current_mark_usd)}
                </td>
                <td className="px-2 py-2 text-right tabular-nums font-medium">
                  {p.dilution_adjusted_mark_usd !== null
                    ? fmtUsd(p.dilution_adjusted_mark_usd)
                    : "—"}
                </td>
                <td className={`px-2 py-2 text-right tabular-nums text-xs ${deltaClass}`}>
                  {delta !== null
                    ? `${delta > 0 ? "+" : ""}${delta.toFixed(0)}%`
                    : "—"}
                </td>
                <td className="px-2 py-2 text-right tabular-nums">
                  {p.expected_exit_usd !== null ? fmtUsd(p.expected_exit_usd) : "—"}
                </td>
                <td className="px-2 py-2 text-right tabular-nums text-gray-600">
                  {p.expected_multiple_on_cost !== null
                    ? fmtMultiple(p.expected_multiple_on_cost, 1)
                    : "—"}
                </td>
                <td className="px-2 py-2 text-center">
                  {p.qsbs_eligible ? (
                    <span className="text-xs text-emerald-700">✓</span>
                  ) : (
                    <span className="text-xs text-gray-300">—</span>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
