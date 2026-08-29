# One Scheduled Event, Four Markets: 2Y/10Y + EUR/JPY (21/63 BD)

**Family** T2-F3 · **as-of 2024-10-31** · targets `UST_2Y, UST_10Y, EUR, JPY`
at horizons [21, 63] BD · unit `percent_per_annum (UST); USD-per-EUR; JPY-per-USD` · split public-dev

Inputs mounted read-only: `/input/panels/rates_daily.parquet`, `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (6 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.
Every draw index must contain rows for ALL target assets (joint draw).

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** A scheduled binary event sits inside the window, its date known ex-ante. Each draw is ONE event outcome propagated across four exposures, and each branch (expansionary repricing vs status-quo continuity) carries its own coherent cross-market signature. A bimodal JOINT distribution whose branches stay internally consistent across all four legs; neither branch is privileged a priori.
