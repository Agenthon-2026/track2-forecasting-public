"""The official entrypoint end to end, over the frozen `input/ref` + `input/res` topology.

This is the test that proves T2-7's "one canonical package": `score_roster` is what the private
final scorer and the CodaBench scoring image both call, so what it does here is what production
does. It also proves the two fault-domain rules under realistic wiring rather than in isolation:
a broken participant tree yields one failure row and a complete leaderboard, while a broken
reference bundle yields no leaderboard at all.
"""

from __future__ import annotations

import copy
import json
import pathlib
from typing import Any

import pytest
from conftest import build_submission, build_unit, forecast_rows, make_plan
from qfbench2_common.contracts import (
    EvaluationPlan,
    FailureCode,
    OrganizerFault,
    ResultState,
    digest_json,
    sign_payload,
)
from qfbench2_common.contracts.fixtures import DEV_KEY_ID, DEV_SEED, load_fixture

from qfbench2_track_forecasting.official import (
    CONTROL_DIR,
    load_plan,
    score_roster,
    write_public_artifacts,
)

HANDLES = ["u-11112222", "u-33334444", "u-55556666"]


def _run_record(handle: str, plan_digest: str, tree_digest: str) -> dict[str, Any]:
    """A synthetic C2, built from the Hub's own fixture so the shape cannot drift from the contract."""
    record = copy.deepcopy(load_fixture("c2_run_record.json"))
    record["run_id"] = f"run-synthetic-{handle}"
    record["unit_handle"] = handle
    record["attempt_slot_index"] = 0  # C2 always names a slot; C4 nulls it on a per_unit plan
    record["bindings"]["plan_digest"] = plan_digest
    record["bindings"]["sanitized_tree_digest"] = tree_digest
    record["output_row_counts"] = {}
    body = {k: v for k, v in record.items() if k != "attestation"}
    body["attestation"] = {
        "observation_verdict": record["attestation"]["observation_verdict"],
        "reason": record["attestation"]["reason"],
    }
    record["attestation"]["signature"] = sign_payload(
        body, seed=DEV_SEED, key_id=DEV_KEY_ID, signed_at="2026-08-21T09:00:00Z"
    ).to_mapping()
    return record


def build_evaluation(
    root: pathlib.Path,
    *,
    handles: list[str] = HANDLES,
    broken: dict[str, str] | None = None,
) -> tuple[pathlib.Path, pathlib.Path, EvaluationPlan]:
    """Lay out `input/ref` and `input/res` exactly as the frozen topology specifies."""
    broken = broken or {}
    ref_root = root / "input" / "ref"
    res_root = root / "input" / "res"
    ref_root.mkdir(parents=True)
    res_root.mkdir(parents=True)

    plan_body = make_plan(handles)
    (ref_root / "evaluation_plan.json").write_text(json.dumps(plan_body, indent=2), "utf-8")
    plan = EvaluationPlan.from_mapping(plan_body)

    control = res_root / CONTROL_DIR / "run_records"
    control.mkdir(parents=True)
    for index, handle in enumerate(handles):
        unit = build_unit(ref_root / handle, unit_id=f"t2-SYN-{index:04d}")
        fault = broken.get(handle)
        if fault == "no_reference":
            (unit / "reference" / "realized.parquet").unlink()
        elif fault == "no_scale":
            (unit / "reference" / "ref_scale.json").unlink()

        out = res_root / handle
        if fault == "no_output":
            out.mkdir()
        elif fault == "malformed_meta":
            build_submission(out, unit_id=f"t2-SYN-{index:04d}")
            (out / "forecast_meta.json").write_text("{oops", encoding="utf-8")
        elif fault == "duplicate_key":
            rows = forecast_rows()
            rows["asset"][3] = "SYN-A"
            rows["horizon"][3] = 1
            build_submission(out, unit_id=f"t2-SYN-{index:04d}", rows=rows)
        else:
            build_submission(out, unit_id=f"t2-SYN-{index:04d}", centre=1.0 + 0.1 * index)

        (control / f"{handle}.json").write_text(
            json.dumps(
                _run_record(handle, plan.plan_digest, digest_json(f"synthetic:tree:{handle}")),
                indent=2,
            ),
            encoding="utf-8",
        )
    return ref_root, res_root, plan


# --------------------------------------------------------------------------- positive control


def test_positive_control_full_roster_scores(tmp_path: pathlib.Path) -> None:
    ref_root, res_root, plan = build_evaluation(tmp_path)
    result = score_roster(plan, ref_root, res_root)
    assert result.aggregate.n_expected == 3
    assert result.aggregate.n_scored == 3
    assert result.aggregate.n_participant_failure == 0
    assert 0.0 <= result.aggregate.value <= 4.0
    assert {r.unit_handle for r in result.rows} == set(HANDLES)
    assert all(r.state is ResultState.PARTICIPANT_SUCCESS for r in result.rows)


def test_load_plan_round_trips(tmp_path: pathlib.Path) -> None:
    ref_root, _, plan = build_evaluation(tmp_path)
    assert load_plan(ref_root).plan_digest == plan.plan_digest


def test_load_plan_refuses_a_public_commitment(tmp_path: pathlib.Path) -> None:
    ref_root, _, plan = build_evaluation(tmp_path)
    public = plan.public_commitment_mapping()
    public["signature"] = sign_payload(
        public, seed=DEV_SEED, key_id=DEV_KEY_ID, signed_at="2026-08-21T09:00:00Z"
    ).to_mapping()
    (ref_root / "evaluation_plan.json").write_text(json.dumps(public), encoding="utf-8")
    with pytest.raises(OrganizerFault):
        load_plan(ref_root)


