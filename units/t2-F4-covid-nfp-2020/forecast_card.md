# Monthly Payrolls Level Under an Emerging Labor Shock (single print)

**Family** T2-F4 · **as-of 2020-03-31** · targets `NFP`
at horizons [21] BD · unit `thousands of jobs (PAYEMS, as-published first-release vintage)` · split public-dev

Inputs mounted read-only: `/input/panels/macro_monthly.parquet` (rows only through
the as-of date) and `/input/text/` (8 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.

Panel values are the vintage as published on the as-of date (31 March 2020), not later revisions; PCE indexes are on the base then in force (2012=100, not today's 2017=100).

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Forecast the April 2020 payrolls LEVEL as first published (released in May 2020), one print beyond the March 2020 print that is next at the as-of date; the panel ends at February 2020 and the intervening March print was not yet public (45-day lag enforced). The corpus contains emergency rate action, expanded asset purchases, and statement language on the outbreak's disruption of economic activity; the documents bear on how the severity of the policy response should scale the forecast relative to the panel's history, an inherently wide exercise. Targets are scored on the AS-PUBLISHED (first-release) level, not later revisions, per the point-in-time rule.
