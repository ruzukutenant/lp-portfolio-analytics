"""
Step 3: Net-to-LP cash projection (fees, carry, taxes).

Reads:
  - sample_fund/audit/corrected_ev.json     (per-position expected exit, gross-to-fund)
  - sample_inputs/k1_summary.json           (QSBS coverage by position)
  - sample_inputs/distribution_notice.json  (already-received cash)

Computes:
  - paid_in (deployed × fee_drag_multiplier for rolling-fund pattern)
  - gross-to-fund total exit
  - carry haircut (20% on profit)
  - gross-to-LP pretax
  - after-tax (QSBS-weighted blended rate)
  - P10 / P50 / P90 sensitivity bands via Monte Carlo over scenario distributions

Output: sample_fund/cash_projection.json
"""
from __future__ import annotations

import json
import random
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EV_INPUT = REPO_ROOT / "sample_fund" / "audit" / "corrected_ev.json"
K1_INPUT = REPO_ROOT / "sample_inputs" / "k1_summary.json"
DIST_INPUT = REPO_ROOT / "sample_inputs" / "distribution_notice.json"
OUTPUT = REPO_ROOT / "sample_fund" / "cash_projection.json"

# Fund-level economics (rolling-fund pattern)
FEE_DRAG_MULTIPLIER = 1.2715  # paid-in = deployed × this
CARRY_PCT = 0.20  # 20% European waterfall on profit
QSBS_STATE_TAX_PCT = 0.05  # state LTCG only on QSBS gains
NON_QSBS_BLENDED_LTCG_PCT = 0.288  # 15% fed + 8% NIIT + 5% state
MONTE_CARLO_TRIALS = 5000


def per_position_random_draw(scenarios: list[dict]) -> float:
    """Sample one multiplier from a position's scenario distribution."""
    r = random.random()
    cumulative = 0.0
    for s in scenarios:
        cumulative += s["prob"]
        if r <= cumulative:
            return s["mult"]
    return scenarios[-1]["mult"]


def main() -> None:
    positions = json.loads(EV_INPUT.read_text())
    k1 = json.loads(K1_INPUT.read_text())
    distributions = json.loads(DIST_INPUT.read_text())

    qsbs_by_company = {p["company"]: p["qsbs_eligible"] for p in k1["positions"]}

    deployed = sum(p["cost_usd"] for p in positions)
    paid_in = deployed * FEE_DRAG_MULTIPLIER
    fee_drag = paid_in - deployed
    already_distributed = sum(d.get("gross_distribution_usd", 0) for d in distributions)

    # Point estimate (P50 anchor): sum of probability-weighted expected exits
    gross_exit_p50 = sum(p["expected_exit_usd"] for p in positions) + already_distributed
    profit_p50 = max(0, gross_exit_p50 - paid_in)
    carry_p50 = profit_p50 * CARRY_PCT
    net_pretax_p50 = gross_exit_p50 - carry_p50

    # Tax math: per-position because QSBS eligibility varies
    qsbs_profit = 0.0
    non_qsbs_profit = 0.0
    for p in positions:
        position_profit = max(0, p["expected_exit_usd"] - p["cost_usd"])
        # apportion carry pro-rata across positions with profit
        position_carry = position_profit * CARRY_PCT
        position_net_profit = position_profit - position_carry
        if qsbs_by_company.get(p["company"]):
            qsbs_profit += position_net_profit
        else:
            non_qsbs_profit += position_net_profit

    tax_p50 = (qsbs_profit * QSBS_STATE_TAX_PCT) + (non_qsbs_profit * NON_QSBS_BLENDED_LTCG_PCT)
    after_tax_p50 = net_pretax_p50 - tax_p50

    # Monte Carlo for P10 / P90 sensitivity
    trials = []
    for _ in range(MONTE_CARLO_TRIALS):
        trial_gross = already_distributed
        for p in positions:
            if p.get("realized"):
                continue  # already in distributions
            mult = per_position_random_draw(p["scenarios"])
            trial_gross += p["dilution_adjusted_mark_usd"] * mult * p["df"]
        trial_profit = max(0, trial_gross - paid_in)
        trial_net = trial_gross - (trial_profit * CARRY_PCT)
        trials.append(trial_net)

    trials.sort()
    p10 = trials[int(0.10 * MONTE_CARLO_TRIALS)]
    p90 = trials[int(0.90 * MONTE_CARLO_TRIALS)]

    result = {
        "model_version": "sample-fund cash projection v1",
        "fund_economics": {
            "pattern": "rolling_fund",
            "fee_drag_multiplier": FEE_DRAG_MULTIPLIER,
            "carry_pct": CARRY_PCT,
            "qsbs_state_tax_pct": QSBS_STATE_TAX_PCT,
            "non_qsbs_blended_ltcg_pct": NON_QSBS_BLENDED_LTCG_PCT,
        },
        "deployed_usd": round(deployed, 0),
        "paid_in_usd": round(paid_in, 0),
        "fee_drag_usd": round(fee_drag, 0),
        "already_distributed_usd": round(already_distributed, 0),
        "p50": {
            "gross_exit_usd": round(gross_exit_p50, 0),
            "carry_usd": round(carry_p50, 0),
            "net_pretax_usd": round(net_pretax_p50, 0),
            "tax_usd": round(tax_p50, 0),
            "after_tax_usd": round(after_tax_p50, 0),
            "moic_on_paid_in": round(net_pretax_p50 / paid_in, 2),
            "moic_after_tax": round(after_tax_p50 / paid_in, 2),
        },
        "range_net_pretax": {
            "p10": round(p10, 0),
            "p50": round(net_pretax_p50, 0),
            "p90": round(p90, 0),
        },
        "qsbs_split": {
            "qsbs_eligible_profit_usd": round(qsbs_profit, 0),
            "non_qsbs_profit_usd": round(non_qsbs_profit, 0),
            "qsbs_coverage_pct": round(
                qsbs_profit / max(1, qsbs_profit + non_qsbs_profit), 3
            ),
        },
    }

    OUTPUT.write_text(json.dumps(result, indent=2))

    print(f"Deployed:          ${deployed:>10,.0f}")
    print(f"Paid-in:           ${paid_in:>10,.0f}  (fee drag = ${fee_drag:,.0f})")
    print(f"Already received:  ${already_distributed:>10,.0f}")
    print()
    print(f"P50 gross exit:    ${gross_exit_p50:>10,.0f}")
    print(f"P50 carry:         ${carry_p50:>10,.0f}")
    print(f"P50 net pretax:    ${net_pretax_p50:>10,.0f}  ({net_pretax_p50/paid_in:.2f}× paid-in)")
    print(f"P50 tax:           ${tax_p50:>10,.0f}  (QSBS coverage {result['qsbs_split']['qsbs_coverage_pct']*100:.0f}%)")
    print(f"P50 after-tax:     ${after_tax_p50:>10,.0f}  ({after_tax_p50/paid_in:.2f}× paid-in)")
    print()
    print(f"Range net pretax:  P10 ${p10:>10,.0f}  P50 ${net_pretax_p50:>10,.0f}  P90 ${p90:>10,.0f}")
    print(f"\nOutput: {OUTPUT}")


if __name__ == "__main__":
    main()
