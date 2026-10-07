# M0 — the official text-blind baseline, specified

## Executive summary (read this first)

Every Track 2 card is scored against one official baseline, called **M0**: a forecast that never
reads the text. Each component of your composite is divided by **the error M0 expects to make on
that card**. That is the average score M0's own forecast would get if the outcome were drawn from
M0's own forecast distribution. It is computed from the card's inputs alone, with exact formulas
(§5), so it is fixed before the outcome exists. A score of **1.0 means your error equals the error
M0 expects of itself on that card**; below 1.0 is better.

M0 itself does not score exactly 1.0. On average it scores about 1.0 where outcomes are as
volatile as its random walk assumes, above 1.0 where they move more than its trailing history
suggests, and below 1.0 where they move less. The leaderboard shows M0's actual score as a
reference row, so you can read your standing against it directly.

This document specifies M0 completely enough that you can rebuild its forecast, and the divisor,
yourself, for any card whose panels you hold, and see exactly what you are being compared against.

Because the divisor no longer depends on the outcome, a card's scale is **no longer
answer-equivalent**: on a released card you can compute every value yourself (§5). Two things
are still not in this repository: the generator's source code, and the scale files. The scale
files of sealed cards are computed from sealed inputs, so they stay with the organizers.

M0 is **not** the reference CLI in `qfbench2_track_forecasting/cli.py`, and it is not any file in
`baselines/`. Section 7 puts the two side by side, naming the function in the shipped CLI where
each difference lives, so you do not calibrate against the wrong thing.

Read [CONCEPTS.md §13](CONCEPTS.md) first if you have not: it explains where the normalization
sits in the leaderboard. This document is the layer below it.

---

## 1 — What M0 is for

Raw scores carry the units of whatever they forecast. A CPI-index card's CRPS is thousands of
times a bond-yield card's, so a plain average over cards would be an average of the largest
numbers, not of the best forecasts.

So each of the three components of your composite — marginal CRPS, joint variogram, tail — is
divided by **M0's expected value of the same component on the same card** before the weights are
applied. "Expected" has its statistical meaning: the average M0 would score on that component if
the outcome were drawn from M0's own forecast distribution. It depends only on M0's forecast,
which is built from the card's inputs (§3), so it is fixed before the outcome exists; the outcome
enters only your side of the ratio. After that division every card is on one scale: 1.0 means
your error equals the error M0 expects of itself, below 1.0 is better, and the leaderboard is the
equal-weight mean over cards.

Because the divisor is fixed before the outcome, the score is **proper**: on every card, your
expected score is lowest when the distribution you submit is the one you actually believe. The
honest forecast is the best strategy. The one qualification is the clip at 8.0
([CONCEPTS.md §13](CONCEPTS.md)): it caps a card's score at 8.0, so it can matter only where a
score that large is a real possibility.

M0 is a **text-blind joint Gaussian random walk**. It reads the numeric panels the card ships and
nothing else — no corpus, no card prose, no model. That is the point: Track 2 exists to measure
whether reading the documents helps, and the yardstick has to be the forecast that did not. M0 is
also scored as an entry: its actual score, against the same outcomes and on the same scale as
yours, is the reference row on the leaderboard.

## 2 — What is published, and what is sealed

| | Status | Why |
|---|---|---|
| The procedure (this document) | **Published** | You cannot reason about a ratio whose denominator is undefined. |
| The per-card seed rule | **Published** | §3.9. It is a function of the card id, which you already have. |
| The divisor formulas | **Published** | §5. They need M0's forecast distribution and nothing else. |
| The generator's source code | **Not published** | It runs on the organizers' copies of the cards, including the sealed cards and fields that released cards do not carry. |
| Every `ref_scale.json` file | **Not shipped** | Computed from the card's inputs only (§5), so not answer-equivalent. On a released card you can compute the values yourself; a sealed card's inputs are sealed, so its values stay with the organizers until results are released. |
| Realized outcomes | **Sealed** | The competition's whole firewall. |

