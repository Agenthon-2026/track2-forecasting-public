# Forecast Card Specification

> **Instructions:** Replace all `TEMPLATE_` placeholders before publishing. Remove this instruction block.
> Card authoring guide: `public/AUTHORING-GUIDE.md`

---

## Card ID

`TEMPLATE_CARD_ID`

---

## Track

`forecasting` (Track 2)

---

## Title

TEMPLATE_TITLE

---

## Card Family

<!-- Select one and delete the others. -->

- [ ] **T2-F1** — Univariate level forecasting; single asset × single horizon; scoring dominated by marginal CRPS
- [ ] **T2-F2** — Multivariate short-to-medium horizon (FX, rates); marginal CRPS + tail coverage
- [ ] **T2-F3** — Joint distribution forecasting; multiple assets × multiple horizons; energy score / joint CRPS dominant
- [ ] **T2-F4** — Regime-conditional forecasting; stress scenarios or turning points; tail CRPS + regime calibration dominant

**Selected family:** `TEMPLATE_FAMILY`

---

## Asset Panel Description

The table below describes every input panel visible to the submission model. All panels end strictly at the as-of date. No data after `TEMPLATE_ASOF_DATE` may be used.

| `panel_id` | `source` | Series included | `frequency` | `end_date` (= asof) |
|---|---|---|---|---|
| `TEMPLATE_PANEL_ID` | `TEMPLATE_SOURCE` | TEMPLATE_SERIES_LIST | `TEMPLATE_FREQ` | `TEMPLATE_ASOF_DATE` |
| *(add rows as needed)* | | | | |

**Panel construction notes:**

- All derived features (e.g., yield spreads) are constructed from raw data with timestamp ≤ `TEMPLATE_ASOF_DATE`.
- Factor lags applied: TEMPLATE_LAG_DESCRIPTION (e.g., "JKP monthly factors lagged 1 month due to reporting delay").
- No forward-looking series, analyst forecasts, or survey data are included.

---

## As-Of Date

**`TEMPLATE_ASOF_DATE`** (ISO 8601: YYYY-MM-DD)

This is the strict information cutoff. The held-out window is `[TEMPLATE_ASOF_DATE + 1 day, TEMPLATE_ASOF_DATE + max_horizon_bd business days]`.

Leakage check status: `cutoff_ok(asof, target_dates)` — **MUST PASS BEFORE PUBLISHING**

---

## Targets

The following assets are to be forecast at each horizon listed below.

| `asset_id` | Description | Unit |
|---|---|---|
| `TEMPLATE_ASSET_1` | TEMPLATE_DESCRIPTION_1 | TEMPLATE_UNIT_1 |
| `TEMPLATE_ASSET_2` | TEMPLATE_DESCRIPTION_2 | TEMPLATE_UNIT_2 |
| *(add rows as needed)* | | |

**`target_type`:** `TEMPLATE_TARGET_TYPE` *(one of: level / log_return / spread)*

**`target_frequency`:** `TEMPLATE_TARGET_FREQUENCY` *(one of: daily / monthly)*

---

## Horizons

| `horizon_bd` (business days) | Approximate calendar equivalent | Target date (if fixed) |
|---|---|---|
| `21` | ~1 calendar month | `TEMPLATE_TARGET_DATE_1` |
| *(add rows as needed)* | | |

**Note:** Horizons are always expressed in **business days**. The mapping to calendar time is approximate and provided for human readability only. The scorer uses business-day counts.

---

## Predictive Distribution Schema

**Output format:** *(select one)*

- [ ] **Samples** (preferred for T2-F3, T2-F4)
- [ ] **Parametric** (mean vector + covariance matrix; acceptable for T2-F1, T2-F2)

### Samples Format (if selected)

Parquet file at `/output/forecast.parquet` with the following schema:

| Column | Type | Description |
|---|---|---|
| `draw` | `int32` | Sample index, 0-indexed |
| `asset` | `string` | Asset ID from the Targets table above |
| `horizon` | `int32` | Horizon in business days |
| `value` | `float64` | Forecasted value in the unit specified above |

**`n_draws`:** `TEMPLATE_N_DRAWS` *(minimum 200; recommended ≥ 500 for joint tasks)*

### Parametric Format (if selected)

- Mean vector: shape `[n_assets × n_horizons]`
- Covariance matrix: shape `[n_assets × n_horizons, n_assets × n_horizons]`, must be positive semi-definite
- Asset and horizon ordering must match the Targets and Horizons tables above

---

## Scoring Weights

| Component | Weight | Description |
|---|---|---|
| Marginal CRPS | `TEMPLATE_MARGINAL_WEIGHT` | Univariate CRPS averaged across assets and horizons |
| Joint / Energy score | `TEMPLATE_JOINT_WEIGHT` | Multivariate energy score over full joint distribution |
| Tail CRPS | `TEMPLATE_TAIL_WEIGHT` | CRPS evaluated at tail quantiles (1%, 5%, 95%, 99%) |
| **Total** | **1.0** | |

**Tail quantile levels:** `[0.01, 0.05, 0.95, 0.99]`

---

## Leakage Statement

> TEMPLATE_LEAKAGE_STATEMENT
>
> *Example: "All panels end on YYYY-MM-DD; `cutoff_ok('YYYY-MM-DD', target_dates)` was called on YYYY-MM-DD and raised no error; no panel series contains any observation after the as-of date."*

---

## Admissibility Requirements

A submission passes gate g3 (calibration admissibility) if and only if:

1. The predictive distribution file is schema-valid
2. All values are finite (no `NaN`, `Inf`, or `-Inf`)
3. Shape is `[n_draws, n_assets, n_horizons]` after pivoting
4. `n_draws >= 200`
5. Marginal standard deviation > 0 for all asset × horizon cells
6. No missing cells for any asset × horizon combination

Gate failure labels: `T2_UNCALIBRATED_MARGINAL`, `T2_BAD_DEPENDENCE`, `T2_TAIL_MISCALIBRATION`, `T2_REGIME_SHIFT_FAILURE`

---

## Notes

*Use this section for any additional context: data quirks, known structural breaks in the target series, rationale for as-of date choice, factor lag documentation, derivation formulas for any computed features, or caveats about the panel construction.*

TEMPLATE_NOTES
