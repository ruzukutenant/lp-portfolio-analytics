import { NoticeBanner } from "@/components/NoticeBanner";
import { PositionTable } from "@/components/PositionTable";
import { RangeBar } from "@/components/RangeBar";
import { ScenarioBar } from "@/components/ScenarioBar";
import { Stat } from "@/components/Stat";
import {
  cashProjection,
  fmtMultiple,
  fmtPct,
  fmtUsd,
  lookupFundamentalEv,
  positions,
  snapshot,
} from "@/lib/data";

export default function HomePage() {
  const topPositions = [...positions]
    .filter((p) => p.expected_exit_usd && p.expected_exit_usd > 0)
    .sort((a, b) => (b.expected_exit_usd ?? 0) - (a.expected_exit_usd ?? 0))
    .slice(0, 5);

  return (
    <main className="max-w-6xl mx-auto px-6 py-12 space-y-12">
      {/* Header */}
      <header className="space-y-2">
        <div className="text-xs text-gray-500 uppercase tracking-wider">
          LP Portfolio Dashboard — Sample Fund
        </div>
        <h1 className="text-3xl font-bold text-gray-900">{snapshot.fund_name}</h1>
        <p className="text-sm text-gray-600 max-w-3xl leading-relaxed">
          {snapshot.fund_description}
        </p>
        <div className="text-xs text-gray-400 pt-1">
          Snapshot date: {snapshot.snapshot_date} ·{" "}
          <span className="italic">Illustrative reconstructions, not actual fund manager marks</span>
        </div>
      </header>

      {/* Top stats */}
      <section className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <Stat
          label="Paid-in"
          value={fmtUsd(snapshot.paid_in_usd, { compact: true })}
          hint={`Deployed ${fmtUsd(snapshot.deployed_usd, { compact: true })} + fee drag ${fmtUsd(snapshot.fee_drag_usd, { compact: true })}`}
        />
        <Stat
          label="P50 net pretax"
          value={fmtUsd(snapshot.total_p50_net_usd, { compact: true })}
          hint={`${fmtMultiple(snapshot.moic_on_paid_in)} on paid-in`}
          tone={snapshot.moic_on_paid_in > 1 ? "positive" : "negative"}
        />
        <Stat
          label="P50 after-tax"
          value={fmtUsd(snapshot.after_tax_p50_usd, { compact: true })}
          hint={`${fmtMultiple(snapshot.moic_after_tax)} after-tax · QSBS coverage ${fmtPct(snapshot.qsbs_coverage_pct, 0)}`}
        />
        <Stat
          label="P10 – P90 range"
          value={`${fmtUsd(snapshot.p10_net_pretax_usd, { compact: true })} – ${fmtUsd(snapshot.p90_net_pretax_usd, { compact: true })}`}
          hint="Monte Carlo over scenario distributions"
        />
      </section>

      {/* Notice banners */}
      <section className="space-y-3">
        <NoticeBanner notice={snapshot.audit_notice} variant="audit" />
        <NoticeBanner notice={snapshot.verification_notice} variant="verification" />
      </section>

      {/* Cash projection range */}
      <section className="space-y-3">
        <h2 className="text-lg font-semibold text-gray-900">Net-to-LP pretax range</h2>
        <div className="border border-gray-200 rounded-lg bg-white p-6">
          <RangeBar
            p10={cashProjection.p10_usd}
            p50={cashProjection.p50_usd}
            p90={cashProjection.p90_usd}
            paidIn={cashProjection.paid_in_usd}
          />
          <div className="text-xs text-gray-600 mt-6 grid grid-cols-2 md:grid-cols-4 gap-3">
            <div>
              <div className="text-gray-400 uppercase tracking-wide">Already received</div>
              <div className="tabular-nums text-gray-700">
                {fmtUsd(cashProjection.p50_composition.already_received_usd)}
              </div>
            </div>
            <div>
              <div className="text-gray-400 uppercase tracking-wide">Principal recovery</div>
              <div className="tabular-nums text-gray-700">
                {fmtUsd(cashProjection.p50_composition.principal_recovery_usd)}
              </div>
            </div>
            <div>
              <div className="text-gray-400 uppercase tracking-wide">Profit pretax</div>
              <div className="tabular-nums text-emerald-700">
                {fmtUsd(cashProjection.p50_composition.profit_pretax_usd)}
              </div>
            </div>
            <div>
              <div className="text-gray-400 uppercase tracking-wide">Carry haircut</div>
              <div className="tabular-nums text-red-700">
                −{fmtUsd(cashProjection.p50_composition.carry_usd)}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Top 5 positions with scenarios */}
      <section className="space-y-3">
        <h2 className="text-lg font-semibold text-gray-900">
          Top 5 positions by expected exit value
        </h2>
        <div className="space-y-3">
          {topPositions.map((p) => {
            const fev = lookupFundamentalEv(p.company);
            return (
              <div
                key={p.company}
                className="border border-gray-200 rounded-lg bg-white p-5 space-y-3"
              >
                <div className="flex justify-between items-baseline">
                  <div>
                    <div className="font-semibold text-gray-900">{p.company}</div>
                    <div className="text-xs text-gray-500">
                      {p.entry_round} entry {p.entry_date} · {p.cohort}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm tabular-nums text-gray-700">
                      Cost {fmtUsd(p.cost_usd)} · Dil-adj{" "}
                      {p.dilution_adjusted_mark_usd
                        ? fmtUsd(p.dilution_adjusted_mark_usd)
                        : "—"}
                    </div>
                    <div className="text-lg font-semibold tabular-nums">
                      P50 exit{" "}
                      {p.expected_exit_usd !== null
                        ? fmtUsd(p.expected_exit_usd)
                        : "—"}{" "}
                      <span className="text-sm text-gray-500 font-normal">
                        ({fmtMultiple(p.expected_multiple_on_cost ?? 0, 1)} cost)
                      </span>
                    </div>
                  </div>
                </div>
                {fev && <ScenarioBar scenarios={fev.scenarios} />}
              </div>
            );
          })}
        </div>
      </section>

      {/* Full position table */}
      <section className="space-y-3">
        <h2 className="text-lg font-semibold text-gray-900">All positions ({positions.length})</h2>
        <p className="text-sm text-gray-600 max-w-3xl">
          The <span className="font-semibold">Δ vs GP</span> column shows where the GP's mark
          differs from the dilution-aware audit. Large positive deltas mean the GP is being
          conservative; large negative deltas mean the GP's mark over-states LP value.
        </p>
        <PositionTable positions={positions} />
      </section>

      {/* Footer */}
      <footer className="text-xs text-gray-500 border-t pt-6 leading-relaxed">
        <p>
          Sample fund built from a real early-stage rolling fund's Q1 2021 cohort, sized to a
          hypothetical $100K LP commitment. Per-position marks and scenarios are illustrative
          reconstructions from public signals — not the fund manager's actual marks, not investment
          advice. Methodology in <code className="bg-gray-100 px-1 py-0.5 rounded">methodology/</code>
          ; pipeline in <code className="bg-gray-100 px-1 py-0.5 rounded">pipeline/</code>.
        </p>
      </footer>
    </main>
  );
}
