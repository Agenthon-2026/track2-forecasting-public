# EUR/USD Under an Explicit Policy Pre-Commitment (65 BD)

**Family** T2-F2 · **as-of 2014-05-30** · targets `EUR`
at horizons [65] BD · unit `usd_per_eur` · split validation

Inputs mounted read-only: `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (4 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** The May 2014 press conference (in corpus) contains an unusually explicit signal that the Council is prepared to act at its next meeting, and a policy meeting falls inside the window. Instruments under open public discussion in the corpus include deposit rates below zero and targeted lending. Price the probability, composition and FX pass-through of a package without assuming any of them.
