"""
Step 2: Comp-anchored scenario weights → expected exit value per position.

For each position, apply probability-weighted multiplier scenarios and a
forward dilution factor (DF), producing:

    expected_exit_usd = dilAdj × Σ(prob × mult) × DF

Scenarios are hand-set here based on the comp anchors in methodology/comp_anchors.md
and the AI tailwind framework in methodology/ai_tailwind_assumptions.md.

In a real deployment, scenarios would be a separate JSON input file edited
during the verification step. Inline for clarity in the public demo.

Output: sample_fund/audit/corrected_ev.json
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INPUT = REPO_ROOT / "sample_fund" / "audit" / "dilution_adjusted.json"
OUTPUT = REPO_ROOT / "sample_fund" / "audit" / "corrected_ev.json"


# Per-position scenarios. Each position has 3 scenarios (bull/base/bear) with
# probabilities summing to 1.0. Multiplier is on dilution-adjusted current mark.
# DF (dilution factor) is forward dilution: 0.875^remaining_rounds.
SCENARIOS = {
    "BusRight": {
        "cohort": "vertical_saas",
        "scenarios": [
            {"label": "bull",  "prob": 0.25, "mult": 4.5,  "_anchor": "Procore-style at 25× rev, Series C exit 2029"},
            {"label": "base",  "prob": 0.55, "mult": 2.0,  "_anchor": "Vertical SaaS M&A at 6-8× rev"},
            {"label": "bear",  "prob": 0.20, "mult": 0.5,  "_anchor": "Encore competitive pressure caps growth"},
        ],
        "df": 0.766,  # 2 more rounds expected
        "exit_year": 2029,
    },
    "Hone Health": {
        "cohort": "consumer_health",
        "scenarios": [
            {"label": "bull",  "prob": 0.30, "mult": 3.5,  "_anchor": "Hims-style scale to $300M ARR + IPO"},
            {"label": "base",  "prob": 0.50, "mult": 1.4,  "_anchor": "PE buyout at 4-5× rev (telehealth comp)"},
            {"label": "bear",  "prob": 0.20, "mult": 0.4,  "_anchor": "GLP-1 attribution shift / multiple compression"},
        ],
        "df": 0.875,  # 1 more round (Series C)
        "exit_year": 2028,
    },
    "Eight Sleep": {
        "cohort": "consumer_hardware",
        "scenarios": [
            {"label": "bull",  "prob": 0.40, "mult": 2.5,  "_anchor": "IPO 2027-28 at $4B+ valuation"},
            {"label": "base",  "prob": 0.45, "mult": 1.3,  "_anchor": "Strategic acquisition at 3-4× rev"},
            {"label": "bear",  "prob": 0.15, "mult": 0.6,  "_anchor": "Hardware-margin compression / tariff exposure"},
        ],
        "df": 1.0,  # profitable, no more rounds expected
        "exit_year": 2028,
    },
    "Atlys": {
        "cohort": "vertical_saas_ai",
        "scenarios": [
            {"label": "bull",  "prob": 0.35, "mult": 5.0,  "_anchor": "Category-defining travel infra, $1B+ exit"},
            {"label": "base",  "prob": 0.45, "mult": 2.2,  "_anchor": "Series B at $500M, M&A at $1.5B"},
            {"label": "bear",  "prob": 0.20, "mult": 0.4,  "_anchor": "Regulatory / customer concentration risk"},
        ],
        "df": 0.766,  # 2 more rounds
        "exit_year": 2030,
    },
    "CowryWise": {
        "cohort": "fintech_emerging",
        "scenarios": [
            {"label": "bull",  "prob": 0.20, "mult": 3.5,  "_anchor": "Nigerian fintech consolidation, M&A at $250M+"},
            {"label": "base",  "prob": 0.50, "mult": 1.5,  "_anchor": "Modest growth, strategic acquisition"},
            {"label": "bear",  "prob": 0.30, "mult": 0.3,  "_anchor": "Naira devaluation, regulatory uncertainty"},
        ],
        "df": 0.766,
        "exit_year": 2029,
    },
    "Fion Technologies": {
        "cohort": "other",
        "scenarios": [
            {"label": "bull",  "prob": 0.10, "mult": 3.0,  "_anchor": "Long-tail acquihire or strategic exit"},
            {"label": "base",  "prob": 0.40, "mult": 1.0,  "_anchor": "Flat — holds bridge valuation"},
            {"label": "bear",  "prob": 0.50, "mult": 0.0,  "_anchor": "Wind-down, no further raise possible"},
        ],
        "df": 0.875,
        "exit_year": 2027,
    },
    "Yac": {
        "cohort": "other",
        "scenarios": [
            {"label": "wipe", "prob": 1.0, "mult": 0.0, "_anchor": "Shutdown Aug 2024, wind-down distribution received"},
        ],
        "df": 1.0,
        "exit_year": 2024,
        "_realized": True,
    },
    "Journey": {
        "cohort": "other",
        "scenarios": [
            {"label": "bull",  "prob": 0.05, "mult": 2.5,  "_anchor": "Unlikely acquihire"},
            {"label": "base",  "prob": 0.30, "mult": 1.0,  "_anchor": "Flat / silent"},
            {"label": "bear",  "prob": 0.65, "mult": 0.0,  "_anchor": "No signal in 2+ years"},
        ],
        "df": 0.875,
        "exit_year": 2027,
    },
    "Fifty Foods": {
        "cohort": "consumer_brand",
        "scenarios": [
            {"label": "bull",  "prob": 0.25, "mult": 4.0,  "_anchor": "Strategic CPG acquisition (post-Immi rebrand)"},
            {"label": "base",  "prob": 0.45, "mult": 1.5,  "_anchor": "Modest growth, mid-size CPG M&A at 3× rev"},
            {"label": "bear",  "prob": 0.30, "mult": 0.3,  "_anchor": "CPG margin compression, slow growth"},
        ],
        "df": 0.875,
        "exit_year": 2029,
    },
    "Valiu": {
        "cohort": "other",
        "scenarios": [
            {"label": "wipe", "prob": 1.0, "mult": 0.0, "_anchor": "Closed 2023, crypto remittance category did not work"},
        ],
        "df": 1.0,
        "exit_year": 2023,
        "_realized": True,
    },
    "Facet": {
        "cohort": "fintech_alt",
        "scenarios": [
            {"label": "bull",  "prob": 0.20, "mult": 3.0,  "_anchor": "Robo-advisor M&A at 5-7× rev"},
            {"label": "base",  "prob": 0.50, "mult": 1.5,  "_anchor": "Flat-ish; secondary sale at modest premium"},
            {"label": "bear",  "prob": 0.30, "mult": 0.5,  "_anchor": "Wealth-mgmt margin compression"},
        ],
        "df": 0.875,
        "exit_year": 2028,
    },
    "On Deck": {
        "cohort": "other",
        "scenarios": [
            {"label": "bull",  "prob": 0.10, "mult": 2.0,  "_anchor": "Niche fellowship niche survives at small scale"},
            {"label": "base",  "prob": 0.30, "mult": 0.7,  "_anchor": "Holds bridge valuation; minimal exit"},
            {"label": "bear",  "prob": 0.60, "mult": 0.0,  "_anchor": "Further down round / wind-down"},
        ],
        "df": 1.0,
        "exit_year": 2027,
    },
    "Peachy Patients": {
        "cohort": "other",
        "scenarios": [
            {"label": "bull",  "prob": 0.05, "mult": 3.0,  "_anchor": "Strategic acquihire"},
            {"label": "base",  "prob": 0.25, "mult": 1.0,  "_anchor": "Flat / silent"},
            {"label": "bear",  "prob": 0.70, "mult": 0.0,  "_anchor": "Pre-seed silent for years; high mortality"},
        ],
        "df": 0.766,
        "exit_year": 2028,
    },
    "Farmstead": {
        "cohort": "other",
        "scenarios": [
            {"label": "wipe", "prob": 1.0, "mult": 0.0, "_anchor": "Closed 2022, grocery delivery did not work post-COVID"},
        ],
        "df": 1.0,
        "exit_year": 2022,
        "_realized": True,
    },
    "Haus": {
        "cohort": "consumer_brand",
        "scenarios": [
            {"label": "bull",  "prob": 0.25, "mult": 3.5,  "_anchor": "Low-ABV category leader, strategic spirits M&A"},
            {"label": "base",  "prob": 0.50, "mult": 1.5,  "_anchor": "Mid-size CPG acquisition at 2-3× rev"},
            {"label": "bear",  "prob": 0.25, "mult": 0.4,  "_anchor": "DTC margin compression, brand fatigue"},
        ],
        "df": 0.875,
        "exit_year": 2028,
    },
    "MarketerHire": {
        "cohort": "other",
        "scenarios": [
            {"label": "wipe", "prob": 1.0, "mult": 0.0, "_anchor": "Closed March 2024, marketplace economics never converged"},
        ],
        "df": 1.0,
        "exit_year": 2024,
        "_realized": True,
    },
}


def main() -> None:
    dilution_data = json.loads(INPUT.read_text())

    results = []
    for pos in dilution_data:
        company = pos["company"]
        dil_adj = pos.get("dilution_adjusted_mark_usd") or 0.0

        spec = SCENARIOS.get(company)
        if not spec:
            print(f"WARNING: no scenarios for {company}; skipping")
            continue

        weighted_mult = sum(s["prob"] * s["mult"] for s in spec["scenarios"])
        expected_exit = dil_adj * weighted_mult * spec["df"]

        results.append({
            "company": company,
            "cohort": spec["cohort"],
            "cost_usd": pos["cost_usd"],
            "dilution_adjusted_mark_usd": dil_adj,
            "weighted_multiplier": round(weighted_mult, 3),
            "df": spec["df"],
            "expected_exit_usd": round(expected_exit, 0),
            "exit_year": spec["exit_year"],
            "realized": spec.get("_realized", False),
            "scenarios": spec["scenarios"],
            "expected_multiple_on_cost": round(expected_exit / pos["cost_usd"], 2) if pos["cost_usd"] > 0 else None,
        })

    # Rank by expected_exit_usd descending
    results.sort(key=lambda r: r["expected_exit_usd"], reverse=True)
    for i, r in enumerate(results, 1):
        r["rank"] = i

    OUTPUT.write_text(json.dumps(results, indent=2))

    total_cost = sum(r["cost_usd"] for r in results)
    total_exit = sum(r["expected_exit_usd"] for r in results)
    print(f"Positions: {len(results)}")
    print(f"Total cost basis: ${total_cost:,.0f}")
    print(f"Gross expected exit (sum): ${total_exit:,.0f}  ({total_exit/total_cost:.2f}× cost)")
    print(f"\nTop 5 by expected exit:")
    for r in results[:5]:
        print(f"  {r['company']:20s} dilAdj=${r['dilution_adjusted_mark_usd']:>9,.0f}  EV=${r['expected_exit_usd']:>9,.0f}  ({r['expected_multiple_on_cost']:.1f}× cost)")
    print(f"\nOutput: {OUTPUT}")


if __name__ == "__main__":
    main()
