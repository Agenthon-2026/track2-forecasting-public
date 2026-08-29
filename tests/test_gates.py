"""g0-g3: fail closed, bind to the trusted card, and never abort the batch on participant bytes.

The four findings this file pins:

* `except ModuleNotFoundError: pass` around `jsonschema.validate` — with the import blocked, a
  garbage sidecar that failed g1 with `jsonschema` present **passed**. Because the 200-draw floor
  lived only in the schema, that one `pass` removed the floor.
* `representation: "parametric"` with 3 draws was fully admissible while the same 3 draws under
  `"samples"` were rejected.
* `json.loads` and `read_parquet` were unguarded and the driver called the verifier with no `try`,
  so one malformed sidecar killed the whole submission as an organizer-shaped crash.
* the declared `asof` was never bound to the card's, so a submission could pick its own as-of.
"""

from __future__ import annotations

import builtins
import json
import pathlib
import tomllib
from typing import Any

import pytest
from conftest import (
    ASOF,
    HORIZONS,
    build_submission,
    build_unit,
    forecast_rows,
    make_plan,
)
from qfbench2_common.contracts import EvaluationPlan, FailureCode, OrganizerFault

from qfbench2_track_forecasting.grid import REALIZED_COLUMNS, flatten_realized, grid_from_plan_entry
from qfbench2_track_forecasting.normalization import NormalizationMode
from qfbench2_track_forecasting.scoring import ACCEPTED_REPRESENTATIONS, build_verifier

HANDLE = "u-1a2b3c4d"


def _ctx(unit: pathlib.Path, out: pathlib.Path, **overrides: Any) -> dict[str, Any]:
    plan = EvaluationPlan.from_mapping(make_plan([HANDLE]))
    entry = plan.expected_units[0]
    spec = grid_from_plan_entry(entry)
    import pyarrow.parquet as pq

    table = pq.read_table(unit / "reference" / "realized.parquet", columns=list(REALIZED_COLUMNS))
    realized = flatten_realized({n: table.column(n) for n in REALIZED_COLUMNS}, spec)
    ctx: dict[str, Any] = {
        "card": tomllib.loads((unit / "card.toml").read_text(encoding="utf-8")),
        "unit_dir": unit,
        "reference_root": unit / "reference",
        "output_dir": out,
        "unit_handle": HANDLE,
        "plan_entry": entry,
        "expected_grid": spec,
        "grid_source": "plan",
        "normalization_mode": NormalizationMode.REF_SCALE,
        "realized": realized,
    }
    ctx.update(overrides)
    return ctx


def _run(unit: pathlib.Path, out: pathlib.Path, **overrides: Any):
    ctx = _ctx(unit, out, **overrides)
    return build_verifier(ctx).run(ctx), ctx


# --------------------------------------------------------------------------- positive control


def test_positive_control_a_correct_submission_scores(tmp_path: pathlib.Path) -> None:
    unit = build_unit(tmp_path / "unit")
    out = build_submission(tmp_path / "out")
    verdict, _ = _run(unit, out)
    assert verdict.admissible, verdict.detail
    assert verdict.detail["normalization_mode"] == "ref_scale"
    assert verdict.detail["grid_source"] == "plan"
    assert 0.0 <= verdict.detail["composite"] < 4.0


# --------------------------------------------------------------------------- g0


def test_missing_output_directory_is_no_output(tmp_path: pathlib.Path) -> None:
    unit = build_unit(tmp_path / "unit")
    verdict, _ = _run(unit, tmp_path / "absent")
    assert verdict.detail["code"] == FailureCode.NO_OUTPUT.value


def test_missing_forecast_parquet_is_no_output(tmp_path: pathlib.Path) -> None:
    unit = build_unit(tmp_path / "unit")
    out = build_submission(tmp_path / "out")
    (out / "forecast.parquet").unlink()
    verdict, _ = _run(unit, out)
    assert verdict.detail["code"] == FailureCode.NO_OUTPUT.value


