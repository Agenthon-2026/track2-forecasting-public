# UST 2Y Through a Statement-Language Shift (126 BD)

**Family** T2-F2 · **as-of 2019-01-30** · targets `UST_2Y`
at horizons [126] BD · unit `percent_per_annum` · split validation

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (3 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Between the 2018-12-19 and 2019-01-30 statements the language shifts sharply on tone: a patience formulation replaces the further-increases bias, alongside new balance-sheet flexibility, while policy action is still pending. The panel shows nothing yet; whether and how the 2Y moves over the horizon must be inferred from text alone.
