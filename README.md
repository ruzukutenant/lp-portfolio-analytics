# LP Portfolio Analytics — reference implementation

A working methodology, pipeline, and dashboard for tracking a venture-capital LP position with comp-anchored, dilution-aware marks and probability-weighted exit projections. Includes a sample fund built from a real early-stage rolling fund cohort sized to a $100K LP commitment.

This is the **public, sanitized** version of a personal LP portfolio workspace. All personal data (statements, K-1s, founder emails, real check sizes) has been removed or fabricated. The methodology, code, and structure are real.

## Why this exists

LP-side portfolio tracking is generally either too sloppy (a spreadsheet with the fund manager's marks pasted in) or too heavy (a service like FundPanel that doesn't let you reason about anything). This repo is a middle path: enough structure to compute defensible marks, enough flexibility to incorporate every signal you get as an LP.

The interesting parts are:

1. **The audit + verification pattern.** Most LP "valuations" are just whatever AngelList or the fund manager shows you. Those marks are often stale by 1–2 quarters and ignore dilution. The audit applies cap-table dilution math to every position; the verification independently rebuilds a sample bottoms-up with comp anchors. Together they catch ~30–50% over-statement that the naive method produces.

2. **The personal-data inputs.** Founder quarterly emails, LP statements, K-1s, distribution notices, cap-table histories — these are the actual signal-bearing inputs. The pipeline mines them. `sample_inputs/` shows fabricated examples of each and explains why each one matters.

3. **The dashboard.** Next.js app that renders the methodology visibly — audit notices, verification notices, per-position cards with scenarios, cash projection charts.

## The data you need (and why each input matters)

The pipeline is only as good as the inputs you can feed it. The key personal-data sources, in order of forecasting value:

| Input | What it tells you | Why the pipeline needs it |
|---|---|---|
| **LP investment CSV** (e.g., AngelList export) | Cost basis per position, entry date, fund manager's current mark | Source of truth for cost. Don't trust your memory. |
| **Founder quarterly emails** | ARR, growth rate, runway, churn, raise plans | Forward signal. The single best predictor of next year's mark. |
| **LP quarterly statements** | Current NAV, distributions, capital calls | What the GP says vs. what you compute — variance is the audit signal. |
| **K-1 tax forms** | §1202 QSBS eligibility, cap account, suspended PALs | After-tax math falls apart without this. QSBS alone can swing returns 20-30%. |
| **Distribution notices** | Realized timing and amount | Pulls "already received" out of projections — separates principal from forward upside. |
| **Cap-table / round history** | Every priced round since LP entry, post-money | Required for dilution math. Without it, marks over-state by 30-50%. |

`sample_inputs/` has a fabricated example of each, with a `README.md` that walks through exactly which fields the pipeline reads and what each signal contributes to the final mark.

## Repo layout

```
.
├── README.md                  ← you are here
├── LICENSE                    ← MIT
├── CLAUDE.md                  ← guide for Claude Code when editing this repo
├── methodology/               ← write-ups of the analytical approach
│   ├── audit_and_verification.md
│   ├── dilution_math.md
│   ├── cash_projection.md
│   ├── comp_anchors.md
│   └── ai_tailwind_assumptions.md
├── sample_inputs/             ← fabricated personal-data inputs
│   ├── README.md              ← why each input matters
│   ├── lp_investments.csv
│   ├── founder_quarterly_email.json
│   ├── lp_quarterly_statement.csv
│   ├── k1_summary.json
│   ├── distribution_notice.json
│   └── round_history.json
├── sample_fund/               ← Sahil 2021 Q1 cohort, $100K LP commit
│   ├── README.md              ← cohort overview + caveats
│   ├── sample_fund.csv        ← 16 positions
│   ├── audit/                 ← dilution audit outputs
│   └── verification/          ← bottoms-up verification outputs
├── pipeline/                  ← Python scripts that turn inputs into dashboard data
│   ├── compute_dilution.py
│   ├── compute_corrected_ev.py
│   ├── cash_return_model.py
│   └── emit_dashboard_json.py
└── dashboard/                 ← Next.js app
    ├── data/                  ← sample-fund JSON wired in
    └── ...
```

