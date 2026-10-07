# Does the Inversion Stick? UST 2Y/10Y Joint (63/126 BD)

**Family** T2-F3 · **as-of 2019-08-14** · targets `UST_2Y, UST_10Y`
at horizons [63, 126] BD · unit `percent_per_annum` · split validation

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (7 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.
Every draw index must contain rows for ALL target assets (joint draw).

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** As-of the day the 2s10s spread closed at 1bp. The corpus holds the July statement, the Chair's press conference, which calls the cut 'a midcycle adjustment to policy', and Beige Book reports of tariffs and trade-policy uncertainty; the documents may bear on the front end and the long end differently. The joint question is the SPREAD's sign and width, with near-unit level correlation between the two tenors.
