# AI tailwind assumptions for portfolio scenarios (May 2026)

Default assumption is exponential AI revenue growth, not "growth decelerates" — calibrate AI-native bull weights accordingly.

## The base rate

For AI-native companies (foundation-model-adjacent or directly riding AI capex), the default scenario should NOT be "growth decelerates by year 2 or 3." Current observed base rates as of May 2026 say something different.

## Foundation-model revenue growth (verified)

| Company | 2022 | 2023 | 2024 | 2025 | YoY pattern |
|---|---:|---:|---:|---:|---|
| OpenAI | $200M | $1.6B | $4B | $13B | 8× → 2.5× → 3.25× |
| Anthropic | n/a | ~$200M | ~$1B | ~$5B run-rate | 5× → 5× sustained |
| Mistral | small | small | ~$30M | ~$200M | 6-7× |
| xAI | n/a | n/a | ~$100M | ~$400M | 4× |

**Pattern: ~3× per year sustained for category leaders, with 5×+ years possible while still small.**

This is unprecedented in software history. The closest historical analogue is the early Salesforce era (2003-2007) but at much smaller scale. Treating "growth decelerates to 50% YoY by year 3" as the base case for AI-native is the WRONG default in this regime.

## Hyperscaler capex (the demand-side anchor)

| Year | Capex (combined Microsoft + Google + Amazon + Meta) |
|---|---:|
| 2023 | ~$150B |
| 2024 | ~$200B |
| 2025 | ~$300B+ |
| 2026 (guided) | $400-500B |

**Pattern: doubling every ~18-24 months. Each $100B of incremental hyperscaler capex translates to multi-billion-dollar TAM expansion for AI-native companies, AI infrastructure, and developer tools.**

## What this means for portfolio scenarios

For AI-native positions, anchoring base cases to "growth decelerates to 30-50% YoY" produces marks that are systematically too conservative in the current regime. Example corrections from a real refresh that ran v1 (conservative AI assumptions) and v2 (AI tailwind credit applied):

| Position type | v1 verdict | v2 verdict | Change driver |
|---|---|---|---|
| AI search | -26% trim | -14% trim | Exponential growth makes 2× ARR-to-2027 plausible |
| Dev infra for AI builders | -14% trim | -3% (audit holds) | AI-builder customer cohort tailwind |
| AI coding IDE | +4% bump | +19% bump | Triple-digit revenue → $1B run-rate is credible |
| GPU cloud | +68% bump | +80% bump | Hyperscaler capex doubling = stronger demand than v1 priced in |

# Calibration rules

## Bull weights for AI-native

For positions that are foundation-model-adjacent OR directly ride AI capex (cloud infra, GPU access, dev tools, AI search, AI coding):

- **Bull case probability**: 25-40% (was 15-25% in pre-AI-tailwind framework)
- **Bull case multiple**: 3-5× current mark for IPO-track at AI-native premium
- **Base case**: assume growth continues for 2-3 more years; multiple compresses but stays elevated
- **Bear case probability**: 15-25% (capex pulls back, multiple resets)
- **Wipe probability**: 10-20% (foundation models commoditize the wedge — real risk for thin-moat positions)

## What's NOT covered by the AI tailwind

Don't apply tailwind credit to:

- Vertical SaaS with AI features bolted on — tailwind is mild, possibly negative if incumbents build the AI in-house
- Consumer health, biotech, fintech-alt — different category
- Revenue-share / SEAL-style structures — capped upside regardless of growth
- Service businesses pricing at multiples below 5× rev — multiple ceiling exists regardless of AI

## Where the tailwind has a ceiling

Even AI-native companies face multiple compression risk:

- **CoreWeave compressed from 25× EV/Rev at IPO peak to 12× currently** — public market multiples for AI infra are NOT staying at peak levels. Apply 12-15× as the realistic public-market base for AI-infra IPOs.
- **AI consumer multiples sustainable while growth >100%, but compression starts when growth dips below ~80%**.
- **Premium multiples for AI dev tools depend on customer cohort persistence** — if the AI-startup customer base contracts, infrastructure-tier dev tools compress with it.

# Red flags that flip an AI-native to "no tailwind"

1. **Foundation models start eating the wedge** — e.g., GPT-4o native vision eating standalone vision-AI startups; foundation-model agents eating workflow-AI startups
2. **Major customer concentration in a single AI startup** — if that customer goes down, so does the company
3. **Hyperscaler insourcing accelerates** — most AI infra startups face this; Lambda has Microsoft as both customer AND supplier (mixed signal)
4. **Multiple compression in public comps** — CoreWeave's -53% from peak is a leading indicator for private AI-infra marks
5. **Antitrust / regulatory blocks on M&A** — limits one of the two exit paths (Amazon vs Comet injunction)

# Tail-risk sensitivity

Modern early-stage portfolios typically have 60-85% of expected-exit value concentrated in AI-native cohorts. A 30% AI multiple compression can knock combined portfolio P50 by 20-25%. This is the single biggest risk factor.

Conversely, if hyperscaler capex doubles again 2026-27 and AI-native multiples expand back to peak levels, +20-40% at the portfolio level is plausible.

**Two-tail risk, not one.** Don't bias toward either outcome — model both.

# Refresh signals

Update this file when:
- Foundation-model revenue prints break the 3×/yr pattern (either accelerating or decelerating)
- Hyperscaler capex commitments shift materially (Microsoft/Google/Amazon Q4 guidance)
- A meaningful AI-native IPO/M&A prices outside the current 12-30× EV/Rev band
- Cohort-level multiple compression becomes broadly observable in public comps

Annual full refresh; trigger-based mid-year updates.

# Related

- `comp_anchors.md` — cohort-specific multiples
- `audit_and_verification.md` — where AI tailwind credit fits (step 3 of verification)
