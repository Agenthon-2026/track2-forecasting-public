# GBP Into a Political-Calendar Fog (21 BD)

**Family** T2-F4 · **as-of 2016-09-30** · targets `GBP`
at horizons [21] BD · unit `usd_per_gbp` · split validation

Inputs mounted read-only: `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (5 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** The panel has stabilised and BoE texts focus on stimulus transmission. The known unknown is political — a party-conference calendar starts inside the window and the constitutional-process stance is undefined. Thin-signal tail card: the corpus justifies variance, and thin-liquidity microstructure justifies a jump component.
