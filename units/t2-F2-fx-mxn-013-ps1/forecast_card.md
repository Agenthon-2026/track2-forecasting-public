# MXN around a scheduled decision or release (1/4 BD)

**Family** T2-F2 · **as-of 2019-06-24** · targets `MXN`
at horizons [1, 4] BD · unit `mxn_per_usd` · split public-dev

**Quote basis.** ECB euro reference rates, cross-calculated per U.S. dollar by the organizers (MXN: units per U.S. dollar).

Inputs mounted read-only: `/input/panels/em_fx_ecb_daily.parquet` (rows only through
the as-of date) and `/input/text/` (6 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json` and `forecast_rationale.md`. `value` = level in the stated unit on the target date.

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against realized outcomes.

**Text corpus role.** 6 official documents, all published before the as-of: 1 Beige Book, 1 central-bank policy decision, 1 set of FOMC minutes, 1 set of central-bank minutes and 2 statistical releases, from Banco de México, Federal Reserve Board and U.S. Bureau of Labor Statistics. They are the official texts available for MXN against the U.S. dollar, together with U.S. monetary-policy documents. The window holds a scheduled policy decision or data release; the corpus covers the run-up to it, not its result. Some documents are in their original language (Spanish).
