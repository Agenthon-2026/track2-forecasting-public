# MKT Tail After a Reassuring Policy-Speech Head-Fake (21 BD)

**Family** T2-F4 · **as-of 2018-11-30** · targets `MKT`
at horizons [21] BD · unit `cumulative_log_return` · split validation

Inputs mounted read-only: `/input/panels/factors_daily.parquet` (rows only through
the as-of date) and `/input/text/` (3 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = cumulative log return over the h business days after the as-of date (sum of ln(1+r_t)).


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** The trap card: a late-November policy speech read dovish and markets bounced hard into the as-of. But the corpus also holds the November minutes ('further gradual increases'), balance-sheet-runoff language, live trade-war headlines, and a December FOMC inside the window. A single reassuring speech is not regime evidence — the left tail must survive it.
