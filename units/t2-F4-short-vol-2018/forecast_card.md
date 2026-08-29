# Market Factor Tail at Peak Short-Vol Crowding (21 BD)

**Family** T2-F4 · **as-of 2018-01-26** · targets `MKT`
at horizons [21] BD · unit `cumulative_log_return` · split public-dev

Inputs mounted read-only: `/input/panels/factors_daily.parquet` (rows only through
the as-of date) and `/input/text/` (4 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = cumulative log return over the h business days after the as-of date (sum of ln(1+r_t)).


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** As-of the top of a euphoric, ultra-low-vol run. Dec-2017 minutes flag continued hikes into fiscal stimulus; a scheduled early-February employment report (release calendar known ex-ante) falls inside the window; pre-asof commentary documents record short-vol product crowding. A wage-inflation surprise could force a mechanical vol unwind — the left tail must stay fat despite the calm panel.