**What a scale depends on.** A scale is M0's *expected* error, computed from the card's inputs
alone (§5).

The scorer's own boundary is unchanged. It reads a scale only as the `ref_scale.json` directly
inside a card's `reference/` directory, which on the ranked path sits under the organizer's
reference root. It opens each directory on the way without following symbolic links, and it
accepts only a single-link regular file of bounded size ([`qfbench2_track_forecasting/normalization.py`](../qfbench2_track_forecasting/normalization.py),
`_read_scale_bytes`, which `load_ref_scale` and `read_ref_scale_bundle` both read through). On the
ranked path it also checks the exact bytes of every scale in the roster against the evaluation plan's
commitment before anything is scored (§5).

A reproducible baseline is still one more handle on a scored board. M0's score on a single card is
its error against that card's outcome, so a per-card M0 score could be inverted to the outcome.
That is why the board reports one aggregate statistic per entry, M0's reference row included, and
nothing per card.

## 3 — The procedure

M0 runs once per card. Its inputs are the card (`card.toml`) and the panels that ship with it.
Its output is a set of **500 joint draws** over the card's grid of `(asset, horizon)` cells — the
same artifact your agent produces, in the same shape.

Throughout: **as-of** is `[provenance] data_cutoff`, the date the card is truncated at.

### 3.1 The history for one asset

Find the asset in the panels: the first `*.parquet` in the unit directory, in sorted filename
order, that contains a row for it. Both `asset` and `asset_id` spellings occur and both are read.

Keep rows dated **at or before the as-of**, sorted by date, and take the **last 300**. That
trailing window is the whole of M0's memory — it does not use the full history. A panel with
fewer than 300 observations at the as-of contributes all of them.

### 3.2 Turning the history into steps, by `target_type`

| `[targets] target_type` | The step series | Why |
|---|---|---|
| `level` | first differences of the values | The target is a level, so the walk moves in level changes. |
| `log_return` | **the row itself** | These panels already ship per-step returns. Differencing them again would be a second difference: it telescopes the drift and inflates the spread by about √2. |

The `log_return` branch carries a tripwire rather than a guess. If the panel's values do not look
like per-step returns — median absolute value at or above **0.2** — the generator **refuses** and
the card is not scaled until a human decides which kind of panel it is. It never falls back to
"assume it is a price series".

One indexing consequence, easy to get wrong: a difference at row *i* spans the interval from row
*i-1* to row *i*, so the differences align to rows 1..n-1. A per-step return at row *i* **is**
row *i*, so the returns align to rows 0..n-1 — and row 0 then falls out anyway under §3.3,
because it has no preceding interval to test. Either way, a step carries the date of the row it
ends on.

### 3.3 The gap rule

Drop any step that spans a hole in the data. A hole is an interval longer than

```
max( 10 x median spacing of the trailing window , 5 days )
```

