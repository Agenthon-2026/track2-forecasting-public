# Joint Curve: Hikes vs a Pinned Long End (2Y/5Y/7Y/10Y, 63+63/126 BD)

**Family** T2-F3 · **as-of 2005-02-18** · targets `UST_2Y, UST_5Y, UST_7Y, UST_10Y`
at horizons [63, 126] BD · unit `percent_per_annum` · split validation

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (4 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.
Every draw index must contain rows for ALL target assets (joint draw).

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Measured-pace hikes are underway; the prevailing regime has the long end resisting the front so far. Whether the curve bear-flattens, bull-steepens, or something else over the horizon — and whether the level-slope correlation departs from what historical PCA (estimated pre-2004) implies — is the forecasting question. 30Y excluded (issuance suspended 2002-2006). Multi-horizon: draws must also correlate across 63/126.
