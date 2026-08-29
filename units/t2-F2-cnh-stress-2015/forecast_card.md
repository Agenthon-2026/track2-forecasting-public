# TRANSFER: CNY from a G10 Panel and Cross-Market Text (64 BD)

**Family** T2-F2 · **as-of 2015-07-31** · targets `CNY`
at horizons [64] BD · unit `cny_per_usd` · split public-dev

**Target basis.** The target's own series is given only as an early window (1995-07-31..2005-07-29) plus its level on the as-of date (CNY = 6.2097, unit `cny_per_usd`). The decade in between is withheld deliberately: enough to see what kind of series this is, not enough to extrapolate where it has been heading. Do not difference across the gap, and do not read the early window as a width calibration -- these episodes are volatility regime breaks, which is what the corpus is for.

Inputs mounted read-only: `/input/panels/` (`g10_fx_daily.parquet`, rows only through the as-of date, and `em_transfer_early.parquet`, the target basis described above) and `/input/text/` (12 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Transfer configuration: the target currency has no recent path in any input panel — only an early window and an as-of anchor (CNY = 6.2097). Broad market-stress coverage and regional central-bank commentary are in corpus while the fix has been rock-steady for months — the question is whether stress of this size forces any change in the management regime. The distribution must weigh continued stability against discrete adjustment in either direction.