## Running the dashboard

```bash
cd dashboard
npm install        # or bun install
npm run dev        # http://localhost:3000
```

The dashboard reads from `dashboard/data/*.json`, which is pre-built from `sample_fund/`. To regenerate after changing inputs:

```bash
cd pipeline
python emit_dashboard_json.py
```

## Running the audit yourself

```bash
cd pipeline
python compute_dilution.py        # produces sample_fund/audit/dilution_adjusted.json
python compute_corrected_ev.py    # produces sample_fund/audit/corrected_ev.json
python cash_return_model.py       # produces sample_fund/cash_projection.json
```

## What's the sample fund?

`sample_fund/` uses the actual 16-position cohort from **Sahil Lavingia's Rolling Fund, 2021 Q1**, sized to a hypothetical $100K LP commitment. Sahil cleared this use. The marks are **illustrative reconstructions** from public signals (announced raises, exit news, shutdowns) — they are not the fund manager's actual marks and should not be quoted as such.

The cohort is a good demonstration set because it has the full range:
- **Clear winners** (Hone Health, Eight Sleep) where bull/base/bear cases are constrained by real comp anchors
- **Walking dead and writedowns** (On Deck, Yac) showing what bear cases look like
- **Confirmed shutdowns** (MarketerHire, Farmstead) showing zero-mark logic
- **AI-adjacent and not-AI-adjacent** to demonstrate the tailwind-credit framework

See `sample_fund/README.md` for the full per-position notes and the "illustrative-only" disclaimer.

## Methodology in 30 seconds

For each position:

```
entry_ownership_pct = LP_cost / entry_post_money
cumulative_survival = Π (1 − raise/post) over every priced round since entry
dilution_adjusted_mark = entry_pct × cumulative_survival × current_post
expected_exit = dilution_adjusted_mark × scenario_weighted_multiplier × DF
   where DF = 0.875 ^ remaining_rounds_to_exit
```

Scenario weights come from comp anchors (`methodology/comp_anchors.md`), with AI-tailwind credit applied to AI-native positions (`methodology/ai_tailwind_assumptions.md`). For multi-position refreshes, a second-pass verification rebuilds 80%+ of expected-exit value bottoms-up to catch audit framework drift.

Full write-up in `methodology/audit_and_verification.md`.

## Using this for your own portfolio

This section walks through how to fork this repo and wire it to your actual LP positions. The pipeline is structured so that **swapping `sample_inputs/` for your real data is the entire customization** for most users — the methodology, the dashboard, and the pipeline don't need to change.

### Step 1: Fork and clone

```bash
git clone https://github.com/<your-account>/lp-portfolio-analytics.git my-portfolio
cd my-portfolio
cd dashboard && npm install && cd ..
```

You'll likely want to keep your fork **private**. The methodology is public; your actual marks should not be.

### Step 2: Replace `sample_inputs/` with your data

There are 6 input files. The order below is the order you'll typically build them. The first two get you to a usable audit; the rest sharpen forecasting and after-tax accuracy.

#### 2a. `lp_investments.csv` — your cost basis (~30 minutes)

Export from your GP portal:

- **AngelList**: Dashboard → Portfolio → Export to CSV
- **Carta**: Investor → Holdings → Export
- **Sydecar / Allocations / other SPV platforms**: similar export

Map to the columns this repo expects:

| Column | Meaning | Required |
|---|---|---|
| `company` | Display name | yes |
| `invest_date` | LP entry date (MM/DD/YYYY) | yes |
| `entry_round` | Round name at entry (Seed, Series A, etc.) | yes |
| `cost_usd` | Your cost basis | yes |
| `gp_current_mark_usd` | GP's current mark | yes (use 0 if shut down) |
| `gp_multiple` | GP's stated multiple | yes |
| `status` | Active / Closed / Walking dead | yes |

For multiple funds, run the pipeline once per fund, each with its own `sample_inputs/lp_investments.csv` (rename the directory or use git branches per fund).

#### 2b. `round_history.json` — every priced round since entry (~2-4 hours per fund, then ~10 min/quarter to maintain)

This is the input the audit depends on most heavily. Without it, you can't compute dilution.

