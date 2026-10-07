"""`.github/validate_units.py` refuses a card whose [metadata] carries a key outside the card format."""

from __future__ import annotations

import importlib.util
import pathlib
import uuid

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _validator():
    spec = importlib.util.spec_from_file_location(
        "validate_units", ROOT / ".github" / "validate_units.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _unit(root: pathlib.Path, extra: str = "") -> None:
    unit = root / "units" / "t2-SYN-unit"
    unit.mkdir(parents=True)
    (unit / "card.toml").write_text(
        'schema_version = "2.0"\n'
        '[task]\nid = "t2-SYN-unit"\ntrack = "forecasting"\ntitle = "Synthetic"\nsplit = "public-dev"\n'
        f'[metadata]\ncategory = "T2-F4"\n{extra}'
        f'[contamination]\ncanary_guid = "{uuid.uuid4()}"\n'
    )


@pytest.mark.parametrize("key", ["difficulty", "design_note", "Difficulty", "DESIGN_NOTE"])
def test_a_retired_metadata_key_is_refused(tmp_path, monkeypatch, capsys, key):
    _unit(tmp_path, f'{key} = "x"\n')
    monkeypatch.chdir(tmp_path)
    assert _validator().main("forecasting", stdlib_only=True) == 1
    assert f"[metadata].{key} is not part of the card format" in capsys.readouterr().out


def test_a_card_without_them_passes(tmp_path, monkeypatch, capsys):
    _unit(tmp_path)
    monkeypatch.chdir(tmp_path)
    assert _validator().main("forecasting", stdlib_only=True) == 0
    assert "metadata keys" in capsys.readouterr().out
