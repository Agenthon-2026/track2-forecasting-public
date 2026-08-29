"""The one official Track 2 entrypoint, shared by the private final scorer and the scoring image.

## Executive summary (read this first)

T2-7 asks for "one canonical package consumed by private final and the scoring image". This module
is that consumption point: it takes the two roots the frozen worker/scoring topology guarantees and
returns a complete, aggregated, provenance-stamped result.

    input/ref/    organizer, read-only: evaluation_plan.json (signed, expanded), trust_store.json,
                  and one directory per unit holding card.toml plus reference/ (realized.parquet,
                  ref_scale.json)
    input/res/    the ingestion output root: <unit_handle>/ sanitized participant bytes,
                  plus _control/ (run_records/, observations/, logs/)

Three properties make this the *official* path rather than merely a convenient one.

1. **The roster is the plan's, not the filesystem's.** The loop is over `plan.expected_handles`.
   A directory present under `input/res/` that the plan does not commit to is an organizer fault;
   a committed unit with no directory is a participant failure with `no_output`, which still
   occupies its slot in the denominator. Neither can change the denominator, which is A01.
2. **Fault domains are separated at the top of the loop, not at the bottom.** A `T2Refusal` becomes
   one participant-failure row. An `OrganizerFault` propagates out of the whole function and the
   caller publishes nothing — the frozen `abort_whole_evaluation` policy. Before the freeze a
   malformed participant sidecar raised `JSONDecodeError` straight out of g0 and killed the entire
   submission as an organizer-shaped crash.
3. **Every participant-visible byte goes through the Hub redactor.** `details.jsonl` is written by
   `qfbench2_common.failure_labels.report(..., sink="public")`, whose default projection is enum
   code plus integer counts. The operator log is a separate sink at a separate path and the caller
   owns where that path points.
"""

from __future__ import annotations

import json
import pathlib
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray
from qfbench2_common.contracts import (
    Aggregate,
    EvaluationPlan,
    FailureCode,
    OrganizerFault,
    RosterEntry,
    RunRecord,
    UnitResult,
)
from qfbench2_common.failure_labels import report

from .aggregate import ScoredUnit, aggregate_submission, failure_row, success_row
from .failures import T2Refusal, organizer_fault
from .grid import REALIZED_COLUMNS, flatten_realized, grid_from_plan_entry
from .limits import DEFAULT_LIMITS, ParseLimits, inspect_parquet
from .normalization import NormalizationMode, load_ref_scale
from .scoring import build_verifier

__all__ = [
    "CONTROL_DIR",
    "OfficialResult",
    "load_plan",
    "score_roster",
    "write_public_artifacts",
]

#: Underscore-prefixed so it can never collide with a unit handle (frozen topology). A C1 roster
#: containing a handle that begins with `_`, or equal to `ref`/`res`, is an organizer fault, and
#: the Hub's `validate_unit_handle` already refuses one.
CONTROL_DIR = "_control"


@dataclass(frozen=True, slots=True)
class OfficialResult:
    """Everything the caller needs and nothing it must redact itself."""

    aggregate: Aggregate
    rows: tuple[UnitResult, ...]
    provenance: dict[str, Any]
    #: `unit_handle -> operator-only reason`, for the refused units. Never public.
    operator_reasons: Mapping[str, str]


def load_plan(ref_root: pathlib.Path) -> EvaluationPlan:
    """Parse `input/ref/evaluation_plan.json` as an expanded C1. Anything else is an abort.

    Signature verification is the caller's, not this function's: it needs a trust store, and a
    function that returned a plan while silently not verifying it would be worse than one that
    never offered to. `EvaluationPlan.verify_signature(trust_store)` is the supported call and an
    empty trust store fails closed by frozen rule 0.5.
    """
    path = ref_root / "evaluation_plan.json"
    if not path.is_file():
        raise organizer_fault(
            "input/ref/evaluation_plan.json is absent. The roster, the denominator and the "
            "failure treatment all come from the signed plan; there is no defaulted roster."
        )
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise organizer_fault(f"input/ref/evaluation_plan.json is unreadable: {exc}") from None
    plan = EvaluationPlan.from_mapping(raw)
    if plan.is_public_commitment:
        raise organizer_fault(
            "the mounted C1 is the PUBLIC COMMITMENT, which carries no unit identities. The "
            "scorer needs the expanded roster; a public commitment here would score zero units."
        )
    return plan


