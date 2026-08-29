# UST 10Y at a Crowded Speculative Positioning Extreme (126/189 BD)

**Family** T2-F1 · **as-of 2018-09-28** · targets `UST_10Y`
at horizons [126, 189] BD · unit `percent_per_annum` · split validation

Inputs mounted read-only: `/input/panels/rates_daily.parquet` (rows only through
the as-of date) and `/input/text/` (3 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.


Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** The in-corpus COT table shows speculative 10Y futures shorts near an extreme as the Fed hikes past neutral. Positioning-as-text logic: crowded positioning cuts both ways — it can amplify the prevailing move or fuel a violent reversal. Widen BOTH tails relative to trailing vol; any asymmetry must come from positioning mechanics, not hindsight.
