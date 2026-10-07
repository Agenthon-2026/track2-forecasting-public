# UST 2Y Into a Scheduled CPI Release (21 BD)

**Family** T2-F4 · **as-of 2022-05-31** · targets `UST_2Y`
at horizons [21] BD · unit `percent_per_annum` · split validation

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (8 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** The prior meeting delivered 50bp, and its press conference took a larger step 'off the table'. An inflation release falls inside the window (date known ex-ante), and the corpus holds real-time gas and rent commentary. The documents are for weighing the official guidance against that commentary.
