# UST 2Y Into an Accelerating Hiking Cycle (126 BD)

**Family** T2-F4 · **as-of 2021-12-31** · targets `UST_2Y`
at horizons [126] BD · unit `percent_per_annum` · split validation

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (3 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Companion to the repo's exemplar F4 card, three months later: the asset-purchase reduction pace accelerated, the dot plot shifted to multiple hikes for the coming year, and the 'transitory' characterisation was retired — yet the 2Y still sits at 0.73. The statement text demands a right tail far beyond anything in the trailing panel history; the dots and the reduction pace quantify the hawkish branch.
