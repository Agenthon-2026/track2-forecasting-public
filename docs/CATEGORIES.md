# Track 2 — Forecast Card Families

## Executive summary (read this first)

Track 2 evaluation tasks are divided into **four card families** (F1 through F4). Every task belongs
to exactly one family. The families are organized around the **role of the text corpus**: what
kind of signal does the text provide, and how much should a reasoning agent beat a text-blind
model? Read all four sections — the sealed evaluation set draws tasks from all of them, and the
best submissions score well across the board.

**The governing distinction:** Track 2 = time-series data (panels indexed by time) → forecast
the future of a series. The agent gets both numeric panels and a frozen text corpus. The text
corpus is time-stamped — every document in it has a date on or before the as-of date. Track 4
(general tabular data → predict a label) is a separate track with a different structure.

**Unfamiliar terms?** See the competition-wide GLOSSARY published with the shared toolkit:
`Agenthon-2026/Agenthon2026-public`, file `docs/GLOSSARY.md`.

Plain one-liner per family:

| Family | What it tests | Role of text | Score component that matters most |
|--------|--------------|--------------|----------------------------------|
| **F1** Continuation-with-context | Can the agent add incremental signal from text to a well-seen series? | Incremental — text refines a forecast the numbers already support | Marginal CRPS (50 %) |
| **F2** Text-cued regime shift | Does early text signal a regime change before the numbers move? | Pivotal — regime shift lives in the text before the panel | Marginal CRPS + tail (50 % + 20 %) |
| **F3** Cross-asset reasoning | Does text about one asset imply moves in correlated assets? | Cross-asset — text connects markets not directly mentioned | Joint variogram (30 %) |
| **F4** Tail/shock-from-text | Does text foreshadow a shock that drives extreme outcomes? | Shock signal — text warns of fat-tail territory | Tail penalty (20 %) |

The composite score formula is:
**S = 0.5 × marginal CRPS + 0.3 × joint variogram + 0.2 × tail penalty**.
Lower is better.

On a **single-cell** card — one asset at one horizon — the joint variogram is 0 by
construction, because there is no second number for it to relate yours to. Its weight is
therefore redistributed over the terms that exist: **S = 0.714 × marginal CRPS + 0.286 × tail
penalty**. This keeps a text-blind baseline at 1.0 on both card shapes; without it a
single-cell card could not reach the same range as a multi-cell one however good the
forecast.

---

## How to read each family section

Each section below covers:

- **What this family tests** — plain description
- **The role of text** — specifically how the text corpus matters here and why an agent should beat a text-blind baseline
- **Which score component is stressed and why** — where your model lives or dies
- **As-of date and leakage rules** — including the text corpus cutoff
- **An example card** — what the task specification looks like
- **Common mistakes** — what to watch out for

---

## F1 — Continuation-with-context

### What this family tests

F1 is the baseline test. The agent has seen every asset in the panel all the way up to the
as-of date (the last date the model is allowed to look at). The numeric series alone is
sufficient to produce a reasonable forecast. The question is: **does the text corpus add
incremental signal on top of the numbers?**

For example, a FOMC statement released on the as-of date might say "the committee remains
attentive to inflation risks" — a phrase that carries information about the near-term rate
path beyond what the yield curve itself already implies. An agent that reads and understands
this text may produce a better-calibrated forecast than one that extrapolates the historical
series alone.

"Calibrated uncertainty" means: if you say "90 % of the time the 10-year yield will be
between 3.5 % and 5.0 %", then across many such forecasts, roughly 90 % of realizations
should indeed land in that interval. Not 40 %, not 100 %, but approximately 90 %.

The **marginal CRPS** (Continuous Ranked Probability Score — a single number that rewards
both accuracy and calibrated uncertainty; lower is better) is the primary score for F1.
See `docs/CONCEPTS.md` for a plain-English explanation of CRPS.

### The role of text

In F1, the text provides **incremental context** on top of a series the agent already knows
well. Examples of useful text signals:

