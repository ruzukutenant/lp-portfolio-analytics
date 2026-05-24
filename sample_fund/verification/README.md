# Verification outputs

In a full deployment, this directory holds the bottoms-up verification artifacts:

- `verification_findings.json` — per-position scenarios with comp anchors, IRR, and cohort tags
- `verification_memo.md` — the analyst write-up (delta vs audit, sensitivity, re-mark recommendations)
- `cohort_breakdown.json` — aggregate exit value by cohort (AI native, vertical SaaS, etc.)

For the sample fund, the verification work is currently inline in `pipeline/compute_corrected_ev.py` (the `SCENARIOS` dict with `_anchor` notes per scenario). In a larger deployment, those would be promoted out to a separate JSON input file edited during the verification step.

See `methodology/audit_and_verification.md` for the full verification workflow.
