# Team 210 Forecasting Agent Baseline

This directory packages the Team 210 participant forecasting agent baseline for Track 2 (Reasoning-Augmented Time-Series Forecasting).

## Architecture

1. **CLI Contract**: Implements `forecast --panels <path> --text <path> --asof <YYYY-MM-DD> --out <path>` conforming to `interface_version = "2.0"`.
2. **Panel Loading**: Loads multivariate time-series panels (rates, FX, macro, factor returns) up to the specified as-of date.
3. **Text Reasoning & Signal Extraction**: Reads the frozen text corpus (FOMC statements, central-bank communications, news releases) to derive macro directional signals.
4. **Probabilistic Forecast Engine**: Emits joint Monte Carlo paths conforming to `forecast.schema.json`, accompanied by `forecast_meta.json` and `forecast_rationale.md`.
5. **Score Metric**: Optimized for the track CRPS composite metric (marginal CRPS + joint variogram + tail penalty).
