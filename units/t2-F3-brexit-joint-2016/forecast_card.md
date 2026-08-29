# Event-Scenario Joint FX: GBP/EUR/CHF/JPY (21/63 BD)

**Family** T2-F3 · **as-of 2016-06-17** · targets `GBP, EUR, CHF, JPY`
at horizons [21, 63] BD · unit `H.10 native quote (GBP,EUR: USD-per-ccy; CHF,JPY: ccy-per-USD)` · split public-dev

Inputs mounted read-only: `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (5 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.
Every draw index must contain rows for ALL target assets (joint draw).

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** A scheduled binary risk event falls shortly after the as-of date; its timing is knowable from the corpus. Each draw is ONE event branch propagated through four exposures with sign-consistent legs: one branch implies sharp GBP depreciation with EUR dragged lower and CHF/JPY haven bids; the other implies a relief recovery with the haven legs fading. A bimodal JOINT distribution with sign-consistent legs — not four independent bimodals; neither branch is privileged a priori.