- An FOMC statement indicating a shift in language from "patient" to "expedient" hints at
  a faster rate path than historical momentum alone would suggest.
- A macro-release commentary noting an upward surprise in CPI may cause an agent to shift
  its rate forecast upward relative to what the numbers implied at month-end.
- COT data showing a sharp build in short positioning may warn of a crowded trade that
  increases volatility.

A text-blind time-series foundation model (Chronos, TimesFM, etc.) cannot use any of this
context. An agent that reads the text and correctly interprets it should produce a better-
calibrated marginal distribution — lower CRPS.

The incremental advantage from text is typically modest in F1 (the numbers carry most of
the signal for in-distribution continuation). F2 and F4 are where text matters more.

### Which score component is stressed and why

**Marginal CRPS is the primary component (50 % weight).**

Every asset is familiar and has a long history. A model that is over-confident (too narrow
uncertainty bands) scores worse than one that is well-calibrated. The CRPS penalizes both
"I missed the target by a lot" and "I was far too sure of myself." The joint variogram is
computed and included in the composite, but for in-distribution, highly correlated series
the joint score does not spread submissions much. The tail penalty is present but is not
the intended stress for F1.

### As-of date and leakage rules

- The as-of date must be at least **6 calendar months** before the first target date.
  Example: as-of `2023-07-03` → earliest target date `2024-01-03`.
- The panel available to the agent ends strictly at the as-of date. No row with
  `date > asof` may appear in any input panel file.
- The text corpus contains only documents with timestamps on or before the as-of date.
  Gate g2 enforces this: if any text document has a post-asof timestamp, the submission
  fails g2 (leakage). Agents may not fetch live text — the restricted network permits
  model-API calls only (audited proxy; vendor-side web search/retrieval disabled).
- Panels are truncated at the as-of date **before publication**: the staging step reads every
  row of every panel and refuses the unit if one is dated after the as-of. There is no runtime
  interceptor — this document used to describe a `LeakageViolation` exception that exists
  nowhere. The check is real; its location is publication time, not read time.

### An example forecast card

```
Card ID:   t2-F1-ust-10y-6m-2023Q3
Family:    T2-F1
Panel:     rates/ust-daily  (DGS10, 2000-01-03 to 2023-07-03)
Text:      text/  (FOMC statements and rate-decision headlines, all dated <= 2023-07-03)
As-of:     2023-07-03
Target:    UST_10Y at horizon 126 business days (approx. 2024-01-03)
Output:    forecast.parquet with columns [draw, asset, horizon, value]
           n_draws >= 200, value in % per annum
Score:     CRPS composite (50 % marginal CRPS dominant)
```

What a submission looks like: 500 rows (one per draw), each row says "in this possible future,
the 10-year yield on 2024-01-03 was X %". The 500 values form a distribution. An agent that
read the FOMC statement dated July 2023 (noting continued rate-hold language) might widen
its distribution slightly relative to a model that only extrapolated the numeric trend.

### Common mistakes in F1

1. **Producing a point forecast dressed as a distribution.** If all 500 draws are within
   0.05 % of each other, the model is effectively forecasting a single number. Gate g3 will
   flag `T2_UNCALIBRATED_MARGINAL` if the per-asset standard deviation is too small.
2. **Ignoring the text corpus entirely.** If your agent passes `--text` but never reads the
   corpus, you will score like a text-blind baseline on F1. Uplift vs. baselines requires
   actually using the text.
3. **Using stale or revised data.** FRED revises some macro series. Use the vintage available
   on the as-of date, not the current revised values.
4. **Too-wide intervals "just in case."** Over-dispersed forecasts also score poorly. CRPS
   penalizes both under-confidence and over-confidence.
5. **Wrong target date.** Horizons are in **business days**, not calendar days.
   21 business days is approximately 1 calendar month but not exactly 21 calendar days.
6. **Including post-asof text.** Even one document dated after the as-of date will fail gate
   g2. Always filter the text corpus by date before mounting.

