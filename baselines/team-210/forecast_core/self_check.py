"""Pre-ship self-backtest: the T1 verifier-first spine, applied to T2.

Before the forecast ships, test it the way the future will: roll a handful of
origins back through the RECENT history the agent has already seen, forecast
with the same sampler, and ask whether the realised values landed inside the
distribution's own 90% band. If they mostly did not, the distribution is too
sharp for this regime - widen it before shipping, and say so.

This is the distributional analogue of T1's mandatory assert block: the agent
never ships a claim it has not tried to falsify with the data in hand. It can
only WIDEN (never sharpen): under a composite with a 0.2 tail penalty and a
4.0 clip, overdispersion costs basis points and underdispersion costs the
card - the same asymmetry that decided the vol-conditioning design.

Everything here uses data at or before the as-of date only; the check is
in-sample by construction and leak-free by construction.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import scenario_mixture

N_ORIGINS = 6
N_DRAWS = 120
#: Coverage thresholds -> extra dispersion. Bounded and coarse on purpose:
#: this is a guardrail, not an optimiser.
LADDER = ((0.4, 1.6), (0.6, 1.25))
EVAL_WINDOW_DAYS = 180


def dispersion_correction(panel: pd.DataFrame, assets: list[str],
                          horizons: list[int]) -> tuple[float, list[str]]:
    """(extra_widen, notes) from a quick rolling self-backtest.

    Returns 1.0 (no correction) whenever the history is too short to test -
    an untestable forecast should not be silently inflated.
    """
    notes: list[str] = []
    try:
        wide = (panel.pivot_table(index="date", columns="asset", values="value")
                .sort_index().ffill())
        present = [a for a in assets if a in wide.columns]
        if not present:
            return 1.0, notes
        wide = wide[present].dropna()
        horizon = int(min(horizons))
        if len(wide) < scenario_mixture.MIN_HISTORY + horizon + N_ORIGINS + 2:
            return 1.0, notes

        last_origin = len(wide) - horizon - 1
        first_origin = max(scenario_mixture.MIN_HISTORY,
                           last_origin - EVAL_WINDOW_DAYS)
        origins = np.linspace(first_origin, last_origin, N_ORIGINS).astype(int)

        hits, total = 0, 0
        for origin in origins:
            asof_date = wide.index[origin]
            history = panel[panel["date"] <= asof_date]
            draws, _ = scenario_mixture.build(
                history, present, [horizon], n_draws=N_DRAWS)
            realised = wide.iloc[min(origin + horizon, len(wide) - 1)]
            sub = draws[draws["horizon"] == horizon]
            for asset in present:
                sample = sub[sub["asset"] == asset]["value"].to_numpy()
                if len(sample) == 0:
                    continue
                lo, hi = np.quantile(sample, 0.05), np.quantile(sample, 0.95)
                hits += int(lo <= float(realised[asset]) <= hi)
                total += 1
        if total == 0:
            return 1.0, notes

        coverage = hits / total
        for threshold, factor in LADDER:
            if coverage < threshold:
                notes.append(
                    f"self-backtest: recent 90% band covered only "
                    f"{coverage:.0%} of {total} realisations; dispersion "
                    f"widened x{factor} before shipping")
                return factor, notes
        notes.append(f"self-backtest: coverage {coverage:.0%} over {total} "
                     "recent realisations; no correction needed")
        return 1.0, notes
    except Exception as error:  # a guardrail must never take the run down
        notes.append(f"self-backtest skipped ({type(error).__name__})")
        return 1.0, notes
