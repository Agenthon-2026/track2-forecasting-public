# UST 10Y in a Maturing Hiking Cycle (126/189 BD)

**Family** T2-F1 · **as-of 2005-02-18** · targets `UST_10Y`
at horizons [126, 189] BD · unit `percent_per_annum` · split public-dev

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (4 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** A steady hiking cycle is underway, yet the 2005-02-16 testimony in the corpus notes that long yields have fallen even as the policy rate rose 150bp. Whether to extrapolate the hiking cycle into the 10Y — or weigh the flat long-end response the testimony describes — is the question the card poses.
