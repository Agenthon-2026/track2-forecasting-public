"""T2-3: bounded, fail-closed reading. Nothing sizes its memory to a participant file.

`test_compression_bomb_is_refused_on_the_footer` is the measured case: a 61 KiB
zstd-compressed, dictionary-encoded parquet holding 4,000,000 rows grew peak RSS by 237 MB. The
assertion that matters is not merely that it is refused — it is that the refusal happens against
the **footer**, so the test would still pass on a machine that could not have allocated the file.
"""

from __future__ import annotations

import json
import os
import pathlib

import pytest
from conftest import ASSETS, HORIZONS, forecast_rows, write_parquet
from qfbench2_common.contracts import FailureCode, OrganizerFault

from qfbench2_track_forecasting.failures import T2Refusal
from qfbench2_track_forecasting.grid import GridSpec, build_sample_matrix
from qfbench2_track_forecasting.limits import (
    DEFAULT_LIMITS,
    ParseLimits,
    inspect_parquet,
    rationale_has_content,
    read_json_bounded,
    stat_regular_file,
)

SPEC = GridSpec(assets=ASSETS, horizons=HORIZONS)


def _bomb(path: pathlib.Path, rows: int) -> None:
    """A dictionary-encodable, highly compressible parquet with `rows` rows.

    Constant columns compress to almost nothing and expand to `rows * columns` cells, which is the
    exact shape of the measured amplification.
    """
    write_parquet(
        path,
        {
            "draw": [0] * rows,
            "asset": ["SYN-A"] * rows,
            "horizon": [1] * rows,
            "value": [1.0] * rows,
        },
        compression="zstd",
    )


# --------------------------------------------------------------------------- positive controls


