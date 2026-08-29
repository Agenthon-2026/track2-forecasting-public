"""Bounded, fail-closed reading of participant artifacts (T2-3).

## Executive summary (read this first)

Nothing in Track 2 may size its memory to a participant-supplied file. A measured **61 KiB**
zstd-compressed, dictionary-encoded `forecast.parquet` holding 4,000,000 rows grew the scorer's
peak RSS by **237 MB — a 3786x amplification** — and then `pivot_table` collapsed the result to a
`(1, 1)` array. The file was never inspected before it was allocated.

Three rules, and every function here is one of them:

1. **Stat before open.** `stat_regular_file` is a no-follow `lstat`: a symlink, a FIFO, a device, a
   directory or a hard link is refused without ever opening it. The C3 sanitizer should already
   have removed those, so meeting one is *usually* an organizer wiring fault — but this is the
   scorer's own perimeter and it does not assume the perimeter upstream held.
2. **Read the footer before the body.** `inspect_parquet` opens only the Parquet metadata: row
   count, column count, row-group count, and the per-row-group *uncompressed* byte total. Every
   ceiling is enforced against those numbers. `read_parquet_columns` refuses to run at all unless
   it is handed a `ParquetFacts` that already passed.
3. **The tight bound is the grid, not a ceiling.** A generic `max_rows` big enough for a legitimate
   submission (5,000,000) is far too big to stop the measured bomb — 4,000,000 rows sails under it.
   The bound that actually holds is *exact*: a draw-format forecast has exactly
   `n_draws x cell_count` rows, both of which come from the signed plan and the validated metadata,
   so `expect_exact_rows` refuses on the footer before a single value is materialized. The generic
   ceilings remain as a backstop for the case where the exact count is not yet known.

Every refusal is a `T2Refusal` with a frozen public code and integer counts. A **parser exception is
never propagated to a participant**: `pyarrow`'s message quotes file offsets and sometimes file
content, and `json`'s quotes the offending text. Both are captured into the operator-only `reason`.
"""

from __future__ import annotations

import json
import os
import pathlib
import stat
from dataclasses import dataclass
from typing import Any, Final

from qfbench2_common.contracts import FailureCode

from .failures import T2Refusal, organizer_fault

__all__ = [
    "DEFAULT_LIMITS",
    "ParquetFacts",
    "ParseLimits",
    "expect_exact_rows",
    "inspect_parquet",
    "read_json_bounded",
    "read_parquet_columns",
    "rationale_has_content",
    "stat_regular_file",
]


@dataclass(frozen=True, slots=True)
class ParseLimits:
    """The bounds a Track 2 scorer applies to participant bytes. All required; none disableable.

    These are the values Track 2 contributed to C3, and they are repeated here rather than
    read from C3 for one reason: C3 bounds the *tree* the sanitizer produced, and this bounds what
    *this parser* will allocate. They should agree, and a mismatch is worth catching, but a scorer
    that trusts an upstream number it never checked has no perimeter of its own.
    """

    #: `forecast_meta.json`. 256 KiB is ~2000x the largest legitimate sidecar.
    max_meta_bytes: int = 256 * 1024
    #: `forecast_rationale.md`. Never scored; read for exactly one bit (non-emptiness).
    max_rationale_bytes: int = 1 * 1024 * 1024
    #: `forecast.parquet`, on disk.
    max_parquet_bytes: int = 64 * 1024 * 1024
    #: Sum of per-row-group uncompressed sizes from the footer. The decompression budget.
    max_uncompressed_bytes: int = 2 * 1024 * 1024 * 1024
    max_row_groups: int = 64
    max_rows: int = 5_000_000
    max_columns: int = 8
    #: Upper bound on `n_draws`. The CRPS estimator's variance falls as 1/m; beyond this the
    #: marginal statistical gain is nil and the cost is quadratic in the joint term.
    max_draws: int = 20_000
    #: Lower bound on `n_draws`, independent of the JSON Schema. There were three separate routes
    #: past the schema's `minimum: 200` (absent `jsonschema`, `representation: parametric`, and the
    #: scorer comparing against the participant's own declaration), so the floor is also enforced
    #: here, in code that cannot be skipped.
    min_draws: int = 200

    def __post_init__(self) -> None:
        if self.min_draws < 1 or self.max_draws < self.min_draws:
            raise ValueError("draw bounds must satisfy 1 <= min_draws <= max_draws")


