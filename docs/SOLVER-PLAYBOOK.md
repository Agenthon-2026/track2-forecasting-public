# Track-2 Solver Playbook — turning the given data into a high-quality forecast

A step-by-step method for producing a well-calibrated probabilistic forecast from a Track-2 unit's
inputs (numeric panels + dated text corpus). It is reverse-engineered from the scoring metric and
from the methods that actually won on the 103-card independent-solve evaluation (2026-07-24): the
top-scoring solves were **regime-aware (26/30), text-conditioned on drift (25/30), scenario
mixtures (20/30) with fat tails (28/30)**. Follow the metric, not your point estimate.

## 0. What is being scored (read this first)

You submit **draws** (a Monte-Carlo sample of the target's value at each horizon), not a point.
The metric is a CRPS composite, **lower is better**:

    S = 0.5 · CRPS_marginal  +  0.3 · S_joint (variogram)  +  0.2 · P_tail (PIT calibration)

Three consequences that dictate everything below:

1. **You are graded on the whole distribution.** A tight wrong distribution is punished harder than
   a wide one that contains the truth. Report your honest uncertainty — *as tight as the evidence
   justifies and no tighter.*
2. **Joint structure matters (30%).** For multi-asset / multi-horizon cards, the cross-asset and
   cross-horizon **dependence** is scored, not just each margin. Simulate correlated paths, don't
   forecast each series independently.
3. **Tail calibration matters (20%).** Your stated 90% interval must contain the truth ~90% of the
   time across the suite. Over-confidence (too-thin tails) is the most common way to lose points —
   the eval found systematic left-tail under-coverage; if in doubt, widen the downside.

## 1. Establish the as-of frame

- The **as-of date** is the panel `end_date` in `forecast_spec.json`. You stand there; nothing after
  it is known. Horizons are in **business days** after the as-of.
- Read `forecast_spec.json`: target `asset_ids`, `horizons`, `target_type` (`level` vs `log_return`
  — this changes everything downstream), `value_unit`, `n_draws_min`.
- Confirm no leakage: every panel row and every text timestamp is ≤ as-of. (The harness enforces
  this at gate g2; a post-as-of document is a disqualification, not a hint.)

## 2. Read the numbers before the words — build the statistical backbone

1. **Load the panel(s)** (long format `date, asset, value, panel_id`). Pivot to the target series;
   record the **spot** (last value at as-of).
2. **Characterise the horizon-h change empirically.** Compute overlapping h-business-day changes
   over history; get their **standard deviation** (this is your baseline spread) and check for
   mean-reversion (regress the h-day change on the prior h-day run-up — many rate/yield series
   partially retrace).
3. **Estimate the current volatility regime** (EWMA or a trailing window) — recent vol usually
   dominates a full-history unconditional vol. Your distribution width should sit between the calm
   estimate and the full-history estimate, closer to whichever the corpus says the regime is.
4. **Set a reference baseline in your head:** a random-walk-from-spot with that empirical spread.
   You must *beat* it; the corpus is how you do that. If the target series is **absent from the
   panel** (the TRANSFER / EM cards — see `data/em_reference/README.md`), there is no own-history:
   derive the level from a related panel series (G10 beta) plus the text, and set width from the
   related series' vol scaled by an appropriate beta.

## 3. Read the corpus — convert text into three quantitative adjustments

Every document is dated and central-bank/statistical-agency sourced. Turn qualitative signal into
numbers on exactly three knobs; do **not** narrate.

- **Drift (center).** Does the text argue the series should trend up/down vs a random walk over this
  horizon? (e.g. a hawkish hold with "ongoing increases" → positive rate drift; an easing pivot →
  negative.) Most winning solves applied only a *modest* drift — the corpus moves the center by a
  fraction of the horizon sd, not multiples.
- **Regime / width.** Does the text imply elevated or compressed uncertainty (crisis, binary policy
  decision inside the window, energy shock)? Widen or tighten the spread accordingly, and fatten the
  tails when a discrete event (vote, decision, peg) sits inside the horizon.
- **Scenarios (shape).** If the corpus describes a **branching** outcome (hike vs hold, Leave vs
  Remain, floor holds vs breaks), do **not** forecast a single blob — build a **scenario mixture**:
  2–4 labelled scenarios, each with its own center/width, weighted by your read of the text. This is
  what produced the best tail scores on event cards.

Two rules govern how far each knob may move, and both exist because of measured failure modes.

- **Mark every adjustment as established or inferred.** An adjustment the corpus *states* — a
  decision taken, a print released, a level announced — may narrow your distribution. An adjustment
  you *infer* from tone may move the centre but must not narrow it. Collapsing the two is how a
  remembered outcome gets laundered into a confident-looking forecast, and it is the single thing
  the `g4`-style distribution checks are looking for. Your `forecast_rationale.md` should make the
  distinction visible line by line.
- **When the panel and the corpus disagree, keep the disagreement.** The temptation is to average a
  corpus down to one tone and nudge the centre by it. Do not: a suite of adversarial variants
  (`units-adversarial/`) exists precisely because tone-averaging a salted corpus is the measured
  failure mode — a naive whole-corpus reader's extracted signal shifted on 10/10 variants. A live
  contradiction between what the numbers have done and what the documents argue is not noise to be
  cancelled; it is the reason the honest distribution is wide. Widen, or split into scenarios, and
  say which document is on which side.

## 4. Build the predictive distribution (the method that wins)

The dominant winning recipe was a **scenario-weighted mixture over a bootstrap/regime engine**:

1. **Innovations engine.** Draw h-day paths by **stationary block bootstrap** of demeaned daily
   returns (blocks ~5–10 days to preserve autocorrelation and fat tails), or a Student-t(≈5) shock
   with the regime vol. Bootstrapping historical shocks keeps the empirical fat tails for free.
2. **Regime blend.** Mix innovations from the recent high-vol window (say 60%) and the full history
   (40%) so tails reflect stress the calm period lacks.
3. **Scenario drift overlay.** For each draw, pick a scenario (per your text weights) and add its
   drift; this yields the mixture shape (possibly multi-modal) the text implies.
4. **Joint cards: simulate paths, not margins.** For multi-asset/multi-horizon targets, drive all
   series from **one correlated shock** (covariance from trailing daily changes) and build the longer
   horizon as the shorter-horizon path *plus* an independent continuation, so cross-asset and
   cross-horizon correlations are preserved (the 30% variogram term rewards this and punishes
   independent margins).
5. **Draw count:** produce ≥ `n_draws_min` (spec floor, often 200; use ≥2000 for stable CRPS).

## 5. Self-check before writing (calibrate, don't over-fit)

- **Width sanity:** is your 90% interval's half-width ≈ 1.6× your horizon-sd estimate? If it's much
  tighter, you're over-confident — the single most common point-loser.
- **Tail asymmetry:** if the plausible surprise is a downside crash (crisis cards), make the left
  tail explicitly fatter; the suite's shocks are overwhelmingly downside.
- **No memorization shortcut:** if you "recognise" the historical episode, do **not** collapse onto
  the remembered outcome. The evaluation shows honest wide distributions beat remembered points once
  scored on CRPS, and a suspiciously tight bull's-eye is exactly what the g4 admissibility gate
  disqualifies. Forecast from the as-of information only.
- **Units & type:** draws are in the panel's units and match `target_type` (a `log_return` target is
  a cumulative return, not a level).

