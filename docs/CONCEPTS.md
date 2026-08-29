# Track 2 — Core Concepts in Plain English

## Executive summary (read this first)

Track 2 asks you to build a **reasoning agent** that forecasts financial time series — not
just "what will the price be?" but "what is the full range of possible futures, and how
likely is each?" The agent gets both numeric time-series panels and a frozen text corpus.
The headline scientific question is whether reading text makes the forecast better.

This document explains the key ideas in plain words. You do not need a PhD in statistics
to understand it. You need a clear mental model so you know what the scoring code is
actually measuring, and why the text corpus matters.

**Unfamiliar terms?** The competition-wide GLOSSARY (`Agenthon-2026/Agenthon2026-public`, file
`docs/GLOSSARY.md`) defines every term used across the competition. That is the same public
repository this track installs `qfbench2-common` from.

Read this document before writing any code.

---

## 1 — Time-series forecasting vs. tabular prediction

**Track 2 = time-series data.** A time series is a sequence of observations indexed by time:
"the 10-year Treasury yield was 4.1% on Monday, 4.12% on Tuesday, 4.08% on Wednesday, ..."
The data has temporal structure — what happened yesterday is relevant to what happens tomorrow.
Track 2 asks you to forecast the continuation of such series forward in time.

**Track 4 = general tabular data.** A table of entities — companies, loans, transactions —
where each row is an independent entity and you predict a label or value for it.
Temporal sequence does not drive Track 4.

Both tracks add text and LLM reasoning, and both run in Docker with no open internet
(model-API calls through the organizer's audited proxy are the only permitted egress).
The distinction matters because the right models differ: Track 2 calls for
**time-series foundation models** (Chronos, TimesFM, Lag-Llama, MOIRAI) combined with
text reasoning; Track 4 calls for **tabular foundation models** combined with text reasoning.

---

## 2 — Point forecast vs. probabilistic forecast

A **point forecast** is a single number: "The 10-year Treasury yield in 3 months will be 4.2 %."
This is what most traditional models produce. It is useful, but it hides the most important
question: *how sure are you?*

A **probabilistic forecast** (also called a **predictive distribution**) answers "what is the
full range of outcomes, and how likely is each?" Instead of "4.2 %", it says:

- "There is a 10 % chance the yield is below 3.5 %"
- "There is a 50 % chance it is below 4.1 %"
- "There is a 90 % chance it is below 5.0 %"

Or equivalently, expressed as a set of 500 random draws that together sketch out the shape
of the distribution.

**Why probabilistic forecasts matter in finance:**
- Risk managers need to know tail probabilities (what is the 1 % worst-case?).
- Portfolio optimizers need the full distribution to compute portfolio variance.
- A narrow "confident" forecast that turns out to be wrong is far more dangerous than an
  honest "I am uncertain" forecast with wide intervals.

Track 2 rewards honest uncertainty. A model that says "I have no idea — it could be anywhere
from 2 % to 6 %" can still score well if those bounds are well-calibrated, even if the point
forecast (midpoint: 4 %) is not particularly precise.

---

## 3 — The text corpus and the as-of cutoff

Every Track 2 card comes with two inputs: a **numeric panel** (time-series data) and a
**text corpus** (a collection of dated documents: FOMC statements, central-bank speeches,
macro-release headlines, COT commentary, news).

The text corpus is **frozen and time-stamped**. Every document in it has a date on or before
the card's as-of date (the information cutoff). There are no documents dated after the as-of
date — that would be look-ahead leakage. The harness enforces this via **gate g2** (the
cutoff-and-resource gate): it checks that every text-corpus document has timestamp <= asof.
If any document fails this check, the submission is rejected for leakage.

**Why a frozen text corpus?** The goal is to simulate what a real investor knew on the
as-of date. An investor on 2021-10-01 had access to the September 2021 FOMC statement but
not the November 2021 statement. The frozen corpus preserves this information boundary.

**Why text at all?** Numeric time-series models can only extrapolate historical patterns.
They cannot read an FOMC statement and understand that "expedient" signals urgency. They
cannot notice that a CPI commentary says "highest in 40 years" and widen their right tail
accordingly. A reasoning agent that reads text can beat a text-blind baseline on exactly
these cases. The four card families (F1–F4) are designed to test different ways text adds
signal — see `docs/CATEGORIES.md`.

**The agent may not fetch new text at inference time.** The restricted network enforces
this: the only egress from the container is model-API calls through the organizer's audited
proxy — no web pages, no data feeds, no live text. Vendor-side tools (web search, retrieval)
must be disabled in those API calls. The agent may only use the text corpus provided in
`/input/text/`; it is sealed inside a Docker container with only the provided inputs plus
its declared model APIs. (Local smoke runs use `--network=none`, which blocks everything.)

---

## 4 — Agentic forecasting

An **agentic forecast** combines two components:

1. **A time-series forecasting component** — a statistical or neural model that produces
   a predictive distribution over future values based on the numeric panel (historical series).
   Examples: a VAR model, a GARCH model, or a time-series foundation model (Chronos, MOIRAI).

2. **An LLM reasoning component** — a language model that reads the text corpus, extracts
   relevant signals (tone shifts, surprise magnitude, risk flags), and adjusts the forecast
   accordingly. The LLM might: widen the right tail after reading an "urgent" central bank
   speech; shift the mean after a CPI surprise headline; adjust cross-asset correlations
   after reading a multi-market commentary.

The two components interact: the LLM nudges or conditions the forecasting component's output.
How exactly they interact is up to you — this is the design space of Track 2.

**Contrast with the baselines.** The five text-blind baselines (Theta/AutoARIMA, Chronos,
TimesFM, Lag-Llama, MOIRAI) use only the numeric panel. They implement the forecasting
component but have no LLM reasoning component. They are the bar your agent must beat.

---

## 5 — Information uplift and text ablation

**Information uplift** is the improvement your agent achieves over the best text-blind
baseline on the same cards. If your composite score is 0.120 and the best baseline scores
0.145 on the same cards, your uplift is 0.025 (lower scores are better, so positive uplift
means you beat the baseline).

The uplift is the headline scientific result of the competition: it answers "does reading
text actually help forecast time series?" The ranking uses composite scores (aggregated on
one board — see "How the leaderboard is built" below); the uplift is a diagnostic reported
alongside.