def _reference_vector(
    reference_root: pathlib.Path, entry: RosterEntry, limits: ParseLimits
) -> NDArray[np.float64]:
    """The realized outcome, flattened in **plan** order. Every failure is an organizer fault."""
    path = reference_root / "realized.parquet"
    if not path.is_file():
        raise organizer_fault(
            "a committed roster unit has no reference/realized.parquet. A roster unit with no "
            "answer aborts the evaluation: it is neither dropped from the denominator nor scored "
            "as a participant failure."
        )
    import pyarrow.parquet as pq

    facts = inspect_parquet(path, what="realized.parquet", limits=limits)
    missing = [c for c in REALIZED_COLUMNS if c not in facts.column_names]
    if missing:
        raise organizer_fault(f"reference/realized.parquet lacks column(s) {missing}")
    table = pq.read_table(path, columns=list(REALIZED_COLUMNS))
    columns = {name: table.column(name) for name in REALIZED_COLUMNS}
    return flatten_realized(columns, grid_from_plan_entry(entry))


def _evidence_digest_pair(control_root: pathlib.Path, handle: str) -> tuple[str, str]:
    """`(run_record_digest, sanitized_tree_digest)` from the signed C2 in `_control/run_records/`.

    C2 is organizer-signed and lives in `_control/` precisely because tampering with it is
    detectable. A missing record is an organizer fault: a C4 row that cannot name its evidence is
    unauditable, and the frozen C4 requires both digests on every row.
    """
    path = control_root / "run_records" / f"{handle}.json"
    if not path.is_file():
        raise organizer_fault(
            f"no C2 run record under {CONTROL_DIR}/run_records for a committed roster unit; the "
            "C4 row would carry no evidence digests"
        )
    try:
        record = RunRecord.from_mapping(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError) as exc:
        raise organizer_fault(f"a C2 run record is unreadable: {exc}") from None
    # `attestation_payload_digest()` is the JCS digest of the record minus `attestation.signature`
    # -- the one field excluded because no structure can contain a digest of itself. It is
    # therefore a stable identifier for the record's whole content, verdict included. C2 does not
    # yet export a name for "the digest OF this record" (contract request T2-CR-3); using the
    # attestation payload digest keeps the C4 row bound to bytes that were actually signed rather
    # than inventing a second construction here.
    return record.attestation_payload_digest(), record.bindings["sanitized_tree_digest"]