def test_positive_control_legitimate_parquet_passes(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "forecast.parquet"
    write_parquet(path, forecast_rows())
    facts = inspect_parquet(path, what="forecast.parquet")
    assert facts.num_rows == 200 * SPEC.cell_count
    assert facts.num_columns == 4
    assert set(facts.column_names) == {"draw", "asset", "horizon", "value"}


def test_positive_control_small_json_reads(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "meta.json"
    path.write_text(json.dumps({"a": 1}), encoding="utf-8")
    assert read_json_bounded(path, what="meta.json", max_bytes=1024) == {"a": 1}


def test_positive_control_rationale_with_content(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "forecast_rationale.md"
    path.write_text("A sentence.\n", encoding="utf-8")
    assert rationale_has_content(path, limits=DEFAULT_LIMITS) is True


# --------------------------------------------------------------------------- the bomb


def test_compression_bomb_is_refused_on_the_footer(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "forecast.parquet"
    _bomb(path, 4_000_000)
    on_disk = path.stat().st_size
    facts = inspect_parquet(path, what="forecast.parquet")
    # The file passes the generic ceilings — 4,000,000 rows is under max_rows — which is exactly
    # why the generic ceiling is not the defence. The grid does the work.
    assert facts.num_rows == 4_000_000
    with pytest.raises(T2Refusal) as exc:
        build_sample_matrix(path, facts, SPEC, 200, limits=DEFAULT_LIMITS)
    assert exc.value.code is FailureCode.INCOMPLETE_OUTPUT
    assert exc.value.detail["expected_count"] == 200 * SPEC.cell_count
    assert exc.value.detail["observed_count"] == 4_000_000
    # And the whole refusal cost roughly the size of the file on disk, not of its expansion.
    assert on_disk < 4 * 1024 * 1024


def test_row_ceiling_refuses_before_the_grid_is_known(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "forecast.parquet"
    _bomb(path, 4_000_000)
    tight = ParseLimits(max_rows=1_000_000)
    with pytest.raises(T2Refusal) as exc:
        inspect_parquet(path, what="forecast.parquet", limits=tight)
    assert exc.value.code is FailureCode.MALFORMED_OUTPUT
    assert exc.value.detail["expected_count"] == 1_000_000


def test_row_group_ceiling(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "forecast.parquet"
    write_parquet(path, forecast_rows(n_draws=200), row_group_size=8)
    with pytest.raises(T2Refusal) as exc:
        inspect_parquet(path, what="forecast.parquet", limits=ParseLimits(max_row_groups=4))
    assert exc.value.detail["expected_count"] == 4


def test_uncompressed_budget(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "forecast.parquet"
    _bomb(path, 500_000)
    with pytest.raises(T2Refusal) as exc:
        inspect_parquet(
            path, what="forecast.parquet", limits=ParseLimits(max_uncompressed_bytes=1024)
        )
    assert exc.value.detail["expected_count"] == 1024


def test_column_ceiling(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "forecast.parquet"
    write_parquet(path, forecast_rows())
    with pytest.raises(T2Refusal) as exc:
        inspect_parquet(path, what="forecast.parquet", limits=ParseLimits(max_columns=2))
    assert exc.value.code is FailureCode.SCHEMA_INVALID


def test_file_byte_ceiling(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "forecast.parquet"
    write_parquet(path, forecast_rows())
    with pytest.raises(T2Refusal) as exc:
        inspect_parquet(path, what="forecast.parquet", limits=ParseLimits(max_parquet_bytes=16))
    assert exc.value.code is FailureCode.MALFORMED_OUTPUT


# --------------------------------------------------------------------------- malformed


def test_garbage_parquet_is_a_bounded_refusal_not_a_crash(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "forecast.parquet"
    path.write_bytes(b"PAR1" + os.urandom(512))
    with pytest.raises(T2Refusal) as exc:
        inspect_parquet(path, what="forecast.parquet")
    assert exc.value.code is FailureCode.MALFORMED_OUTPUT
    assert exc.value.detail == {"code": "malformed_output"}


def test_empty_file_is_a_bounded_refusal(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "forecast.parquet"
    path.write_bytes(b"")
    with pytest.raises(T2Refusal):
        inspect_parquet(path, what="forecast.parquet")


def test_oversized_json_is_refused_without_reading(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "forecast_meta.json"
    path.write_text(json.dumps({"pad": "x" * 40_000}), encoding="utf-8")
    with pytest.raises(T2Refusal) as exc:
        read_json_bounded(path, what="forecast_meta.json", max_bytes=1024)
    assert exc.value.code is FailureCode.MALFORMED_OUTPUT
    assert exc.value.detail["expected_count"] == 1024


def test_unparseable_json_does_not_echo_the_document(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "forecast_meta.json"
    path.write_text('{"unit_id": "SEALED-SENTINEL-VALUE"', encoding="utf-8")
    with pytest.raises(T2Refusal) as exc:
        read_json_bounded(path, what="forecast_meta.json", max_bytes=4096)
    assert exc.value.code is FailureCode.MALFORMED_OUTPUT
    assert exc.value.detail == {"code": "malformed_output"}
    assert "SEALED-SENTINEL-VALUE" not in json.dumps(exc.value.detail)


def test_json_array_at_top_level_is_refused(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "forecast_meta.json"
    path.write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(T2Refusal) as exc:
        read_json_bounded(path, what="forecast_meta.json", max_bytes=4096)
    assert exc.value.code is FailureCode.SCHEMA_INVALID


def test_invalid_utf8_is_refused(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "forecast_meta.json"
    path.write_bytes(b'{"a": "\xff\xfe"}')
    with pytest.raises(T2Refusal):
        read_json_bounded(path, what="forecast_meta.json", max_bytes=4096)


# --------------------------------------------------------------------------- node types


def test_symlink_is_refused_without_being_followed(tmp_path: pathlib.Path) -> None:
    target = tmp_path / "elsewhere.json"
    target.write_text("{}", encoding="utf-8")
    link = tmp_path / "forecast_meta.json"
    link.symlink_to(target)
    with pytest.raises(T2Refusal) as exc:
        stat_regular_file(link, required=True, what="forecast_meta.json", max_bytes=4096)
    assert exc.value.detail["rejected_node_count"] == 1


def test_fifo_is_refused(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "forecast_meta.json"
    os.mkfifo(path)
    with pytest.raises(T2Refusal) as exc:
        stat_regular_file(path, required=True, what="forecast_meta.json", max_bytes=4096)
    assert exc.value.detail["rejected_node_count"] == 1


def test_hard_link_is_refused(tmp_path: pathlib.Path) -> None:
    target = tmp_path / "elsewhere.json"
    target.write_text("{}", encoding="utf-8")
    link = tmp_path / "forecast_meta.json"
    os.link(target, link)
    with pytest.raises(T2Refusal) as exc:
        stat_regular_file(link, required=True, what="forecast_meta.json", max_bytes=4096)
    assert exc.value.detail["rejected_node_count"] == 1


def test_missing_required_file_is_no_output(tmp_path: pathlib.Path) -> None:
    with pytest.raises(T2Refusal) as exc:
        stat_regular_file(tmp_path / "absent.json", required=True, what="absent.json", max_bytes=16)
    assert exc.value.code is FailureCode.NO_OUTPUT


# --------------------------------------------------------------------------- organizer faults


def test_missing_pyarrow_is_an_organizer_fault(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Never skip a bound because a module is absent (global rule 5)."""
    import builtins

    real_import = builtins.__import__

    def blocked(name: str, *args: object, **kwargs: object):
        if name.startswith("pyarrow"):
            raise ModuleNotFoundError("No module named 'pyarrow'")
        return real_import(name, *args, **kwargs)

    path = tmp_path / "forecast.parquet"
    write_parquet(path, forecast_rows())
    monkeypatch.setattr(builtins, "__import__", blocked)
    with pytest.raises(OrganizerFault):
        inspect_parquet(path, what="forecast.parquet")


def test_limits_reject_an_impossible_draw_range() -> None:
    with pytest.raises(ValueError):
        ParseLimits(min_draws=500, max_draws=100)
