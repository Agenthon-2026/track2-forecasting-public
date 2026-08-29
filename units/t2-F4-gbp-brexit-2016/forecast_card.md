# GBP/USD Around a Binary Referendum Tail (21 BD)

**Family** T2-F4 · **as-of 2016-05-31** · targets `GBP`
at horizons [21] BD · unit `usd_per_gbp` · split public-dev

Inputs mounted read-only: `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (4 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** A scheduled binary referendum falls inside the window and its date is known ex-ante. Central-bank texts in the corpus quantify a conditional tail before the event (a warned, potentially sharp depreciation if one branch resolves); polls are close to even. The institutional warnings turn a binary political outcome into an estimable two-sided tail, with neither branch presumed.