DEFAULT_LIMITS: Final[ParseLimits] = ParseLimits()


def stat_regular_file(
    path: pathlib.Path, *, required: bool, what: str, max_bytes: int
) -> os.stat_result:
    """No-follow `lstat` of a file the scorer is about to read. Refuses anything but a plain file.

    `required=False` still refuses a *present* non-regular node; absence is signalled by raising
    the `NO_OUTPUT` refusal only when `required` is true, so the caller can distinguish
    "not supplied" from "supplied as a symlink".
    """
    try:
        st = os.lstat(path)
    except FileNotFoundError:
        if required:
            raise T2Refusal(
                FailureCode.NO_OUTPUT, f"{what} is missing from the submission tree"
            ) from None
        raise
    except OSError as exc:
        raise T2Refusal(
            FailureCode.MALFORMED_OUTPUT, f"{what} could not be stat'd: {exc.strerror}"
        ) from None
    mode = st.st_mode
    if stat.S_ISLNK(mode):
        raise T2Refusal(
            FailureCode.MALFORMED_OUTPUT,
            f"{what} is a symlink; the scorer reads regular files only and never resolves a "
            "participant-controlled link",
            rejected_node_count=1,
        )
    if not stat.S_ISREG(mode):
        raise T2Refusal(
            FailureCode.MALFORMED_OUTPUT,
            f"{what} is not a regular file (type bits 0o{stat.S_IFMT(mode):o})",
            rejected_node_count=1,
        )
    if st.st_nlink > 1:
        raise T2Refusal(
            FailureCode.MALFORMED_OUTPUT,
            f"{what} is a hard link (st_nlink={st.st_nlink}); its bytes may be shared with a file "
            "outside the submission tree",
            rejected_node_count=1,
        )
    if st.st_size > max_bytes:
        raise T2Refusal(
            FailureCode.MALFORMED_OUTPUT,
            f"{what} is {st.st_size} bytes, over the {max_bytes}-byte ceiling",
            observed_count=int(st.st_size),
            expected_count=int(max_bytes),
        )
    return st


def read_json_bounded(
    path: pathlib.Path, *, what: str, max_bytes: int, required: bool = True
) -> dict[str, Any]:
    """Read a JSON object after bounding it, and convert every parse failure into a refusal.

    The parser message is captured into the operator-only `reason`. `json.JSONDecodeError.__str__`
    quotes the offending region of the document — participant-authored bytes — which is exactly
    what must not reach a public artifact.
    """
    stat_regular_file(path, required=required, what=what, max_bytes=max_bytes)
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise T2Refusal(
            FailureCode.MALFORMED_OUTPUT, f"{what} could not be read: {exc.strerror}"
        ) from None
    if len(raw) > max_bytes:  # pragma: no cover - lstat already bounded it; belt and braces
        raise T2Refusal(
            FailureCode.MALFORMED_OUTPUT,
            f"{what} grew past its {max_bytes}-byte ceiling between stat and read",
        )
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise T2Refusal(
            FailureCode.MALFORMED_OUTPUT, f"{what} is not valid UTF-8: {exc.reason}"
        ) from None
    except json.JSONDecodeError as exc:
        raise T2Refusal(
            FailureCode.MALFORMED_OUTPUT, f"{what} is not parseable JSON: {exc.msg}"
        ) from None
    if not isinstance(parsed, dict):
        raise T2Refusal(
            FailureCode.SCHEMA_INVALID,
            f"{what} must hold a JSON object, got {type(parsed).__name__}",
        )
    return parsed