---

## F2 — Text-cued regime shift

### What this family tests

F2 asks: can the agent detect a **regime change that is signalled in text before it appears
in the numbers?** The text corpus contains early warnings — a central bank's tone shift,
a policy announcement, an unusual inflation commentary — that precede a structural break in
the numeric panel. The agent must read these signals and shift its forecast accordingly,
beating a text-blind baseline that can only extrapolate historical numeric patterns.

This is the family where the text corpus is most pivotal. The regime change signal often
lives entirely in text (speeches, minutes, press conference phrasing) while the panel still
looks calm. A text-blind model will miss the shift; a reasoning agent should detect it early.

The family also tests generalization in some configurations: some F2 cards ask the agent
to forecast an asset it has not seen in the panel (e.g., an EM currency) by reading text
about related markets. In those configurations, the text becomes the primary information
source.

### The role of text

In F2, the text provides **pivotal leading-indicator signals**. Examples:

- An FOMC press conference transcript from three months before a hiking cycle begins,
  where the chair uses words like "expedient" and "resolve" that historically precede
  aggressive tightening. A text-blind model sees flat rates in the panel. The reasoning
  agent reads the text and front-runs the shift.
- A Bank of England MPC statement noting "uncomfortably high inflation" ahead of a
  cable (GBP/USD) shock. The FX panel looks calm; the text is the canary.
- An ECB speech mentioning "fragmentation risk" — historically a precursor to spread
  widening in peripheral European rates.

A text-blind baseline cannot use any of these signals. This is where the information
uplift vs. baselines should be largest.

### Which score component is stressed and why

**Marginal CRPS is primary (50 % weight), with the tail penalty (20 %) as an important
secondary differentiator.**

Why the tail matters: regime shifts create fat-tailed outcomes. A model that misses the
early text signal will produce a tight Gaussian around the historical mean. When the
regime shift arrives, the realized outcome falls far in the tail, and the tail penalty
compounds. Agents that correctly widen their distribution based on text signals will pay
a much lower tail penalty.

The joint variogram matters less for most F2 cards (many are single-asset or two-asset
with a seen anchor). But for multi-asset regime-shift cards, joint behavior matters too.

### As-of date and leakage rules

- The as-of date must be at least **3 calendar months** before any target date.
  Example: as-of `2023-04-03` → earliest target `2023-07-03`.
- The text corpus contains only documents with timestamps on or before the as-of date.
  The regime-shift signal is in the pre-asof text — the whole point of F2 is that the
  text warns in advance. Gate g2 rejects any corpus document dated after the asof.
- For transfer-configuration F2 cards: the target series must be **entirely absent from
  the input panel**. The harness checks that no row with the target asset ID appears in
  `/input/panels`. The text corpus (not the numeric panel) is the primary information source
  for the unseen asset.
- All series (including proxy / related series) must end at the as-of date.

### An example forecast card

```
Card ID:   t2-F2-gbp-boe-shock-2022Q3
Family:    T2-F2
Panel:     fx/g10-daily (10 G10 currencies, 2000-01-03 to 2022-08-01)
Text:      text/  (Bank of England MPC statements, governor speeches,
                   UK CPI release commentary, all dated <= 2022-08-01)
As-of:     2022-08-01
Target:    GBP/USD at horizons 21 BD and 63 BD
Output:    forecast.parquet [draw, asset, horizon, value]
Score:     CRPS composite; tail penalty is secondary differentiator
```

A reasoning agent that reads the Bank of England's August 2022 language carefully might
produce a wider, left-skewed distribution for GBP/USD — anticipating the September
mini-budget shock that sent cable to approximately 1.03. A text-blind model extrapolating
from 1.20 would score very poorly on tail calibration.

### Common mistakes in F2

1. **Treating it like F1.** F2 is not about incremental text adjustment. The text is the
   primary early-warning signal. An agent that barely glances at the text and mostly
   extrapolates the panel will not beat a text-blind baseline.
