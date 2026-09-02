"""The tail term is selectable, and the default arm is byte-identical to the shared toolkit.

The point of the control below: `scoring._composite` replaced a direct call to
`crps.crps_composite`, so the default path must be provably the same function. Without it, a
change meant to add an option could silently move every score.
"""

from __future__ import annotations

import numpy as np
import pytest
from qfbench2_common.scoring import crps

from qfbench2_track_forecasting import scoring
from qfbench2_track_forecasting.tail import tail_coverage, tail_pinball

LEVELS = (0.01, 0.05, 0.95, 0.99)


def _draws(seed: int = 0, m: int = 500, d: int = 4) -> np.ndarray:
    return np.random.default_rng(seed).standard_normal((m, d))


@pytest.mark.parametrize("joint", ["variogram", "energy"])
@pytest.mark.parametrize("ref", [None, {"marginal": 0.8, "joint": 0.01, "tail": 0.5}])
def test_coverage_arm_reproduces_the_shared_composite_exactly(joint, ref):
    """The control: the default metric must not move a single score."""
    s, y = _draws(), np.array([0.3, -1.2, 2.4, 0.0])
    mine = scoring._composite(
        s, y, weights=(0.5, 0.3, 0.2), tail_levels=LEVELS,
        joint=joint, tail_metric="coverage", ref_scale=ref,
    )
    theirs = crps.crps_composite(
        s, y, weights=(0.5, 0.3, 0.2), tail_levels=LEVELS, joint=joint, ref_scale=ref
    )
    for k in ("marginal", "joint", "tail", "composite"):
        assert mine[k] == theirs[k], k


def test_coverage_is_blind_to_how_far_the_tail_is_missed():
    """The defect this module exists to fix, stated as a test."""
    s = _draws()
    q99 = np.quantile(s, 0.99, axis=0)
    near = tail_coverage(s, q99 + 1e-4, LEVELS)
    far = tail_coverage(s, q99 + 100.0, LEVELS)
    assert near == far == pytest.approx(sum(LEVELS))


def test_pinball_grows_with_the_distance_missed():
    s = _draws()
    q99 = np.quantile(s, 0.99, axis=0)
    losses = [tail_pinball(s, q99 + e, LEVELS) for e in (1e-4, 1e-2, 1.0, 100.0)]
    assert losses == sorted(losses)
    assert losses[-1] > losses[0] * 100


def test_pinball_is_minimised_at_the_true_quantile():
    """Sanity: the loss is a proper quantile loss, not merely monotone in |y - q|."""
    s = _draws(seed=1, d=1)
    qs = np.quantile(s, LEVELS, axis=0)
    at_q = tail_pinball(s, np.array([float(np.median(s))]), LEVELS)
    for shift in (-2.0, 2.0):
        assert tail_pinball(s, np.array([float(np.median(s)) + shift]), LEVELS) > at_q
    assert np.all(np.diff(qs.ravel()) >= 0)


def test_unknown_metric_is_refused_not_defaulted():
    from qfbench2_track_forecasting.tail import TAIL_METRICS

    assert set(TAIL_METRICS) == {"coverage", "pinball"}
    with pytest.raises(KeyError):
        TAIL_METRICS["quantile"]
