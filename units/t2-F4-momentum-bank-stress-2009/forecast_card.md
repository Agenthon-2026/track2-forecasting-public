# Momentum Factor Under Early-2009 Bank-Stress Texts (63 BD)

**Family** T2-F4 · **as-of 2009-03-06** · targets `MOM`
at horizons [63] BD · unit `cumulative_log_return` · split validation

Inputs mounted read-only: `/input/panels/factors_daily.parquet` (rows only through
the as-of date) and `/input/text/` (10 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = cumulative log return over the h business days after the as-of date (sum of ln(1+r_t)).


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** As-of a deeply depressed market. The momentum factor's loser leg is concentrated in financials, so its path depends on whether bank stress resolves. Stress-test and nationalization texts in the corpus frame exactly that binary; how it resolves over the horizon is the forecasting question.
