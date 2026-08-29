# UST 2Y Into a Hot-Print Window (21 BD)

**Family** T2-F4 · **as-of 2022-05-31** · targets `UST_2Y`
at horizons [21] BD · unit `percent_per_annum` · split validation

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (3 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** The prior meeting delivered 50bp and took a larger step 'off the table' — text the front end took at face value. An inflation release falls inside the window (date known ex-ante); real-time gas and rent commentary argue the prints may not be done rising. If the data overrides the guidance, the repricing could be violent; if the guidance holds, the front end stays anchored. Both tails must survive the reassuring official text, with neither side presumed.
