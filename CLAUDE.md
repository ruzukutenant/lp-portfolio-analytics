# LP Portfolio Analytics — guide for Claude Code

This is a reference implementation of an LP-side portfolio analytics workspace: a sample fund + audit/verification methodology + Next.js dashboard. Public, sanitized version of a personal portfolio tracker.

## What this repo is for

- Maintain comp-anchored, dilution-aware marks for an LP position in an early-stage VC fund
- Project 5-year cash returns (gross pretax, net pretax, after-tax) with realistic ranges
- Surface which positions could move the portfolio P50 materially
- Render everything as a Next.js dashboard

## Canonical state lives in three places

1. **`sample_inputs/`** — fabricated example inputs (LP investment CSV, founder emails, K-1s, etc.). The pipeline reads these.
2. **`sample_fund/`** — the cohort being analyzed (Sahil Rolling Fund 2021 Q1 at $100K LP commit). Has audit/ and verification/ subdirs.
3. **`dashboard/data/*.json`** — what the UI reads. Five core files: `snapshot.json`, `positions.json`, `cash_projection.json`, `fundamental_evs.json`, `findings.json`.

When updating valuations, update `sample_fund/` first, then run the pipeline to refresh dashboard data. Don't hand-edit `dashboard/data/`.

## The audit + verification pattern

Two-step workflow for any meaningful refresh:

1. **Audit** — apply cap-table dilution math across every position:
   ```
   entry_pct = LP_cost / entry_post_money
   cumul_survival = Π (1 - raise/post) across all priced rounds since entry
   dilution_adjusted_mark = entry_pct × cumul_survival × current_post_money
   expected_exit = dilAdj × scenario_weighted_mult × DF(0.875^remaining_rounds)
   ```
2. **Verification** — independently rebuild positions bottoms-up (target 80%+ coverage of expected-exit value) with comp anchors + AI tailwind credit + IRR, then compare. If aggregate delta is within ±5%, audit holds. Per-position deltas surface re-mark candidates.

Full write-up: `methodology/audit_and_verification.md`.

## Don't mutate canonical numbers without explicit approval

- Audit output is canonical.
- Verification re-marks are *recommendations* until the user says "implement the re-marks."
- When verification finds discrepancies, surface them as **pending re-marks** (visible UI banner, additive) before mutating data files.
- The `verification_notice` block in `snapshot.json` has a `status: "implemented" | "pending"` flag so the UI can flip without code changes.

## Net-cash conversion math

For Sahil-style rolling funds:
- ~21% fee drag baked into paid-in (paid-in = deployed × 1.2715)
- 20% carry on profit (European waterfall)
- QSBS coverage assumption: 65% (see `methodology/cash_projection.md` for §1202 logic)
- Effective tax: ~13.3% blended (0.65 × 5% state + 0.35 × 28.8% blended LTCG)

For other fund types (access funds, traditional closed-end), adjust per the LPA.

## AI tailwind — current assumption (May 2026 base rates)

For AI-native companies, the default scenario should NOT be "growth decelerates by year 2 or 3." Foundation-model revenue trajectories (~3×/yr for OpenAI, 5×/yr for Anthropic) and hyperscaler capex doubling argue for sustained elevated multiples. Calibrate AI-native bull weights at 25-40%, not 15-25%.

Detail: `methodology/ai_tailwind_assumptions.md`.

## Sample selection bias is real

A 5-7 position spot-check is anecdote, not verification. To validate audit aggregates within ±5%, sample at least 12-16 positions covering 70-90% of expected exit value. The 16-position sample in this repo covers ~85% of cohort expected exit.

## File conventions

- Sample fund data: `sample_fund/sample_fund.csv` — flat, hand-editable
- Audit pipeline outputs: `sample_fund/audit/*.json`
- Verification outputs: `sample_fund/verification/*.json`
- Dashboard data: only edit via `pipeline/emit_dashboard_json.py`, not by hand
- Methodology: `methodology/*.md` — long-form write-ups

## Dashboard conventions (Next.js 16, Turbopack)

`dashboard/AGENTS.md` says: "This is NOT the Next.js you know. APIs, conventions, and file structure may all differ from your training data." Read the Next.js docs before introducing new patterns. Existing patterns to follow:

- Notice components (AuditNotice, VerificationNotice) read from `snapshot.{audit_notice,verification_notice}` blocks. To add a new system-wide banner, add a JSON block + component, don't hardcode.
- Per-position pages use `lookupFundamentalEv()` keyed by `${fundId}::${slug(company)}`.
- All money formatting via `fmtUsd()` from `lib/data.ts`. Don't `Intl.NumberFormat` inline.
- TS check: `npx tsc --noEmit` from `dashboard/`. Should be clean before commits.

## Common pitfalls

1. **Hand-editing dashboard JSON** — too easy to introduce inconsistencies. Always go through the pipeline.
2. **Using AngelList "current value" as the mark** — it lags rounds by 1-2 quarters and ignores dilution. Use dilution-adjusted mark instead.
3. **Quoting gross-to-fund numbers as LP returns** — always net of fees and carry.
4. **Over-aggressive AI bull weights without comp anchor** — "5× because AI" is judgment-only. Anchor to UserTesting at $1.3B, CoreWeave at 12× rev, etc.
5. **Under-aggressive AI bull weights** by treating "growth decelerates" as the default — see AI tailwind section above.

## Workflow for a refresh

1. Update `sample_inputs/` with new data (or, in a real deployment, the actual personal-data inputs)
2. Run `pipeline/compute_dilution.py` → `pipeline/compute_corrected_ev.py`
3. If touching >5 positions, run the verification step (see methodology doc)
4. Run `pipeline/cash_return_model.py` → `pipeline/emit_dashboard_json.py`
5. Verify dashboard in browser: `cd dashboard && npm run dev`
6. Update `methodology/` docs if framework changed (not just numbers)
