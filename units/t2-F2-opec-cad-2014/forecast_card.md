# CAD After a Supply-Side Surprise in Oil (63 BD)

**Family** T2-F2 · **as-of 2014-11-28** · targets `CAD`
at horizons [63] BD · unit `cad_per_usd` · split validation

Inputs mounted read-only: `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (5 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Cross-domain reading: a supply-side decision in the oil market (visible in the crude positioning table and producer-group communication in corpus) bears on a petro-currency whose central bank's own speeches stress the terms-of-trade channel. The FX panel barely moves by the as-of; how strongly and how persistently the shock transmits, in either direction, is the question.
