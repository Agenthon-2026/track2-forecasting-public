"""T2-2: the grid is exact, unique, complete, finite and ordered — proven, not assumed.

Each negative case below is one edit to the positive control in `conftest.forecast_rows`, and each
corresponds to a measured exploit:

* `test_repeating_an_asset_is_refused` — set equality dropped multiplicity; declaring the easy
  asset ten times and the hard one once moved the composite 0.2327 -> 0.1659 with every gate green.
* `test_duplicate_primary_key_is_refused_not_averaged` — `pivot_table`'s default `aggfunc="mean"`
  let a participant steer the averaged column onto the realized value: 74.09 -> 0.11.
* `test_missing_cell_is_refused` / `test_extra_cell_is_refused` — `reindex` dropped extra rows
  silently and caught missing ones only indirectly.
* `test_realized_missing_cell_is_an_organizer_fault` — the private loader filled `np.empty`, so a
  missing cell returned uninitialized memory (measured `9.8e-322`) with no error.
"""

from __future__ import annotations

import pathlib

import pytest
from conftest import ASSETS, HORIZONS, forecast_rows, write_parquet
from qfbench2_common.contracts import FailureCode, OrganizerFault

from qfbench2_track_forecasting.failures import T2Refusal
from qfbench2_track_forecasting.grid import (
    REALIZED_COLUMNS,
    GridSpec,
    build_sample_matrix,
    check_declared_grid,
    flatten_realized,
)
from qfbench2_track_forecasting.limits import DEFAULT_LIMITS, inspect_parquet

SPEC = GridSpec(assets=ASSETS, horizons=HORIZONS)
SMALL_DRAWS = 200


def _matrix(tmp_path: pathlib.Path, rows: dict, n_draws: int = SMALL_DRAWS):
    path = tmp_path / "forecast.parquet"
    write_parquet(path, rows)
    facts = inspect_parquet(path, what="forecast.parquet", limits=DEFAULT_LIMITS)
    return build_sample_matrix(path, facts, SPEC, n_draws, limits=DEFAULT_LIMITS)


# --------------------------------------------------------------------------- positive controls


def test_positive_control_complete_grid_builds(tmp_path: pathlib.Path) -> None:
    """A gate that rejects the legitimate case makes every rejection beside it uninterpretable."""
    matrix = _matrix(tmp_path, forecast_rows())
    assert matrix.shape == (SMALL_DRAWS, SPEC.cell_count)


def test_positive_control_declared_grid_matches(tmp_path: pathlib.Path) -> None:
    meta = {"asset_ids": list(ASSETS), "horizons": list(HORIZONS)}
    check_declared_grid(meta, SPEC)  # must not raise


def test_positive_control_realized_flattens_in_plan_order() -> None:
    import pyarrow as pa

    columns = {
        "asset": pa.array(["SYN-B", "SYN-A", "SYN-B", "SYN-A"]),
        "horizon": pa.array([5, 1, 1, 5]),
        "value": pa.array([4.0, 1.0, 3.0, 2.0]),
    }
    out = flatten_realized(columns, SPEC)
    # Plan order is asset-major, horizon-minor: (A,1) (A,5) (B,1) (B,5).
    assert list(out) == [1.0, 2.0, 3.0, 4.0]


# --------------------------------------------------------------------------- multiplicity


def test_repeating_an_asset_is_refused() -> None:
    meta = {"asset_ids": ["SYN-A", "SYN-A", "SYN-B"], "horizons": list(HORIZONS)}
    with pytest.raises(T2Refusal) as exc:
        check_declared_grid(meta, SPEC)
    assert exc.value.code is FailureCode.SCHEMA_INVALID
    assert exc.value.detail["invalid_row_count"] == 1


def test_repeating_a_horizon_is_refused() -> None:
    meta = {"asset_ids": list(ASSETS), "horizons": [1, 1, 5]}
    with pytest.raises(T2Refusal):
        check_declared_grid(meta, SPEC)


def test_declared_order_must_match_the_plan() -> None:
    """T2-16: the two entrypoints flattened differently, so a legal reorder scored 187x apart."""
    meta = {"asset_ids": ["SYN-B", "SYN-A"], "horizons": list(HORIZONS)}
    with pytest.raises(T2Refusal) as exc:
        check_declared_grid(meta, SPEC)
    assert exc.value.code is FailureCode.SCHEMA_INVALID
    # No asset is missing and none is extra: the refusal is purely about order.
    assert exc.value.detail["missing_count"] == 0
    assert exc.value.detail["extra_count"] == 0


