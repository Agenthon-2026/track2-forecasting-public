# One Policy Scenario, Four Markets: UST 2Y + EUR/GBP/JPY (21/63 BD)

**Family** T2-F3 · **as-of 2022-09-01** · targets `UST_2Y, EUR, GBP, JPY`
at horizons [21, 63] BD · unit `percent_per_annum (UST_2Y); H.10 native quote (EUR,GBP: USD-per-ccy; JPY: JPY-per-USD)` · split validation

Inputs mounted read-only: `/input/panels/rates_daily.parquet`, `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (4 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.
Every draw index must contain rows for ALL target assets (joint draw).

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Cross-panel joint card: the policy signal in the text must propagate coherently across all four legs as one joint distribution (correlated moves, not independent per-asset draws), with MoF intervention rhetoric as a live tail risk. Independent per-asset draws overstate cross-market distances.
