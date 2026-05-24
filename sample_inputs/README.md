# Sample personal-data inputs

This directory shows fabricated examples of the personal-data sources the pipeline depends on, plus what each one contributes to the final mark. **All files in this directory are made up.** Real-deployment data would replace each with the actual artifact from your LP relationships.

The whole point of this repo is that the methodology is only as good as these inputs. Founder emails and K-1s aren't ornamental — they're how you escape the "trust the GP's stale marks" trap.

## The inputs, ranked by forecasting value

### 1. Founder quarterly emails — `founder_quarterly_email.json`

**What it carries:** ARR, growth rate, runway in months, raise plans, churn, hiring, named customer wins, product launches.

**Why it matters most:** This is the single strongest forward signal you get as an LP. A founder who emails quarterly with concrete metrics is telegraphing how confident they are. A founder who stops emailing is telegraphing distress. The pipeline parses these into structured signals that feed the verification step's scenario weights.

**What the pipeline reads:**
- `current_arr_usd` → revenue anchor for the comp-anchored bull/base/bear scenarios
- `yoy_growth_pct` → directly informs bull-weight calibration (>200% triggers AI-tailwind credit; <30% triggers bear-weight)
- `runway_months` → bear-case weight (<9 months runway shifts bear-case probability up by 10-15 points)
- `raise_planned` → forward dilution input for DF (dilution factor)
- `customer_metrics.churn_monthly_pct` → for SaaS positions, >3% monthly churn caps bull case
- `risk_flags` → can trigger immediate re-mark down (founder departure, lawsuit, lost major customer)

**How to collect:** Set up a Gmail label `lp/<fund-name>` and route founder updates there. Quarterly, dump the label to JSON via the Gmail API and run the parser. ~30 emails per fund per year is typical.

### 2. LP investment CSV — `lp_investments.csv`

**What it carries:** Cost basis per position, entry date, entry round name, GP's current mark and multiple.

**Why it matters:** Source of truth for cost. You will forget what you actually paid. The GP's reporting system (AngelList, Carta, etc.) is the canonical record.

**What the pipeline reads:**
- `cost_usd` → denominator for `entry_pct = cost / entry_post_money` in dilution math
- `invest_date` → years-to-exit for IRR computation
- `entry_round` → triggers the right stage-multiplier when post-money is undisclosed
- `gp_current_mark_usd` → comparison point for the audit (audit vs GP mark delta is itself a signal)
- `gp_multiple` → sanity-check on dilAdj output (if dilAdj/cost wildly diverges from GP multiple, investigate)

**How to collect:** AngelList exports a CSV from your investor dashboard. Carta has a similar export. Real deployments would set up a quarterly refresh from the GP's portal.

### 3. LP quarterly statement — `lp_quarterly_statement.csv`

**What it carries:** Current NAV per position (the GP's mark, by quarter), distributions received, capital calls made.

**Why it matters:** The variance between the GP's mark over time and the audit's dilAdj mark is the audit signal. If a GP holds a mark flat for 6 quarters while comps compress 40%, that's a mark to scrutinize. If the GP suddenly marks UP without a priced round, ask why.

**What the pipeline reads:**
- `nav_usd` quarterly series → drift detection vs audit dilAdj
- `distributions_received_usd` → "already received" subtraction from forward projection
- `capital_calls_paid_usd` → cumulative paid-in for net-multiple math (especially important for closed-end funds where capital calls span years)

**How to collect:** GPs send these PDFs quarterly. OCR or hand-extract to CSV. (A pipeline for K-1/statement OCR is one of the unsolved problems flagged in the top-level README.)

### 4. K-1 summary — `k1_summary.json`

**What it carries:** §1202 QSBS eligibility flags per position, capital account changes, suspended PALs (passive activity losses), entity classification.

**Why it matters:** After-tax returns are 25-30% lower than pretax without QSBS, and 5-10% lower with it. Getting QSBS coverage right is the single biggest after-tax lever. Suspended PALs released on full fund exit can be a meaningful late-stage tax shield.

**What the pipeline reads:**
- `qsbs_eligible` per position → blended tax-rate computation
- `suspended_pal_carryforward_usd` → released-on-exit tax-shield assumption
- `capital_account_end_usd` → independent check on cost basis (should reconcile with LP investment CSV)
- `entity_type` (LLC / C-corp / LP) → drives federal/state treatment differences

**How to collect:** GPs send K-1s annually in March-April. Hand-extract the key fields to JSON until OCR tooling matures. The §1202 flag is often NOT on the K-1 directly — derive it from the entity type + holding period + gross assets at issuance (which means you need round-history data too).

### 5. Distribution notices — `distribution_notice.json`

**What it carries:** Realized exit proceeds — amount, date, source position, tax character (LTCG / STCG / ordinary).

**Why it matters:** Separates "already received" from forward projection. Without this, your model double-counts realized exits in expected exit value. Also feeds IRR (early distributions matter disproportionately).

**What the pipeline reads:**
- `gross_distribution_usd` → subtracted from per-position expected exit before computing forward projection
- `distribution_date` → IRR cash-flow timing
- `tax_character` → drives whether the gain pays QSBS-eligible rate, LTCG, or ordinary income

**How to collect:** GPs send these as PDFs or portal notifications around the time of an exit. Capture in real-time; don't wait for the K-1 next March.

### 6. Round history — `round_history.json`

**What it carries:** Every priced round each portfolio company has done since LP entry — date, amount raised, post-money valuation, lead investor.

**Why it matters:** This is the input to the dilution math. Without it, the audit step can't run — you'd be back to the naive "current_post / entry_post × cost" approach that over-states marks by 30-90%.

**What the pipeline reads:**
- For each priced round: `raise_amount_usd`, `post_money_usd` → cumulative survival product
- `round_name` → fallback to stage-multiplier imputation when post-money is undisclosed
- `lead_investor` → soft signal for round quality (top-tier lead = higher comp-anchor confidence)

**How to collect:** This is the hardest input. Sources: Crunchbase (incomplete), PitchBook (paid), AngelList's deal feed (only for portfolio companies that fund through AL), founder updates (often the most accurate), TechCrunch / The Information for big rounds. A real deployment would maintain `round_history.json` as a living file, updated whenever a portfolio company announces a round.

## Why the pipeline is more than a spreadsheet

The temptation is to skip all this and just paste GP marks into a spreadsheet. That's faster, but:

- GP marks lag rounds by 1-2 quarters (sometimes more)
- GP marks ignore dilution (they show post-money for the company, not LP fractional ownership)
- GP marks don't compute after-tax (QSBS, suspended PALs, state breakdowns)
- GP marks don't show probability-weighted scenarios — they're point estimates that imply false precision

The pipeline replaces each of those with: dilution-aware marks, scenario-weighted projections, after-tax conversion, and a forward signal (founder emails) that the GP report doesn't carry. The personal-data inputs are how you escape the GP's reporting framing.

## How to build your own

For a real deployment:

1. Replace `lp_investments.csv` with your GP-portal export (AngelList / Carta / etc.)
2. Wire up a quarterly Gmail pull for founder updates → `founder_quarterly_email.json` (one entry per email)
3. Hand-extract LP statements quarterly → `lp_quarterly_statement.csv`
4. Hand-extract K-1s annually → `k1_summary.json`
5. Real-time-add distribution notices → `distribution_notice.json` (append; don't overwrite)
6. Maintain `round_history.json` as you read about portfolio company rounds — set a Google Alert per company

Then run `pipeline/compute_dilution.py` and the rest of the pipeline reads from these files.
