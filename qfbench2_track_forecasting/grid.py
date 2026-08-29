"""Exact unique complete Cartesian grids, for the forecast side and the realized side (T2-2).

## Executive summary (read this first)

A Track 2 submission is a matrix over `assets x horizons x draws`. Three separate findings
were all one defect — *nothing ever proved the matrix was that matrix*:

* **Set equality discarded multiplicity.** `scoring.py` compared `{assets}` to `{expected assets}`.
  Declaring the easy asset ten times and the hard one once passed all four gates and moved the
  composite from 0.2327 to 0.1659 on a measured 1σ difficulty gap. Lower is better, so that is a
  29% rank improvement for writing the same number down repeatedly.
* **`pivot_table` silently averaged duplicates.** The pandas default is `aggfunc="mean"`. Appending
  one extra constant-valued row per `(draw, asset, horizon)` let a participant steer the averaged
  column onto the realized value: composite **74.09 -> 0.11**, roughly 650x, every gate green and
  no label emitted. This was the most directly exploitable defect in the pair.
* **The realized side used `np.empty`.** A missing cell in the private loader returned
  *uninitialized memory* (measured: `9.8e-322`) with no error at all.

The fix is one shape, applied on both sides: build the dense array by **index arithmetic with an
exact occupancy count**, never by a pivot and never into an uninitialized buffer. `np.bincount`
over the flattened cell index gives duplicates and omissions in the same pass, so "every cell
exactly once" is a measured fact rather than an assumption.

### Order is part of the contract now, and that is a fix, not a restriction

The pre-freeze `_grid_mismatch` deliberately permitted any declared order, on the reasoning that
the sample matrix and the realized vector both followed the *declared* order and therefore agreed.
They agreed on the CodaBench path. On the private path `load_realized` ordered by
`sorted(df["asset"].unique())` while the samples followed metadata order, so an identical
submission scored **0.1342** on one entrypoint and **25.1128** on the other — 187x, on a
submission that broke no rule. Two entrypoints that disagree about which number faces which
outcome do not have a scoring bug each; they have one missing contract.

`GridSpec` is that contract. It comes from C1, it is ordered, and both entrypoints flatten against
it. A participant who lists assets in a different order than the plan is refused with
`schema_invalid` — a clear, early, deterministic refusal, rather than a silently different score.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray
from qfbench2_common.contracts import FailureCode, RosterEntry

from .failures import T2Refusal, organizer_fault
from .limits import ParquetFacts, ParseLimits, expect_exact_rows, read_parquet_columns

__all__ = [
    "FORECAST_COLUMNS",
    "REALIZED_COLUMNS",
    "GridSpec",
    "build_sample_matrix",
    "check_declared_grid",
    "flatten_realized",
    "grid_from_card",
    "grid_from_plan_entry",
]

#: The exact column set of a draw-format `forecast.parquet`. Exact, not minimal: see
#: `limits.read_parquet_columns` for why an extra column is refused rather than ignored.
FORECAST_COLUMNS: tuple[str, ...] = ("draw", "asset", "horizon", "value")

#: The exact column set the scorer reads from a reference `realized.parquet`. The organizer's file
#: may carry `draw` and `target_date` as well; those are selected out by the reference loader
#: before this tuple is applied, because `target_date` is sealed and must never enter the scoring
#: namespace as a value the scorer can accidentally echo.
REALIZED_COLUMNS: tuple[str, ...] = ("asset", "horizon", "value")


@dataclass(frozen=True, slots=True)
class GridSpec:
    """The ordered `(assets, horizons)` grid a unit is scored on. Immutable, unique, non-empty.

    Construction is the validation: a `GridSpec` that exists is a grid with no duplicate asset, no
    duplicate horizon, at least one of each, and integral positive horizons. Callers therefore
    never have to re-check those properties, which is what stops one call site from checking and
    the next from forgetting.
    """

    assets: tuple[str, ...]
    horizons: tuple[int, ...]

    def __post_init__(self) -> None:
        if not self.assets:
            raise ValueError("a grid must declare at least one asset")
        if not self.horizons:
            raise ValueError("a grid must declare at least one horizon")
        if len(set(self.assets)) != len(self.assets):
            raise ValueError("a grid may not repeat an asset id")
        if len(set(self.horizons)) != len(self.horizons):
            raise ValueError("a grid may not repeat a horizon")
        for horizon in self.horizons:
            if isinstance(horizon, bool) or not isinstance(horizon, int) or horizon < 1:
                raise ValueError("horizons are positive integers, in business days")

    @property
    def cell_count(self) -> int:
        return len(self.assets) * len(self.horizons)

    def cells(self) -> tuple[tuple[str, int], ...]:
        """The canonical flattening: asset-major, horizon-minor, in **declared** order."""
        return tuple((a, h) for a in self.assets for h in self.horizons)

    def as_mapping(self) -> dict[str, Any]:
        """The provenance projection. Asset ids and horizons are participant-supplied task
        material — they are printed on the card the participant already holds — so this is not a
        sealed value. Target dates and realized outcomes are, and neither appears here."""
        return {
            "assets": list(self.assets),
            "horizons": list(self.horizons),
            "cell_count": self.cell_count,
        }


def grid_from_plan_entry(entry: RosterEntry) -> GridSpec:
    """The authoritative grid: C1's per-unit commitment.

    A roster entry with no `grid` is an organizer fault, not a fallback. The Hub's C1 parser
    already requires `grid` on every forecasting entry, so reaching this branch means the caller
    handed us something that is not a forecasting roster entry.
    """
    if entry.grid is None:
        raise organizer_fault(
            "C1 roster entry carries no grid commitment; the forecasting scorer validates the "
            "participant grid against the signed plan, never against a card that also sits "
            "inside the participant mount"
        )
    grid: Mapping[str, Any] = entry.grid
    assets = tuple(str(a) for a in grid["assets"])
    horizons = tuple(int(h) for h in grid["horizons"])
    try:
        spec = GridSpec(assets=assets, horizons=horizons)
    except ValueError as exc:
        raise organizer_fault(f"C1 grid commitment is not a valid grid: {exc}") from exc
    declared = int(grid["cell_count"])
    if declared != spec.cell_count:
        raise organizer_fault(
            f"C1 grid.cell_count={declared} disagrees with {len(assets)}x{len(horizons)}"
        )
    return spec


def grid_from_card(card: Mapping[str, Any]) -> GridSpec:
    """The **unranked** grid source: `card.toml [targets]`.

    Legitimate for a participant smoke run, where no evaluation plan exists and the card is the
    only statement of the task. Never legitimate for a ranked score: the card travels inside the
    participant mount, so a scorer that trusts it is trusting a file the participant can see and,
    on a misconfigured mount, edit. `scoring.resolve_expected_grid` stamps the source so the
    aggregator can refuse a ranked unit that was graded against a card.
    """
    targets = card.get("targets")
    if not isinstance(targets, Mapping):
        raise organizer_fault("card.toml has no [targets] table; the unit declares no grid")
    try:
        assets = tuple(str(a) for a in targets["asset_ids"])
        horizons = tuple(int(h) for h in targets["horizons"])
    except (KeyError, TypeError, ValueError) as exc:
        raise organizer_fault(f"card.toml [targets] grid is unreadable: {exc}") from exc
    try:
        return GridSpec(assets=assets, horizons=horizons)
    except ValueError as exc:
        raise organizer_fault(f"card.toml [targets] is not a valid grid: {exc}") from exc


def _sequence_of(value: Any, *, what: str) -> Sequence[Any]:
    if isinstance(value, str | bytes) or not isinstance(value, Sequence):
        raise T2Refusal(
            FailureCode.SCHEMA_INVALID,
            f"forecast_meta.json {what} must be an array, got {type(value).__name__}",
        )
    # Named rather than returned straight: mypy does not carry the narrowing from a negated
    # isinstance across the `or`, so `value` is still Any here and --strict rejects returning it.
    # This binding is where Any becomes the declared type, which is what the annotation is for.
    sequence: Sequence[Any] = value
    return sequence


def check_declared_grid(meta: Mapping[str, Any], spec: GridSpec) -> None:
    """Refuse unless `forecast_meta.json` declares **exactly** the committed grid, in order.

    Exactly, in order, and with multiplicity — the three properties the pre-freeze set comparison
    dropped. The public detail carries counts only: how many assets were missing, how many were
    unexpected. Which ones is an operator fact, because on a sealed unit the asset list is the
    task, and the participant is being told their declaration does not match, not what it should
    have been.
    """
    if "asset_ids" not in meta or "horizons" not in meta:
        raise T2Refusal(
            FailureCode.SCHEMA_INVALID,
            "forecast_meta.json must declare both asset_ids and horizons",
            missing_count=int("asset_ids" not in meta) + int("horizons" not in meta),
        )
    raw_assets = _sequence_of(meta["asset_ids"], what="asset_ids")
    raw_horizons = _sequence_of(meta["horizons"], what="horizons")

    got_assets = tuple(str(a) for a in raw_assets)
    try:
        got_horizons = tuple(int(h) if not isinstance(h, bool) else -1 for h in raw_horizons)
    except (TypeError, ValueError):
        raise T2Refusal(
            FailureCode.SCHEMA_INVALID,
            "forecast_meta.json horizons must be integers",
            invalid_row_count=len(raw_horizons),
        ) from None

    # Multiplicity first, and explicitly: a repeated entry is the exploit, and reporting it as a
    # generic "grid mismatch" would hide which of the two problems the participant has.
    asset_dupes = len(got_assets) - len(set(got_assets))
    horizon_dupes = len(got_horizons) - len(set(got_horizons))
    if asset_dupes or horizon_dupes:
        raise T2Refusal(
            FailureCode.SCHEMA_INVALID,
            f"forecast_meta.json repeats {asset_dupes} asset id(s) and {horizon_dupes} "
            "horizon(s); a grid axis is a set of distinct labels and repeating one duplicates "
            "an easy cell into the average",
            invalid_row_count=asset_dupes + horizon_dupes,
        )

    if got_assets != spec.assets or got_horizons != spec.horizons:
        missing = len([a for a in spec.assets if a not in got_assets]) + len(
            [h for h in spec.horizons if h not in got_horizons]
        )
        extra = len([a for a in got_assets if a not in spec.assets]) + len(
            [h for h in got_horizons if h not in spec.horizons]
        )
        raise T2Refusal(
            FailureCode.SCHEMA_INVALID,
            "forecast_meta.json declares a different (asset, horizon) grid than the committed "
            "plan. A submission is scored on the plan's full grid, in the plan's order — order is "
            "part of the contract because the realized vector is flattened the same way.",
            missing_count=missing,
            extra_count=extra,
            expected_count=len(spec.assets) + len(spec.horizons),
            observed_count=len(got_assets) + len(got_horizons),
        )


def _codes_for(
    labels: Any, index: Mapping[Any, int], *, axis: str, participant: bool
) -> NDArray[np.int64]:
    """Map a column of labels onto grid positions, refusing any label outside the grid."""
    values = labels.to_pylist() if hasattr(labels, "to_pylist") else list(labels)
    out = np.empty(len(values), dtype=np.int64)
    unknown = 0
    for i, raw in enumerate(values):
        if axis == "horizon":
            key: Any
            if isinstance(raw, bool) or raw is None:
                key = None
            else:
                try:
                    key = int(raw)
                except (TypeError, ValueError):
                    key = None
        else:
            key = None if raw is None else str(raw)
        position = index.get(key)
        if position is None:
            unknown += 1
            out[i] = 0
        else:
            out[i] = position
    if unknown:
        message = (
            f"{unknown} row(s) name an {axis} outside the committed grid; the grid is exact and "
            "an extra row is refused, never dropped"
        )
        if participant:
            raise T2Refusal(
                FailureCode.SCHEMA_INVALID, message, extra_count=unknown, invalid_row_count=unknown
            )
        raise organizer_fault("reference " + message)
    return out


def _finite_values(column: Any, *, participant: bool, what: str) -> NDArray[np.float64]:
    values = column.to_pylist() if hasattr(column, "to_pylist") else list(column)
    out = np.empty(len(values), dtype=np.float64)
    invalid = 0
    for i, raw in enumerate(values):
        if raw is None or isinstance(raw, bool) or not isinstance(raw, int | float):
            invalid += 1
            out[i] = np.nan
            continue
        out[i] = float(raw)
    nonfinite = int(np.count_nonzero(~np.isfinite(out))) - invalid
    if invalid or nonfinite:
        message = (
            f"{what} carries {invalid} non-numeric and {nonfinite} non-finite value(s); NaN and "
            "infinity never reach the metric"
        )
        if participant:
            # Frozen C4: a non-finite value in participant DATA is a participant failure.
            raise T2Refusal(
                FailureCode.SCHEMA_INVALID,
                message,
                invalid_row_count=invalid,
                nonfinite_count=max(nonfinite, 0),
            )
        # ...while a non-finite value in ORGANIZER material aborts the evaluation.
        raise organizer_fault(message)
    return out


def _place_exactly_once(
    flat_index: NDArray[np.int64],
    values: NDArray[np.float64],
    size: int,
    *,
    participant: bool,
    what: str,
) -> NDArray[np.float64]:
    """Scatter `values` into a dense buffer, proving every cell is filled exactly once.

    `np.bincount` counts occupancy per cell in one pass, so a duplicate key and a missing key are
    both detected before any value is written. This is the structural replacement for
    `pivot_table`: there is no aggregation function to default to `mean`, because there is no
    aggregation — a cell claimed twice is a refusal.
    """
    occupancy = np.bincount(flat_index, minlength=size)
    duplicates = int(np.count_nonzero(occupancy > 1))
    missing = int(np.count_nonzero(occupancy == 0))
    if duplicates or missing:
        message = (
            f"{what} does not cover its grid exactly once: {duplicates} cell(s) claimed more than "
            f"once and {missing} cell(s) absent. Duplicate keys are refused, never averaged."
        )
        if participant:
            raise T2Refusal(
                FailureCode.INCOMPLETE_OUTPUT,
                message,
                invalid_row_count=duplicates,
                missing_count=missing,
                expected_count=size,
            )
        raise organizer_fault("reference " + message)
    out = np.zeros(size, dtype=np.float64)
    out[flat_index] = values
    return out


def build_sample_matrix(
    path: Any,
    facts: ParquetFacts,
    spec: GridSpec,
    declared_draws: int,
    *,
    limits: ParseLimits,
) -> NDArray[np.float64]:
    """`forecast.parquet` -> `[m, d]`, proving exact unique complete coverage on the way.

    Order of checks is deliberate and each one is cheaper than the next:

    1. the declared draw count is inside `[min_draws, max_draws]` (metadata only);
    2. the **footer** row count equals `declared_draws x cell_count` exactly (metadata only);
    3. the column set is exactly `FORECAST_COLUMNS` (metadata only);
    4. only then are four columns materialized;
    5. draw ids are exactly `0..m-1`, assets and horizons are inside the grid, values are finite;
    6. every `(draw, asset, horizon)` cell is occupied exactly once.

    Steps 1-3 are the resource bound: a decompression bomb is refused having allocated nothing.
    """
    if declared_draws < limits.min_draws or declared_draws > limits.max_draws:
        raise T2Refusal(
            FailureCode.SCHEMA_INVALID,
            f"forecast_meta.json declares n_draws={declared_draws}; the contract is "
            f"[{limits.min_draws}, {limits.max_draws}]",
            observed_count=max(declared_draws, 0),
            expected_count=limits.min_draws,
        )
    size = declared_draws * spec.cell_count
    expect_exact_rows(facts, size, what="forecast.parquet")
    columns = read_parquet_columns(path, facts, FORECAST_COLUMNS, what="forecast.parquet")

    draws_raw = columns["draw"].to_pylist()
    draw_ids = np.empty(len(draws_raw), dtype=np.int64)
    bad_draw = 0
    for i, raw in enumerate(draws_raw):
        if raw is None or isinstance(raw, bool) or not isinstance(raw, int):
            bad_draw += 1
            draw_ids[i] = -1
            continue
        draw_ids[i] = raw
    lowest = int(draw_ids.min(initial=0))
    highest = int(draw_ids.max(initial=0))
    if bad_draw or lowest < 0 or highest >= declared_draws:
        outside = bad_draw + int(np.count_nonzero((draw_ids < 0) | (draw_ids >= declared_draws)))
        raise T2Refusal(
            FailureCode.SCHEMA_INVALID,
            f"forecast.parquet has {outside} row(s) whose draw id is not an integer in "
            f"[0, {declared_draws}); draw ids are contiguous and zero-based",
            invalid_row_count=outside,
            expected_count=declared_draws,
        )

    asset_index = {a: i for i, a in enumerate(spec.assets)}
    horizon_index = {h: i for i, h in enumerate(spec.horizons)}
    asset_codes = _codes_for(columns["asset"], asset_index, axis="asset", participant=True)
    horizon_codes = _codes_for(columns["horizon"], horizon_index, axis="horizon", participant=True)
    values = _finite_values(columns["value"], participant=True, what="forecast.parquet")

    cell = asset_codes * len(spec.horizons) + horizon_codes
    flat = draw_ids * spec.cell_count + cell
    dense = _place_exactly_once(flat, values, size, participant=True, what="forecast.parquet")
    observed_draws = int(np.unique(draw_ids).size)
    if observed_draws != declared_draws:  # pragma: no cover - implied by exact occupancy
        raise T2Refusal(
            FailureCode.INCOMPLETE_OUTPUT,
            f"forecast.parquet holds {observed_draws} distinct draws but declares {declared_draws}",
            observed_count=observed_draws,
            expected_count=declared_draws,
        )
    return dense.reshape(declared_draws, spec.cell_count)


def flatten_realized(columns: Mapping[str, Any], spec: GridSpec) -> NDArray[np.float64]:
    """Reference `realized.parquet` columns -> the `[d]` outcome vector, in **plan** order.

    Every failure here is an `OrganizerFault`. A reference file that is incomplete, duplicated or
    non-finite is a defect in organizer material, and the frozen C1 policy is to abort the whole
    evaluation rather than charge it to whoever happened to be scored against it. The pre-freeze
    private loader did the opposite twice over: it filled an `np.empty` buffer, so a missing cell
    became uninitialized memory, and it ordered by `sorted(unique(asset))` rather than by the grid.
    """
    asset_index = {a: i for i, a in enumerate(spec.assets)}
    horizon_index = {h: i for i, h in enumerate(spec.horizons)}
    asset_codes = _codes_for(columns["asset"], asset_index, axis="asset", participant=False)
    horizon_codes = _codes_for(columns["horizon"], horizon_index, axis="horizon", participant=False)
    values = _finite_values(columns["value"], participant=False, what="realized.parquet")
    flat = asset_codes * len(spec.horizons) + horizon_codes
    return _place_exactly_once(
        flat, values, spec.cell_count, participant=False, what="realized.parquet"
    )
