# Value's Duration Problem in a Demand-Disruption Window (21 BD)

**Family** T2-F4 · **as-of 2020-02-14** · targets `HML`
at horizons [21] BD · unit `cumulative_log_return` · split validation

Inputs mounted read-only: `/input/panels/factors_daily.parquet` (rows only through
the as-of date) and `/input/text/` (6 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = cumulative log return over the h business days after the as-of date (sum of ln(1+r_t)).


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Same pre-crash as-of as the rates card, factor-side target: value portfolios are long the physical economy (banks, energy, travel) and short the names leveraged to a shift toward remote-consumption business models. If the disruption branch materialises, HML is the maximally exposed factor — a channel the warning texts imply but never state. The left tail must be constructed from sector exposure reasoning, not from trailing factor vol.