def rationale_has_content(path: pathlib.Path, *, limits: ParseLimits) -> bool:
    """True iff `forecast_rationale.md` holds one non-whitespace character. Reads nothing else.

    The public promise (README, `forecast.schema.json`) is that scoring learns **exactly one bit**
    about this file. Streaming in fixed chunks keeps that promise cheap and keeps the scorer's
    memory independent of the file: splitting cannot change the answer, because whitespace stays
    whitespace across a chunk boundary.
    """
    stat_regular_file(
        path, required=True, what="forecast_rationale.md", max_bytes=limits.max_rationale_bytes
    )
    try:
        with path.open("rb") as fh:
            while chunk := fh.read(65536):
                if chunk.strip():
                    return True
    except OSError as exc:
        raise T2Refusal(
            FailureCode.MALFORMED_OUTPUT,
            f"forecast_rationale.md could not be read: {exc.strerror}",
        ) from None
    return False


@dataclass(frozen=True, slots=True)
class ParquetFacts:
    """What the Parquet **footer** says, before any column is materialized."""

    num_rows: int
    num_columns: int
    num_row_groups: int
    file_bytes: int
    uncompressed_bytes: int
    column_names: tuple[str, ...]


def inspect_parquet(
    path: pathlib.Path, *, what: str, limits: ParseLimits = DEFAULT_LIMITS
) -> ParquetFacts:
    """Read only the Parquet metadata and enforce every generic ceiling against it.

    `pyarrow.parquet.ParquetFile` reads the footer, not the row groups, so this costs one seek and
    a few KiB regardless of how many rows the file claims. Every bound below is checked *here*, so
    `read_parquet_columns` can be a straight materialization with no surprises left in it.

    A missing `pyarrow` is an **organizer fault**, not a participant failure: the production image
    is supposed to ship it, and silently skipping validation because a module is absent is the
    fail-open shape global rule 5 forbids.
    """
    try:
        import pyarrow.parquet as pq
    except ModuleNotFoundError as exc:  # pragma: no cover - production images pin pyarrow
        raise organizer_fault(
            "pyarrow is not importable, so Parquet metadata cannot be inspected before "
            "allocation. Refusing to score behind a bound that did not run."
        ) from exc

    st = stat_regular_file(path, required=True, what=what, max_bytes=limits.max_parquet_bytes)
    try:
        handle = pq.ParquetFile(path)
        meta = handle.metadata
        schema = handle.schema_arrow
    except Exception as exc:  # noqa: BLE001 - pyarrow raises a wide family here
        raise T2Refusal(
            FailureCode.MALFORMED_OUTPUT,
            f"{what} is not a readable Parquet file: {type(exc).__name__}: {exc}",
        ) from None

    num_rows = int(meta.num_rows)
    num_row_groups = int(meta.num_row_groups)
    names = tuple(str(n) for n in schema.names)
    num_columns = len(names)

    if num_row_groups > limits.max_row_groups:
        raise T2Refusal(
            FailureCode.MALFORMED_OUTPUT,
            f"{what} declares {num_row_groups} row groups, over the {limits.max_row_groups} "
            "ceiling",
            observed_count=num_row_groups,
            expected_count=limits.max_row_groups,
        )
    if num_columns > limits.max_columns:
        raise T2Refusal(
            FailureCode.SCHEMA_INVALID,
            f"{what} declares {num_columns} columns, over the {limits.max_columns} ceiling",
            observed_count=num_columns,
            expected_count=limits.max_columns,
        )
    if num_rows < 0 or num_rows > limits.max_rows:
        raise T2Refusal(
            FailureCode.MALFORMED_OUTPUT,
            f"{what} declares {num_rows} rows, over the {limits.max_rows} ceiling",
            observed_count=max(num_rows, 0),
            expected_count=limits.max_rows,
        )
    if len(set(names)) != len(names):
        raise T2Refusal(
            FailureCode.SCHEMA_INVALID,
            f"{what} declares a duplicate column name; the column set must be exact",
            observed_count=num_columns,
            expected_count=len(set(names)),
        )

    uncompressed = 0
    for index in range(num_row_groups):
        try:
            uncompressed += int(meta.row_group(index).total_byte_size)
        except Exception as exc:  # noqa: BLE001 - a corrupt footer row-group entry
            raise T2Refusal(
                FailureCode.MALFORMED_OUTPUT,
                f"{what} has an unreadable row-group footer entry: {type(exc).__name__}: {exc}",
            ) from None
    if uncompressed > limits.max_uncompressed_bytes:
        raise T2Refusal(
            FailureCode.MALFORMED_OUTPUT,
            f"{what} would decompress to {uncompressed} bytes, over the "
            f"{limits.max_uncompressed_bytes}-byte budget",
            observed_count=uncompressed,
            expected_count=limits.max_uncompressed_bytes,
        )

    return ParquetFacts(
        num_rows=num_rows,
        num_columns=num_columns,
        num_row_groups=num_row_groups,
        file_bytes=int(st.st_size),
        uncompressed_bytes=uncompressed,
        column_names=names,
    )