The median is taken over the intervals between the rows §3.1 selected, not over the asset's full
history. (On a daily panel the two agree; on a transfer card's panel they do not.) The dropped step
becomes missing, not zero.

This matters most on transfer cards, whose target asset ships as an early window plus a single
row at the as-of, with the years between deliberately withheld. Differenced naively that hole
reads as one day in which the asset moved a decade's worth. The card text tells you not to do
that; M0 does not do it either.

### 3.4 Date alignment across assets

Each asset's step series is indexed **by date**. The multi-asset step frame is then the
**intersection of dates present for every asset** — rows where any asset is missing a step,
including one dropped by the gap rule, are dropped for all of them.

This is the only set a covariance can honestly use. Assets with different holiday calendars do
not line up row-for-row, and pairing them by position instead of by date can invert the sign of a
correlation. Where the dates cannot support the alignment — wrong length, unparseable,
duplicated — the generator refuses rather than falling back to positional pairing.

### 3.5 Drift and covariance

From that date-aligned frame:

- **mu** = the mean step per asset (a vector over assets).
- **Sigma** = the covariance of the steps across assets (`numpy.cov`, sample convention, over the
  same intersected rows).

Both are estimated on the trailing window only. There is no shrinkage, no winsorizing, no regime
model. M0 is meant to be the floor.

### 3.6 The anchor

For a `level` target, the walk starts at that asset's **last observation in the panel** — not at
the as-of, and not at any interpolation of it.

The distinction is load-bearing on monthly macro panels, which stop at the as-of minus their
publication lag. Measured 2026-09-18 on the published card `t2-F1-cpi-glidepath-2023`: the as-of
is 2023-07-12 and `CPI_ALL`'s last observation is 2023-05-01, a 72-day lag. Anchoring at the
as-of would start the walk from a value the panel does not contain, and would also mis-count the
steps below.

For a `log_return` target the anchor is **0.0**: the target is a cumulative return over the
horizon, and the last observed return belongs to the history, not to that future total.

### 3.7 Horizon to panel steps

A card's `horizon` is the participant-visible grid key. It is not always stated in the panel's own
units: a few released macro cards state a business-day horizon over a monthly panel. Feeding that
straight into a per-step walk would rescale the baseline by the ratio between the two, so M0
converts.

**A cell that names its observation month.** A monthly card can name, in `forecast_spec.json`,
the month each cell forecasts: `targets.observation_periods`, aligned with `targets.horizons`, or
`observation_period` on the cell's row of `questions` (see
[MONTHLY-HORIZONS.md](MONTHLY-HORIZONS.md)). On such a cell M0 walks one step per calendar month,
from the month of the target series' last observation (§3.6) to the named month:
`12·(y1-y0) + (m1-m0)`, with `y0, m0` the year and month of the last observation and `y1, m1`
those of the named month. The declared horizon and steps 1–5 below play no part. If the named
month is not the month of the cell's sealed target date, the generator **refuses**, and the card
is not scaled until an organizer resolves the disagreement.

On the monthly cards of the Final phase, that count is one or two more than the number of months
from the as-of month to the named month, because their target series end one or two months before
the as-of month. Steps 1–5 would not always see that: step 5 keeps any declared horizon within 2x
of the count (one counted from the as-of month, for example), and the walk would then stop one or
two months short of the month being forecast. §4 works a synthetic case.

**Every other cell** is converted in five steps:

1. Take the dates of that asset's trailing window. If there are fewer than three, or the target
   date is missing or malformed, **use the declared horizon** and stop.
2. Estimate the panel's spacing as the mean interval, over intervals that are not holes (§3.3).
3. Count steps from the **last observation** (§3.6) to the target date:
   - spacing **> 20 days** → count **calendar months**: `12·(y1-y0) + (m1-m0)`.
   - otherwise → `round( (target_date - last_observation).days / spacing )`.
4. If that count is ≤ 0, **use the declared horizon**.
5. Otherwise compare the two. Let `ratio = max(steps, horizon) / max(min(steps, horizon), 1)`.
   **The declared horizon wins unless `ratio >= 2`.**

On these cells step 5 is the whole of the override rule, and the 2x threshold is not a tuning knob.
A card that already states its horizon in panel steps lands close to the counted value, and
overriding it there would move the baseline for no reason. A genuine unit mismatch is never
marginal — the affected cells are all at least 8x apart — so 2x separates the two cases with wide
margin on both sides.

Whichever rule applies, call the resulting per-cell step count **s**.

**Where the target date comes from, and what that means for you.** Steps 1–5 read each cell's
target date from the organizers' sealed copy of the card, never from its outcome; a cell that names
its observation month uses that date only for the check above. Released cards do not publish target
dates, with two exceptions. The worked exemplar in §4 carries them in its `card.toml`
(`[targets] target_dates`).
The four monthly-panel cards listed below name each target's observation month in
`forecast_spec.json`, under `targets.observation_periods`; that is the month being forecast, not a
release date (see [MONTHLY-HORIZONS.md](MONTHLY-HORIZONS.md)). On every other card step 1's
fallback fires for you, and you use the declared horizon.

