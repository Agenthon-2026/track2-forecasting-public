# UST 2Y Under Building Funding Stress (63 BD)

**Family** T2-F4 · **as-of 2008-09-12** · targets `UST_2Y`
at horizons [63] BD · unit `percent_per_annum` · split validation

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (5 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** As-of Friday 2008-09-12. The corpus knows: GSE conservatorship (Sep-7), a failing broker-dealer in the headlines, August minutes fretting about financial fragility. It does NOT know the weekend outcome. Draws need a systemic branch (2Y toward zero) alongside a muddle-through branch.
