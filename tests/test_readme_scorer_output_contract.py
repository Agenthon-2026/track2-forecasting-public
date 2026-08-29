"""The README's two `scoring.py score` output examples must be what the CLI actually prints.

The sidecar the participant writes and the report the scorer prints are two different documents
with two different identity keys, and the README shows both within forty lines of each other:

* `forecast_meta.json` declares **`unit_id`** -- that is `tests/test_readme_sidecar_contract.py`;
* the scorer's own output declares **`card_id`** -- `scoring.py:569,583` builds both payloads with
  `"card_id": card.get("task", {}).get("id")`, and that is what this file pins.

The distinction is easy to lose. A proposed fix for the sidecar defect renamed the key in *both*
blocks, which would have made the output example wrong in exactly the way the sidecar example had
been. Renaming either one to match the other is a regression whichever direction it goes, so the
tests below read the examples out of the README and compare them against a real CLI run rather
than against a restated expectation.

Two published key sets were wrong before 2026-08-27 and are pinned here so they cannot drift back:

* the gates-only command was illustrated with a **scored** payload, so a participant running the
  documented command saw output that did not match the documentation; and
* that payload advertised `assets_scored` and `horizons_scored`, which the scorer has never
  emitted, while omitting `normalization_mode`, `rankable` and `cell_count`, which it always does.
"""

from __future__ import annotations

import contextlib
import io
import json
import pathlib
import re

import pytest
from conftest import build_submission, build_unit

from qfbench2_track_forecasting.scoring import _main

README = pathlib.Path(__file__).resolve().parent.parent / "README.md"

#: The section holding the two scorer-output examples. The participant-authored sidecar example
#: lives under a different heading and legitimately uses `unit_id`, so anchoring here is what
#: keeps this file off that block.
_HEADING = "### Running the scorer locally"


def _documented_outputs() -> list[dict]:
    """Every ```json block in the 'Running the scorer locally' section, in document order."""
    text = README.read_text(encoding="utf-8")
    assert (
        text.count(_HEADING) == 1
    ), f"expected exactly one {_HEADING!r} section; found {text.count(_HEADING)}"
    section = text.split(_HEADING, 1)[1].split("\n## ", 1)[0]
    blocks = [json.loads(m) for m in re.findall(r"```json\n(.*?)\n```", section, re.DOTALL)]
    assert (
        len(blocks) == 2
    ), f"expected the gates-only and the scored example under {_HEADING!r}; found {len(blocks)}"
    return blocks


def _run(tmp_path: pathlib.Path, *, realized: bool) -> dict:
    """One real `scoring.py score` invocation on a synthetic unit, parsed back from stdout."""
    unit = build_unit(tmp_path / "unit")
    out = build_submission(tmp_path / "out")
    argv = ["score", "--card", str(unit / "card.toml"), "--forecast", str(out / "forecast.parquet")]
    if realized:
        argv += ["--realized", str(unit / "reference" / "realized.parquet")]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        _main(argv)
    return json.loads(buf.getvalue())


@pytest.mark.parametrize("index,realized", [(0, False), (1, True)])
def test_the_documented_output_has_exactly_the_keys_the_cli_emits(
    tmp_path: pathlib.Path, index: int, realized: bool
) -> None:
    documented = set(_documented_outputs()[index])
    emitted = set(_run(tmp_path, realized=realized))
    invented = sorted(documented - emitted)
    omitted = sorted(emitted - documented)
    assert not invented, (
        f"the README's {'scored' if realized else 'gates-only'} example advertises key(s) "
        f"{invented} that `scoring.py score` does not emit"
    )
    assert not omitted, (
        f"the README's {'scored' if realized else 'gates-only'} example omits key(s) {omitted} "
        "that `scoring.py score` always emits"
    )


def test_both_documented_outputs_name_the_unit_with_card_id() -> None:
    """The direction that catches renaming the scorer's output to match the sidecar."""
    for index, block in enumerate(_documented_outputs()):
        assert "card_id" in block, (
            f"scorer-output example #{index} does not declare `card_id`. The scorer emits "
            "`card_id` for its own report; only the participant's forecast_meta.json uses "
            "`unit_id`, and the two are not interchangeable."
        )
        assert "unit_id" not in block, (
            f"scorer-output example #{index} declares `unit_id`. That is the sidecar's key, not "
            "the scorer's -- `scoring.py` emits `card_id` and a reader parsing for `unit_id` "
            "finds nothing."
        )


def test_the_control_a_scorer_run_really_does_key_on_card_id(tmp_path: pathlib.Path) -> None:
    """Control: if the CLI ever stopped emitting `card_id`, the test above would be pinning a
    fiction. Assert the fact from the running scorer, not from the README."""
    emitted = _run(tmp_path, realized=False)
    assert emitted["card_id"] == "t2-SYN-0001"
    assert "unit_id" not in emitted
