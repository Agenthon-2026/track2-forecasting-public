# INR: short-horizon continuation (1/4 BD)

**Family** T2-F1 · **as-of 2015-07-20** · targets `INR`
at horizons [1, 4] BD · unit `inr_per_usd` · split public-dev

**Quote basis.** ECB euro reference rates, cross-calculated per U.S. dollar by the organizers (INR: units per U.S. dollar).

Inputs mounted read-only: `/input/panels/em_fx_ecb_daily.parquet` (rows only through
the as-of date) and `/input/text/` (6 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json` and `forecast_rationale.md`. `value` = level in the stated unit on the target date.

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against realized outcomes.

**Text corpus role.** 6 official documents, all published before the as-of: 1 Beige Book, 1 FOMC statement, 2 sets of FOMC minutes and 2 statistical releases, from Federal Reserve Board and U.S. Bureau of Labor Statistics. They are U.S. official texts, context for INR against the U.S. dollar. They are background for a one-week continuation of the panel. The text signal for INR is thin: the corpus carries no Reserve Bank of India text, whose reuse terms are not established, and the documents are context from other issuers.
