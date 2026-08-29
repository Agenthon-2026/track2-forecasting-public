# EUR Under Published Warnings (21 BD)

**Family** T2-F4 · **as-of 2022-02-18** · targets `EUR`
at horizons [21] BD · unit `usd_per_eur` · split validation

Inputs mounted read-only: `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (5 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Escalation warnings are published and explicit before the as-of — a rare case of governments pre-announcing a tail. Energy dependence means the geopolitical branch, if it materialises, could act as a terms-of-trade shock for the euro; the tail size is estimable from the corpus, though the branch is conditional and its direction over the horizon is left open.
