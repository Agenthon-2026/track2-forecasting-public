# UST 10Y After an Asset-Purchase Program Concludes (126/189 BD)

**Family** T2-F1 · **as-of 2014-10-29** · targets `UST_10Y`
at horizons [126, 189] BD · unit `percent_per_annum` · split validation

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (3 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** The asset-purchase program terminates at the as-of meeting while the statement retains its rate-timing reassurance. Consensus at the as-of says yields rise once purchases stop; the statement text hedges both ways, and the oil-price slide already visible in pre-asof data pushes the other way. Weigh the supply argument against the disinflation argument.
