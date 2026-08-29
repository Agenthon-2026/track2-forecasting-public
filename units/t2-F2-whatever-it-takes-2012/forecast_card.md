# EUR/USD After an Unconditional Backstop Signal (64 BD)

**Family** T2-F2 · **as-of 2012-07-27** · targets `EUR`
at horizons [64] BD · unit `usd_per_eur` · split public-dev

Inputs mounted read-only: `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (5 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Corpus centers on a 2012-07-26 central-bank address containing an unconditional commitment regarding the currency's integrity, alongside two earlier ECB communications, an FOMC statement, and a Beige Book. At the as-of date, speculative EUR positioning is heavily short and sovereign spreads are elevated.
