# Readout-Calendar Factor Rotation: MOM/HML/SMB (21/63 BD)

**Family** T2-F3 · **as-of 2020-10-30** · targets `MOM, HML, SMB`
at horizons [21, 63] BD · unit `cumulative_log_return` · split validation

Inputs mounted read-only: `/input/panels/factors_daily.parquet` (rows only through
the as-of date) and `/input/text/` (3 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = cumulative log return over the h business days after the as-of date (sum of ln(1+r_t)).
Every draw index must contain rows for ALL target assets (joint draw).

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Joint companion to the marginal MOM card: the SEC filings put a binary readout inside the window. On a readout the factor complex FLIPS together as one coherent scenario across MOM/HML/SMB — a joint distribution, not independent per-factor draws. Independent marginals cannot represent the flip.