**Text ablation** is running your agent with an empty text corpus (or a corpus of blank
documents) and comparing the score to your full agent. This isolates the marginal value
of text within your system. We encourage teams to submit both a full and an ablated forecast
for at least one validation card and report the difference.

If your ablated score is nearly the same as your full score, the LLM is not effectively
using the text. Improve your retrieval strategy, prompting, or how the LLM output is
connected to the forecasting component.

---

## 6 — Time-series foundation models

A **time-series foundation model** is a neural network pre-trained on a large collection of
diverse time-series datasets, designed to generalize to new time series at inference time
without task-specific retraining. Think of it as the "GPT" equivalent for time-series data.

Examples in the baselines:

| Model | Pre-training | Key strength |
|-------|-------------|--------------|
| Chronos (Amazon) | Millions of TS from diverse domains | Good zero-shot probabilistic forecasting |
| TimesFM (Google) | Large-scale TS corpus | Strong marginal calibration |
| Lag-Llama (Meta) | Open financial and general TS | Designed for heavy tails |
| MOIRAI (Salesforce) | Diverse frequency TS | Multi-frequency aware |
| Theta/AutoARIMA | Classical statistical | Fast, interpretable, solid baseline |

These models are text-blind: they see only the numeric panel. Your task is to build a
reasoning agent that combines one (or more) of these with LLM text reasoning.

---

## 7 — Marginal vs. joint distribution

**Marginal** means: looking at one asset in isolation. "What is the distribution of UST_10Y
in 21 business days?" is a marginal question. You can answer it without caring about what
UST_2Y is doing.

**Joint** means: looking at multiple assets together. "What is the joint distribution of
UST_2Y, UST_10Y, and UST_30Y in 21 business days?" is a joint question. It asks not just
where each yield will be, but *how they will move relative to each other*. Will they all rise
together? Will the 2Y rise more than the 30Y (a flattening)? Will they diverge?