On daily panels that costs you nothing: the counted and declared values land within 2x of each
other, so step 5 keeps the declared horizon and M0 does the same. **On the four released cards that
sit on the monthly macro panel it is the whole difference.** Their step counts:

| Card | Declared `horizons` | Panel steps M0 uses |
|---|---|---|
| `t2-F1-cpi-glidepath-2023` | `[140, 160]` | **8, 9** |
| `t2-F1-sahm-watch-2024` | `[145, 165]` | **8, 9** |
| `t2-F4-covid-nfp-2020` | `[21]` | **2** |
| `t2-F4-cpi-vintage-2022` | `[21]` | **2** |

Three of them take the named-month rule, so their counts follow from the months their
`forecast_spec.json` names. The fourth, `t2-F1-sahm-watch-2024`, takes steps 1–5; use the table.
With the table's numbers you reproduce M0 on all four cards; with the declared horizon you are
forecasting years out with a spread to match.

The conversion changes the walk, not the grid. `forecast.parquet` keeps the declared horizon keys
(140, 160, 145, 165 and 21 on these four cards), as [MONTHLY-HORIZONS.md](MONTHLY-HORIZONS.md)
requires, and scoring joins on `(asset, horizon)`. The reference CLI derives its own monthly step
counts from `targets.observation_periods` (§7).

### 3.8 The mean vector and the covariance matrix

Over the card's `d` cells, indexed `i = (asset a, horizon with step count s_i)`:

```
mean[i]   = anchor[a_i] + s_i * mu[a_i]            # anchor is 0 for a log_return target
cov[i, j] = min(s_i, s_j) * Sigma[a_i, a_j]
```

`min(s_i, s_j)` is what makes the draws a **path** rather than a bundle of unrelated marginals: a
random walk observed at two horizons shares the variance accumulated up to the earlier one. That
cross-horizon structure is the part the joint variogram term is there to reward. On daily cards it
is the part the shipped reference CLI does not have; on the four monthly-panel cards the CLI's
monthly path builds a path too (§7).

Then `1e-10` is added to the diagonal, and the Cholesky factor is taken of `cov + 1e-9·I`. If that
still fails, the factor is taken of the **diagonal** of `cov + 1e-9·I` — a card whose covariance
cannot be factorized gets independent marginals, for its draws and for its divisor (§5), rather
than no baseline at all.

### 3.9 The draws

```
seed    = crc32(unit_id) & 0x7FFFFFFF        # unit_id is card.toml [task] id
rng     = numpy.random.default_rng(seed)
Z       = rng.standard_normal((500, d))
samples = mean + Z @ cholesky_factor.T
```

500 draws, always. The seed is a function of the card id alone, so any party can regenerate any
one card's baseline in isolation, without the rest of the suite and in any order.

**Cell order: the card's grid order.** `Z`'s columns are assigned to cells in the order of the
card's grid: each asset in `[targets] asset_ids` order and, within an asset, each horizon in
`[targets] horizons` order. That is the order your `forecast_meta.json` declares and the order the
scorer flattens the grid to. On the exemplar of §4 it is `UST_2Y`, `UST_5Y`, `UST_10Y`, `UST_30Y`,
the card's own list, which is not sorted.

Re-ordering the cells gives the same *distribution* but different draws from the same seed. The
order therefore matters for an exact match of M0's draws, which are what M0's reference row on the
leaderboard is scored from. It does not matter for the divisor at all: §5 computes it from M0's
mean and covariance, not from the draws, and every formula there is a sum or a mean over cells
and pairs. (The scales in force before the expected-error rule were computed from the draws, in an
order stored with each card's sealed answer, sorted by asset id on most released cards. That order
no longer plays any part.)

The assets of `mu` and `Sigma` are ordered separately, by sorted asset id; that ordering is internal
to the estimate and changes nothing.

## 4 — Worked example, on a card you already have