## 6. Write the deliverables

- `forecast.parquet` / `forecast.csv` — columns `draw, asset, horizon, value`, ≥ `n_draws_min`.
- `forecast_meta.json` — `asset_ids`, `horizons` (so the scorer can pivot).
- `rationale.md` — state, per directional judgement, **which dated document** drove it (cite
  `doc_id`), the method, and the main uncertainties. This is the audit artifact; it also disciplines
  you into using the corpus rather than your memory.

## Worked mini-example (event card)

Target: EUR/USD level, 64 BD after an as-of one day after a credible ECB backstop commitment.
1. Spot 1.237; empirical 64-day sd ≈ 5.5%; EWMA vol ≈ 0.66%/day (elevated). Baseline = RW ± 5.5%.
2. Corpus: a strong policy-backstop commitment (EUR-supportive) vs residual crisis-re-escalation
   risk. → three scenarios: 55% backstop-holds (+1.5% drift), 30% muddle-through (0), 15%
   re-escalation (−4%, 1.3× vol).
3. Engine: length-5 block bootstrap of vol-standardised daily shocks, rescaled to as-of vol, one
   scenario drift per path. 2500 draws.
4. Result: median ≈ 1.238, 90% interval ≈ [1.11, 1.37] — centered near spot, honestly wide, mild
   upside skew from the backstop weight. (A memoriser would spike on the realised value and lose
   the tail term when the path there was not knowable ex-ante.)

---
*Companion to `EVALUATION.md` and the difficulty table in `scripts/difficulty_calibration.py`.
The methods here describe what scored well on the internal blind-solve eval; they are guidance,
not a required submission format.*