2. **Missing the regime-shift language.** FOMC and MPC statements use specific phrasing
   that historically precedes rate moves. Build prompts that ask the LLM to identify
   tone shifts, not just summarize the text.
3. **For transfer-configuration cards: embedding the target series in model weights.**
   If you trained your foundation model on data that includes the held-out period for the
   absent series, you have look-ahead. The calibration-width heuristic will flag your
   submission.
4. **Symmetric uncertainty when direction is clear.** If the text strongly implies
   depreciation risk (e.g., a currency's central bank sounds dovish while inflation
   surges), the distribution should reflect that directionality, not be symmetric.
5. **Wrong asset IDs in output.** The parquet must use the exact asset IDs listed in
   `card.toml [targets] asset_ids`. Case and format matter.

---

## F3 — Cross-asset reasoning

### What this family tests

F3 is the **hardest family to game**. It tests whether the agent uses text about one asset
to make inferences about *correlated but distinct assets*. The text corpus may discuss one
market explicitly (e.g., an FOMC statement about rate policy), but the card asks for a
**joint forecast** of multiple correlated assets (e.g., the full yield curve: 2Y, 5Y, 10Y,
30Y). An agent that reads the FOMC statement and understands the term-structure implications
should produce a joint forecast where all tenors co-move consistently.

A text-blind model forecasting assets independently will produce draws where the 2Y and
10Y yield diverge unrealistically — the joint score (variogram) will penalize this even if
each marginal distribution is correct.

The cross-asset aspect means: the text is about market A, but market B is implied. For
example, Fed communications about rate policy imply FX moves; CPI commentary implies both
rates and equity factor returns.

### The role of text

In F3, the text provides **cross-market inference signals**. Examples:

- An FOMC statement about "sustained restrictive policy" implies: (a) short yields stay
  elevated, (b) long yields may lag, (c) the yield curve slope shifts toward a specific
  shape. An agent that reads this and applies it consistently across all curve tenors should
  produce a more realistic joint draw than one that only models each tenor from its own
  history.
- A CPI surprise commentary noting "broad-based price pressures" implies both:
  (a) upward rate pressure, and (b) downward equity factor returns (value vs. growth).
  An agent that connects these via text can produce a consistent multi-asset joint forecast.
- A Bank of Japan speech hinting at a policy shift implies correlated moves across JPY
  and rates that a text-blind model would treat as independent.

### Which score component is stressed and why

**Joint variogram is primary (30 % weight).**

The variogram score measures whether the *distances* between assets in the draws match the
distances between assets in reality. A model with independent draws — each asset sampled
separately — overstates cross-asset distances. A reasoning agent that applies text signals
consistently across all assets in a single draw should produce a more realistic correlation
structure.

The marginal CRPS is still secondary — if the marginals are very wrong, the composite
suffers. But the differentiating factor between submissions is the variogram.

**Why the minimum draw count matters more here**: the variogram estimator uses pairwise
distances between draws. With 200 draws you have approximately 20,000 pairs. With 500 draws
you have approximately 125,000 pairs. The harness warns if draws < 500 for F3 cards, and
recommends >= 500.

### As-of date and leakage rules

- The as-of date must be at least **1 calendar month** before the first target date.
  (Shorter than F1/F2 because the dependence structure, not the forecast horizon, is the
  test.) Example: as-of `2024-01-02` → earliest target `2024-02-02`.
- All target assets must be excluded from the panel after the as-of date.
- The text corpus contains only documents with timestamps <= as-of date. Gate g2 enforces
  this. A post-asof FOMC release would constitute leakage if it informed the joint forecast.
- Derived features (rolling covariance, DCC-GARCH estimates, PCA loadings) must be
  constructed using only data through the as-of date. Post-asof correlation estimates are
  leakage.

### An example forecast card

