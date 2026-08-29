"""T2-1: omitting, corrupting or failing a hard card can never improve a lower-is-better result.

## The exact repro

Five easy cards at 0.10 and one hard card at 9.00 mean to **1.5833**. Making the hard card
inadmissible dropped it out of the numerator *and* the denominator, so the mean became **0.1000** —
a 15x improvement for failing on purpose, on the hardest card in the exam.

`test_failing_the_hard_card_cannot_improve_the_mean` is that scenario, and it asserts the property
rather than a number: whatever the honest run scores, the sabotaged run must not score better.

## Why the clip is tested separately and just as hard

A bare penalty is not enough on an unbounded-above metric. With `W = 4.0` and no clipping, a
participant whose honest composite is 9.00 still profits by failing: 4.0 beats 9.0. The clip caps
the honest score at 4.0 too, so the best a deliberate failure can achieve is a tie.
`test_clipping_makes_deliberate_failure_never_strictly_better` sweeps honest scores from 0 to 12
and asserts that at no point does failing win.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

import pytest
from conftest import make_plan
from qfbench2_common.contracts import (
    ContractError,
    EvaluationPlan,
    FailureCode,
    OrganizerFault,
    ParticipantFailure,
    ResultState,
    digest_json,
)

from qfbench2_track_forecasting.aggregate import ScoredUnit, aggregate_submission
from qfbench2_track_forecasting.failures import T2Refusal
from qfbench2_track_forecasting.normalization import NormalizationMode

HANDLES = [f"u-card{i:04d}" for i in range(6)]
EASY, HARD = HANDLES[:5], HANDLES[5]

EVIDENCE = {
    h: (digest_json(f"synthetic:c2:{h}"), digest_json(f"synthetic:c3:{h}")) for h in HANDLES
}


def _plan(**kwargs: object) -> EvaluationPlan:
    return EvaluationPlan.from_mapping(make_plan(HANDLES, **kwargs))


def _success(handle: str, score: float) -> ScoredUnit:
    return ScoredUnit(
        unit_handle=handle,
        state=ResultState.PARTICIPANT_SUCCESS,
        score=score,
        failure_code=None,
        detail={},
        normalization_mode=NormalizationMode.REF_SCALE,
        grid_source="plan",
    )


def _failure(handle: str, code: FailureCode = FailureCode.SCHEMA_INVALID) -> ScoredUnit:
    return ScoredUnit(
        unit_handle=handle,
        state=ResultState.PARTICIPANT_FAILURE,
        score=None,
        failure_code=code,
        detail={"code": code.value},
        normalization_mode=NormalizationMode.REF_SCALE,
        grid_source="plan",
    )


def _mean(plan: EvaluationPlan, units: Sequence[ScoredUnit]) -> float:
    aggregate, _, _ = aggregate_submission(plan, units, evidence_digests=EVIDENCE)
    return aggregate.value


# --------------------------------------------------------------------------- the exploit


def test_positive_control_the_honest_run_aggregates() -> None:
    plan = _plan()
    units = [_success(h, 0.10) for h in EASY] + [_success(HARD, 3.00)]
    aggregate, rows, provenance = aggregate_submission(plan, units, evidence_digests=EVIDENCE)
    assert aggregate.n_expected == 6
    assert aggregate.n_scored == 6
    assert aggregate.n_participant_failure == 0
    assert math.isclose(aggregate.value, (0.10 * 5 + 3.00) / 6)
    assert provenance["denominator"] == "c1_roster"
    assert len(rows) == 6


def test_failing_the_hard_card_cannot_improve_the_mean() -> None:
    plan = _plan()
    honest = _mean(plan, [_success(h, 0.10) for h in EASY] + [_success(HARD, 3.00)])
    sabotaged = _mean(plan, [_success(h, 0.10) for h in EASY] + [_failure(HARD)])
    assert sabotaged >= honest, "failing the hard card improved a lower-is-better score"
    # And the denominator did not move.
    aggregate, _, _ = aggregate_submission(
        plan,
        [_success(h, 0.10) for h in EASY] + [_failure(HARD)],
        evidence_digests=EVIDENCE,
    )
    assert aggregate.n_expected == 6
    assert aggregate.n_scored + aggregate.n_participant_failure == 6


def test_omitting_the_hard_card_entirely_is_an_organizer_fault() -> None:
    """Not a smaller denominator, and not a silently better score: the evaluation refuses."""
    plan = _plan()
    with pytest.raises(OrganizerFault):
        aggregate_submission(plan, [_success(h, 0.10) for h in EASY], evidence_digests=EVIDENCE)


def test_an_extra_row_for_an_uncommitted_unit_is_refused() -> None:
    plan = _plan()
    units = [_success(h, 0.10) for h in EASY] + [
        _success(HARD, 3.0),
        _success("u-notinroster", 0.0),
    ]
    with pytest.raises(OrganizerFault):
        aggregate_submission(plan, units, evidence_digests=EVIDENCE)


def test_a_duplicate_row_is_refused() -> None:
    plan = _plan()
    units = [_success(h, 0.10) for h in EASY] + [_success(HARD, 3.0), _success(HARD, 0.0)]
    with pytest.raises(OrganizerFault):
        aggregate_submission(plan, units, evidence_digests=EVIDENCE)


@pytest.mark.parametrize(
    "code",
    [
        FailureCode.SCHEMA_INVALID,
        FailureCode.MALFORMED_OUTPUT,
        FailureCode.NO_OUTPUT,
        FailureCode.INCOMPLETE_OUTPUT,
        FailureCode.CUTOFF_VIOLATION,
        FailureCode.CONTAMINATION_DETECTED,
        FailureCode.RESOURCE_TIMEOUT,
    ],
)
def test_every_public_failure_code_costs_exactly_w(code: FailureCode) -> None:
    """`by_code` is reserved and empty, so no code is cheaper than any other."""
    plan = _plan()
    units = [_success(h, 0.0) for h in EASY] + [_failure(HARD, code)]
    assert math.isclose(_mean(plan, units), 4.0 / 6)


# --------------------------------------------------------------------------- the clip


@pytest.mark.parametrize("honest", [0.0, 0.5, 3.9, 4.0, 4.1, 6.0, 9.0, 12.0, 1e9])
def test_clipping_makes_deliberate_failure_never_strictly_better(honest: float) -> None:
    plan = _plan()
    trying = _mean(plan, [_success(h, 0.10) for h in EASY] + [_success(HARD, honest)])
    failing = _mean(plan, [_success(h, 0.10) for h in EASY] + [_failure(HARD)])
    assert trying <= failing + 1e-12, (
        f"an honest score of {honest} was punished harder than a deliberate failure; the clip "
        "is what stops that"
    )


def test_a_plan_that_disclaims_clipping_is_not_rankable() -> None:
    plan = EvaluationPlan.from_mapping(make_plan(HANDLES, clip=False))
    assert not plan.is_rankable
    with pytest.raises(ContractError):
        aggregate_submission(
            plan,
            [_success(h, 0.1) for h in EASY] + [_success(HARD, 0.1)],
            evidence_digests=EVIDENCE,
        )


def test_a_score_above_the_domain_is_clipped_not_refused() -> None:
    plan = _plan()
    units = [_success(h, 0.0) for h in EASY] + [_success(HARD, 100.0)]
    assert math.isclose(_mean(plan, units), 4.0 / 6)


def test_a_nonfinite_score_never_reaches_the_aggregate() -> None:
    plan = _plan()
    with pytest.raises(ParticipantFailure):
        aggregate_submission(
            plan,
            [_success(h, 0.0) for h in EASY] + [_success(HARD, float("nan"))],
            evidence_digests=EVIDENCE,
        )


# --------------------------------------------------------------------------- normalization


def test_mixed_normalization_is_refused() -> None:
    plan = _plan()
    units = [_success(h, 0.10) for h in EASY] + [_success(HARD, 3.0)]
    raw = ScoredUnit(
        unit_handle=HARD,
        state=ResultState.PARTICIPANT_SUCCESS,
        score=3.0,
        failure_code=None,
        detail={},
        normalization_mode=NormalizationMode.RAW_UNRANKABLE,
        grid_source="plan",
    )
    units[-1] = raw
    with pytest.raises(OrganizerFault):
        aggregate_submission(plan, units, evidence_digests=EVIDENCE)


def test_a_card_derived_grid_cannot_be_ranked() -> None:
    plan = _plan()
    units = [_success(h, 0.10) for h in EASY] + [_success(HARD, 3.0)]
    units[-1] = ScoredUnit(
        unit_handle=HARD,
        state=ResultState.PARTICIPANT_SUCCESS,
        score=3.0,
        failure_code=None,
        detail={},
        normalization_mode=NormalizationMode.REF_SCALE,
        grid_source="card",
    )
    with pytest.raises(OrganizerFault):
        aggregate_submission(plan, units, evidence_digests=EVIDENCE)


# --------------------------------------------------------------------------- evidence binding


def test_a_row_with_no_evidence_digest_is_refused() -> None:
    plan = _plan()
    units = [_success(h, 0.10) for h in EASY] + [_success(HARD, 3.0)]
    partial = {k: v for k, v in EVIDENCE.items() if k != HARD}
    with pytest.raises(OrganizerFault):
        aggregate_submission(plan, units, evidence_digests=partial)


def test_a_whole_evaluation_organizer_fault_publishes_nothing() -> None:
    plan = _plan()
    units = [_success(h, 0.10) for h in EASY] + [_success(HARD, 3.0)]
    with pytest.raises(OrganizerFault):
        aggregate_submission(
            plan,
            units,
            evidence_digests=EVIDENCE,
            organizer_failure_scope="reference bundle unreadable",
        )


def test_provenance_names_the_roster_and_the_mode() -> None:
    plan = _plan()
    units = [_success(h, 0.10) for h in EASY] + [_success(HARD, 3.0)]
    _, _, provenance = aggregate_submission(plan, units, evidence_digests=EVIDENCE)
    assert provenance["roster_count"] == 6
    assert provenance["roster_digest"] == plan.roster_digest
    assert provenance["plan_digest"] == plan.plan_digest
    assert provenance["normalization_mode"] == "ref_scale"
    assert provenance["participant_failure_score"] == 4.0
    assert provenance["clip_real_scores_to_domain"] is True
    assert provenance["metric_direction"] == "asc"
    assert provenance["domain"] == [0.0, 4.0]


def test_failure_rows_carry_a_code_and_no_score() -> None:
    plan = _plan()
    units = [_success(h, 0.10) for h in EASY] + [_failure(HARD)]
    _, rows, _ = aggregate_submission(plan, units, evidence_digests=EVIDENCE)
    failed = next(r for r in rows if r.unit_handle == HARD)
    assert failed.score is None
    assert failed.failure_code is FailureCode.SCHEMA_INVALID
    assert set(failed.detail) <= {"code"}


def test_failure_row_from_a_refusal_keeps_only_counts() -> None:
    from qfbench2_track_forecasting.aggregate import failure_row

    refusal = T2Refusal(
        FailureCode.INCOMPLETE_OUTPUT,
        "operator-only text naming a sealed date 2024-07-31",
        missing_count=2,
        expected_count=8,
    )
    row = failure_row(
        "u-abcd1234",
        refusal,
        normalization_mode=NormalizationMode.REF_SCALE,
        grid_source="plan",
    )
    assert row.detail == {
        "code": "incomplete_output",
        "missing_count": 2,
        "expected_count": 8,
    }
    assert "2024-07-31" not in str(row.detail)
