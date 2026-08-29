# Energy-Exposure Decoupling: NOK/CAD vs EUR/SEK (21/63 BD)

**Family** T2-F3 · **as-of 2022-02-18** · targets `NOK, CAD, EUR, SEK`
at horizons [21, 63] BD · unit `H.10 native quotes (NOK,CAD,SEK: ccy-per-USD; EUR: USD-per-ccy)` · split validation

Inputs mounted read-only: `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (3 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.
Every draw index must contain rows for ALL target assets (joint draw).

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Published escalation warnings sit in the corpus while FX correlations still reflect the joint-dollar regime. In the conflict branch, energy exporters (NOK, CAD) and energy-exposed Europe (EUR, SEK) DECOUPLE — a within-G10 correlation break that trailing covariance cannot produce.