**Example of the difference:**
- A model that draws UST_2Y and UST_10Y independently will sometimes produce draws where
  UST_2Y = 5.0 % and UST_10Y = 2.0 % (inverted by 300 bps). This rarely happens in reality.
  This is a *joint* error, even if each marginal distribution is correct.
- A model that draws from a joint distribution (e.g., a multivariate normal or a VAR model)
  will keep the relationship: when UST_2Y is high, UST_10Y tends to also be high.

**Which score measures each:**
- Marginal CRPS measures each asset in isolation.
- Joint variogram score measures the relationships between assets.

See sections 9 and 10 below for the formulas.

---

## 8 — CRPS: the core accuracy and calibration score

**CRPS** stands for Continuous Ranked Probability Score. It is a number that rewards two
things at once: (1) being close to the realized outcome, and (2) being honest about
uncertainty. Lower CRPS is better.

**Intuition:**
Imagine you bet on the temperature tomorrow. You can bet by naming a full distribution
(not just a single number). CRPS measures how well your distribution matched the actual
temperature. If you were confident (narrow distribution) and right, you score very well.
If you were confident and wrong, you score very poorly. If you were uncertain (wide
distribution), you score moderately regardless of whether you were right or wrong.

**A tiny example with numbers:**
The 10-year yield today is 4.0 %. You forecast two possible distributions:

- **Model A (overconfident):** mean = 4.1 %, standard deviation = 0.1 % (very narrow)
- **Model B (honest):** mean = 4.1 %, standard deviation = 0.5 % (moderate)

Realized outcome: 4.6 % (a surprise rise).

Model A's distribution assigns near-zero probability to 4.6 %. It pays a large CRPS penalty
because the outcome was far in its tail.

Model B's distribution assigns meaningful probability to 4.6 %. It pays a smaller CRPS
penalty.

Even though both models had the same mean forecast, Model B scores better because it was
honest about uncertainty.

**The CRPS formula (simplified):**
For a set of S draws {d_1, d_2, ..., d_S} and realized value y:

```
CRPS = (1/S) * sum |d_s - y|  -  (1/(2*S^2)) * sum_s sum_t |d_s - d_t|
```

Term 1: average distance from each draw to the realized outcome (accuracy).
Term 2: average pairwise distance between draws (penalizes over-spread).

Together: CRPS is low when draws cluster near the realized outcome. It is high when
draws are far from the realized outcome, OR when draws are unnecessarily spread out.

**In the Track 2 composite score**, CRPS is computed for each (asset, horizon) pair and
averaged. It has weight 50 %.

---

## 9 — Variogram score: measuring dependence

For a single asset, CRPS is sufficient. But Track 2 also evaluates *joint* behavior —
how well the model captures the relationships between multiple assets.

**Variogram score** measures dependence structure specifically. It focuses on whether
the *distances* between assets in the draws match the distances between assets in reality.

**Plain explanation of the variogram score:**
Take two assets: UST_2Y and UST_30Y.
- In each draw, compute (draw_UST_2Y - draw_UST_30Y).
- The average squared value of this difference across all draws measures
  "how spread out are the yield pairs in the model's view?"
- Now compare to (realized_UST_2Y - realized_UST_30Y) squared.
- If the model's spread matches the realized spread, the variogram score is low.
- If the model treats the assets as independent (too much spread in the differences),
  the variogram score is high.

**Why "variogram"?** In geostatistics, a variogram measures spatial correlation.
The variogram score uses the same idea: it checks whether the model's draws exhibit
the same *correlation structure* as the actual outcomes.

**In the Track 2 composite score**, the variogram score has weight 30 %. It is most
important for F3 (cross-asset reasoning) cards.

---

## 10 — Tail calibration and the tail penalty

### Tail calibration

A forecast is **tail-calibrated** if the extreme quantiles of the predictive distribution
match the observed frequency of extreme outcomes. Concretely:

- "The 1st percentile" of your distribution is the value below which your draws say outcomes
  fall 1 % of the time. Across many forecasts, approximately 1 % of realized outcomes should
  actually fall below that threshold.
- If 10 % of realized outcomes fall below your "1st percentile" threshold, your distribution
  has tails that are too thin (overconfident at the extremes).

**The tail penalty** in Track 2 is computed at the four extreme quantiles: 1 %, 5 %, 95 %, 99 %.
It uses the **pinball loss** (also called the "check function") at each quantile:

```
pinball(y, q_hat, tau) =
    tau * (y - q_hat)         if y > q_hat    (outcome above quantile: you were too conservative)
    (1 - tau) * (q_hat - y)   if y <= q_hat   (outcome at or below quantile: you were too optimistic)
```

where y is the realized outcome, q_hat is the quantile value from your draws, and
tau is the quantile level (0.01, 0.05, 0.95, or 0.99).

In F4 (tail/shock-from-text) cards, the tail penalty is where reasoning agents should
visibly outperform text-blind baselines: the text foreshadows the shock before the numbers
show it, letting the agent assign meaningful tail probability before the event.

### PIT (Probability Integral Transform)

The **PIT** is a diagnostic tool. For each forecast, compute the percentile of the realized
outcome within the predictive distribution. If your forecasts are well-calibrated, PIT values
should be **uniformly distributed** between 0 and 1 across many forecasts. If PIT values
cluster near 0 or 1, your distribution is too narrow. If they cluster in the middle, your
distribution is too wide.

The harness computes PIT for 50 % and 90 % coverage intervals and reports them as diagnostics.
They do not directly affect the score but help you diagnose calibration problems.

### Coverage

**Coverage** is the simplest tail calibration check. For a 90 % prediction interval:
- Compute the interval [5th percentile draw, 95th percentile draw] for each forecast.
- Count what fraction of realized outcomes fall within that interval.
- If well-calibrated: approximately 90 % should be inside.

If coverage is 60 %, your intervals are too narrow. If coverage is 99 %, too wide.

---

## 11 — As-of date and look-ahead leakage

The **as-of date** (sometimes written "asof") is the **last date your agent is allowed to
look at**. Everything the agent sees must come from on or before this date. Everything it is
asked to forecast must come from strictly after it.

**Look-ahead leakage** (also just "leakage") is when the agent — accidentally or
intentionally — uses information from after the as-of date.

**Two kinds of leakage in Track 2:**

1. **Panel leakage.** A panel contains a row with `date > asof`. This is an ORGANIZER defect,
   not a participant one, and it is caught before you ever see the unit: the staging step reads
   every row of every published panel against the card's as-of and refuses to publish a unit
   that fails. There is no runtime exception — earlier revisions of this document described a
   `LeakageViolation` that exists in no repository.

2. **Text corpus leakage.** A document in the text corpus has a timestamp after the as-of
   date. Gate g2 checks every document timestamp in `card.toml [text] cutoff` and in the
   corpus metadata. If any text document is dated after the asof, the submission fails g2.
   The agent may not fetch new text at inference time — the restricted network (model-API
   proxy only, everything else blocked) enforces this.

**Examples of leakage:**
- Training the model on data through 2024 and then setting the as-of date to 2023. The model
  "remembers" 2024 events and its forecasts for late 2023 → 2024 will be suspiciously accurate.
- Including the December 2021 FOMC statement in a corpus for a card with as-of November 2021.
  Even one day of post-asof text is leakage.
- Calling an external API at inference time that returns current (post-asof) market data.
  This is why the harness restricts the network: model APIs are reachable (through the
  audited proxy, with vendor-side web search and retrieval disabled), data feeds are not.

**How the harness prevents leakage:**
1. Panel cutoff, enforced at PUBLICATION time: every row of every staged panel is read against
   the card's as-of, and a unit with a post-as-of row is refused rather than published.
2. Text corpus cutoff: gate g2 verifies every text document timestamp <= asof.
3. Restricted network: at scoring time the only egress is model-API calls through the
   organizer's audited proxy; every connection is logged. Local smoke runs use
   `--network=none`, which blocks all network calls outright.