def expect_exact_rows(facts: ParquetFacts, expected_rows: int, *, what: str) -> None:
    """Refuse on the footer when the row count is not exactly the grid's cardinality.

    This is the bound that stops the measured decompression bomb, and it is exact rather than a
    ceiling: a draw-format forecast has precisely `n_draws x cell_count` rows. A file claiming
    4,000,000 rows against a 6-cell, 200-draw grid is refused after reading a footer, having
    allocated nothing.
    """
    if facts.num_rows != expected_rows:
        raise T2Refusal(
            FailureCode.INCOMPLETE_OUTPUT,
            f"{what} declares {facts.num_rows} rows; the committed grid requires exactly "
            f"{expected_rows} (one row per (draw, asset, horizon) cell)",
            observed_count=facts.num_rows,
            expected_count=expected_rows,
        )


def read_parquet_columns(
    path: pathlib.Path,
    facts: ParquetFacts,
    required_columns: tuple[str, ...],
    *,
    what: str,
) -> dict[str, Any]:
    """Materialize exactly `required_columns` from an already-inspected file.

    The column set must be **exactly** `required_columns` — an extra column is refused rather than
    ignored. "Ignore what you do not recognise" is how an answer file renamed into place gets
    accepted: the check that a file is what it claims to be is the column set, and a check that
    tolerates additions is not that check.
    """
    missing = tuple(c for c in required_columns if c not in facts.column_names)
    extra = tuple(c for c in facts.column_names if c not in required_columns)
    if missing or extra:
        raise T2Refusal(
            FailureCode.SCHEMA_INVALID,
            f"{what} column set is {sorted(facts.column_names)}; the contract is exactly "
            f"{sorted(required_columns)}",
            missing_count=len(missing),
            extra_count=len(extra),
        )
    import pyarrow.parquet as pq

    try:
        table = pq.read_table(path, columns=list(required_columns))
    except Exception as exc:  # noqa: BLE001 - pyarrow raises a wide family here
        raise T2Refusal(
            FailureCode.MALFORMED_OUTPUT,
            f"{what} could not be materialized: {type(exc).__name__}: {exc}",
        ) from None
    if table.num_rows != facts.num_rows:
        raise T2Refusal(
            FailureCode.MALFORMED_OUTPUT,
            f"{what} materialized {table.num_rows} rows but its footer declared "
            f"{facts.num_rows}; the file disagrees with itself",
            observed_count=int(table.num_rows),
            expected_count=facts.num_rows,
        )
    return {name: table.column(name) for name in required_columns}