```
Card ID:   t2-F3-ust-curve-joint-2024Q1
Family:    T2-F3
Panel:     rates/ust-daily (DGS2, DGS5, DGS10, DGS30, 2000-01-03 to 2024-01-02)
Text:      text/  (FOMC January 2024 statement, December 2023 minutes,
                   macro commentary, all dated <= 2024-01-02)
As-of:     2024-01-02
Targets:   UST_2Y, UST_5Y, UST_10Y, UST_30Y at horizons 21 BD and 63 BD
Output:    forecast.parquet [draw, asset, horizon, value]
           n_draws >= 200 (strongly recommend >= 500)
           Each draw MUST contain rows for ALL FOUR assets (joint draw, not independent)
Score:     CRPS composite; joint variogram (30 %) is the primary differentiator
```

Correct output structure for draw 0:
```
draw  asset    horizon  value
0     UST_2Y   21       4.32
0     UST_5Y   21       4.18
0     UST_10Y  21       4.10
0     UST_30Y  21       4.25
```
All four yields in draw 0 come from the same "scenario" — they are internally consistent.
A reasoning agent that read the FOMC statement and applied a consistent macro view across
all tenors should produce draws where the tenors co-move realistically.

### Common mistakes in F3

1. **Independent draws.** The most common mistake: sampling each asset separately and stacking.
   The variogram score detects this because independent draws overstate cross-asset distances.
   Use a multivariate model (VAR, copula, deep generative) or draw from a joint posterior.
2. **Applying text to marginals only.** An agent might use text to adjust each tenor's mean
   individually but still draw them independently. This misses the whole point. The text
   should inform the joint scenario: "in this draw, Fed policy stays restrictive, so ALL
   tenors are elevated and the curve is flat."
3. **Too few draws.** Less than 200 draws fails gate g3. Less than 500 draws triggers a warning.
4. **Mismatched draw indices.** In the output parquet, every draw index must have exactly one
   row for each target asset x horizon. A missing (draw, asset, horizon) combination fails g3.
5. **Forgetting cross-horizon correlation.** For multi-horizon cards, the draws at horizon 21
   and horizon 63 for the same asset should also be correlated (the future at 63 BD depends
   on the future at 21 BD).

---

## F4 — Tail/shock-from-text

### What this family tests

F4 is the stress test for extreme events driven by text signals. The text corpus contains
documents that foreshadow a shock — a central bank communication warning of exceptional
measures, an inflation release commentary noting the highest reading in 40 years, a political
risk dispatch about an upcoming policy event. The as-of date is set before the shock. The
target window spans the shock's impact.

The agent must read the text, recognize the shock signal, and assign **meaningful probability
to extreme outcomes** — even if the recent numeric history looks calm. This is where text
matters most: a text-blind time-series model that only sees historical volatility will produce
too-narrow tails. The reasoning agent that reads "inflation at 8.5 %, highest since 1981" and
understands its implications for the rate path can produce the fat-tailed forecast that the
shock demands.

### The role of text

In F4, the text provides the **shock foreshadowing signal**. Examples:

- FOMC minutes from October 2021 using the word "expedient" in the context of tapering,
  months before the 2022 hiking cycle — the panel still shows rates near zero. A text-blind
  model says "rates will stay near zero." A reasoning agent says "the Fed is telegraphing
  urgency — widen the right tail dramatically."
- A UK CPI release commentary (August 2022) noting "inflation well above target with no
  near-term relief" — months before the mini-budget GBP crash. The panel shows GBP/USD
  near 1.20. The text warns of tail risk.
- An FOMC Jackson Hole speech (August 2022) where Powell uses the phrase "forceful and rapid"
  — directly foreshadowing the fastest hiking cycle in decades. Text-blind models miss this.

### Which score component is stressed and why

**Tail penalty is primary (20 % weight).**

The tail penalty formula: take your draws, find the 1st, 5th, 95th, and 99th percentile
values. For each quantile q, compute how far the realized outcome fell outside that quantile.
Sum across all quantiles, assets, and horizons. Lower is better.

A text-blind model anchored on calm history will have its 99th percentile far below the
realized shock outcome. The penalty for missing the extreme quantile is multiplied by 0.01
(the quantile level) — but when the realized outcome is 10x the 99th percentile, the penalty
is still enormous.

