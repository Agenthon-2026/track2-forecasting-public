# UST 10Y as Tariffs Escalate Past the Cut (64 BD)

**Family** T2-F2 · **as-of 2019-08-02** · targets `UST_10Y`
at horizons [64] BD · unit `percent_per_annum` · split validation

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (6 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** NEW (EPU-spike screen): the day after a cut framed as a limited recalibration, not the start of a cycle, new tariffs on remaining imports are announced — the corpus holds a Fed trying to stop at one cut and trade texts forcing its hand. The long end arbitrates between the two.
