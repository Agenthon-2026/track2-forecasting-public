# High-Beta Europe at the UK Fiscal Event: SEK/NOK/GBP (21/63 BD)

**Family** T2-F3 · **as-of 2022-09-23** · targets `SEK, NOK, GBP`
at horizons [21, 63] BD · unit `H.10 native quotes (SEK,NOK: ccy-per-USD; GBP: USD-per-ccy)` · split validation

Inputs mounted read-only: `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (3 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.
Every draw index must contain rows for ALL target assets (joint draw).

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** As-of the UK fiscal-event day: BoE and Fed texts define a global-tightening regime, with a UK-idiosyncratic overlay building. Joint draws must carry a common dollar factor PLUS a GBP-specific stress component — two-factor structure, not one.