An agent that reads the text and widens its right tail (for a rate shock) or left tail (for a
crash) before the event will pay a much lower tail penalty.

The marginal CRPS is secondary — if the marginals are very wrong, the composite suffers.
But the differentiating factor is the tail penalty.

**Recommendations for F4**: use Student-t distributions (heavier tails than Gaussian),
jump-diffusion models, historical simulation with stress scenarios, or any model that
explicitly allows for fat tails. Use the LLM to shift the tail explicitly: "given this
text, the probability of a 200 bps rate hike within 6 months is approximately X% — skew
the draw distribution accordingly." Use at least 1,000 draws for F4 cards.

### As-of date and leakage rules

- The as-of date must precede the shock event by at least the forecast horizon.
  For a 63-BD (approximately 3-month) card targeting the Q1 2022 rate shock, the as-of date
  must be no later than approximately 2021-10-01.
- The text corpus contains only documents with timestamps <= as-of date. The shock-foreshadowing
  text is in the pre-asof corpus. Gate g2 rejects any corpus document dated after the asof.
- No post-event data may appear in the input panel. This includes Fed funds futures, swap
  rates, or any series that would reveal the event's timing or magnitude in advance.
- **Critical**: participants must NOT engineer features that use look-ahead knowledge of the
  event. The agent must work from information available at the as-of date — including the
  text corpus. Using ex-post knowledge of event dates defeats the entire point.

### An example forecast card

```
Card ID:   t2-F4-ust-hike-cycle-2021Q4
Family:    T2-F4
Panel:     rates/ust-daily (DGS2, DGS10, 2000-01-03 to 2021-10-01)
Text:      text/  (FOMC September 2021 statement, Jackson Hole August 2021 speech,
                   CPI commentary September 2021, all dated <= 2021-10-01)
As-of:     2021-10-01
Targets:   UST_2Y, UST_10Y at horizons 63 BD (approx. Jan 2022) and 126 BD (approx. Apr 2022)
           The held-out window spans the onset of the 2022 Fed tightening cycle.
Output:    forecast.parquet [draw, asset, horizon, value]
           n_draws >= 200 (strongly recommend >= 1000 for tail quantile accuracy)
Score:     CRPS composite; tail penalty (20 %) is the primary differentiator
```

What good draws look like: a wide, right-skewed distribution — some draws near historical
levels (0.3-0.5%), but a meaningful fraction reaching 2-4%+ (the actual outcome). The
agent that read the September 2021 FOMC language and the August Jackson Hole speech should
have skewed its distribution rightward even with rates near zero in the panel.

### Common mistakes in F4

1. **Gaussian marginals without fat-tail correction.** The single biggest failure mode.
   Always check: does your model's 99th percentile allow for a 5-10x move from current
   levels? If not, it will fail on shock events.
2. **Not using the text to inform the tail.** Many agents read the text and adjust their
   mean forecast but leave the tails symmetric. The text's value in F4 is specifically
   about widening the tail in the direction the text signals.
3. **Too few draws.** The 1st percentile needs at least 100 draws to estimate reasonably.
   200 gives you just 2 order statistics at the 1% tail. Use 1,000+ for F4.
4. **Looking-ahead at event timing.** Manually setting higher volatility for a specific
   window because you know (ex-post) it was a crisis period. The agent must derive increased
   uncertainty from the pre-event text and series, not from privileged knowledge.
5. **Symmetric tails when direction is clear.** In 2021, with rates near zero, the
   distribution should be right-skewed (rates can go up a lot, but not far below zero).
   Symmetric Gaussian tails overstate the probability of negative yields.
6. **Not running `require_samples = true` cards in samples mode.** F4 cards reject
   parametric submissions. Gaussian mean + covariance cannot represent fat tails adequately.

---

## Scoring component matrix (summary)

