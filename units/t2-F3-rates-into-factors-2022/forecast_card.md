# Rates Text, Equity Factors: HML + MOM (63/126 BD)

**Family** T2-F3 · **as-of 2022-01-05** · targets `HML, MOM`
at horizons [63, 126] BD · unit `cumulative_log_return` · split validation

Inputs mounted read-only: `/input/panels/factors_daily.parquet`, `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (3 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = cumulative log return over the h business days after the as-of date (sum of ln(1+r_t)).
Every draw index must contain rows for ALL target assets (joint draw).

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** As-of the day the December minutes land — balance-sheet runoff discussion arrives years earlier than the market assumed. The rates panel is an INPUT; the targets are equity factors: a discount-rate shock reprices long-duration growth against value, so HML and MOM must co-move through the rates branch.
