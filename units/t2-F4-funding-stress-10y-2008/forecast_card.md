# UST 10Y Under Building Funding Stress (21 BD)

**Family** T2-F4 · **as-of 2008-09-12** · targets `UST_10Y`
at horizons [21] BD · unit `percent_per_annum` · split validation

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (5 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Same Friday as-of as the 2Y card, long-end target: systemic-risk text against a flight-to-quality channel PLUS a supply channel (rescue financing) pulling the opposite way. The 10Y tail is two-sided where the 2Y tail is one-sided — the pair tests whether agents differentiate tenors under the same corpus.