| Family | Marginal CRPS (50 %) | Joint variogram (30 %) | Tail penalty (20 %) | Text role |
|--------|---------------------|------------------------|---------------------|-----------|
| F1 Continuation-with-context | **Primary** | Secondary | Incidental | Incremental signal |
| F2 Text-cued regime shift | **Primary** | Secondary | Important | Pivotal leading indicator |
| F3 Cross-asset reasoning | Secondary | **Primary** | Incidental | Cross-market inference |
| F4 Tail/shock-from-text | Secondary | Secondary | **Primary** | Shock foreshadowing |

"Primary" = this component differentiates strong from weak submissions in this family.
"Secondary" = non-trivial but not the main differentiator.
"Incidental" = present in the composite but rarely the source of meaningful score spread.

---

## How the composite score works across all four families

The sealed evaluation set draws cards from all four families. Your position is the
equal-weight mean of your composite scores across every card, lower is better — single-cell
and multi-cell alike, because the weight redistribution above puts the text-blind baseline at
1.0 on both shapes. Every card counts equally, and a card you do not score takes the
pre-committed worst-case value (4.0) rather than dropping out of the average. This means:

- A model that is great at F1 but ignores dependence (F3) and tails (F4) will score mid-tier.
- A model that nails tail calibration (F4) but is wildly over-confident on in-distribution
  series (F1) will also score mid-tier.
- An agent that ignores the text corpus entirely will score like a text-blind baseline on
  all four families.
- The winning submission is typically the one that reads text well, applies it consistently
  across assets and time horizons, and produces fat-tailed joint distributions.

The baselines (Theta/AutoARIMA, Chronos, TimesFM, Lag-Llama, MOIRAI) are text-blind
reference points. A submission that does not beat at least two baselines on the validation
split receives a warning flag on the leaderboard. The goal is to build something
demonstrably better — not just to pass the gates.

The **information uplift** (the best text-blind baseline's score minus yours on the same
cards — composite scores are lower-better, so positive uplift means you beat the baseline)
is reported as a diagnostic. It tells you how much value your agent extracted from the text
corpus. A zero or negative uplift means the text is not helping — review your prompting
and retrieval strategy.

---

## Quick reference: per-family checklist

### F1
- [ ] All target assets are present in the training panel through the as-of date
- [ ] Text corpus has timestamps <= as-of date (gate g2 will check this)
- [ ] Agent actually reads and uses the text corpus (not just the panel)
- [ ] As-of date >= 6 calendar months before first target date
- [ ] n_draws >= 200; per-asset standard deviation > 0
- [ ] No NaN or Inf in any draw value

### F2
- [ ] Text corpus contains the regime-shift signal in pre-asof documents
- [ ] Agent identifies and uses tone-shift / early-warning language from text
- [ ] For transfer-configuration: target series is **entirely absent** from all input panel files
- [ ] Text corpus has timestamps <= as-of date
- [ ] Distribution is appropriately asymmetric if text implies directional risk
- [ ] As-of date >= 3 calendar months before first target date
- [ ] n_draws >= 200

### F3
- [ ] Every draw index has rows for all target assets AND all horizons (joint draws)
- [ ] Text signals are applied consistently across all assets within each draw
- [ ] n_draws >= 200 (recommend >= 500)
- [ ] `require_samples = true` — samples format mandatory
- [ ] Model uses a multivariate approach (not independent-marginal sampling)
- [ ] Text corpus has timestamps <= as-of date
- [ ] As-of date >= 1 calendar month before first target date

### F4
- [ ] `require_samples = true` — samples format mandatory, Gaussian parametric rejected
- [ ] n_draws >= 200 (strongly recommend >= 1000 for tail accuracy)
- [ ] Distribution has fat tails informed by text shock signals
- [ ] Text-driven tail direction is correct (right-skewed for rate hikes, etc.)
- [ ] As-of date precedes the regime event by at least the forecast horizon
- [ ] Text corpus has timestamps <= as-of date; no post-event documents
- [ ] No post-event information in model weights or input panels
