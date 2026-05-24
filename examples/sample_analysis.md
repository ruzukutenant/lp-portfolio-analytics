# Sample analysis — Rolling Fund 2021 Q1 cohort

A worked example of what the [lp-portfolio-analytics](https://github.com/ruzukutenant/lp-portfolio-analytics) pipeline produces. Cohort is real (16 positions from an early-stage rolling fund's 2021 Q1 quarter); the LP check size is hypothetical ($100K commitment); per-position marks are **illustrative reconstructions from public signals** (announced raises, exit news, shutdowns), not the fund manager's actual marks.

The point isn't the specific dollar numbers. The point is what the framework surfaces vs. what GP-reported marks would tell you.

---

## Headline

- **Paid-in**: $118K ($100K commit + ~21% rolling-fund fee drag)
- **P50 net pretax**: $256K (**2.17× paid-in**, ~12% IRR over ~6 years)
- **Range (P10–P90)**: $176K – $346K
- **After-tax P50**: $244K (2.06× paid-in, 92% QSBS coverage on expected gain)

Good early-stage cohort. Not a moonshot, not a disaster.

---

## The audit finding — naive GP marks over-state by ~113%

Stacking the GP's current marks across all 16 positions gives an aggregate of **$390K** (~4.2× cost). Re-marking each position with cap-table dilution math gives **$183K** (~2.0× cost). The naive view over-states the LP's economic claim by 113%.

```
entry_pct        = LP_cost / entry_post_money
cumul_survival   = Π (1 − raise/post) across every priced round since entry
dilution_adj_mark = entry_pct × cumul_survival × current_post_money
```

This isn't a critique of the GP — most GP reporting shows post-money values for the company, not LP fractional ownership over time. But if you take the GP's number at face value and run cash projections off it, you'll be ~50% too optimistic in aggregate. Three rounds of "modest" 15% dilution compound to a 39% haircut on your original ownership percentage.

The verification step takes this further: bottoms-up rebuild of 16 positions against the [exit comp anchors](https://github.com/ruzukutenant/lp-portfolio-analytics/blob/main/methodology/comp_anchors.md) (Auth0 at 28× rev, UserTesting at $1.3B, CoreWeave compressed from 25× to 12×, etc.) lands within ±5% of the audit aggregate — so the dilution-adjusted marks aren't being secretly bailed out by aggressive scenario weights.

---

## Top 5 positions by expected exit value

| Company | Entry round | Cost | GP mark | Dil-adj mark | Δ vs GP | P50 exit | × cost |
|---|---|---:|---:|---:|---:|---:|---:|
| Hone Health | Seed 2021-02 | $6,200 | $68,200 | $57,347 | −16% | $91,826 | 14.8× |
| Atlys | Pre-Seed 2021-03 | $4,500 | $49,500 | $31,596 | −36% | $68,251 | 15.2× |
| BusRight | Seed 2021-01 | $5,800 | $46,400 | $16,042 | **−65%** | $28,571 | 4.9× |
| Eight Sleep | Series C 2021-02 | $9,400 | $103,400 | $15,289 | **−85%** | $25,609 | 2.7× |
| Fifty Foods (Immi) | Seed 2021-02 | $5,600 | $28,000 | $14,000 | −50% | $21,621 | 3.9× |

The biggest dilution gap is **Eight Sleep**. Entry was at the Series C post of $415M — but the company's gone through a Series C extension at $720M and (per the model's assumption) won't raise again before exit. The LP-fraction math is brutal here: a position that looks like an 11× on the GP statement is actually ~1.6× on dilution-aware basis, and the forward expected value isn't much above current dilAdj mark because there's no more multiple expansion to capture.

**BusRight** is the opposite story — looks like a winner on the GP statement (8× mark), but it's been through three priced rounds since entry (Seed → Series A → A-extension), each diluting the original Seed stake. The forward case is healthy (likely Series B + path to growth-stage exit), but the LP only owns ~35% of the original entry percentage.

---

## Scenario discipline — what's driving the expected exits

Each position has bull/base/bear scenarios anchored to public exit comps. A representative set:

**Hone Health (consumer health / telehealth)**
- Bull (30%, 3.5×): scales to $300M ARR + IPO at Hims-style multiple
- Base (50%, 1.4×): PE buyout at 4-5× rev, the telehealth M&A comp
- Bear (20%, 0.4×): GLP-1 attribution shift, multiple compression

Anchor: Hims at ~4-5× rev publicly. Capped the bull case there because consumer healthcare M&A historically pays 4-6× revenue, not SaaS-style 10×+.

**On Deck (services / cohort education)**
- Bull (10%, 2.0×): niche fellowship survives at small scale
- Base (30%, 0.7×): holds bridge valuation
- Bear (60%, 0.0×): further down round or wind-down

Down-round signal in the founder email made this nearly a binary write-down. Notable that this is non-QSBS-eligible (services business, §1202(e)(3) exclusion) — so even the bull case has worse after-tax treatment.

**Atlys (vertical SaaS, cross-border)**
- Bull (35%, 5.0×): category-defining travel infrastructure, $1B+ exit
- Base (45%, 2.2×): Series B at $500M, M&A at $1.5B
- Bear (20%, 0.4×): regulatory / customer concentration risk

AI-tailwind credit pushed the bull weight from a default ~20% to 35% — the company just closed a Series A at $185M post on 280% YoY growth, which is foundation-model-trajectory pacing (see [ai_tailwind_assumptions.md](https://github.com/ruzukutenant/lp-portfolio-analytics/blob/main/methodology/ai_tailwind_assumptions.md) for why "growth decelerates by year 3" is the wrong default in this regime).

---

## Cash composition at P50

```
Gross-to-fund exit (sum across 16 positions + already received) = $291K
  − Carry (20% on profit above paid-in)                          = $35K
  = Net-to-LP pretax                                             = $256K

Already received (Yac wind-down distribution)                    = $5K
+ Principal recovery (back to paid-in)                           = $114K
+ Profit pretax                                                  = $138K
= Net pretax P50                                                 = $256K

  − Tax: 92% QSBS coverage × 5% state-only + 8% non-QSBS × 28.8% = $13K
  = After-tax P50                                                = $244K
```

The QSBS coverage is unusually high because the audit happens to concentrate expected exit in §1202-eligible C-corps (Hone, Atlys, BusRight). Realistic cohort-level QSBS coverage typically lands 60-75%; this cohort benefits from the eligible companies being the winners.

---

## What changes vs. trusting the GP statement

| Lens | What it says |
|---|---|
| GP marks at face value | Cohort up ~4× on cost; on track for a strong outcome |
| Dilution-aware audit | Cohort up ~2× on cost; net P50 ~2.2× paid-in |
| Verification (comp-anchored) | Audit aggregate holds within ±5%; no systemic upward re-mark warranted |

If you were sizing future commitments off the GP-reported marks, you'd be ~50% too optimistic about this cohort's actual cash return. The audit-and-verification pattern is what catches that gap — not because the GP is wrong (most GP reporting just isn't designed to show LP fractional economics over time) but because compounding dilution doesn't show up in any single-quarter mark.

---

## Repo + methodology

- Code: [github.com/ruzukutenant/lp-portfolio-analytics](https://github.com/ruzukutenant/lp-portfolio-analytics)
- Methodology: [`methodology/audit_and_verification.md`](https://github.com/ruzukutenant/lp-portfolio-analytics/blob/main/methodology/audit_and_verification.md)
- Per-position scenarios in code: [`pipeline/compute_corrected_ev.py`](https://github.com/ruzukutenant/lp-portfolio-analytics/blob/main/pipeline/compute_corrected_ev.py)
- Comp anchor table: [`methodology/comp_anchors.md`](https://github.com/ruzukutenant/lp-portfolio-analytics/blob/main/methodology/comp_anchors.md)
- Use this for your own portfolio: README, section *"Using this for your own portfolio"*

MIT-licensed. Fork it, replace `sample_inputs/` with your own LP data, run the pipeline.

---

*Cohort names are real (with the fund manager's clearance); per-position dollar amounts, scenario weights, and exit projections are illustrative reconstructions. Nothing here is investment advice or a representation of any fund manager's actual marks.*