`units/t2-EXAMPLE-ust-curve-1m` — 4 UST tenors, `target_type = "level"`, `horizons = [21]`,
as-of `2024-06-28`, target date `2024-07-31`. All figures below are **measured 2026-09-18** from
the published panel in this repository (the divisors in the last row on 2026-10-02), and none of
them touches a sealed artifact. This card is not scored, so no scale file exists for it; the
example shows the procedure applied to a card you hold in full, not a record of a scored run, and
the last row is what §5 gives for it.

| Step | On this card |
|---|---|
| Trailing window (§3.1) | `rates_daily.parquet` has 516 rows, 129 per asset at or before the as-of — fewer than 300, so all 129 are used |
| Steps (§3.2) | `level` → first differences, 128 of them per asset |
| Anchor (§3.6) | last observation is `2024-06-28`, the as-of itself: this panel has no publication lag |
| Spacing (§3.7.2) | 1.391 days over non-hole intervals |
| Counted steps (§3.7.3) | `round(33 / 1.391) = 24` |
| Override test (§3.7.5) | `ratio = 24/21 = 1.14 < 2` → **the declared horizon 21 is used** |
| Seed (§3.9) | `crc32("t2-EXAMPLE-ust-curve-1m") & 0x7FFFFFFF = 795546941` |
| Draws | 500 x 4 cells in the card's grid order (`UST_2Y`, `UST_5Y`, `UST_10Y`, `UST_30Y`), mean `last + 21·mu`, covariance `21·Sigma` (one horizon, so `min(s,g)` is 21 everywhere) |
| Divisors (§5) | `marginal` 0.05260, `joint` 0.1772, `tail` 0.006051, from M0's standard deviations 0.0872, 0.0924, 0.0905 and 0.1028 (percentage points) and its covariance |

Contrast, same repository: `units/t2-F1-cpi-glidepath-2023` is a monthly macro card whose card
states `horizons = [140, 160]` in business days. The published card carries no target dates, but
its `forecast_spec.json` names the observation months:
`targets.observation_periods = ["2024-01", "2024-02"]`. So §3.7's named-month rule applies.
Counted from the last observation (2023-05, §3.6), that is 8 and 9 steps, the counts §3.7 lists.
Steps 1–5 give the same here: the panel's spacing measures 30.4 days, so step 3 counts months, and
140 against 8 is far more than 2x apart, so the counted month step wins. On the sealed set, by
contrast, you can reproduce neither the target date nor the outcome.

A synthetic case shows where the two rules part. A monthly card's as-of is 5 June 2031, and its
target series' last observation in the panel is April 2031, because the May figure is not yet
published. A question names `observation_period: "2031-09"` at horizon key 3. The named-month rule
walks 5 steps, April to September. Steps 1–5 would count the same 5 steps to a September target
date and then keep the key, because 5 against 3 is under 2x apart. That walk would end in July,
two months short, with three fifths of the variance.

## 5 — From M0's distribution to a scale: the expected error

This half needs no outcome, so you can run it yourself on any card whose panels you hold.

**A one-cell example first.** Suppose M0's forecast for a cell is normal with standard deviation
0.10. If the outcome were drawn from that same normal, M0's average CRPS would be
0.10 / √π = 0.0564, and its average pinball loss over the four default tail levels would be
0.10 × 0.0648939 = 0.00649. Those two numbers are the cell's marginal and tail divisors. A
forecast whose CRPS on that cell is 0.0564 scores exactly 1.0 on the marginal term, whatever the
outcome turns out to be.

**The general rule.** §3.8 defines M0's forecast as a normal distribution over the card's `d`
cells, with mean vector `mean` and a covariance. Call that covariance `C`: it is the matrix M0's
draws are sampled from, that is §3.8's matrix with the two small diagonal terms added there (or
its diagonal, if §3.8's fallback applies). Let `sd_i = sqrt(C[i,i])`, let `φ` and `Φ` be the
standard normal density and distribution function, and let `z_τ` be the standard normal
`τ`-quantile. Each divisor is the value M0 would score on average on that component if the
outcome `Y` were drawn from this distribution. Each has an exact formula, so nothing is sampled:
the formulas use M0's exact distribution, not its 500 draws.

