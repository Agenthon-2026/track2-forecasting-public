# Joint Rates-FX Under a Fiscal-Risk Event: UST 10Y + CHF + JPY (21/63 BD)

**Family** T2-F3 · **as-of 2011-07-22** · targets `UST_10Y, CHF, JPY`
at horizons [21, 63] BD · unit `percent_per_annum (UST_10Y); CHF,JPY per USD` · split public-dev

Inputs mounted read-only: `/input/panels/rates_daily.parquet`, `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (5 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.
Every draw index must contain rows for ALL target assets (joint draw).

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Fiscal brinkmanship with a rating agency on negative watch. The naive causal read (fiscal-risk => UST yields UP) can conflict with the flow-of-funds logic of risk-off episodes, where the deepest safe asset and haven FX can strengthen instead. Joint draws must take a stance on the correlation sign between the rates leg and the FX legs; both signs should be representable.
