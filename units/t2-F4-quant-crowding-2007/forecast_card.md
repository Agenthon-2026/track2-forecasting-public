# Joint Factor Tail Into August 2007 (MOM/HML/SMB, 7 BD)

**Family** T2-F4 · **as-of 2007-07-31** · targets `MOM, HML, SMB`
at horizons [7] BD · unit `cumulative_log_return` · split validation

Inputs mounted read-only: `/input/panels/factors_daily.parquet` (rows only through
the as-of date) and `/input/text/` (4 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = cumulative log return over the h business days after the as-of date (sum of ln(1+r_t)).
Every draw index must contain rows for ALL target assets (joint draw).

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** The panel is calm; the warning is textual — June-2007 minutes and central-bank speeches discussing subprime deterioration and leveraged-fund stress. KL07 mechanism: crowded quant books facing forced deleveraging unwind over DAYS, with partial reversal — hence the short 7-BD horizon. Draws need fat JOINT tails: a deleveraging branch hits MOM, HML and SMB simultaneously.
