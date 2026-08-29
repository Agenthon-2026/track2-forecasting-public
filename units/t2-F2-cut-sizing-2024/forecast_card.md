# 2Y/10Y as a Policy Turn Is Sized (63 BD)

**Family** T2-F2 · **as-of 2024-09-06** · targets `UST_2Y, UST_10Y`
at horizons [63] BD · unit `percent_per_annum` · split public-dev

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (3 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.
Every draw index must contain rows for ALL target assets (joint draw).

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** As-of a jobs-report Friday ahead of a policy meeting: a same-day governor speech addresses the pace of policy adjustment, and its wording on sequencing bears on the size of the upcoming decision. The front end reprices the near-term path; the slope's sign is in play after a prolonged inversion.
