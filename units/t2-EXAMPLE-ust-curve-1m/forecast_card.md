# Forecast Card: t2-EXAMPLE-ust-curve-1m

**Title:** 1-Month-Ahead Joint US Treasury Yield Curve (2Y/5Y/10Y/30Y)
**Track:** Track 2 — Reasoning-Augmented Time-Series Forecasting
**Card Family:** T2-F3 (Cross-Asset Dependence)
**Split:** Public (exemplar)

## Task Description
Given daily US Treasury par yield observations from FRED H.15 through the as-of date of 2024-06-28, produce a **joint** predictive distribution over the 2-year, 5-year, 10-year, and 30-year constant-maturity yields 21 business days forward (target settlement date: approximately 2024-07-31).

This card stresses the **joint/variogram score** (weight 0.3) because the primary evaluation question is whether the model captures the dependence structure of the yield curve—not merely individual marginal distributions. A model that forecasts each yield independently will score poorly on the joint component even if its marginals are well-calibrated.

## Input Panel

| Panel ID | Source | Series IDs | Asset IDs | Frequency | Start | End (= as-of) |
|---|---|---|---|---|---|---|
| rates_daily | FRED H.15 | DGS2, DGS5, DGS10, DGS30 | UST_2Y, UST_5Y, UST_10Y, UST_30Y | Business daily | 2000-01-03 | 2024-06-28 |

**Note:** Missing values are forward-filled within a 3-business-day window only. Days with no value for ≥2 series are dropped entirely. The panel file is provided at `/input/rates_daily.parquet` with columns `[date, asset, value, panel_id]` (the shape every Track 2 panel uses; `panel_id` is `rates_daily`).

## As-Of Date
`2024-06-28` (Friday, end of Q2 2024). All input data has `date <= 2024-06-28`. No observations from 2024-06-29 onward may be used.

## Targets

| Asset ID | Description | Unit |
|---|---|---|
| UST_2Y | 2-Year Constant-Maturity Treasury Yield | % per annum |
| UST_5Y | 5-Year Constant-Maturity Treasury Yield | % per annum |
| UST_10Y | 10-Year Constant-Maturity Treasury Yield | % per annum |
| UST_30Y | 30-Year Constant-Maturity Treasury Yield | % per annum |

## Horizons

| Horizon (BD) | Calendar Approximate | Target Date |
|---|---|---|
| 21 | ~1 month | 2024-07-31 |

## Predictive Distribution Schema

- **Format:** `samples` — the only accepted representation
- **Samples format:** Parquet file at `/output/forecast.parquet` with columns `[draw: int32, asset: string, horizon: int32, value: float64]`
- **Minimum draws:** 200, maximum 20,000 (strongly recommend ≥500 for tail calibration)
- **Draw ids:** contiguous and zero-based, `0 … n_draws-1`
- **Grid:** exactly one row per `(draw, asset, horizon)` cell, in the order the card declares. A
  repeated asset, a duplicate key or a missing cell is refused; duplicates are never averaged.

## Scoring Weights

| Component | Formula | Weight |
|---|---|---|
| Marginal CRPS | Mean CRPS over 4 assets × 1 horizon | 0.5 |
| Joint / Variogram | Variogram score with p=0.5 over the 4-asset vector | 0.3 |
| Tail Penalty | Mean interval score at quantiles 0.01/0.05/0.95/0.99 | 0.2 |
| **Composite S** | Weighted sum | **lower is better** |

## Leakage Statement
This card passes `qfbench2_common.leakage.cutoff_ok(asof="2024-06-28", target_dates=["2024-07-31"])`. The panel end date equals asof. No target series data is included in the panel after 2024-06-28.

## Admissibility Requirements (Gate g3)
- Output parquet must have exactly the columns `[draw, asset, horizon, value]`
- `asset` column must contain exactly `{"UST_2Y","UST_5Y","UST_10Y","UST_30Y"}`
- `horizon` column must contain exactly `{21}`
- `n_draws >= 200` (validated by schema check)
- All `value` entries must be finite (no NaN, no ±Inf)
- Per-asset standard deviation must be > 0 (degenerate point mass fails g3)

## Panel Context Notes
- As of 2024-06-28, the Fed funds rate had been at 5.25–5.50% since July 2023 (no hike since then). The yield curve was inverted (2Y > 10Y) throughout Q1–Q2 2024.
- This panel is **not** a regime-shift card (T2-F4); it is an in-distribution joint forecast of an actively traded yield curve series.
- A strong baseline model should produce a correlated multivariate predictive distribution reflecting the typical level–slope–curvature factor structure of the UST curve.

## Notes
This is a **public exemplar** card. Realized outcomes are NOT provided here and no public artifact names where they live: the sentence this replaces gave the id of a real private unit and the exact path to its answer file, which is a sealed identifier in a public repository however harmless the unit itself is.

Validate your forecast locally with the canonical scorer:

```bash
python -m qfbench2_track_forecasting.scoring score \
  --card units/t2-EXAMPLE-ust-curve-1m/card.toml \
  --forecast /output/forecast.parquet
```

That run is **unranked by construction** — it grades against `card.toml` with no reference scale, so its composite is raw and not comparable across units. The official path grades against the signed evaluation plan and normalizes; see `docs/CONCEPTS.md`.
