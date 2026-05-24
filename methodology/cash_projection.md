# Net-cash projection: fees, carry, and taxes

Converting gross-to-fund exit value into net-to-LP after-tax cash. Different fund structures need different math; this doc covers the common patterns.

## The conversion chain

```
gross_to_fund (audit expected exit, dilution-adjusted)
  → minus carry on profit
    → minus fund-level fee drag (if applicable)
      → gross-to-LP pretax
        → minus taxes (LTCG, QSBS, state)
          → net-to-LP after-tax
```

## Rolling fund pattern (e.g., Sahil-style AngelList Rolling Fund)

**Fee structure:**
- Management fee: 2% per annum × 10 years = 20% of committed capital, prepaid in 16 quarterly installments (years 1-4)
- Platform admin fee: 1.5% of committed capital over 10 years
- Combined drag: ~21.5% of paid-in capital
- **CSV "cost" columns from AngelList exports are POST-fee deployed capital, not paid-in.** True paid-in ≈ deployed × 1.2715

**Carry structure:**
- 20% carry on profit above paid-in capital (European waterfall)
- LP gets paid-in back first (aggregated across all Series Funds in the program), then 80/20 split on profit
- No hurdle / preferred return

**Worked example, $100K commitment:**

```
commitment = $100,000
deployed (CSV cost basis) = ~$78,650 (commitment × 1 / 1.2715)
paid-in = $100,000 (sub agreement)
fee drag = $21,350 (paid-in - deployed)

If gross-to-fund exit = $250,000:
  profit = $250,000 - $100,000 = $150,000
  carry = $150,000 × 0.20 = $30,000
  gross-to-LP pretax = $250,000 - $30,000 = $220,000
  multiple on paid-in = 2.20×
  multiple on deployed = 2.79×  ← don't quote this as LP returns; it ignores fee drag
```

## Access fund pattern (single-vintage closed-end LP)

**Fee structure:**
- No periodic fee drag on LP
- Fees are deducted from the GP's check, not the LP's commitment
- CSV cost basis ≈ paid-in

**Carry structure:**
- 20% carry on profit, European waterfall, no hurdle

**Worked example, $100K commitment:**

```
commitment = $100,000
paid-in = $100,000 (= deployed)

If gross-to-fund exit = $250,000:
  profit = $150,000
  carry = $30,000
  gross-to-LP pretax = $220,000
  multiple on paid-in = 2.20×
```

The only real difference vs the rolling fund is the absence of fee drag.

## Tax math — §1202 QSBS

Qualified Small Business Stock (§1202) is the single biggest after-tax lever. Eligibility roughly:
- C-corp, US, gross assets < $50M at issuance
- Held > 5 years
- Active trade or business (excludes most services, finance, real estate, hospitality)

When eligible: federal capital gains tax on the gain is **0%** up to the greater of $10M or 10× basis. State taxes still apply (some states conform to §1202, others don't).

**Per-fund coverage assumption** (the % of expected exit value that is §1202 eligible):

| Fund type | Typical coverage |
|---|---:|
| Direct early-stage SPVs (rolling fund) | 60-70% |
| Access fund | 60-75% |
| Traditional closed-end seed | 80-95% |
| Late-stage SPVs (Series C+ entry) | 20-40% |
| Crypto/structured/revenue-share | 0% |

The non-eligible portion pays standard LTCG rates (15-20% federal + state).

## Effective blended tax rate

For a Sahil-style rolling fund with 65% QSBS coverage, assuming a Northeast state at 5% state LTCG rate:

```
QSBS-eligible portion (65%): 5% state only = 5% tax
Non-eligible portion (35%): 15% federal + 8% NIIT + 5% state = 28% blended
Effective rate = 0.65 × 5% + 0.35 × 28% = 3.25% + 9.8% = 13.05%
```

For a fund with 90% QSBS coverage and a low-state-tax filer, the blended rate can drop below 8%. For 0% coverage funds (crypto, SEAL revenue-share), the blended rate is 25-30%.

## Probability-weighted projection

The pipeline runs scenario weights per position and aggregates:

```
For each position:
  expected_exit = sum(prob × multiple) × dilAdj_mark × DF

For the fund:
  gross_exit_total = sum(expected_exit) + already_distributed
  profit = gross_exit_total - paid_in
  carry = max(0, profit × 0.20)
  gross_to_LP_pretax = gross_exit_total - carry
  after_tax = gross_to_LP_pretax - (profit × effective_blended_rate)
```

Then run sensitivity bands (P10, P50, P90) on the aggregate scenario distribution to get a realistic range, not a false point estimate.

## What to report

Always report:
- **Multiple on paid-in** (not on deployed). LPs care about what they wrote checks for.
- **Net-to-LP** (after carry). Gross-to-fund is for the GP, not the LP.
- **IRR using paid-in dates** (not deployed dates). The fee-drag period matters for IRR.
- **A range, not a point**. P10 - P50 - P90 is honest; "$220K projected" is a lie of false precision.

## What NOT to report

- Gross-to-fund multiples as if they were LP returns (over-states by carry, sometimes 25%+)
- Deployed-basis multiples for fee-drag funds (over-states by ~25%)
- After-tax assuming 0% QSBS when most positions are §1202 eligible (over-states tax by 15-25 percentage points)
- A single P50 number without the range

## Related

- `dilution_math.md` — what feeds the `dilAdj_mark` upstream
- `audit_and_verification.md` — the broader two-step refresh framework
- `comp_anchors.md` — what feeds the scenario multiples
