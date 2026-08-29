# UST 10Y and the Telegraphed QE1 Expansion (63 BD)

**Family** T2-F4 · **as-of 2009-01-30** · targets `UST_10Y`
at horizons [63] BD · unit `percent_per_annum` · split validation

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (3 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** The Dec-2008 statement says the Fed is 'evaluating the potential benefits of purchasing longer-term Treasuries'; January repeats it, and FOMC decision dates inside the window are known ex-ante. The text literally pre-announces a possible purchase program: put real mass on an announcement-effect rally branch AND on a no-action branch (supply pressure cuts the other way).
