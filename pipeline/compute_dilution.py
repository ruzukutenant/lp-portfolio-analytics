"""
Step 1: Cap-table dilution math.

For each position in sample_inputs/lp_investments.csv, walk the round history
from sample_inputs/round_history.json and compute:

    entry_pct = LP_cost / entry_post_money
    cumulative_survival = Π (1 - raise/post) across all priced rounds since entry
    dilution_adjusted_mark = entry_pct × cumulative_survival × current_post_money

Output: sample_fund/audit/dilution_adjusted.json

Where post-money is undisclosed, fall back to stage-multiplier imputation.
Where the company is shut down (status: Closed), mark to zero.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
LP_CSV = REPO_ROOT / "sample_inputs" / "lp_investments.csv"
ROUND_HISTORY = REPO_ROOT / "sample_inputs" / "round_history.json"
OUTPUT = REPO_ROOT / "sample_fund" / "audit" / "dilution_adjusted.json"

STAGE_MULTIPLIERS = {
    "Pre-Seed": 8.0,
    "Seed": 5.0,
    "Series A": 4.5,
    "Series B": 5.5,
    "Series C": 7.0,
    "Series D": 10.0,
    "Series E": 10.0,
    "Bridge": 1.2,
    "Series A extension": 4.5,
    "Series B extension": 5.5,
    "Series C extension": 7.0,
    "Pre-Series A": 4.5,
    "Seed extension": 5.0,
    "Bridge / down round": 1.0,
    "Bridge 2 / down": 1.0,
}


def impute_post_money(round_record: dict) -> Optional[float]:
    """Impute post-money via stage multiplier when not disclosed."""
    raise_amt = round_record.get("raise_usd")
    stage = round_record.get("round", "")
    multiplier = STAGE_MULTIPLIERS.get(stage)
    if raise_amt and multiplier:
        return raise_amt * multiplier
    return None


def post_money(round_record: dict) -> Optional[float]:
    disclosed = round_record.get("post_money_usd")
    if disclosed:
        return float(disclosed)
    return impute_post_money(round_record)


def compute_position(
    cost_usd: float,
    rounds: list[dict],
    status: str,
) -> dict:
    """Compute dilution-adjusted mark for a single position."""
    if status == "Closed":
        return {
            "entry_pct": None,
            "entry_post_money_usd": None,
            "current_post_money_usd": None,
            "cumulative_survival": None,
            "dilution_adjusted_mark_usd": 0.0,
            "rounds_since_entry": 0,
            "notes": f"Marked to zero — status: {status}",
        }

    if not rounds:
        return {
            "entry_pct": None,
            "entry_post_money_usd": None,
            "current_post_money_usd": None,
            "cumulative_survival": None,
            "dilution_adjusted_mark_usd": None,
            "rounds_since_entry": 0,
            "notes": "No round history available",
        }

    # The first round in the list is entry; subsequent rounds dilute.
    entry_round = rounds[0]
    entry_post = post_money(entry_round)
    if not entry_post:
        return {
            "entry_pct": None,
            "entry_post_money_usd": None,
            "current_post_money_usd": None,
            "cumulative_survival": None,
            "dilution_adjusted_mark_usd": None,
            "rounds_since_entry": 0,
            "notes": "Entry post-money missing and not imputable",
        }

    entry_pct = cost_usd / entry_post

    cumulative_survival = 1.0
    for r in rounds[1:]:
        post = post_money(r)
        raise_amt = r.get("raise_usd")
        if not post or not raise_amt:
            continue
        survival = 1.0 - (raise_amt / post)
        cumulative_survival *= survival

    current_post = post_money(rounds[-1]) if len(rounds) > 1 else entry_post
    dil_adj = entry_pct * cumulative_survival * current_post

    return {
        "entry_pct": round(entry_pct, 8),
        "entry_post_money_usd": entry_post,
        "current_post_money_usd": current_post,
        "cumulative_survival": round(cumulative_survival, 6),
        "dilution_adjusted_mark_usd": round(dil_adj, 2),
        "rounds_since_entry": len(rounds) - 1,
        "notes": None,
    }


def main() -> None:
    rounds_by_company = json.loads(ROUND_HISTORY.read_text())
    # Drop comment keys
    rounds_by_company = {k: v for k, v in rounds_by_company.items() if not k.startswith("_")}

    results = []
    with LP_CSV.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            company = row["company"]
            cost = float(row["cost_usd"])
            gp_mark = float(row["gp_current_mark_usd"])
            status = row["status"]
            rounds = rounds_by_company.get(company, [])

            audit = compute_position(cost, rounds, status)

            results.append({
                "company": company,
                "cost_usd": cost,
                "entry_date": row["invest_date"],
                "entry_round": row["entry_round"],
                "status": status,
                "gp_current_mark_usd": gp_mark,
                "gp_multiple": float(row["gp_multiple"]),
                **audit,
                "audit_vs_gp_delta_pct": (
                    round(((audit["dilution_adjusted_mark_usd"] - gp_mark) / gp_mark) * 100, 1)
                    if audit["dilution_adjusted_mark_usd"] is not None and gp_mark > 0
                    else None
                ),
            })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(results, indent=2))

    # Print summary
    total_cost = sum(r["cost_usd"] for r in results)
    total_gp_mark = sum(r["gp_current_mark_usd"] for r in results)
    total_dil_adj = sum(r["dilution_adjusted_mark_usd"] or 0 for r in results)
    print(f"Positions processed: {len(results)}")
    print(f"Total cost basis: ${total_cost:,.0f}")
    print(f"Total GP mark:    ${total_gp_mark:,.0f}  ({total_gp_mark/total_cost:.2f}× cost)")
    print(f"Total dilAdj:     ${total_dil_adj:,.0f}  ({total_dil_adj/total_cost:.2f}× cost)")
    print(f"Naive over-state: {((total_gp_mark - total_dil_adj) / total_dil_adj * 100):.1f}%")
    print(f"\nOutput: {OUTPUT}")


if __name__ == "__main__":
    main()
