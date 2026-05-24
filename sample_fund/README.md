# Sample fund — Rolling Fund 2021 Q1 cohort

This directory holds the data and computed outputs for the sample fund used throughout this repo. The cohort is real (Sahil Lavingia's Rolling Fund, 2021 Q1 quarter, 16 positions); the LP check size is hypothetical ($100K commitment); and the per-position marks are **illustrative reconstructions from public signals** (announced raises, exit news, shutdowns) — they are not the fund manager's actual marks.

## Why this cohort?

It's a good demonstration set because it covers the full range:

| Outcome type | Positions | Why useful |
|---|---|---|
| Clear winners with funding momentum | Hone Health, Eight Sleep, Atlys, BusRight | Show how comp anchors + AI tailwind credit constrain bull cases |
| Cap-table dilution material | Hone Health (3 rounds), BusRight (3 rounds), MarketerHire (2 rounds before shutdown) | Show how naive marks over-state |
| Walking dead | On Deck, Fion Technologies, Journey, Peachy Patients | Show what bear-case math looks like |
| Confirmed shutdowns | Yac, MarketerHire, Farmstead, Valiu | Show the zero-mark + §1244 ordinary-loss path |
| Mixed AI/non-AI exposure | Atlys (AI-adjacent), Hone Health (consumer health), CowryWise (fintech) | Show selective AI tailwind credit |
| QSBS-eligible / not | 10 of 16 eligible (62.5% by count, ~92% by expected exit value) | Show how QSBS coverage swings after-tax math |

The cohort produces a P50 of ~$256K net pretax on $118K paid-in (2.17×), with the P10-P90 range spanning ~$176K - $346K. That's a typical "good early-stage cohort" outcome — not a moonshot, not a disaster.

## Layout

```
sample_fund/
├── README.md                    ← this file
├── audit/
│   ├── dilution_adjusted.json   ← step 1 output: cap-table dilution math
│   └── corrected_ev.json        ← step 2 output: scenario-weighted expected exits
├── verification/                ← (where verification-step outputs land)
│   └── README.md
└── cash_projection.json         ← step 3 output: P10/P50/P90 net-cash math
```

The data flow:

```
sample_inputs/
  ├── lp_investments.csv         → │
  ├── round_history.json         → │  pipeline/compute_dilution.py
  ├── k1_summary.json            → │  → sample_fund/audit/dilution_adjusted.json
  └── distribution_notice.json   → │  → ...corrected_ev.json
                                    │  → ...cash_projection.json
                                    │  → dashboard/data/*.json
```

## Illustrative-only disclaimer

The per-position cost basis numbers, current marks, scenario weights, and expected exits in this directory are **constructed for demonstration**. They are anchored to public signals where available (announced rounds, confirmed shutdowns, comp anchors from `methodology/comp_anchors.md`) but they should not be quoted as the fund manager's marks, as the LP's actual returns, or as anyone's investment recommendation.

The fund manager (Sahil Lavingia) cleared use of the cohort's company names for this public reference implementation. Nothing here represents his official position on any portfolio company.

## To rebuild

```bash
cd pipeline
python compute_dilution.py        # → sample_fund/audit/dilution_adjusted.json
python compute_corrected_ev.py    # → sample_fund/audit/corrected_ev.json
python cash_return_model.py       # → sample_fund/cash_projection.json
python emit_dashboard_json.py     # → dashboard/data/*.json
```

To change scenarios (the verification step), edit the `SCENARIOS` dict in `pipeline/compute_corrected_ev.py` and re-run from there.
