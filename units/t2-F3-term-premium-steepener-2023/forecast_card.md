# Joint UST Curve: Front-End vs Long-End Loadings (2Y/5Y/10Y/30Y, 21/63 BD)

**Family** T2-F3 · **as-of 2023-09-21** · targets `UST_2Y, UST_5Y, UST_10Y, UST_30Y`
at horizons [21, 63] BD · unit `percent_per_annum` · split public-dev

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (4 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.
Every draw index must contain rows for ALL target assets (joint draw).

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Sep-2023 SEP moved the 2024 dots up 50bp with the policy rate on hold — 'higher for longer' in text — while QRA/supply commentary flags growing duration issuance. Dots pin the front end; supply pressure loads on the long end. Draws should be able to represent both front-led (flattening) and long-end-led (steepening) curve loadings, in selloff and rally directions alike — parallel-shift-only models cannot.
