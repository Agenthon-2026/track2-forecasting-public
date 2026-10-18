# KRW, INR, ZAR jointly over one week (4 BD)

**Family** T2-F3 · **as-of 2014-01-27** · targets `KRW, INR, ZAR`
at horizons [4] BD · unit `krw_per_usd; inr_per_usd; zar_per_usd` · split public-dev

**Quote basis.** ECB euro reference rates, cross-calculated per U.S. dollar by the organizers (KRW, INR, ZAR: units per U.S. dollar).

Inputs mounted read-only: `/input/panels/em_fx_ecb_daily.parquet` (rows only through
the as-of date) and `/input/text/` (8 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json` and `forecast_rationale.md`. `value` = level in the stated unit on the target date.
Every draw index must contain rows for ALL target assets (joint draw).

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against realized outcomes.

**Text corpus role.** 8 official documents, all published before the as-of: 1 Beige Book, 1 FOMC statement, 1 government press release, 1 government statement, 1 set of FOMC minutes and 3 statistical releases, from Press Information Bureau (India), Prime Minister's Office archive (India), Federal Reserve Board, U.S. Bureau of Labor Statistics and Statistics South Africa. They are the official texts available for KRW, INR and ZAR against the U.S. dollar, together with U.S. monetary-policy documents. The targets are forecast as one joint distribution. The text signal for KRW is thin: the corpus carries no Bank of Korea text, whose reuse terms are not established, and the documents are context from other issuers. The text signal for INR is thin: the corpus carries no Reserve Bank of India text, whose reuse terms are not established, and 2 of the 8 documents come from Indian official sources. The text signal for ZAR is thin: the corpus carries no South African Reserve Bank text, whose reuse terms are not established, and 1 of the 8 documents comes from South African official sources.
