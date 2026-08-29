# Forecast rationale — reg-t2-daily

As of **2026-05-29**, joint distribution over SYN_A, SYN_B at horizon(s)
21 business days. 500 draws.

## Anchor

The last observed value of each series at the as-of, taken from the shipped panels
(259 rows of overlapping daily history used for the covariance).

## Adjustments

**None.** This is a driftless random walk: the centre is the anchor, unadjusted. Every
adjustment is zero and is listed as such rather than omitted, so the ledger below sums.

## Scale and shape

Per-asset daily standard deviation of first differences, scaled by sqrt(horizon). Gaussian
shape — deliberately not fat-tailed, since nothing here justifies a tail view.

The draws are **joint**: a single innovation vector is drawn per draw from the empirical
correlation of daily changes across assets, so cross-asset structure is preserved rather than
assembled from independent marginals. The composite's variogram term scores exactly that.

## Adjustment ledger

| asset | anchor | daily sd | sd at horizon | horizon (BD) |
|---|---|---|---|---|
| SYN_A | 92.5807 | 0.5633 | 2.5814 | 21 |
| SYN_B | 4.1378 | 0.0201 | 0.0921 | 21 |

Centre = anchor + 0 for every asset and horizon.

## What the text corpus contributed

**Nothing.** 2 document(s) were present at the text path and none was read. This is the
statistical floor a reasoning agent has to beat, not an example of using text — the whole point
of Track 2 is the gap between this and an agent that reads the corpus. A real submission would
use the documents to move the centre, skew the distribution, or widen the tails, and would say
here which document drove which adjustment and by how much.

## What would change this forecast

Any evidence at all. It currently uses none beyond the panel's own volatility.
