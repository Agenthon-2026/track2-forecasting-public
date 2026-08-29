# Full G10 Panel Under Funding Stress (10 currencies, 21/63 BD)

**Family** T2-F3 · **as-of 2020-03-13** · targets `EUR, GBP, JPY, CHF, AUD, CAD, NZD, SEK, NOK, DKK`
at horizons [21, 63] BD · unit `H.10 native quotes (see per-asset units table in data/PROVENANCE.md)` · split validation

Inputs mounted read-only: `/input/panels/g10_fx_daily.parquet` (rows only through
the as-of date) and `/input/text/` (6 dated documents, all timestamps <= as-of;
see `text/corpus_index.json`).

Produce `forecast.parquet` with columns `[draw:int32, asset:string, horizon:int32,
value:float64]`, n_draws >= 200 (>= 500 recommended),
plus `forecast_meta.json`. `value` = level in the stated unit on the target date.
Every draw index must contain rows for ALL target assets (joint draw).

Scoring: S = 0.5 x marginal CRPS + 0.3 x joint variogram + 0.2 x tail penalty (lower
is better) against sealed realized outcomes.

**Text corpus role.** Largest joint card in the batch: all ten panel currencies through a dollar-funding squeeze. Within one draw, havens (JPY, CHF) and high-beta currencies (AUD, NOK, SEK) must move with consistent signs and beta-sorted magnitudes; draws must span both a continued-squeeze branch and a policy-response branch. Ten assets give the variogram maximal discriminating power.