| Component | What the scorer computes | Divisor stored in `ref_scale.json` |
|---|---|---|
| `marginal` | fair ensemble CRPS, mean over the `d` cells | `mean over i of sd_i / sqrt(pi)` |
| `tail` | pinball loss at each level in `tail_levels`, mean over levels and cells | `(mean over τ of φ(z_τ)) × (mean over i of sd_i)` |
| `joint` | variogram score of order 1/2 with unit weights, summed over every ordered pair `(i, j)` with `i ≠ j` | `sum over i ≠ j of Var(\|D_ij\|^(1/2))` |

Where each formula comes from:

- **Marginal.** For a normal forecast with standard deviation `σ`, the expected CRPS against an
  outcome drawn from the same normal is `σ / √π`. The scorer's fair ensemble CRPS is an unbiased
  estimate of the CRPS of the distribution its draws come from.
- **Tail.** At the true `τ`-quantile of a normal, `mean_i + sd_i · z_τ`, the expected pinball loss
  is `sd_i · φ(z_τ)`. With the default levels `[0.01, 0.05, 0.95, 0.99]`, the mean of `φ(z_τ)`
  over the four levels is 0.0648939.
- **Joint.** For cells `i` and `j`, the difference `D_ij = Y_i - Y_j` is normal with mean
  `δ = mean[i] - mean[j]` and variance `s² = C[i,i] + C[j,j] - 2·C[i,j]`. For each pair the
  variogram compares `|y_i - y_j|^(1/2)` with its expected value under the forecast, so the
  pair's expected score is the variance of `|D_ij|^(1/2)`:

  ```
  Var(|D|^(1/2)) = E|D| - (E|D|^(1/2))^2
  E|D|           = s·sqrt(2/π)·exp(-δ²/(2s²)) + δ·(1 - 2·Φ(-δ/s))
  E|D|^(1/2)     = ∫ |δ + s·z|^(1/2) φ(z) dz
                 = s^(1/2) · 2^(1/4) · Γ(3/4) / sqrt(π) · M(-1/4, 1/2, -δ²/(2s²))
  ```

  `M` is Kummer's confluent hypergeometric function (`scipy.special.hyp1f1`). If you integrate
  numerically instead, split the integral at `z = -δ/s`, where the integrand has a cusp. Plain
  Gauss–Hermite quadrature converges slowly there: with 150 nodes it is still about 0.8% off at
  `δ = 0`. The scorer's variogram sums its full `d × d` matrix, so each unordered pair counts
  twice, and the divisor does the same.

Only the marginal standard deviations enter the marginal and tail divisors; the joint divisor also
uses the cross-cell covariances and the differences between cell means. None of the three depends
on the outcome, on the seed or on the order of the cells.

**A component that comes out zero is stored as 1.0**, i.e. that component is not normalized at
all. The case this exists for: a single-cell card has no pairs, so its joint divisor is 0, and its
variogram score is 0 too, **by construction, not by merit**; dividing one by the other would poison
the composite. Those cards are also the ones whose weights are redistributed — see
[CONCEPTS.md §13](CONCEPTS.md), step 2 — so 1.0 means the same thing there as on a multi-cell card.

The tail divisor above is for the pinball metric. The tail component is computed under the metric
the card asks for, `[scoring.params] tail_metric`, defaulting to `pinball`
(`qfbench2_track_forecasting/tail.py`, `DEFAULT_TAIL_METRIC`). A scale and the scorer that divides
by it must be built under the same tail metric — the two metrics are not in the same units, and
mixing them is meaningless rather than merely imprecise. No released card overrides it — measured
2026-10-02, none of the 104 declares `tail_metric` — so in practice the default is what every card
is scored under.

Because the divisor needs no outcome, a card's scale can be built before its outcome exists. The
three values are stored **raw** in `reference/ref_scale.json`, as before: the scale is not
normalized by itself.

### How the scales in force are pinned

