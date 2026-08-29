# Panel Description: rates_daily

**Panel ID:** `rates_daily`
**File path (at inference time):** `/input/rates_daily.parquet`
**Source:** FRED H.15 Selected Interest Rates (Federal Reserve Board)

## Schema

| Column | Type | Description |
|---|---|---|
| `date` | `date32` | Calendar date of the observation (business days only; no weekends or US federal holidays) |
| `asset_id` | `string` | Asset identifier: one of `UST_2Y`, `UST_5Y`, `UST_10Y`, `UST_30Y` |
| `value` | `float64` | Constant-maturity Treasury par yield in percent per annum (e.g., 4.72 = 4.72% p.a.) |

The file is in long/tidy format: one row per (date, asset_id) pair. For N business days and 4 series the file contains approximately 4N rows.

## Construction

1. Raw series downloaded from FRED: `DGS2`, `DGS5`, `DGS10`, `DGS30` (daily, percent per annum).
2. Series renamed to canonical asset IDs: `DGS2 -> UST_2Y`, `DGS5 -> UST_5Y`, `DGS10 -> UST_10Y`, `DGS30 -> UST_30Y`.
3. Weekend and US federal holiday rows dropped (business-day calendar only).
4. Missing values filled by last-observation-carried-forward (LOCF) within a rolling 3-business-day window. Days where ≥2 series are still missing after LOCF are dropped entirely.
5. Panel truncated to `start_date = 2000-01-03` through `end_date = 2024-06-28` (as-of date). No data beyond 2024-06-28 is present.

## Coverage
- Approximately 6,400 business days × 4 series = ~25,600 rows.
- FRED occasionally publishes revised values; the panel snapshot was locked on 2024-07-01.
- No derived features (no spreads, no rolling statistics) are pre-computed; participants must engineer features themselves.
