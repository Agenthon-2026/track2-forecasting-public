# ZAR around a scheduled decision or release (1/4 BD)

**Family** T2-F2 · **as-of 2020-01-27** · targets `ZAR`
at horizons [1, 4] BD · unit `zar_per_usd` · split public-dev

**Quote basis.** ECB euro reference rates, cross-calculated per U.S. dollar by the organizers (ZAR: units per U.S. dollar).

Inputs mounted read-only: `/input/panels/em_fx_ecb_daily.parquet` (rows only through
the as-of date) and `/input/text/` (7 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json` and `forecast_rationale.md`. `value` = level in the stated unit on the target date.

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against realized outcomes.

**Text corpus role.** 7 official documents, all published before the as-of: 1 Beige Book, 1 FOMC statement, 1 government speech, 1 set of FOMC minutes and 3 statistical releases, from National Treasury (South Africa), Federal Reserve Board, U.S. Bureau of Labor Statistics and Statistics South Africa. They are the official texts available for ZAR against the U.S. dollar, together with U.S. monetary-policy documents. The window holds a scheduled policy decision or data release; the corpus covers the run-up to it, not its result. The text signal for ZAR is thin: the corpus carries no South African Reserve Bank text, whose reuse terms are not established, and 2 of the 7 documents come from South African official sources.
