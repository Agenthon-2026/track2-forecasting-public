# MXN, BRL, ZAR jointly over one week (2/4 BD)

**Family** T2-F3 · **as-of 2009-08-10** · targets `MXN, BRL, ZAR`
at horizons [2, 4] BD · unit `mxn_per_usd; brl_per_usd; zar_per_usd` · split public-dev

**Quote basis.** ECB euro reference rates, cross-calculated per U.S. dollar by the organizers (MXN, BRL, ZAR: units per U.S. dollar).

Inputs mounted read-only: `/input/panels/em_fx_ecb_daily.parquet` (rows only through
the as-of date) and `/input/text/` (8 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json` and `forecast_rationale.md`. `value` = level in the stated unit on the target date.
Every draw index must contain rows for ALL target assets (joint draw).

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against realized outcomes.

**Text corpus role.** 8 official documents, all published before the as-of: 1 Beige Book, 1 FOMC statement, 2 central-bank policy decisions, 1 government speech, 1 set of FOMC minutes, 1 set of central-bank minutes and 1 statistical release, from National Treasury (South Africa), Federal Reserve Board, Banco de México, Banco Central do Brasil and Statistics South Africa. They are the official texts available for MXN, BRL and ZAR against the U.S. dollar, together with U.S. monetary-policy documents. The targets are forecast as one joint distribution. Some documents are in their original language (Portuguese and Spanish). The text signal for ZAR is thin: the corpus carries no South African Reserve Bank text, whose reuse terms are not established, and 2 of the 8 documents come from South African official sources.
