"""Track 2's tail term, and the reason there is a choice of two.

The shipped tail penalty is a COVERAGE statistic:

    P_tail = sum_a |coverage_a - a|,   coverage_a = mean_d 1{y_d <= Q_a}

`1{y <= Q}` records *whether* the realized value cleared a quantile, never *how far*. So a
forecast whose 99th percentile is missed by 0.0001 and one missed by 100 are scored
identically -- measured, both 2.000000, while the marginal CRPS over the same range moves
from 1.68 to 101.67. The term saturates at `sum(levels)` the instant the outermost quantile
is crossed.

Two structural consequences, both measured on the private tree:

* On a **1-cell grid** `coverage_a` can only be 0 or 1, so the whole term takes one of three
  values -- {0.12, 1.02, 2.00} for the default levels -- and its floor is 0.12, never 0. More
  than half the roster is single-cell (40 of 71 validation, 38 of 123 private-test), and the
  single-cell renormalization lifts the tail's live weight from 0.20 to 0.2857 there.
* 79% of the frozen `ref_scale.tail` denominators are already at that floor or that ceiling
  (64 of 115 at 0.12, 26 at 2.0), so the normaliser is itself a degenerate quantity.

The effect lands hardest on F4, whose stated test *is* tail calibration: the term meant to
separate those submissions cannot separate them.

`pinball` replaces the indicator with the quantile (pinball) loss, which is proportional to
the distance by which each quantile is missed:

    L_a(y, q) = (a - 1{y < q}) * (y - q)          >= 0, minimised at the true a-quantile

It carries the target's units, exactly like the marginal CRPS, so it is normalized by
`ref_scale.tail` the same way -- but a ref_scale computed under `coverage` is a *unitless*
number and MUST NOT be reused. Regenerate the scales under the same metric that scores them.

Which metric runs is read from the card's `[scoring.params] tail_metric` and reported in the
verdict detail as `tail_metric`, so a score can always be attributed to the metric that
produced it. The default is `coverage`, i.e. today's behaviour, until the organizers flip it
together with a regenerated set of reference scales.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

import numpy as np
from numpy.typing import NDArray
from qfbench2_common.scoring import crps

#: The metric the cards default to: what the competition scores today.
DEFAULT_TAIL_METRIC = "coverage"


def tail_coverage(
    samples: NDArray[np.float64], y: NDArray[np.float64], levels: Sequence[float]
) -> float:
    """`sum_a |coverage_a - a|` -- the shipped statistic, delegated to the shared toolkit.

    Kept as a named arm so the two metrics are selected the same way, and so this module
    never becomes a second implementation of the one that is live.
    """
    return float(crps.tail_penalty(samples, y, levels=tuple(levels)))


def tail_pinball(
    samples: NDArray[np.float64], y: NDArray[np.float64], levels: Sequence[float]
) -> float:
    """Sum over levels of the mean pinball loss at that level. Lower is better.

    Mean over cells (not sum) so the term does not grow with grid size, matching how
    `crps_marginal` averages its d marginals.
    """
    s = np.asarray(samples, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    total = 0.0
    for a in levels:
        q = np.quantile(s, a, axis=0)  # [d]
        # (a - 1{y < q})(y - q): a*(y-q) above the quantile, (1-a)*(q-y) below it.
        loss = np.where(y >= q, a * (y - q), (1.0 - a) * (q - y))
        total += float(np.mean(loss))
    return total


#: name -> metric. `scoring.py` refuses anything not named here rather than falling back.
TAIL_METRICS: dict[str, Callable[..., float]] = {
    "coverage": tail_coverage,
    "pinball": tail_pinball,
}
