# UST 2Y Under Building Funding Stress (63 BD)

**Family** T2-F4 · **as-of 2008-09-12** · targets `UST_2Y`
at horizons [63] BD · unit `percent_per_annum` · split validation

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (13 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** As-of Friday 2008-09-12. The corpus holds the GSE conservatorship statements (Sep-7), a broker-dealer's announcement of a strategic restructuring (8-K, Sep-10) and the August minutes discussing financial fragility. The documents bear on how much weight a systemic scenario deserves next to a muddle-through one.
