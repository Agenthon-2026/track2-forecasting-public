# BRL with a live risk channel or scheduled event (3/4 BD)

**Family** T2-F4 · **as-of 2016-11-07** · targets `BRL`
at horizons [3, 4] BD · unit `brl_per_usd` · split public-dev

**Quote basis.** ECB euro reference rates, cross-calculated per U.S. dollar by the organizers (BRL: units per U.S. dollar).

Inputs mounted read-only: `/input/panels/em_fx_ecb_daily.parquet` (rows only through
the as-of date) and `/input/text/` (7 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json` and `forecast_rationale.md`. `value` = level in the stated unit on the target date.

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against realized outcomes.

**Text corpus role.** 7 official documents, all published before the as-of: 1 Beige Book, 1 FOMC statement, 1 central-bank policy decision, 1 set of FOMC minutes, 1 set of central-bank minutes and 2 statistical releases, from Federal Reserve Board, U.S. Bureau of Labor Statistics and Banco Central do Brasil. They are the official texts available for BRL against the U.S. dollar, together with U.S. monetary-policy documents. As an F4 card, the corpus carries a live risk channel or a scheduled event inside the window; it doesn't promise that a shock happens. Some documents are in their original language (Portuguese).
