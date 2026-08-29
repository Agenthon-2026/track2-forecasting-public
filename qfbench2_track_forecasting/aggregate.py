"""Fixed-roster aggregation for Track 2 (T2-1), and the provenance that proves which roster.

## Executive summary (read this first)

Track 2 is the only ascending track: **lower is better**. That makes the pre-freeze aggregation
exploitable in the most direct way available. `score.py:162-163` added a unit to the mean only
`if verdict.admissible and verdict.score is not None`, and `final_scorer.py:702-720` filtered NaN
composites and averaged the survivors. Measured: five easy cards at 0.10 plus one hard card at 9.00
mean to 1.5833; making the hard card inadmissible means 0.1000. **A 15x rank improvement for
failing on purpose**, and the hardest card is exactly the one worth failing.

The frozen fix (R-2) has two halves and needs both:

* every expected unit resolves to a C4 state and a failure contributes `W = 4.0` while **staying in
  the denominator**; and
* every real score is **clipped into `[0.0, 4.0]`**.

The clip is not decoration. On an unbounded-above metric a bare penalty is still exploitable: a
participant whose honest composite would be 9.00 improves their mean by failing that unit, because
4.0 is better than 9.0. Clipping caps the honest score at exactly the penalty, so failing is never
*strictly better* than trying — the best a deliberate failure can do is tie. `plan.clip()` and
`plan.failure_score_for()` are the Hub's implementations of both halves and this module calls them
rather than restating the arithmetic.

### What this module adds on top of the Hub's `Aggregate.from_results`

Two Track-2-specific refusals, both of which the generic aggregator cannot make because they are
about *how the number was produced* rather than about the roster:

1. **Mixed normalization is refused.** A raw composite and a `ref_scale`-normalized composite are
   different quantities on different scales; averaging them yields a leaderboard whose ordering
   depends on which units happened to carry a scale file. Today 114 of 226 units have one, so the
   mix is latent rather than live — and it arms the moment the backfill runs.
2. **A card-derived grid cannot be ranked.** `grid_source` must be `"plan"` for every scored row.
   The card travels inside the participant mount; a ranked score graded against it is graded
   against a file on the wrong side of the firewall.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from qfbench2_common.contracts import (
    Aggregate,
    EvaluationPlan,
    FailureCode,
    ResultState,
    UnitResult,
    digest_json,
)

from .failures import T2Refusal, organizer_fault
from .normalization import NormalizationMode

__all__ = [
    "SCORER_INTERFACE_VERSION",
    "ScoredUnit",
    "aggregate_submission",
    "failure_row",
    "success_row",
]

#: The `scorer.interface_version` Track 2 rows carry. Bumped when the ctx contract or the gate
#: order changes, which is what a consumer pinning it actually cares about.
SCORER_INTERFACE_VERSION = "2.0"


@dataclass(frozen=True, slots=True)
class ScoredUnit:
    """One unit's outcome before it becomes a C4 row, with the provenance the aggregate checks."""

    unit_handle: str
    state: ResultState
    score: float | None
    failure_code: FailureCode | None
    detail: Mapping[str, Any]
    normalization_mode: NormalizationMode
    grid_source: str
    components: Mapping[str, float] | None = None


def success_row(
    unit_handle: str,
    verdict_detail: Mapping[str, Any],
) -> ScoredUnit:
    """Build the success row from a `_score` payload, refusing anything that is not rankable here.

    The refusals below are `OrganizerFault` rather than participant failures on purpose: a raw
    composite or a card-derived grid is a *wiring* mistake in how the scorer was invoked, and
    charging it to whoever happened to be scored is the fault-domain confusion global rule 4
    forbids.
    """
    mode = NormalizationMode(verdict_detail["normalization_mode"])
    grid_source = str(verdict_detail["grid_source"])
    return ScoredUnit(
        unit_handle=unit_handle,
        state=ResultState.PARTICIPANT_SUCCESS,
        score=float(verdict_detail["score"]),
        failure_code=None,
        detail={},
        normalization_mode=mode,
        grid_source=grid_source,
        components={
            k: float(verdict_detail[k]) for k in ("marginal", "joint", "tail", "composite")
        },
    )


def failure_row(
    unit_handle: str,
    refusal: T2Refusal,
    *,
    normalization_mode: NormalizationMode,
    grid_source: str,
) -> ScoredUnit:
    """Build the failure row. It carries **no score**: C1 is authoritative for failure treatment.

    A scorer that attached its own number here would be overriding the signed plan, which is the
    one thing R-2 exists to stop. The row carries the code; `plan.failure_score_for(code)` decides
    what it is worth.
    """
    return ScoredUnit(
        unit_handle=unit_handle,
        state=ResultState.PARTICIPANT_FAILURE,
        score=None,
        failure_code=refusal.code,
        detail=dict(refusal.detail),
        normalization_mode=normalization_mode,
        grid_source=grid_source,
    )


