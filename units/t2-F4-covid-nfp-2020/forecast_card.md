# Monthly Payrolls Level Under an Emerging Labor Shock (single print)

**Family** T2-F4 · **as-of 2020-03-31** · targets `NFP`
at horizons [21] BD · unit `thousands of jobs (PAYEMS, as-published first-release vintage)` · split public-dev

Inputs mounted read-only: `/input/panels/macro_monthly.parquet` (rows only through
the as-of date) and `/input/text/` (3 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Forecast the next-month payrolls LEVEL with the intervening print not yet public (45-day lag enforced). The corpus contains emergency rate action, expanded asset purchases, and activity-restriction language; if the disruption branch dominates, the magnitude must be scaled from policy-response severity into a range far outside the panel's history, an inherently wide exercise. Targets are scored on the AS-PUBLISHED (first-release) level, not later revisions, per the point-in-time rule.
