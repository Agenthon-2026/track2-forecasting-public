# UST 10Y Into a Text-Warned Repricing (21 BD)

**Family** T2-F4 · **as-of 2020-02-14** · targets `UST_10Y`
at horizons [21] BD · unit `percent_per_annum` · split public-dev

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (6 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended; >= 1000 for tail accuracy),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Pre-shock as-of: the panel is calm and trailing vol sits at cycle lows, but the corpus already contains central-bank speeches naming an emerging external risk. If that branch materialises, prior crisis analogues imply a move worth many multiples of trailing vol, with the lower policy bound within reach; the direction and size over the horizon remain open. The text is the only tail warrant available.
