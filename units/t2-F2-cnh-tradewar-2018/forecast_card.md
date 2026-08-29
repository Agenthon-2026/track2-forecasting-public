# TRANSFER: CNY as New Tariff Lists Take Effect (64 BD)

**Family** T2-F2 · **as-of 2018-06-15** · targets `CNY`
at horizons [64] BD · unit `cny_per_usd` · split validation

**Target basis.** The target's own series is given only as an early window (1998-06-15..2008-06-13) plus its level on the as-of date (CNY = 6.4379, unit `cny_per_usd`). The decade in between is withheld deliberately: enough to see what kind of series this is, not enough to extrapolate where it has been heading. Do not difference across the gap, and do not read the early window as a width calibration -- these episodes are volatility regime breaks, which is what the corpus is for.

Inputs mounted read-only: `/input/panels/` (`g10_fx_daily.parquet`, rows only through the as-of date, and `em_transfer_early.parquet`, the target basis described above) and `/input/text/` (10 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Transfer configuration: the target currency has no recent path in any input panel — only an early window and an as-of anchor (CNY = 6.4379). Transfer card at the moment the first tariff list is finalized: the PBoC governor's own remarks (in corpus) frame the policy stance, Fed texts price the macro spillover. A managed currency facing a terms-of-trade shock can absorb it through reserves or through the fix — the two regimes imply very different distributions, and the choice is readable from policy text.