def _unit_result(
    plan: EvaluationPlan,
    unit: ScoredUnit,
    *,
    run_record_digest: str,
    sanitized_tree_digest: str,
) -> UnitResult:
    # A success row carries an EMPTY detail. There is nothing bounded and public to say about a
    # unit that scored: the components are provenance, not participant-visible diagnostics, and a
    # per-unit component vector on a sealed unit is a per-unit private diagnostic.
    detail = dict(unit.detail) if unit.state is ResultState.PARTICIPANT_FAILURE else {}
    return UnitResult.from_mapping(
        {
            "schema_version": "1.0.0",
            "unit_handle": unit.unit_handle,
            "attempt_slot_index": None,
            "state": unit.state.value,
            "score": unit.score,
            "failure_code": None if unit.failure_code is None else unit.failure_code.value,
            "detail": detail,
            "plan_digest": plan.plan_digest,
            "run_record_digest": run_record_digest,
            "sanitized_tree_digest": sanitized_tree_digest,
            "scorer": {
                "package": plan.scorer_package,
                "digest": plan.scorer_digest,
                "interface_version": plan.scorer_interface_version,
            },
            "judge": None,
        }
    )


def aggregate_submission(
    plan: EvaluationPlan,
    units: Sequence[ScoredUnit],
    *,
    evidence_digests: Mapping[str, tuple[str, str]],
    organizer_failure_scope: str | None = None,
) -> tuple[Aggregate, tuple[UnitResult, ...], dict[str, Any]]:
    """Aggregate over the **complete** C1 roster and return `(aggregate, rows, provenance)`.

    `evidence_digests` maps `unit_handle -> (run_record_digest, sanitized_tree_digest)`. A unit with
    no evidence entry is an organizer fault: C4 rows carry the digests of the evidence that
    produced them, and a row that cannot name its evidence is unauditable.

    Every refusal here raises `OrganizerFault`, and the frozen C1 policy on an organizer fault is
    `abort_whole_evaluation` — no partial leaderboard.
    """
    plan.require_rankable()
    if plan.track != "forecasting":
        raise organizer_fault(f"this is the forecasting aggregator; the plan is {plan.track!r}")

    normalization = plan.normalization
    if normalization is None or normalization.get("mode") != "ref_scale":
        raise organizer_fault(
            "the forecasting plan does not commit to ref_scale normalization; an unnormalized "
            "mean over units with different natural scales is not a comparable ranking"
        )

    by_handle: dict[str, ScoredUnit] = {}
    for unit in units:
        if unit.unit_handle in by_handle:
            raise organizer_fault(f"duplicate scored row for {unit.unit_handle!r}")
        by_handle[unit.unit_handle] = unit

    expected = plan.expected_handles
    missing = [h for h in expected if h not in by_handle]
    extra = sorted(set(by_handle) - set(expected))
    if missing or extra:
        raise organizer_fault(
            f"the scored set does not cover the C1 roster: {len(missing)} expected unit(s) have "
            f"no row and {len(extra)} row(s) are for units the plan does not commit to. A unit "
            "with no row must never silently leave the denominator."
        )

    bad_mode = sorted(
        h for h in expected if by_handle[h].normalization_mode is not NormalizationMode.REF_SCALE
    )
    if bad_mode:
        raise organizer_fault(
            f"{len(bad_mode)} unit(s) were scored under a normalization mode other than "
            "'ref_scale'. Raw and normalized composites are different quantities; averaging them "
            "produces an ordering that depends on which units happened to ship a scale file."
        )
    bad_grid = sorted(h for h in expected if by_handle[h].grid_source != "plan")
    if bad_grid:
        raise organizer_fault(
            f"{len(bad_grid)} unit(s) were graded against a card-derived grid rather than the "
            "signed C1 commitment. The card travels inside the participant mount; a ranked score "
            "must be bound to the plan."
        )

    rows: list[UnitResult] = []
    for handle in expected:
        evidence = evidence_digests.get(handle)
        if evidence is None:
            raise organizer_fault(
                f"no C2/C3 evidence digests recorded for {handle!r}; a C4 row that cannot name "
                "the evidence behind it is unauditable"
            )
        run_digest, tree_digest = evidence
        rows.append(
            _unit_result(
                plan,
                by_handle[handle],
                run_record_digest=run_digest,
                sanitized_tree_digest=tree_digest,
            )
        )

    aggregate = Aggregate.from_results(plan, rows, organizer_failure_scope=organizer_failure_scope)
    provenance = {
        "denominator": "c1_roster",
        "plan_digest": plan.plan_digest,
        "roster_digest": plan.roster_digest,
        "roster_count": plan.roster_count,
        "metric_direction": plan.metric.direction,
        "domain": [plan.metric.domain_min, plan.metric.domain_max],
        "participant_failure_score": plan.participant_failure.score,
        "clip_real_scores_to_domain": plan.participant_failure.clip_real_scores_to_domain,
        "normalization_mode": NormalizationMode.REF_SCALE.value,
        "ref_scale_commitment": normalization["ref_scale_commitment"],
        "scorer": {
            "package": plan.scorer_package,
            "digest": plan.scorer_digest,
            "interface_version": plan.scorer_interface_version,
        },
        "results_digest": digest_json([r.to_mapping() for r in rows]),
    }
    return aggregate, tuple(rows), provenance