def test_subset_of_the_grid_is_refused() -> None:
    meta = {"asset_ids": ["SYN-A"], "horizons": list(HORIZONS)}
    with pytest.raises(T2Refusal) as exc:
        check_declared_grid(meta, SPEC)
    assert exc.value.detail["missing_count"] == 1


# --------------------------------------------------------------------------- primary key


def test_duplicate_primary_key_is_refused_not_averaged(tmp_path: pathlib.Path) -> None:
    rows = forecast_rows()
    # Claim (draw=0, SYN-A, 1) a second time. Under pivot_table the two values would be averaged.
    for key, extra in (("draw", 0), ("asset", "SYN-A"), ("horizon", 1), ("value", 999.0)):
        rows[key].append(extra)
    with pytest.raises(T2Refusal) as exc:
        _matrix(tmp_path, rows)
    # The row count is now wrong, which the footer catches before anything is allocated.
    assert exc.value.code is FailureCode.INCOMPLETE_OUTPUT
    assert exc.value.detail["observed_count"] == SMALL_DRAWS * SPEC.cell_count + 1


def test_duplicate_key_with_a_compensating_omission_is_still_refused(
    tmp_path: pathlib.Path,
) -> None:
    """The row COUNT can be made right and the coverage still wrong. That is the real exploit.

    A participant who wants a cell averaged does not have to add a row: they can duplicate one key
    and drop another, keeping `num_rows` exactly at `n_draws * cell_count`. `np.bincount` catches
    it because it counts occupancy per cell rather than rows in total.
    """
    rows = forecast_rows()
    # Turn the (draw 0, SYN-B, 5) row into a second (draw 0, SYN-A, 1) row.
    index = 3  # draw 0: (A,1) (A,5) (B,1) (B,5)
    rows["asset"][index] = "SYN-A"
    rows["horizon"][index] = 1
    rows["value"][index] = 999.0
    with pytest.raises(T2Refusal) as exc:
        _matrix(tmp_path, rows)
    assert exc.value.code is FailureCode.INCOMPLETE_OUTPUT
    assert exc.value.detail["invalid_row_count"] == 1  # one cell claimed twice
    assert exc.value.detail["missing_count"] == 1  # one cell absent


def test_extra_cell_outside_the_grid_is_refused(tmp_path: pathlib.Path) -> None:
    rows = forecast_rows()
    rows["asset"][0] = "SYN-Z"
    with pytest.raises(T2Refusal) as exc:
        _matrix(tmp_path, rows)
    assert exc.value.code is FailureCode.SCHEMA_INVALID
    assert exc.value.detail["extra_count"] == 1


def test_extra_horizon_outside_the_grid_is_refused(tmp_path: pathlib.Path) -> None:
    rows = forecast_rows()
    rows["horizon"][1] = 21
    with pytest.raises(T2Refusal) as exc:
        _matrix(tmp_path, rows)
    assert exc.value.detail["extra_count"] == 1


# --------------------------------------------------------------------------- draws


def test_declared_draw_count_must_match_observed(tmp_path: pathlib.Path) -> None:
    rows = forecast_rows(n_draws=SMALL_DRAWS)
    with pytest.raises(T2Refusal) as exc:
        _matrix(tmp_path, rows, n_draws=SMALL_DRAWS + 1)
    assert exc.value.code is FailureCode.INCOMPLETE_OUTPUT


def test_too_few_draws_is_refused(tmp_path: pathlib.Path) -> None:
    rows = forecast_rows(n_draws=3)
    with pytest.raises(T2Refusal) as exc:
        _matrix(tmp_path, rows, n_draws=3)
    assert exc.value.code is FailureCode.SCHEMA_INVALID
    assert exc.value.detail["expected_count"] == DEFAULT_LIMITS.min_draws