4. Weight freeze: Docker image digest is recorded; model weights frozen at build time.

---

## 12 — What n_draws means and why >= 200

**n_draws** is the number of Monte Carlo samples (draws) in your submitted forecast. Each
draw represents one possible future path of the forecasted variables.

All the scoring metrics (CRPS, variogram, tail penalty) are estimated from your draws.
The estimation error from using S draws instead of the true distribution is approximately
proportional to 1/sqrt(S). Specific impacts:

| Metric | Why n_draws matters |
|--------|---------------------|
| Marginal CRPS | Converges well at 200 draws; 500 is comfortable |
| Variogram score | Uses pairwise distances; 200 draws gives ~20,000 pairs; 500 gives ~125,000 |
| Tail penalty at 1 % | From 200 draws, only 2 draws are below the 1 % quantile — very noisy estimate |
| Tail penalty at 1 % | From 1,000 draws, 10 draws are below 1 % — still small but manageable |

**Mandatory minimums:**
- All cards: n_draws >= 200 (hard gate g3 failure if below this)
- F3 and F4 cards: the harness issues a warning if n_draws < 500
- F4 cards specifically: we recommend n_draws >= 1000 for reliable tail estimates

---

## 13 — How the leaderboard is built

Your composite score is computed per card. Turning many per-card scores into one position
takes three steps, and all three are fixed before dev-phase scoring opens.

**Step 1 — every card is put on a comparable scale.** Raw composites carry the units of what
they forecast: a CPI-index card's CRPS is thousands of times a bond-yield card's, so a plain
average across cards would be dominated by whichever card has the largest numbers. Each card's
components are therefore divided by the same components of an official **text-blind baseline**
on that card (a random walk that sees the panel and none of the text). After that division a
score of **1.0 means "no better than the text-blind baseline"** and below 1.0 means you beat
it, on every card alike.

**Step 2 — a single-number card has its weights redistributed, so every card is on the same
scale.** A card that asks for a single number (one asset, one horizon) has no relationships
between forecasts for the joint-variogram term to measure, so that term is 0 *by construction,
not by merit*. Under the plain 0.5/0.3/0.2 weighting the baseline would anchor at 0.7 on such
a card and 1.0 everywhere else — two different scales. The variogram's weight is therefore
redistributed over the terms that structurally exist (see [CATEGORIES.md](CATEGORIES.md)):

| Card shape | Effective weights | Baseline anchors at |
|---|---|---|
| **single-cell** (one asset × one horizon) | 0.714 x CRPS + 0.286 x tail | 1.0 |
| **multi-cell** (everything else) | 0.5 x CRPS + 0.3 x variogram + 0.2 x tail | 1.0 |

Because both shapes anchor in the same place, they belong in the same average. Your score is
reported with a bootstrap confidence interval that resamples whole groups of cards sharing an
as-of date, because cards written against the same date share the same market shock and are
not independent samples.

**Step 3 — one ranking: the equal-weight mean over every card, lower is better.** Every card
counts the same. No card family or shape dominates by scale, and adding cards on the
pre-announced schedule dilutes every card's share equally rather than changing any card's
standing relative to another.

**Every card is in the denominator.** A card that is inadmissible (a failed gate), errors, or
is never attempted takes a **pre-committed worst-case value of 4.0** — four times as bad as
ignoring the text entirely, since 1.0 is the text-blind baseline. Real scores are **clipped at
that same 4.0**. Neither number is chosen per-track after the fact: 4.0 is the worst end of the
declared metric domain `[0.0, 4.0]` in the signed evaluation plan, fixed before scoring opens.

Both halves matter, and the second is the one worth reading twice. If failures were simply
dropped, a card would leave the numerator *and* the denominator, and you would be better off
failing the cards you expect to score worst on. And a penalty without the clip would still be
beatable — facing a card you expect to score 5.0 on, you would rather fail it and take 4.0.
With the clip, **failing a card can at best tie the worst possible attempt at it, never beat
it**. There is no card you are better off skipping.

Your entry reports the number of cards scored alongside the total, so coverage is visible.

