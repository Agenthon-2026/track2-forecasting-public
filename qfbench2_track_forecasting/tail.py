"""Track 2's tail term, and the record of a defect that is now FIXED.

For a period the shipped code did not compute the metric the docs describe. It does now:
`pinball` is the default, none of the 104 shipped cards overrides it, and
`tests/test_tail_metric.py` pins the default to that function. A submission scored today is
scored by the metric `docs/CONCEPTS.md:285` spells out.

The history below is kept rather than deleted, because two things outlive the fix: the
`coverage` arm is still reachable, and a `ref_scale` generated under it is still invalid for
scoring under `pinball` (see the regeneration note at the end). Read it in the past tense.

`docs/CONCEPTS.md:285` tells participants, with the formula spelled out:

    pinball(y, q_hat, tau) =
        tau * (y - q_hat)         if y > q_hat
        (1 - tau) * (q_hat - y)   if y <= q_hat

and `README.md:361` calls the term "Mean pinball loss at the 1st, 5th, 95th, and 99th
percentiles", promising that "a model that misses a rate shock or macro surprise will pay a
massive tail penalty". `docs/CONCEPTS.md:451` repeats it in the results glossary.

The code USED TO compute something else entirely -- a COVERAGE statistic, still reachable
today as the `coverage` arm:

    P_tail = sum_a |coverage_a - a|,   coverage_a = mean_d 1{y_d <= Q_a}

`1{y <= Q}` records *whether* the realized value cleared a quantile, never *how far*. So a
forecast whose 99th percentile is missed by 0.0001 and one missed by 100 are scored
identically -- measured, both 2.000000, while the marginal CRPS over the same range moves
from 1.68 to 101.67. The term saturates at `sum(levels)` the instant the outermost quantile
is crossed.

Two structural consequences OF THE COVERAGE ARM, both measured on the private tree. They
are why it was replaced, and they remain true of it wherever it is still selected:

* On a **1-cell grid** `coverage_a` can only be 0 or 1, so the whole term collapses to one of
  three values for the default levels, with a non-zero floor. A large share of the roster is
  single-cell, and the single-cell renormalization lifts the tail's live weight from 0.20 to
  0.2857 there.
* The frozen `ref_scale.tail` denominators are drawn from that same small value set, so under
  `coverage` the normaliser inherits the degeneracy instead of correcting it.

  (Stated structurally and without the distribution. `ref_scale.tail` is derived from the
  reference forecast's realized outcome, which `normalization.py:33` already documents as
  answer-equivalent, so any description of how those denominators are spread would leak the
  shape of sealed answers across the roster. The argument needs the term's structure, and the
  structure is enough.)

The effect lands hardest on F4, whose stated test *is* tail calibration: the term meant to
separate those submissions cannot separate them.

None of that was what the participant was promised. "A massive tail penalty" is not something
coverage can produce: it is bounded by sum(levels) and reaches that bound the moment the
outermost quantile is crossed at all.

`pinball` is the documented metric, implemented to the documented formula -- proportional to
the distance by which each quantile is missed:

    L_a(y, q) = (a - 1{y < q}) * (y - q)          >= 0, minimised at the true a-quantile

It carries the target's units, exactly like the marginal CRPS, so it is normalized by
`ref_scale.tail` the same way -- but a ref_scale computed under `coverage` is a *unitless*
number and MUST NOT be reused. Regenerate the scales under the same metric that scores them.

Which metric runs is read from the card's `[scoring.params] tail_metric` and reported in the
verdict detail as `tail_metric`, so a score can always be attributed to the metric that
produced it. The default is `pinball`: the documented metric is the one that should need no
card to ask for it. `coverage` stays reachable so a pre-change score can be reproduced.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

import numpy as np
from numpy.typing import NDArray
from qfbench2_common.scoring import crps

#: The metric the cards default to. This is the one `docs/CONCEPTS.md` documents.
DEFAULT_TAIL_METRIC = "pinball"


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
    """Mean pinball loss over the (level, cell) pairs. Lower is better.

    A MEAN over levels, not a sum, because that is what the docs call it: "Mean pinball loss at
    the 1st, 5th, 95th, and 99th percentiles". The two differ by a constant factor of
    `len(levels)` that `ref_scale.tail` divides straight back out, so it changes no ranking --
    but the number a participant reads should be the number the sentence describes.

    Mean over cells too, so the term does not grow with grid size, matching how `crps_marginal`
    averages its d marginals.
    """
    s = np.asarray(samples, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    total = 0.0
    for a in levels:
        q = np.quantile(s, a, axis=0)  # [d]
        # (a - 1{y < q})(y - q): a*(y-q) above the quantile, (1-a)*(q-y) below it.
        loss = np.where(y >= q, a * (y - q), (1.0 - a) * (q - y))
        total += float(np.mean(loss))
    return total / len(tuple(levels))


#: name -> metric. `scoring.py` refuses anything not named here rather than falling back.
TAIL_METRICS: dict[str, Callable[..., float]] = {
    "coverage": tail_coverage,
    "pinball": tail_pinball,
}