def test_too_many_draws_is_refused(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "forecast.parquet"
    write_parquet(path, forecast_rows(n_draws=200))
    facts = inspect_parquet(path, what="forecast.parquet")
    with pytest.raises(T2Refusal):
        build_sample_matrix(path, facts, SPEC, DEFAULT_LIMITS.max_draws + 1, limits=DEFAULT_LIMITS)


def test_non_contiguous_draw_ids_are_refused(tmp_path: pathlib.Path) -> None:
    rows = forecast_rows()
    rows["draw"] = [d + 1 for d in rows["draw"]]  # 1..m instead of 0..m-1
    with pytest.raises(T2Refusal) as exc:
        _matrix(tmp_path, rows)
    assert exc.value.code is FailureCode.SCHEMA_INVALID


# --------------------------------------------------------------------------- finiteness


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_participant_value_is_a_participant_failure(
    tmp_path: pathlib.Path, bad: float
) -> None:
    """Frozen C4: a non-finite value in participant DATA is the participant's failure."""
    rows = forecast_rows()
    rows["value"][0] = bad
    with pytest.raises(T2Refusal) as exc:
        _matrix(tmp_path, rows)
    assert exc.value.code is FailureCode.SCHEMA_INVALID
    assert exc.value.detail["nonfinite_count"] >= 1


def test_null_participant_value_is_a_participant_failure(tmp_path: pathlib.Path) -> None:
    rows = forecast_rows()
    rows["value"][0] = None
    with pytest.raises(T2Refusal) as exc:
        _matrix(tmp_path, rows)
    assert exc.value.detail["invalid_row_count"] >= 1


# --------------------------------------------------------------------------- realized side


def test_realized_missing_cell_is_an_organizer_fault() -> None:
    """`np.empty` returned uninitialized memory here. It must abort the evaluation instead."""
    import pyarrow as pa

    columns = {
        "asset": pa.array(["SYN-A", "SYN-A", "SYN-B"]),
        "horizon": pa.array([1, 5, 1]),
        "value": pa.array([1.0, 2.0, 3.0]),
    }
    with pytest.raises(OrganizerFault):
        flatten_realized(columns, SPEC)


def test_realized_duplicate_cell_is_an_organizer_fault() -> None:
    import pyarrow as pa

    columns = {
        "asset": pa.array(["SYN-A", "SYN-A", "SYN-A", "SYN-A"]),
        "horizon": pa.array([1, 1, 5, 5]),
        "value": pa.array([1.0, 2.0, 3.0, 4.0]),
    }
    with pytest.raises(OrganizerFault):
        flatten_realized(columns, SPEC)


def test_realized_nonfinite_is_an_organizer_fault() -> None:
    """A NaN realized value produced a NaN composite that reached the aggregator. Now it aborts."""
    import pyarrow as pa

    columns = {
        "asset": pa.array(["SYN-A", "SYN-A", "SYN-B", "SYN-B"]),
        "horizon": pa.array([1, 5, 1, 5]),
        "value": pa.array([1.0, float("nan"), 3.0, 4.0]),
    }
    with pytest.raises(OrganizerFault):
        flatten_realized(columns, SPEC)


def test_realized_asset_outside_the_grid_is_an_organizer_fault() -> None:
    import pyarrow as pa

    columns = {
        "asset": pa.array(["SYN-A", "SYN-A", "SYN-B", "SYN-Z"]),
        "horizon": pa.array([1, 5, 1, 5]),
        "value": pa.array([1.0, 2.0, 3.0, 4.0]),
    }
    with pytest.raises(OrganizerFault):
        flatten_realized(columns, SPEC)


# --------------------------------------------------------------------------- GridSpec itself


@pytest.mark.parametrize(
    "assets,horizons",
    [
        ((), (1,)),
        (("SYN-A",), ()),
        (("SYN-A", "SYN-A"), (1,)),
        (("SYN-A",), (1, 1)),
        (("SYN-A",), (0,)),
        (("SYN-A",), (-1,)),
    ],
)
def test_gridspec_construction_is_the_validation(assets: tuple, horizons: tuple) -> None:
    with pytest.raises(ValueError):
        GridSpec(assets=assets, horizons=horizons)


def test_realized_columns_exclude_target_date() -> None:
    """`target_date` is sealed. It must not be in the tuple the scorer selects and can echo."""
    assert "target_date" not in REALIZED_COLUMNS
    assert set(REALIZED_COLUMNS) == {"asset", "horizon", "value"}
