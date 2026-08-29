# Joint Rates-FX Under a Policy-Divergence Scenario: UST 10Y + EUR + JPY (63/126 BD)

**Family** T2-F3 · **as-of 2014-09-30** · targets `UST_10Y, EUR, JPY`
at horizons [63, 126] BD · unit `percent_per_annum (UST_10Y); USD-per-EUR; JPY-per-USD` · split validation

Inputs mounted read-only: `/input/panels/rates_daily.parquet`, `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (9 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.
Every draw index must contain rows for ALL target assets (joint draw).

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** One central-bank-divergence scenario must price the three legs (EUR, JPY yen-per-USD, and the UST 10Y) as one coherent joint scenario — correlated moves driven by a common global discount-rate setup, not independent per-asset draws. Draws sampling the three legs independently overstate cross-market distances — this is the variogram test.