The evaluation plan carries a `ref_scale_commitment` field. The recipe that computes it is in
[`qfbench2_track_forecasting/normalization.py`](../qfbench2_track_forecasting/normalization.py)
(`RefScaleBundle`, built by `read_ref_scale_bundle`):

```
ref_scale_commitment = digest_json({
    unit_handle: sha256_bytes(exact bytes of <unit_handle>/reference/ref_scale.json)
    for every unit handle in the plan's roster
})
```

Both helpers come from the shared toolkit, `qfbench2_common.contracts.digest`. `sha256_bytes`
returns `sha256:` followed by the hex SHA-256 of its input. `digest_json` is `sha256_bytes` of the
RFC 8785 (JCS) canonical JSON of its argument. So the commitment is one digest over a map from each
unit handle to the `sha256:`-prefixed SHA-256 of that file's exact bytes.

`load_verified_ref_scales` recomputes it from the files on disk before any score is computed, and
refuses to rank when the bytes do not reproduce the plan's value. The commitment binds the values
without revealing them.

## 6 — Fidelity: what you will match, and what you will not

### What you can reproduce, and what you cannot

For a released card whose panels you hold, §3 and §5 are enough to rebuild both M0's **500 draws**
and the card's **scale**. The scale needs only M0's mean and covariance, so it does not depend on
the seed or on the order of the cells, and getting it right does not require matching the draws.
That is enough to answer the questions that motivated publishing this — what the divisor assumes,
where it is weak, and what beating M0 requires.

Two things stand between §3 and an exact match, in descending order of size:

- **The four monthly-panel cards.** M0 does not walk their declared horizon (§3.7). Three take the
  months their `forecast_spec.json` names; `t2-F1-sahm-watch-2024` takes steps 1–5. Use the step
  counts in §3.7's table and this disappears; ignore them and you are not close, on the draws or
  on the scale.
- **Sealed cards.** You do not have the panels, the as-of or the target date, so the draws and the
  scale are out of reach entirely. This one is by design and is not going away.

Nothing else does. Cell ordering no longer stands in the way: M0's draws follow the card's grid
order (§3.9), which the card itself fixes, and the scale does not depend on the order at all. The
F2 transfer cards are **not** an exception either: each ships its transfer target's early window
in its own panel bundle, and all four single-asset F2 transfer cards reproduce bit-exactly from
published panels (measured 2026-09-18). What is sealed on those cards is the withheld middle of
the series and the outcome, not M0's ability to read what you can read.

### Which revision produced the scales in force

Every scale in force is M0's expected error under §5, built by the procedure of §3 with no outcome
read. The scales in force before this rule were M0's error against the realized outcome. They were
generated on **2026-09-03**, and four of them were regenerated on **2026-09-25**: those of the
practice cards with a `macro_monthly` panel (`t2-F1-cpi-glidepath-2023`, `t2-F1-sahm-watch-2024`,
`t2-F4-covid-nfp-2020`, `t2-F4-cpi-vintage-2022`), whose panels were rebuilt as the data vintage
published on each card's as-of date. Those scales are retired, and every finished Development
submission is re-scored with the new ones, so every entry on the board is on one scale. On the
published cards, the named-month rule of §3.7 gives the same step count as steps 1–5 on every cell
where M0 applies it.

The procedure of §3 still carries three corrections made on 2026-09-03, relative to the scales that
had been in force before that date. If you have read earlier organizer statements about the
baseline, these are the differences:

| Corrected on 2026-09-03 | Effect |
|---|---|
| Assets in the covariance were aligned by **row position** rather than by date (§3.4) | Reaches only multi-asset cards whose assets have different observation calendars — a handful of them. The largest move in any card's joint component was under 10%, and on one card the affected correlation changed sign. |
| `log_return` panels were **differenced a second time** (§3.2) | Reaches the return-target cards only: drift telescoped, spread inflated by about √2. |
| The tail component used a **coverage** penalty rather than pinball (§5) | Under coverage many tail scales collapsed onto a floor and a ceiling. Under pinball each card's tail scale is distinct and carries the target's units, like the marginal term beside it. |

