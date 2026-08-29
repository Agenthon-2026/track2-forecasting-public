# Momentum Factor Tail Around Published Clinical-Readout Timelines (21 BD)

**Family** T2-F4 · **as-of 2020-10-30** · targets `MOM`
at horizons [21] BD · unit `cumulative_log_return` · split validation

Inputs mounted read-only: `/input/panels/factors_daily.parquet` (rows only through
the as-of date) and `/input/text/` (3 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = cumulative log return over the h business days after the as-of date (sum of ln(1+r_t)).


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** SEC 8-K press-release exhibits (timestamps = EDGAR filing dates) from late October 2020 state clinical trial-readout timing ('interim analysis expected in November'). A binary readout inside the 21-BD window can violently reprice crowded momentum (DM16 loser-leg optionality). The text gives the event calendar and its probability, not the outcome.
