"""T2-7: a rankable unit without a complete positive finite scale is an ORGANIZER failure.

Two faults, both armed and both latent because today's 114 units that have a scale are
exactly the 114 that have an answer:

* a partial scale (`{"tail": 1.0}`) raised an **uncaught `KeyError: 'marginal'`** out of the
  scorer, because `crps_composite` indexes `ref_scale["marginal"]` unconditionally whenever the
  dict is truthy;
* `ctx.setdefault("ref_scale", None)` made a missing scale file a silent fall back to raw
  components, and the driver then averaged raw and normalized composites together.

They go live the moment the backfill runs, because `build_ref_scales.py` is a separate manual step
after `backfill_realized.py` with nothing enforcing the pairing.
"""

from __future__ import annotations

import json
import pathlib

import pytest
from conftest import build_submission, build_unit
from qfbench2_common.contracts import OrganizerFault

from qfbench2_track_forecasting.normalization import (
    REF_SCALE_COMPONENTS,
    NormalizationMode,
    RefScale,
    load_ref_scale,
)


def _write_scale(reference: pathlib.Path, payload: object) -> None:
    reference.mkdir(parents=True, exist_ok=True)
    (reference / "ref_scale.json").write_text(json.dumps(payload), encoding="utf-8")


def test_positive_control_complete_scale_loads(tmp_path: pathlib.Path) -> None:
    reference = tmp_path / "reference"
    _write_scale(reference, {"marginal": 0.5, "joint": 2.0, "tail": 0.25})
    scale = load_ref_scale(reference)
    assert scale.as_mapping() == {"marginal": 0.5, "joint": 2.0, "tail": 0.25}


def test_missing_scale_is_an_organizer_fault_not_a_raw_fallback(tmp_path: pathlib.Path) -> None:
    reference = tmp_path / "reference"
    reference.mkdir()
    with pytest.raises(OrganizerFault) as exc:
        load_ref_scale(reference)
    assert "fallback" in str(exc.value)


@pytest.mark.parametrize("present", ["marginal", "joint", "tail"])
def test_partial_scale_is_refused_rather_than_raising_a_keyerror(
    tmp_path: pathlib.Path, present: str
) -> None:
    reference = tmp_path / "reference"
    _write_scale(reference, {present: 1.0})
    with pytest.raises(OrganizerFault) as exc:
        load_ref_scale(reference)
    assert "missing" in str(exc.value)


@pytest.mark.parametrize("bad", [0.0, -1.0, float("nan"), float("inf")])
def test_nonpositive_or_nonfinite_scale_is_refused(tmp_path: pathlib.Path, bad: float) -> None:
    reference = tmp_path / "reference"
    _write_scale(reference, {"marginal": bad, "joint": 1.0, "tail": 1.0})
    with pytest.raises(OrganizerFault):
        load_ref_scale(reference)


def test_unknown_key_in_the_scale_is_refused(tmp_path: pathlib.Path) -> None:
    reference = tmp_path / "reference"
    _write_scale(reference, {"marginal": 1.0, "joint": 1.0, "tail": 1.0, "energy": 1.0})
    with pytest.raises(OrganizerFault):
        load_ref_scale(reference)


def test_positive_control_the_generator_shape_loads(tmp_path: pathlib.Path) -> None:
    """`build_ref_scales.py` writes `method`, `seed` and `generated` beside the three components.

    All 114 scale files in the private tree carry them. A loader that refused them would reject
    every legitimate unit, and a gate that rejects the legitimate case makes every rejection
    beside it uninterpretable.
    """
    reference = tmp_path / "reference"
    _write_scale(
        reference,
        {
            "marginal": 0.0533,
            "joint": 1.0,
            "tail": 0.12,
            "method": "m0_text_blind_grw",
            "seed": 2140827255,
            "generated": "2026-08-01T00:00:00Z",
        },
    )
    scale = load_ref_scale(reference)
    assert scale.as_mapping() == {"marginal": 0.0533, "joint": 1.0, "tail": 0.12}


def test_non_numeric_scale_value_is_refused(tmp_path: pathlib.Path) -> None:
    reference = tmp_path / "reference"
    _write_scale(reference, {"marginal": "1.0", "joint": 1.0, "tail": 1.0})
    with pytest.raises(OrganizerFault):
        load_ref_scale(reference)


def test_unparseable_scale_is_an_organizer_fault_not_a_participant_failure(
    tmp_path: pathlib.Path,
) -> None:
    reference = tmp_path / "reference"
    reference.mkdir()
    (reference / "ref_scale.json").write_text("{not json", encoding="utf-8")
    with pytest.raises(OrganizerFault):
        load_ref_scale(reference)


def test_the_scale_is_never_loaded_from_the_participant_tree(tmp_path: pathlib.Path) -> None:
    """`ref_scale.json` is answer-equivalent (C6). A participant-reachable copy is refused."""
    from qfbench2_track_forecasting.normalization import assert_reference_only

    reference = tmp_path / "reference"
    reference.mkdir()
    outside = tmp_path / "res" / "u-abcd1234" / "ref_scale.json"
    outside.parent.mkdir(parents=True)
    with pytest.raises(OrganizerFault):
        assert_reference_only(outside, reference)


def test_scoring_refuses_ref_scale_mode_with_no_reference_root(tmp_path: pathlib.Path) -> None:
    from qfbench2_track_forecasting.scoring import hydrate_ctx

    unit = build_unit(tmp_path / "unit")
    out = build_submission(tmp_path / "out")
    import tomllib

    ctx = {
        "card": tomllib.loads((unit / "card.toml").read_text(encoding="utf-8")),
        "output_dir": out,
        "reference_root": None,
        "normalization_mode": NormalizationMode.REF_SCALE,
    }
    with pytest.raises(OrganizerFault):
        hydrate_ctx(ctx)


def test_hydrate_does_not_default_the_scale_to_none_under_ref_scale_mode(
    tmp_path: pathlib.Path,
) -> None:
    """The exact line removed: `ctx.setdefault("ref_scale", None)` after the file lookup."""
    from qfbench2_track_forecasting.scoring import hydrate_ctx

    unit = build_unit(tmp_path / "unit")
    (unit / "reference" / "ref_scale.json").unlink()
    out = build_submission(tmp_path / "out")
    import tomllib

    ctx = {
        "card": tomllib.loads((unit / "card.toml").read_text(encoding="utf-8")),
        "unit_dir": unit,
        "output_dir": out,
        "normalization_mode": NormalizationMode.REF_SCALE,
    }
    with pytest.raises(OrganizerFault):
        hydrate_ctx(ctx)


def test_smoke_path_is_named_unrankable_rather_than_silently_raw(tmp_path: pathlib.Path) -> None:
    from qfbench2_track_forecasting.scoring import hydrate_ctx

    unit = build_unit(tmp_path / "unit", with_reference=False)
    out = build_submission(tmp_path / "out")
    ctx = {"unit_dir": unit, "output_dir": out}
    hydrate_ctx(ctx)
    assert ctx["normalization_mode"] is NormalizationMode.RAW_UNRANKABLE
    assert ctx["grid_source"] == "card"
    assert ctx["ref_scale"] is None


def test_refscale_construction_is_the_validation() -> None:
    assert set(REF_SCALE_COMPONENTS) == {"marginal", "joint", "tail"}
    with pytest.raises(OrganizerFault):
        RefScale(marginal=1.0, joint=0.0, tail=1.0)
