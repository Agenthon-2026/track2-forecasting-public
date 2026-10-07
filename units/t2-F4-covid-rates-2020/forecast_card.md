# UST 10Y as Speeches Name an Emerging External Risk (21 BD)

**Family** T2-F4 · **as-of 2020-02-14** · targets `UST_10Y`
at horizons [21] BD · unit `percent_per_annum` · split public-dev

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (9 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** The corpus contains central-bank speeches from early February that name the coronavirus outbreak as an emerging external risk. The documents bear on how much weight that risk deserves over the horizon.
