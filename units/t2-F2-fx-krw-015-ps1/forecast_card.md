# KRW around a scheduled decision or release (1/3 BD)

**Family** T2-F2 · **as-of 2021-03-15** · targets `KRW`
at horizons [1, 3] BD · unit `krw_per_usd` · split public-dev

**Quote basis.** ECB euro reference rates, cross-calculated per U.S. dollar by the organizers (KRW: units per U.S. dollar).

Inputs mounted read-only: `/input/panels/em_fx_ecb_daily.parquet` (rows only through
the as-of date) and `/input/text/` (6 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json` and `forecast_rationale.md`. `value` = level in the stated unit on the target date.

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against realized outcomes.

**Text corpus role.** 6 official documents, all published before the as-of: 1 FOMC statement, 2 government press releases, 1 set of FOMC minutes and 2 statistical releases, from Federal Reserve Board, U.S. Bureau of Labor Statistics and Korea Policy Briefing (korea.kr). They are the official texts available for KRW against the U.S. dollar, together with U.S. monetary-policy documents. The window holds a scheduled policy decision or data release; the corpus covers the run-up to it, not its result. Some documents are in their original language (Korean). The text signal for KRW is thin: the corpus carries no Bank of Korea text, whose reuse terms are not established, and 2 of the 6 documents come from Korean official sources.
