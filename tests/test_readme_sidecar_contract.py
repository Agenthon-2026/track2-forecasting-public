"""The README's `forecast_meta.json` example must be a sidecar the gates actually accept.

Until 2026-08-27 it was not. The published example declared `card_id`, and every scoring path
reads `unit_id`:

* `forecast.schema.json` lists `unit_id` among its five required keys, and
* `bind_metadata` compares `meta["unit_id"]` against the card's `[task].id`.

A participant who copied the README verbatim therefore shipped a sidecar declaring no unit at
all. Measured against `units/t2-EXAMPLE-ust-curve-1m/card.toml`:

    README as published (card_id)    -> T2Refusal: ... declares unit_id=None but was scored
                                        against 't2-EXAMPLE-ust-curve-1m'
    with unit_id instead             -> ADMISSIBLE

That is 226 of 226 ranked units failing g1 for a correct forecast, so it is not a typo class of
defect -- it is a total DNF for anyone who trusted the documentation.

The tests below read the example out of the README rather than restating it, because a test that
restates the shape it is checking cannot notice the README drifting away from it. The last test
is the control: it feeds the *old* spelling through the same path and requires a refusal, so a
detector that silently stopped discriminating would fail here rather than go quietly green.
"""

from __future__ import annotations

import json
import pathlib
import re

import pytest
from qfbench2_common.taskcard import load_schema

from qfbench2_track_forecasting.cutoff import bind_metadata
from qfbench2_track_forecasting.failures import T2Refusal

README = pathlib.Path(__file__).resolve().parent.parent / "README.md"

#: The heading the participant-authored sidecar example lives under. The scorer's OUTPUT example
#: further down the same file legitimately uses `card_id` -- it is a different document, written
#: by us -- so anchoring on the heading is what keeps this test off the wrong block.
_HEADING = "### Required metadata file: forecast_meta.json"


def _documented_sidecar() -> dict:
    text = README.read_text(encoding="utf-8")
    assert text.count(_HEADING) == 1, (
        f"expected exactly one {_HEADING!r} section; found {text.count(_HEADING)}. This test "
        "anchors on it to avoid reading the scorer-output example instead."
    )
    after = text.split(_HEADING, 1)[1]
    match = re.search(r"```json\n(.*?)\n```", after, re.DOTALL)
    assert match, "no ```json block follows the forecast_meta.json heading"
    return json.loads(match.group(1))


def test_the_documented_sidecar_declares_every_key_the_schema_requires():
    schema = load_schema("forecast.schema.json")
    missing = sorted(set(schema["required"]) - set(_documented_sidecar()))
    assert not missing, (
        f"the README's forecast_meta.json example omits required key(s) {missing}. A participant "
        "copying it fails g1 before any forecast is read."
    )


def test_the_documented_sidecar_invents_no_key_the_schema_does_not_declare():
    """The direction that caught this one: `card_id` was not missing-and-noticed, it was present
    and meaningless."""
    schema = load_schema("forecast.schema.json")
    undeclared = sorted(set(_documented_sidecar()) - set(schema["properties"]))
    assert not undeclared, (
        f"the README documents key(s) {undeclared} that forecast.schema.json does not declare. "
        "The gates ignore them, so the README is telling participants to fill in a field nothing "
        "reads -- which is how `card_id` survived."
    )


def _card_for(meta: dict) -> dict:
    """A trusted card that agrees with the example, so the only thing under test is the sidecar."""
    return {"task": {"id": meta.get("unit_id")}, "forecast": {"asof": meta["asof"]}}


def test_the_documented_sidecar_binds_against_a_card_that_agrees_with_it():
    meta = _documented_sidecar()
    bind_metadata(meta, _card_for(meta), unit_handle="u-readme")


def test_the_old_spelling_still_refuses(monkeypatch):
    """The control. Without it, the three assertions above would all pass on a `bind_metadata`
    that had stopped checking identity at all.

    `T2Refusal` specifically, not any exception: an `OrganizerFault` here would mean the fixture
    fell apart rather than the gate discriminating, and that must not read as a pass."""
    meta = _documented_sidecar()
    card = _card_for(meta)
    broken = {("card_id" if k == "unit_id" else k): v for k, v in meta.items()}
    with pytest.raises(T2Refusal) as excinfo:
        bind_metadata(broken, card, unit_handle="u-readme")
    assert "unit_id" in str(
        excinfo.value
    ), f"expected the refusal to name unit_id; got {excinfo.value!r}"