def test_load_plan_refuses_an_absent_plan(tmp_path: pathlib.Path) -> None:
    (tmp_path / "ref").mkdir()
    with pytest.raises(OrganizerFault):
        load_plan(tmp_path / "ref")


# --------------------------------------------------------------------------- participant faults


@pytest.mark.parametrize(
    "fault,code",
    [
        ("no_output", FailureCode.NO_OUTPUT),
        ("malformed_meta", FailureCode.MALFORMED_OUTPUT),
        ("duplicate_key", FailureCode.INCOMPLETE_OUTPUT),
    ],
)
def test_one_broken_submission_yields_one_failure_row_and_a_full_leaderboard(
    tmp_path: pathlib.Path, fault: str, code: FailureCode
) -> None:
    ref_root, res_root, plan = build_evaluation(tmp_path, broken={HANDLES[1]: fault})
    result = score_roster(plan, ref_root, res_root)
    assert result.aggregate.n_expected == 3
    assert result.aggregate.n_scored == 2
    assert result.aggregate.n_participant_failure == 1
    failed = next(r for r in result.rows if r.unit_handle == HANDLES[1])
    assert failed.state is ResultState.PARTICIPANT_FAILURE
    assert failed.failure_code is code
    assert failed.score is None


def test_failing_a_unit_does_not_shrink_the_denominator(tmp_path: pathlib.Path) -> None:
    honest_root = tmp_path / "honest"
    honest_root.mkdir()
    ref_a, res_a, plan_a = build_evaluation(honest_root)
    honest = score_roster(plan_a, ref_a, res_a).aggregate

    sabotage_root = tmp_path / "sabotaged"
    sabotage_root.mkdir()
    ref_b, res_b, plan_b = build_evaluation(sabotage_root, broken={HANDLES[2]: "no_output"})
    sabotaged = score_roster(plan_b, ref_b, res_b).aggregate

    assert sabotaged.n_expected == honest.n_expected == 3
    assert sabotaged.value >= honest.value


# --------------------------------------------------------------------------- organizer faults


@pytest.mark.parametrize("fault", ["no_reference", "no_scale"])
def test_a_broken_reference_bundle_publishes_nothing(tmp_path: pathlib.Path, fault: str) -> None:
    ref_root, res_root, plan = build_evaluation(tmp_path, broken={HANDLES[0]: fault})
    with pytest.raises(OrganizerFault):
        score_roster(plan, ref_root, res_root)


def test_an_unexpected_unit_directory_aborts(tmp_path: pathlib.Path) -> None:
    ref_root, res_root, plan = build_evaluation(tmp_path)
    (res_root / "u-99998888").mkdir()
    with pytest.raises(OrganizerFault):
        score_roster(plan, ref_root, res_root)


def test_a_missing_run_record_aborts(tmp_path: pathlib.Path) -> None:
    ref_root, res_root, plan = build_evaluation(tmp_path)
    (res_root / CONTROL_DIR / "run_records" / f"{HANDLES[0]}.json").unlink()
    with pytest.raises(OrganizerFault):
        score_roster(plan, ref_root, res_root)


def test_a_missing_card_aborts(tmp_path: pathlib.Path) -> None:
    ref_root, res_root, plan = build_evaluation(tmp_path)
    (ref_root / HANDLES[0] / "card.toml").unlink()
    with pytest.raises(OrganizerFault):
        score_roster(plan, ref_root, res_root)


# --------------------------------------------------------------------------- public artifacts


def test_public_artifacts_carry_no_free_text(tmp_path: pathlib.Path) -> None:
    ref_root, res_root, plan = build_evaluation(tmp_path, broken={HANDLES[1]: "duplicate_key"})
    result = score_roster(plan, ref_root, res_root)
    scores_path, details_path = write_public_artifacts(result, tmp_path / "public")

    scores = json.loads(scores_path.read_text(encoding="utf-8"))
    assert scores["aggregate"]["denominator"] == "c1_roster"
    assert scores["aggregate"]["n_expected"] == 3
    assert scores["provenance"]["normalization_mode"] == "ref_scale"

    lines = [json.loads(line) for line in details_path.read_text().splitlines()]
    assert len(lines) == 1
    row = lines[0]
    assert row["unit_handle"] == HANDLES[1]
    assert row["detail"]["code"] == FailureCode.INCOMPLETE_OUTPUT.value
    assert all(k == "code" or isinstance(v, int) for k, v in row["detail"].items())
    assert "note" not in row["detail"] and "resolves_after" not in row["detail"]


def test_operator_reasons_are_not_in_the_public_artifacts(tmp_path: pathlib.Path) -> None:
    ref_root, res_root, plan = build_evaluation(tmp_path, broken={HANDLES[1]: "duplicate_key"})
    result = score_roster(plan, ref_root, res_root)
    scores_path, details_path = write_public_artifacts(result, tmp_path / "public")
    blob = scores_path.read_text() + details_path.read_text()
    for reason in result.operator_reasons.values():
        assert reason not in blob


def test_scores_json_never_contains_a_target_date_or_a_realized_value(
    tmp_path: pathlib.Path,
) -> None:
    from conftest import TARGET_DATES

    ref_root, res_root, plan = build_evaluation(tmp_path)
    result = score_roster(plan, ref_root, res_root)
    scores_path, details_path = write_public_artifacts(result, tmp_path / "public")
    blob = scores_path.read_text() + details_path.read_text()
    for date in TARGET_DATES:
        assert date not in blob
    # No per-unit component vector either: a per-unit private diagnostic on a sealed unit.
    assert "marginal" not in blob and "variogram" not in blob