def test_unexpected_file_in_the_submission_tree_is_refused(tmp_path: pathlib.Path) -> None:
    unit = build_unit(tmp_path / "unit")
    out = build_submission(tmp_path / "out")
    (out / "cov.parquet").write_bytes(b"whatever")
    verdict, _ = _run(unit, out)
    assert verdict.detail["code"] == FailureCode.SCHEMA_INVALID.value
    assert verdict.detail["extra_count"] == 1


def test_malformed_sidecar_is_one_participant_failure_not_a_crash(
    tmp_path: pathlib.Path,
) -> None:
    unit = build_unit(tmp_path / "unit")
    out = build_submission(tmp_path / "out")
    (out / "forecast_meta.json").write_text("{not json", encoding="utf-8")
    verdict, _ = _run(unit, out)  # must NOT raise
    assert not verdict.admissible
    assert verdict.detail["code"] == FailureCode.MALFORMED_OUTPUT.value


# --------------------------------------------------------------------------- g1


def test_schema_validation_is_mandatory(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With jsonschema absent, the pre-fix gate PASSED a garbage sidecar. Now it aborts."""
    unit = build_unit(tmp_path / "unit")
    out = build_submission(tmp_path / "out")
    real_import = builtins.__import__

    def blocked(name: str, *args: object, **kwargs: object):
        if name == "jsonschema":
            raise ModuleNotFoundError("No module named 'jsonschema'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked)
    with pytest.raises(OrganizerFault):
        _run(unit, out)


def test_garbage_meta_fails_schema_with_jsonschema_present(tmp_path: pathlib.Path) -> None:
    unit = build_unit(tmp_path / "unit")
    out = build_submission(tmp_path / "out")
    (out / "forecast_meta.json").write_text(json.dumps({"unit_id": 5}), encoding="utf-8")
    verdict, _ = _run(unit, out)
    assert verdict.detail["code"] == FailureCode.SCHEMA_INVALID.value


def test_parametric_representation_is_refused(tmp_path: pathlib.Path) -> None:
    """Advertised by the shared schema, implemented by nothing, and a route past the draw floor."""
    assert "parametric" not in ACCEPTED_REPRESENTATIONS
    unit = build_unit(tmp_path / "unit")
    out = build_submission(tmp_path / "out", representation="parametric")
    verdict, _ = _run(unit, out)
    assert verdict.detail["code"] == FailureCode.SCHEMA_INVALID.value


def test_parametric_with_three_draws_is_refused(tmp_path: pathlib.Path) -> None:
    """The exact measured bypass: `parametric` made `n_draws` optional, so 3 draws were admissible."""
    unit = build_unit(tmp_path / "unit")
    rows = forecast_rows(n_draws=3)
    out = build_submission(
        tmp_path / "out",
        rows=rows,
        representation="parametric",
        meta_overrides={"representation": "parametric", "n_draws": 3},
    )
    verdict, _ = _run(unit, out)
    assert not verdict.admissible


def test_draw_floor_is_enforced_in_code_not_only_in_the_schema(tmp_path: pathlib.Path) -> None:
    unit = build_unit(tmp_path / "unit")
    rows = forecast_rows(n_draws=10)
    out = build_submission(tmp_path / "out", rows=rows, n_draws=10)
    verdict, _ = _run(unit, out)
    assert verdict.detail["code"] == FailureCode.SCHEMA_INVALID.value


def test_missing_rationale_is_refused(tmp_path: pathlib.Path) -> None:
    unit = build_unit(tmp_path / "unit")
    out = build_submission(tmp_path / "out", rationale=None)
    verdict, _ = _run(unit, out)
    assert verdict.detail["code"] == FailureCode.NO_OUTPUT.value


def test_empty_rationale_is_refused(tmp_path: pathlib.Path) -> None:
    unit = build_unit(tmp_path / "unit")
    out = build_submission(tmp_path / "out", rationale="   \n\t\n")
    verdict, _ = _run(unit, out)
    assert verdict.detail["code"] == FailureCode.SCHEMA_INVALID.value


def test_rationale_content_cannot_change_the_score(tmp_path: pathlib.Path) -> None:
    """The published promise is that scoring learns exactly one bit about this file."""
    unit = build_unit(tmp_path / "unit")
    a = build_submission(tmp_path / "a", rationale="short\n")
    b = build_submission(tmp_path / "b", rationale="a much longer and different rationale\n" * 40)
    va, _ = _run(unit, a)
    vb, _ = _run(unit, b)
    assert va.admissible and vb.admissible
    assert va.detail["composite"] == vb.detail["composite"]


# --------------------------------------------------------------------------- g2


def test_declared_asof_must_equal_the_card(tmp_path: pathlib.Path) -> None:
    unit = build_unit(tmp_path / "unit")
    out = build_submission(tmp_path / "out", asof="2020-01-01")
    verdict, _ = _run(unit, out)
    assert verdict.detail["code"] == FailureCode.CUTOFF_VIOLATION.value
    assert verdict.detail["violation_count"] == 1


def test_declared_unit_id_must_equal_the_card(tmp_path: pathlib.Path) -> None:
    unit = build_unit(tmp_path / "unit")
    out = build_submission(tmp_path / "out", unit_id="t2-SYN-9999")
    verdict, _ = _run(unit, out)
    assert verdict.detail["code"] == FailureCode.SCHEMA_INVALID.value


def test_declared_target_must_equal_the_card(tmp_path: pathlib.Path) -> None:
    unit = build_unit(tmp_path / "unit")
    out = build_submission(tmp_path / "out", meta_overrides={"target": "log_return"})
    verdict, _ = _run(unit, out)
    assert verdict.detail["code"] == FailureCode.SCHEMA_INVALID.value


def test_a_card_whose_target_precedes_its_asof_is_an_organizer_fault(
    tmp_path: pathlib.Path,
) -> None:
    from conftest import write_card

    unit = build_unit(tmp_path / "unit")
    write_card(unit, target_dates=["2020-01-01"])  # before the as-of
    out = build_submission(tmp_path / "out")
    with pytest.raises(OrganizerFault):
        _run(unit, out)


def test_no_gate_detail_ever_carries_a_target_date(tmp_path: pathlib.Path) -> None:
    """The pre-freeze g2 returned `{"asof": asof, "targets": targets}` — the sealed dates."""
    unit = build_unit(tmp_path / "unit")
    out = build_submission(tmp_path / "out", asof="2020-01-01")
    verdict, _ = _run(unit, out)
    blob = json.dumps(verdict.detail)
    assert "2020-07-01" not in blob and "2020-07-07" not in blob
    assert "targets" not in verdict.detail and "asof" not in verdict.detail
    assert all(k == "code" or isinstance(v, int) for k, v in verdict.detail.items())


# --------------------------------------------------------------------------- g3


def test_grid_mismatch_is_refused_before_the_parquet_is_read(tmp_path: pathlib.Path) -> None:
    unit = build_unit(tmp_path / "unit")
    out = build_submission(tmp_path / "out")
    (out / "forecast.parquet").write_bytes(b"not a parquet at all")
    # A grid that disagrees is refused at g3's first step, before the unreadable file is opened.
    (out / "forecast_meta.json").write_text(
        json.dumps(
            {
                "unit_id": "t2-SYN-0001",
                "asof": ASOF,
                "representation": "samples",
                "asset_ids": ["SYN-A"],
                "horizons": list(HORIZONS),
                "n_draws": 200,
                "target": "level",
            }
        ),
        encoding="utf-8",
    )
    verdict, _ = _run(unit, out)
    assert verdict.detail["code"] == FailureCode.SCHEMA_INVALID.value
    assert verdict.detail["missing_count"] == 1


def test_gate_order_is_the_published_order() -> None:
    from qfbench2_track_forecasting.scoring import GATES

    assert [name for name, _ in GATES] == [
        "g0_integrity",
        "g1_schema",
        "g2_cutoff_resource",
        "g3_domain_semantics",
    ]
