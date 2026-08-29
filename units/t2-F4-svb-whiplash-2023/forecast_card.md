# UST 2Y Under Conflicting Same-Week Texts (21 BD)

**Family** T2-F4 · **as-of 2023-03-08** · targets `UST_2Y`
at horizons [21] BD · unit `percent_per_annum` · split public-dev

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (5 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Two same-window texts point OPPOSITE ways: recent policy testimony leans toward re-accelerating hikes and pushed the front end to cycle highs by the as-of, while a bank's 8-K (in corpus, from EDGAR) discloses a large securities loss and an emergency capital raise. If funding stress spreads, prior banking-stress analogues imply violent front-end repricing; if it is contained, the hawkish path dominates. Both tails must be fat and neither side is presumed.
