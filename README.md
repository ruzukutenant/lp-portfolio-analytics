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
