# Joint G10 FX Under a Funding-vs-Carry Scenario: JPY/CHF vs AUD/NZD (21/63 BD)

**Family** T2-F3 · **as-of 2024-07-26** · targets `JPY, CHF, AUD, NZD`
at horizons [21, 63] BD · unit `H.10 native quote (JPY,CHF: ccy-per-USD; AUD,NZD: USD-per-ccy)` · split validation

Inputs mounted read-only: `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (4 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.
Every draw index must contain rows for ALL target assets (joint draw).

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** As-of ahead of back-to-back central-bank meetings: positioning reports show crowded funder shorts, policy speeches hint at normalization, and prior intervention is on the record. A carry-unwind branch would realign the funders (JPY, CHF) against the carry longs (AUD, NZD) into a correlation regime different from the as-of history. Draws must be able to represent that branch as a coherent joint scenario across the four crosses (correlated moves, not independent per-asset noise); correlations estimated on trailing data alone cannot.