The procedure of §3, with §5, is the procedure that produces the scales in force.

### Which scorer divides by it

A scale is only half of a normalized score; the other half is the scorer that divides by it. The
published package defaults to the pinball tail (`tail.py`, `DEFAULT_TAIL_METRIC`), the metric §5's
tail divisor is built for. The switch to expected-error scales changes no scorer code: the scorer
divides by whatever scales the evaluation plan commits, so the change reaches your score through
the scale files and the signed plan, not through this package.

## 7 — What M0 is **not**

`qfbench2_track_forecasting/cli.py` is the reference submission CLI: a runnable floor that proves
the interface, passes the gates offline and can be edited into a real agent. **It is not M0**, and
a submission that runs it unchanged does not score what M0 scores. Every difference below is
deliberate.

The CLI samples on one of two paths. The **daily path** is the default. The **monthly path** is
taken when the card declares `target_frequency = "monthly"` and the selected target series really
have monthly observations; it then requires a `level` target and an explicit observation month for
every grid cell, and refuses otherwise (`_monthly_inputs`). Among the released cards, the four
monthly-panel cards of §3.7 take it. [MONTHLY-HORIZONS.md](MONTHLY-HORIZONS.md) specifies the month
mapping it reads. Where the two paths differ, the table gives both.

| | M0 (this document) | Reference CLI |
|---|---|---|
| History used | trailing 300 observations (§3.1) | the full history at or before the as-of (`_series`); the monthly path uses only changes between consecutive calendar months (`_draw`) |
| Drift on a `level` target | `s · mu` (§3.8) | **none** — `drift = np.zeros(...)` for a level target, a driftless walk on both paths (`_draw`) |
| Across horizons | one path: `cov[i,j] = min(s_i,s_j)·Sigma` (§3.8) | daily: a **fresh** innovation per horizon — no cross-horizon covariance at all (`_draw`, the `for hi, h in enumerate(horizons)` loop). Monthly: one correlated innovation per calendar month, accumulated along a single path and reused at every later target period (`_monthly_walk`) |
| Across assets | full covariance of steps (§3.5) | correlation of steps, nearest-PSD clipped, times each asset's own sd |
| Spread with horizon | from `min(s,g)·Sigma` | daily: `sd · sqrt(h)`. Monthly: `sd · sqrt(s)`, with `sd` estimated from monthly changes and `s` the calendar-month steps |
| Horizon units | converted to panel steps (§3.7) | daily: the card's `horizon` used as-is. Monthly: calendar-month steps counted from the last panel observation to each cell's observation month (`_monthly_inputs` → `horizons.monthly_horizon_steps`); the key written to `forecast.parquet` is unchanged |
| Seed | `crc32(unit_id)` (§3.9) | `--seed`, default **0**, the same for every card |

How far apart that leaves them was last measured on 2026-09-18, under the **earlier** rule: the
per-outcome scales, under which M0 scored exactly 1.0 on every card, and the 4.0 clip. Over the
103 released cards that have a resolved answer, the shipped reference CLI at its default seed then
averaged about 1.29 (median 1.05), with five cards at the clip. **Those figures are to be
re-measured under §5's scales and the 8.0 clip, and should not be read as current.** Either way the
measurement needs the sealed outcomes, so it cannot be reproduced from published material. What
does not change is the table above: it lists what separates the CLI from M0, the driftless level
walk most visibly.

The five adapter scaffolds in `baselines/` are further away still: whatever model each is named
after, they all return a seeded Gaussian random walk whose draws are, in their own docstring's
words, i.i.d. across assets with no modelled cross-asset dependence
(`baselines/base.py`, `_gaussian_rw_samples`; `baselines/README.md` opens by saying they are
scaffolds). Do not read a gap against any of them as a gap against M0.

---

*Questions about this document belong on the public issue tracker. Realized outcomes, sealed card
identifiers, the scale values of sealed cards and per-card scores will not be posted there, here,
or anywhere a participant can read, at any point before results are released.*