For each company in your CSV, populate the rounds chronologically from your LP entry forward:

```json
"CompanyName": [
  {"round": "Seed", "date": "2021-01-15", "raise_usd": 4000000, "post_money_usd": 22000000, "lead": "...", "_lp_entry": true},
  {"round": "Series A", "date": "2023-06-20", "raise_usd": 13500000, "post_money_usd": 78000000, "lead": "..."},
  ...
]
```

Sources, in order of reliability:

1. **Founder updates** — they'll tell you exact terms; mine your `lp/<fund-name>` Gmail label
2. **AngelList deal feed** — for AL-routed deals, the round info is in the deal page
3. **PitchBook** — paid; most accurate for institutional rounds
4. **Crunchbase Pro** — paid, ~80% coverage of priced rounds
5. **TechCrunch / The Information / Forbes** — for high-profile rounds
6. **Google Alerts per portfolio company** — set these up once; round announcements ping you

For undisclosed post-money rounds (~40% of priced rounds), the pipeline falls back to stage-multiplier imputation. See `methodology/dilution_math.md` for the multiplier table.

#### 2c. `k1_summary.json` — QSBS eligibility (~1 hour per K-1, annually)

After-tax math is mostly about QSBS coverage. Hand-extract per position from your K-1s:

- `entity_type` — C-corp / LLC / LP (only C-corps qualify for §1202)
- `qsbs_eligible` — true if C-corp + held >5 years + gross assets <$50M at issuance + active trade
- `qsbs_basis_usd` — for the eligible portion
- `section_1202_5yr_clear_date` — entry_date + 5 years

The §1202 eligibility flag is usually NOT directly on the K-1 — derive it from entity type + holding period + your round-history data (gross assets at issuance). For ambiguous positions, default to `false` and revisit if material.

For non-US LPs or non-§1202 jurisdictions, edit `pipeline/cash_return_model.py` to use your tax constants instead.

#### 2d. `lp_quarterly_statement.csv` — GP marks over time (~30 min per quarter)

Hand-extract NAV per position from each quarterly LP statement. The pipeline doesn't currently use this for the headline mark (it uses dilution audit instead) but you'll want this for:

- Drift detection — has the GP's mark held flat while comps compressed?
- Reconciliation — does the GP's reported cost basis match your CSV?
- Distribution history — for already-received cash going into IRR

#### 2e. `distribution_notice.json` — realized cash (real-time)

Append every distribution as it lands. Captures:

- `gross_distribution_usd` — what hit your account
- `tax_character` — QSBS / LTCG / ordinary / §1244 loss
- `source_company` — which position generated it

These get subtracted from forward expected-exit value so your model doesn't double-count realized exits.

#### 2f. `founder_quarterly_email.json` — forward signal (~15 min/email)

The single highest-value forecasting input. Set up a Gmail label `lp/<fund-name>` and route founder updates there. Quarterly, dump to JSON via the Gmail API (`gmail_api_python_quickstart` works for personal use).

Parse out:

- `current_arr_usd` — anchors the comp-anchored scenarios
- `yoy_growth_pct` — triggers AI-tailwind credit (>200%) or bear weight (<30%)
- `runway_months` — shifts bear weight if <9 months
- `raise_planned` — forward dilution input
- `customer_metrics.churn_monthly_pct` — caps bull case if >3% for SaaS
- `risk_flags` — concrete distress signals (founder departure, lost major customer)

You can keep these as raw email text and parse with an LLM, or hand-extract the fields. Both work.

### Step 3: Customize the scenario weights

The biggest single change you'll make is the `SCENARIOS` dict in `pipeline/compute_corrected_ev.py`. Each position has its bull/base/bear probabilities and multipliers. Anchor each scenario to a real comp from `methodology/comp_anchors.md` — write the anchor in the `_anchor` field so it shows in the dashboard.

This is the verification step in code form. Edit, re-run, compare. For most LPs, scenario calibration is where the analytical work actually happens.

### Step 4: Run the pipeline

```bash
cd pipeline
python compute_dilution.py        # → sample_fund/audit/dilution_adjusted.json
python compute_corrected_ev.py    # → sample_fund/audit/corrected_ev.json
python cash_return_model.py       # → sample_fund/cash_projection.json
python emit_dashboard_json.py     # → dashboard/data/*.json
```