def score_roster(
    plan: EvaluationPlan,
    ref_root: pathlib.Path,
    res_root: pathlib.Path,
    *,
    limits: ParseLimits = DEFAULT_LIMITS,
    evidence_digests: Mapping[str, tuple[str, str]] | None = None,
) -> OfficialResult:
    """Score every unit the plan commits to, then aggregate over that exact roster."""
    if plan.track != "forecasting":
        raise organizer_fault(f"this is the forecasting entrypoint; the plan is {plan.track!r}")

    observed = (
        sorted(p.name for p in res_root.iterdir() if p.is_dir() and p.name != CONTROL_DIR)
        if res_root.is_dir()
        else []
    )
    unexpected = sorted(set(observed) - set(plan.expected_handles))
    if unexpected:
        raise organizer_fault(
            f"{len(unexpected)} directory/ies under the ingestion output root are not in the C1 "
            "roster. An unexpected unit means the ingestion stage and the plan disagree about "
            "what was run, and no partial leaderboard is published on that disagreement."
        )

    control_root = res_root / CONTROL_DIR
    digests: dict[str, tuple[str, str]] = dict(evidence_digests or {})
    units: list[ScoredUnit] = []
    reasons: dict[str, str] = {}

    for entry in plan.expected_units:
        handle = entry.unit_handle
        if handle not in digests:
            digests[handle] = _evidence_digest_pair(control_root, handle)

        unit_ref = ref_root / handle
        reference_root = unit_ref / "reference"
        card_path = unit_ref / "card.toml"
        if not card_path.is_file():
            raise organizer_fault(
                "a committed roster unit has no card.toml under input/ref; the reference bundle "
                "is incomplete"
            )
        import tomllib

        card = tomllib.loads(card_path.read_text(encoding="utf-8"))

        # Organizer material is resolved FIRST and outside the participant try/except, so a defect
        # in it can never be recorded as a participant failure.
        ref_scale = load_ref_scale(reference_root, limits=limits)
        realized = _reference_vector(reference_root, entry, limits)
        spec = grid_from_plan_entry(entry)

        output_dir = res_root / handle
        ctx: dict[str, Any] = {
            "card": card,
            "unit_dir": unit_ref,
            "reference_root": reference_root,
            "output_dir": output_dir,
            "unit_handle": handle,
            "plan_entry": entry,
            "expected_grid": spec,
            "grid_source": "plan",
            "normalization_mode": NormalizationMode.REF_SCALE,
            "ref_scale": ref_scale,
            "realized": realized,
            "limits": limits,
        }
        try:
            verdict = build_verifier(ctx).run(ctx)
        except T2Refusal as exc:  # pragma: no cover - gates convert their own refusals
            units.append(
                failure_row(
                    handle,
                    exc,
                    normalization_mode=NormalizationMode.REF_SCALE,
                    grid_source="plan",
                )
            )
            reasons[handle] = exc.reason
            continue

        if verdict.admissible:
            units.append(success_row(handle, verdict.detail))
            continue

        code = _code_from_detail(verdict.detail)
        refusal = T2Refusal(code, "gate refusal", **_counts_from_detail(verdict.detail))
        units.append(
            failure_row(
                handle,
                refusal,
                normalization_mode=NormalizationMode.REF_SCALE,
                grid_source="plan",
            )
        )
        reasons[handle] = f"gates: {[lab.value for lab in verdict.labels]}"

    aggregate, rows, provenance = aggregate_submission(plan, units, evidence_digests=digests)
    return OfficialResult(
        aggregate=aggregate,
        rows=rows,
        provenance=provenance,
        operator_reasons=reasons,
    )


def _code_from_detail(detail: Mapping[str, Any]) -> FailureCode:
    """Recover the public code a gate already put in its (already-redacted) detail."""
    raw = detail.get("code")
    if raw is None:
        # A gate that refused without a code is a defect in this package, not in the submission.
        raise organizer_fault(
            "a Track 2 gate refused a submission without attaching a public failure code; an "
            "uncoded failure is not explainable to the participant"
        )
    return FailureCode(raw)


def _counts_from_detail(detail: Mapping[str, Any]) -> dict[str, int]:
    return {k: int(v) for k, v in detail.items() if k != "code"}


def write_public_artifacts(
    result: OfficialResult, output_dir: pathlib.Path
) -> tuple[pathlib.Path, pathlib.Path]:
    """Write `scores.json` and `details.jsonl` — participant-visible, redacted by the Hub.

    `report(..., sink="public")` is the default and applies `public_detail`, so nothing that
    reaches `details.jsonl` can carry a free-form string. That matters here specifically: the
    pre-freeze private path logged `verdict.detail` — which contained the card's sealed target
    dates — at ERROR and returned it inside `error`.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    scores_path = output_dir / "scores.json"
    details_path = output_dir / "details.jsonl"
    scores_path.write_text(
        json.dumps(
            {
                "score": result.aggregate.value,
                "aggregate": result.aggregate.to_mapping(),
                "provenance": result.provenance,
            },
            indent=2,
            allow_nan=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    # Always (re)create the file, even with no failures. A consumer that has to distinguish
    # "no failures" from "the scorer died before writing" reads an absent file as the first, and
    # that is exactly backwards.
    details_path.write_text("", encoding="utf-8")
    for row in result.rows:
        if row.failure_code is None:
            continue
        report(
            details_path,
            row.unit_handle,
            "forecasting",
            [],
            dict(row.detail),
            sink="public",
        )
    return scores_path, details_path


# Re-exported so a consumer catching organizer aborts does not have to import two packages.
OrganizerAbort = OrganizerFault