> **In force from the scoring-bundle refresh.** The scorer deployed as this is written still
> drops a failed card from the average instead of charging it 4.0. Until the refresh lands, a
> failed card simply does not count on the Development board. The rule above is what the signed
> evaluation plan commits to and what decides the Final ranking; if you see the older behaviour
> on the practice board, that is why. This note is removed when the refresh ships.

## 14 — Quick glossary of terms used in scoring output

| Term | Plain meaning |
|------|--------------|
| `composite_score` | The final weighted score: 0.5 x CRPS + 0.3 x variogram + 0.2 x tail. Lower is better. On a single-cell card the variogram is 0 by construction and its weight is redistributed: 0.714 x CRPS + 0.286 x tail. |
| `marginal_crps` | Average CRPS across all (asset, horizon) pairs. Measures accuracy + per-asset calibration. |
| `joint_variogram` | Variogram score measuring cross-asset dependence. Measures whether the model got relationships right. |
| `tail_penalty` | Mean pinball loss at 1%/5%/95%/99% quantiles. Measures tail calibration. |
| `n_draws` | Number of Monte Carlo samples you submitted. |
| `pit_50` | Fraction of realized outcomes inside the 50 % prediction interval (should be ~0.50). |
| `pit_90` | Fraction of realized outcomes inside the 90 % prediction interval (should be ~0.90). |
| `information_uplift` | The best text-blind baseline's composite score minus your composite score on the same cards. Lower composite is better, so positive uplift means text helped. (Diagnostic, not ranking.) |
| `text_ablation_delta` | Your text-ablated score minus your full-agent score. Lower composite is better, so positive means text is contributing. |
| `T2_UNCALIBRATED_MARGINAL` | Gate g3 flag: marginal distribution is degenerate (std ~= 0) or has non-finite values. |
| `T2_BAD_DEPENDENCE` | Gate g3 flag: cross-asset or cross-horizon dependence is inconsistent with the joint task. |
| `T2_TAIL_MISCALIBRATION` | Gate g3 flag: 1%/5%/95%/99% coverage is outside tolerance. |
| `DNF` | Did Not Finish — scored as the worst possible score; caused by leakage, missing files, or wall-time excess. |
| `asof` | As-of date: the last date the agent may see. All forecasts are for dates after this. |
| `horizon` | Number of business days between the as-of date and the target date. |
| `card_family` | One of F1, F2, F3, F4 — determines which scoring component is primary. |

---

## 15 — Putting it all together: how a good agent thinks

A strong Track 2 submission does all of the following:

1. **Reads the text corpus actively.** Retrieves relevant documents for the forecast period,
   extracts signal (tone shifts, surprise magnitudes, risk flags), and connects them to the
   time-series model's parameters or outputs.

2. **Outputs a full distribution, not a point forecast.** 200+ draws per card, covering a
   realistic range of outcomes.

3. **Is honest about uncertainty.** Does not produce falsely narrow intervals. Intervals
   widen when the forecast horizon is longer, when the asset is more volatile, and when
   the text signals higher uncertainty.

4. **Captures relationships between assets.** Draws from the joint distribution, not
   independent marginals. When oil rises in draw 7, the airline stock should also fall in
   draw 7 (if the agent has learned that relationship). Text signals should be applied
   consistently across all co-moving assets within each draw.

5. **Has fat tails when text signals shock risk.** Uses Student-t, jump-diffusion, historical
   simulation, or another fat-tail method when the text corpus warns of extreme outcomes.
   Does not rely purely on Gaussian assumptions anchored to calm history.

6. **Respects the as-of date.** Uses no data or text after the as-of date. Verifies with
   `cutoff_ok`. Does not call external APIs at inference time.

7. **Can be ablated.** The text component should be cleanly separable so you can measure
   its marginal contribution by running the agent without text.

The baselines (Theta, AutoARIMA, Chronos, TimesFM, Lag-Llama, MOIRAI) are text-blind
time-series foundation models. Beating them requires either better multivariate joint
modeling (for F3), better tail coverage from text signals (for F4), or better regime
detection from text (for F2) — or all three.