Each script prints summary stats so you can sanity-check before moving to the next step.

### Step 5: View the dashboard

```bash
cd dashboard
npm run dev          # http://localhost:3000
```

You'll see your audit + verification banners at top, the P10/P50/P90 range bar, top-5 positions with scenarios, and the full position table with `GP mark` vs `dil-adj mark` deltas.

### Step 6: Refresh cadence

| Trigger | Action |
|---|---|
| New priced round announced for a position | Update `round_history.json`, re-run pipeline |
| Quarterly LP statement arrives | Update `lp_quarterly_statement.csv`, eyeball drift |
| Founder quarterly email | Update `founder_quarterly_email.json`, revisit that position's scenarios |
| K-1 arrives (annually) | Update `k1_summary.json`, re-check QSBS coverage |
| Distribution lands | Append to `distribution_notice.json` |
| Quarterly (regardless) | Full verification pass on top 12-16 positions per `methodology/audit_and_verification.md` |
| Annually | Refresh `methodology/comp_anchors.md` with new exit comps |

### Common customizations

**Different fund economics** — edit constants in `pipeline/cash_return_model.py`:

- `FEE_DRAG_MULTIPLIER` — 1.0 for access funds, 1.2-1.3 for rolling funds depending on fee structure
- `CARRY_PCT` — 0.20 standard, 0.25 for premium funds
- `QSBS_STATE_TAX_PCT` / `NON_QSBS_BLENDED_LTCG_PCT` — your state's LTCG rate

**Multiple funds** — the current pipeline assumes one fund. For multi-fund:

- Option A (simplest): one fork per fund, each runs independently. Aggregate in a spreadsheet.
- Option B: extend `lib/data.ts` and the snapshot schema to handle a `funds` map (the original private repo this was sanitized from did exactly this).

**Different dashboard** — `dashboard/app/page.tsx` is ~200 lines. Fork it, rearrange, add charts (Recharts is a clean add). The component library in `dashboard/components/` is the methodology-specific UI; reuse what fits.

**Different methodology** — the methodology docs are markdown. Edit them. They drive your thinking, not the pipeline.

### What this repo intentionally doesn't solve

- **Round-history scraping** — manual today. PitchBook's API is the obvious automation path.
- **K-1 OCR** — manual today. Tabula + an LLM cleanup pass would work.
- **Founder-email parsing into structured signals** — manual today. An LLM with a structured-output schema would handle this well.
- **PME (public-market equivalent) comparison** — needs multi-fund history; sample fund is too short for meaningful PME. Add this when you have 3+ years of quarterly cash flows.
- **Tax software integration** — the K-1 summary is the input format you'd extract for tax prep; integration with TurboTax/Drake/etc. is on you.

### Frequently useful prompts (if using Claude Code on your fork)

- "Update `round_history.json` to add a Series B for Acme Inc.: $40M raise, $250M post-money, March 15 2026, lead Index Ventures. Then re-run the pipeline and tell me how the audit mark moved."
- "Look at the founder email from Q1 2026 for Acme. What scenario weights should I use given the signals? Update `SCENARIOS` in `compute_corrected_ev.py` and explain your reasoning."
- "Run the verification step on the top 12 positions by expected exit. For each, pick a comp anchor from `methodology/comp_anchors.md`, set scenario weights, and report the per-position and aggregate delta vs the current audit."

## What's NOT in this repo

- Real LP positions or check sizes (the actual portfolio this was built for)
- Real founder emails or LP statements
- Tax-specific advice or numbers tied to a particular filer
- A PME (public market equivalent) benchmark — that requires multi-fund history; the single-fund example doesn't benefit from it

## License

MIT. Use it, fork it, build something better.

## Contributing

This is a personal reference implementation, not a maintained product. Issues and PRs welcome but no SLA. The interesting unsolved problems:

- Round-history scraping from public sources (Crunchbase, PitchBook, AngelList feeds) — currently manual
- K-1 OCR pipeline — currently manual
- Founder-email parsing into structured signals — currently manual extraction
- PME comparison wired up for any benchmark, not just hardcoded
