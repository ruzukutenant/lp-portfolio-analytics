# Dilution math for LP positions

The single biggest source of mark over-statement for LPs in SPVs / SAFEs is ignoring cumulative dilution from rounds after entry. This doc lays out the right formula and why naive approaches fail.

## The rule

For each position, compute:

```
entry_ownership_pct = LP_cost / entry_post_money
cumulative_survival = Π (1 - raise / post) across all subsequent priced rounds
dilution_adjusted_current_mark = entry_ownership_pct × cumulative_survival × current_post_money
```

Apply scenario multipliers and a dilution factor (DF) to that dilution-adjusted current mark — not to a naive "current_post / entry_post × cost" mark.

## Worked example

LP invests $1,000 at $20M post-money seed. Two subsequent rounds:

| Round | Raise | Post | Dilution factor |
|---|---:|---:|---:|
| Entry (seed) | $4M | $20M | (entry) |
| Series A | $15M | $75M | 1 - 15/75 = 0.80 |
| Series B | $40M | $250M | 1 - 40/250 = 0.84 |

Compute:

```
entry_pct = $1,000 / $20M = 0.00005 = 0.005%
cumulative_survival = 0.80 × 0.84 = 0.672
dilAdj = 0.00005 × 0.672 × $250M = $8,400
```

Naive comparison:

```
naive_mark = ($250M / $20M) × $1,000 = $12,500
```

Naive over-states by 49%. That's the typical magnitude across an early-entry portfolio after 2-3 rounds.

## Why it compounds

A single round at 15% dilution sounds small but accumulates fast:

| Rounds since entry | Cumulative survival | Naive over-state |
|---|---:|---:|
| 1 | 0.85 | 18% |
| 2 | 0.72 | 39% |
| 3 | 0.61 | 64% |
| 4 | 0.52 | 92% |

Early-entry positions that survive to Series C or D will be 2× over-marked by the naive method. For an LP, this is the difference between thinking the portfolio is up 2.5× and it actually being up 1.3×.

## Where post-money is undisclosed

About 40% of priced rounds aren't public. Impute via stage multipliers:

| Stage | Typical post = raise × |
|---|---:|
| Pre-Seed | 8× |
| Seed | 5× |
| Series A | 4.5× |
| Series B | 5.5× |
| Series C | 7× |
| Series D+ | 10× |

These are rough but better than guessing. Where the imputation feels too uncertain, fall back to a manual override anchored to the GP's stated mark + revenue signals.

## SAFE-cap caveat

When LPs enter via SAFE that converts at a cap below the next round price, true entry-pct is higher than `cost / next_round_post`. If the audit framework treats SAFE entries at the next-round price (no cap discount applied), dilution-adjusted marks are systematically conservative by ~10-25% across positions where SAFE caps applied.

If you have the cap data, use `cost / safe_cap` for entry_pct instead.

## Dilution factor (DF) for forward projections

Beyond current dilution, expected future dilution from rounds-to-exit:

```
DF = 0.875 ^ remaining_rounds_to_exit
```

`0.875` per round is conservative — assumes ~12.5% average dilution per round. For capital-efficient companies that won't raise again, use DF = 1.00. For hardware / heavy-capex companies that will go through 3-4 more rounds, DF can compress to 0.50-0.60.

| Remaining rounds | DF |
|---|---:|
| 0 (next is exit) | 1.00 |
| 1 | 0.875 |
| 2 | 0.766 |
| 3 | 0.670 |
| 4 | 0.586 |

## What this corrects

Common naive approaches and their failure modes:

1. **"Trust the GP's mark"** — GP marks are typically stale by 1-2 quarters and often don't fully reflect dilution either (since they show post-money for the company, not LP fractional ownership)
2. **"current_post / entry_post × cost"** — ignores every round in between, over-states by 30-90%
3. **"Compute it once and stop"** — re-run on every new round announcement, or marks drift again

## When to apply

Every meaningful position (top-N by expected exit value). For tail positions worth <$5K dilAdj, the simpler "use the GP's mark" is OK because the dollars don't matter for portfolio P50.

## Related

- `audit_and_verification.md` — the two-step refresh framework that wraps this formula
- `cash_projection.md` — net-cash conversion (fees, carry, taxes) downstream of dilAdj
