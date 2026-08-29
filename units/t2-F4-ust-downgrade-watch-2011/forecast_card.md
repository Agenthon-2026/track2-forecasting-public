# UST 10Y Under Sovereign-Brinkmanship Rate Pressure (21 BD)

**Family** T2-F4 · **as-of 2011-07-22** · targets `UST_10Y`
at horizons [21] BD · unit `percent_per_annum` · split validation

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (5 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Fiscal-deadline brinkmanship with a rating agency on negative watch. Two ex-ante mechanisms compete in the corpus: the credit-risk reading (yields up) and the risk-off/flight reading seen in prior systemic scares (yields down). Allocate tail mass across BOTH branches rather than centering on either.
