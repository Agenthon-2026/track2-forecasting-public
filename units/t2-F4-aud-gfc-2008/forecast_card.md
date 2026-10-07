# AUD Under September 2008 Funding Stress (21 BD)

**Family** T2-F4 · **as-of 2008-09-12** · targets `AUD`
at horizons [21] BD · unit `usd_per_aud` · split validation

Inputs mounted read-only: `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (10 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** As-of Friday 2008-09-12, for a commodity and carry currency: the RBA's decision records a 25bp cut, while US systemic-risk texts accumulate. The documents bear on how carry, commodity and liquidity channels could act on AUD at the same time; whether they do over the horizon is the open question.
