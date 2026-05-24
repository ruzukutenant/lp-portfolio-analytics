# Audit + verification methodology

A two-step framework for keeping LP-side portfolio marks honest.

## Why two steps?

Single-pass valuations drift. The audit applies a deterministic formula across every position; the verification independently rebuilds a sample bottoms-up and checks whether the audit's aggregate holds. Together they catch ~30-50% over-statement that the naive "trust the GP's marks" approach produces.

This pattern was developed after a portfolio refresh that over-stated marks by 49% in aggregate because it ignored cumulative dilution from each subsequent priced round. The audit catches that. The verification then asks: do the comp anchors and forward signals support the audit's expected exits?

## When to use it

- Portfolio refresh touching more than ~5 top-N positions
- When the user asks "are we sure?" about aggregate numbers
- After a major market event (multi-comp compression, AI valuation reset, sector shock)

For single-position re-marks from a known signal (a priced round announcement, a K-1 distribution), the simpler dilution math in `dilution_math.md` is sufficient.

## Step 1: Audit

Apply cap-table dilution math across every priced round since LP entry:

```
entry_pct = LP_cost / entry_post_money
cumulative_survival = Π (1 - raise/post) across all priced rounds since entry
dilution_adjusted_current_mark = entry_pct × cumulative_survival × current_post_money
expected_exit_mark = dilAdj × scenario_weighted_multiplier × DF
DF = 0.875 ^ remaining_rounds_to_exit
```

Where post-money is undisclosed (~40% of priced rounds), impute via stage multipliers:

| Stage | Multiplier on raise |
|---|---|
| Pre-Seed | 8× |
| Seed | 5× |
| Series A | 4.5× |
| Series B | 5.5× |
| Series C | 7× |
| Series D+ | 10× |

Where imputation is too uncertain, use a manual override anchored to the GP's current mark + revenue/round signals.

Output: `sample_fund/audit/corrected_ev.json` with per-position dilAdj + expected exit. This is canonical; the dashboard reads from it.

## Step 2: Verification

Independently rebuild 12-16+ positions bottoms-up. Coverage target: 80%+ of audit expected exit. For each position:

### 1. Pull fresh signals

Gather (manually, or via research agents):
- Latest revenue / ARR with date and source
- Most recent priced round (verify date, amount, post-money, lead) — be skeptical, confirm with multiple sources
- Growth trajectory and customer signals
- Realistic exit pathway with comparable acquisition multiples
- Risk flags (lawsuits, competitive shifts, exec departures)

If using LLM research agents: tell them explicitly "do not invent URLs or numbers. Tell me when sources are thin."

### 2. Anchor scenarios in observable comps

For each position, identify 3-5 actual exit comps with EV/Revenue multiples. See `comp_anchors.md` for the reference table.

Don't pick scenario probabilities purely from judgment. Triangulate:
- Bull case anchors to a recent premium-multiple comp (e.g., Auth0 at 28× rev, Abnormal Security at 35× rev)
- Base case anchors to a category-average comp
- Bear case anchors to a known cautionary tale (Olive AI shutdown, Bench → Employer.com, Ginkgo SPAC collapse)

### 3. Apply AI tailwind credit

For AI-native positions, "growth decelerates" base cases are too conservative. See `ai_tailwind_assumptions.md` for current base rates.

Practical effect: bull weights for AI-native go from ~20% to 30-40%; base case multiples nudge up.

### 4. Compute IRR per position

```
IRR = (analyst_exit / cost) ^ (1 / years) - 1
```

Where `years = exit_year - entry_year`. Then aggregate cost-weighted across the sample. Top-decile VC is 30-50% IRR; sample IRRs above 80% are concentrated in late-entry small-stake positions where dilution math compresses years-to-exit (legitimate but worth flagging).

### 5. Cohort breakdown

Tag positions: `ai_native`, `dev_infra_ai`, `vertical_saas_ai`, `consumer_health`, `fintech_alt`, `biotech`, `other`. Sum audit and analyst exits by cohort. The cohort-level deltas tell the real story — aggregate is often misleading.

### 6. Sensitivity tests

Run at minimum:
- AI multiple compression scenarios (-10%, -20%, -30%, -50%)
- Timing slip (1-year delay across IPO-track positions)
- IPO → M&A conversion (haircut on assumed IPO comps if 30-50% don't make it)

### 7. Self-critique

If a single position moves by >50% in either direction, re-examine. Bull weights >25% paired with multiples >5× usually indicate over-aggressive scenarios. Always check against a real comp at scale (e.g., for category-leader user-research SaaS, UserTesting → Thoma Bravo at $1.3B is the right anchor, not bubble-era multiples).

## Decision rules

| Aggregate analyst delta vs audit | Action |
|---|---|
| Within ±5% | Audit holds. Surface per-position re-marks but don't mutate canonical numbers. |
| 5-15% | Audit framework still sound but worth a focused refresh on the highest-delta positions. |
| >15% | Re-run the audit; something is methodologically off. |

| Per-position delta | Action |
|---|---|
| Within ±20% | No action; within forecasting noise |
| 20-50% | Surface as candidate re-mark; require concrete recent signal (priced round, ARR disclosure, M&A interest) |
| >50% | Treat as actionable re-mark; tighten with comp anchor before recommending |
| >100% | Re-examine your own scenarios for over-aggressiveness before recommending |

## Sample selection guidance

| Sample size | Coverage of expected exit | Expected aggregate precision |
|---|---|---|
| 5-7 | ~30-40% | Anecdote — directional only |
| 8-10 | ~45-55% | Useful but noisy (±5-8%) |
| 12-16 | ~70-90% | Tight (±2-5%) — use for canonical verification |
| 20+ | ~95%+ | Diminishing returns; do this only if 12-16 surfaced material concerns |

The marginal value of positions 9-16 is substantial. Don't stop at 8.

## Output format

A memo with:

1. Headline aggregate delta + verdict
2. Per-position table with audit / analyst / Δ / IRR / comp anchor / rationale
3. Cohort breakdown
4. Sensitivity tables
5. Reverse-engineering: what does the audit assume each company must achieve?
6. 3-5 actionable findings (highest-magnitude deltas with concrete drivers)
7. Self-critique of any prior verification's overshoots

## Common failure modes

1. **Sample too small** — 5-8 positions can be off by 10-15% from selection bias alone
2. **Hallucinating company names** — verify against your authoritative position list before referencing
3. **Over-aggressive bull weights for AI-native** without comp anchor — UserTesting at $1.3B is real; "$5B because AI" is judgment-only
4. **Under-aggressive bull weights for AI-native** by ignoring exponential growth — OpenAI-trajectory companies don't decelerate at $500M ARR
5. **Forgetting carry/fees in net-cash conversion** — for Sahil-style rolling funds, paid-in is 1.2715× deployed; carry haircut on profit is 20%
6. **Treating gross-to-LP as net** — the audit's `expected_exit_mark` is gross (pre-carry); apply carry haircut for net
7. **Hallucinated funding rounds** — research agents will sometimes invent recent rounds. Always check that primary URLs resolve.

## When to NOT verify

- Single-position update from a known signal (priced round announcement, K-1 distribution)
- Funds with no top-N exposure (mostly-realized funds, very small commitments)
- Refresh cycles less than ~60 days after the previous verification

## Related

- `dilution_math.md` — the per-position formula in detail
- `comp_anchors.md` — exit comp table by category
- `ai_tailwind_assumptions.md` — current base rates for AI-native scenarios
- `cash_projection.md` — net-cash conversion (fees, carry, taxes)
