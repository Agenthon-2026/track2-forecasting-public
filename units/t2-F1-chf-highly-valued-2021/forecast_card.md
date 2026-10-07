# CHF Under Standing 'Highly Valued' Language (126/189 BD)

**Family** T2-F1 · **as-of 2021-06-17** · targets `CHF`
at horizons [126, 189] BD · unit `chf_per_usd` · split validation

Inputs mounted read-only: `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (9 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** The SNB's decision of the as-of day says the franc remains 'highly valued' and that the SNB remains willing to intervene in the foreign exchange market as necessary, a policy reaction function stated in text. The documents bear on how that stated reaction function should shape the distribution of CHF.
