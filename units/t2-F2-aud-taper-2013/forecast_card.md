# AUD Between Global Funding and a Domestic Downturn (64 BD)

**Family** T2-F2 · **as-of 2013-05-24** · targets `AUD`
at horizons [64] BD · unit `usd_per_aud` · split validation

Inputs mounted read-only: `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (3 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Two regime texts converge on one currency: the Fed's purchase-pace language (global funding) and the RBA's own easing bias as the mining-investment boom rolls over (domestic cycle). Both point the same way — the card tests whether agents SIZE a move when signals align, rather than hedging to symmetry.
