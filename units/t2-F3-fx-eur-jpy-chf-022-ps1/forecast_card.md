# EUR, JPY, CHF jointly over one week (3 BD)

**Family** T2-F3 · **as-of 2010-04-05** · targets `EUR, JPY, CHF`
at horizons [3] BD · unit `usd_per_eur; jpy_per_usd; chf_per_usd` · split public-dev

**Quote basis.** Federal Reserve H.10 noon buying rates, native quotes (JPY, CHF: units per U.S. dollar; EUR: U.S. dollars per unit).

Inputs mounted read-only: `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (7 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json` and `forecast_rationale.md`. `value` = level in the stated unit on the target date.
Every draw index must contain rows for ALL target assets (joint draw).

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against realized outcomes.

**Text corpus role.** 7 official documents, all published before the as-of: 1 Beige Book, 1 FOMC statement, 2 central-bank policy decisions, 1 set of FOMC minutes and 2 statistical releases, from European Central Bank, Federal Reserve Board and U.S. Bureau of Labor Statistics. They are euro-area and U.S. official texts bearing on EUR, JPY and CHF against the U.S. dollar. The targets are forecast as one joint distribution. The text signal for JPY and CHF is thin: the corpus carries no Bank of Japan text, whose reuse terms are not established, and no Swiss National Bank text, whose published terms allow non-commercial use only.
