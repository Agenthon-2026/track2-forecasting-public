# TRANSFER: BRL from Fed Text and a G10 Panel (64 BD)

**Family** T2-F2 · **as-of 2013-05-24** · targets `BRL`
at horizons [64] BD · unit `brl_per_usd` · split validation

**Target basis.** The target's own series is given only as an early window (1995-01-02..2003-05-23) plus its level on the as-of date (BRL = 2.0516, unit `brl_per_usd`). The decade in between is withheld deliberately: enough to see what kind of series this is, not enough to extrapolate where it has been heading. Do not difference across the gap, and do not read the early window as a width calibration -- these episodes are volatility regime breaks, which is what the corpus is for.

Inputs mounted read-only: `/input/panels/` (`g10_fx_daily.parquet`, rows only through the as-of date, and `em_transfer_early.parquet`, the target basis described above) and `/input/text/` (4 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Transfer configuration: the target currency has no recent path in any input panel — only an early window and an as-of anchor (BRL = 2.0516). Same corpus as the INR card, different transfer target: Brazil pairs the purchase-pace shock with an active central-bank intervention program — the policy-response offset differentiates the two cards' distributions.
