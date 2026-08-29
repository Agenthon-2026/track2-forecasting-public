"""Cutoff binding and corpus/panel look-ahead checks, with no sealed value in any output (T2-6).

## Executive summary (read this first)

Track 2 is an as-of construct: the agent may see everything dated on or before `asof` and nothing
after it. Three separate things enforce that, and each of them was found either partial or
leaky.

1. **Binding.** `forecast_meta.json` declares its own `asof`, `unit_id` and `target`. Before the
   freeze the scorer compared the *declared* `asof` against the card's target dates, so a
   submission could declare any as-of it liked as long as it stayed before the targets.
   `bind_metadata` now requires the declared trio to equal the trusted card's exactly. A
   declaration is a claim; binding is what turns it into a checked fact.

2. **Panels.** `cutoff_ok(asof, targets)` is a string comparison over the card's declared target
   dates. **No staged panel row was ever read.** A panel accidentally published with rows past the
   as-of hands the agent the future in the one file it is guaranteed to open.
   `scan_panel_cutoff` reads the actual rows.

3. **Text.** `_check_text_corpus_cutoff` returned *clean* when `corpus_index.json` was absent, and
   otherwise trusted the index — so a document sitting in `text/` but missing from the index was
   never checked. The check was one-directional in both senses.
   `scan_text_corpus_cutoff` requires the index to exist and to match the directory exactly, in
   both directions.

### Where sealed values are, and are not

The card's `target_dates` are sealed: `asof + horizon` is derivable, but the exact realized target
date is the thing `stage_bundle` redacts out of the participant-facing card. Before the freeze
`_g2_cutoff_resource` returned `{"asof": asof, "targets": targets}` straight into
`GateResult.detail`, mitigated on the CodaBench path by a private allowlist and not mitigated at
all on the private path, where it was logged at ERROR and returned inside `error`.

Nothing in this module puts a date in a participant-visible structure. Refusals carry a frozen
`cutoff_violation` code and integer counts; the dates live only in the operator-only `reason`.
`resolves_after` — the other channel by which a sealed Track 2 date reached a public artifact — is
gone from the Hub allowlist and is not reintroduced here under any name, because the public
projection has no key that accepts a string at all.
"""

from __future__ import annotations

import pathlib
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from qfbench2_common.contracts import FailureCode
from qfbench2_common.leakage import cutoff_ok

from .failures import T2Refusal, organizer_fault
from .limits import DEFAULT_LIMITS, ParseLimits, inspect_parquet, read_json_bounded

__all__ = [
    "ISO_DATE_RE",
    "CorpusVerdict",
    "PanelVerdict",
    "bind_metadata",
    "check_declared_cutoff",
    "scan_panel_cutoff",
    "scan_text_corpus_cutoff",
    "trusted_asof",
]

#: ISO 'YYYY-MM-DD'. Lexical ordering is chronological, which is the whole reason the format is
#: used for cutoffs — but only if the string really is that format, which is what this checks.
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

_CORPUS_INDEX = "corpus_index.json"


def trusted_asof(card: Mapping[str, Any]) -> str:
    """The card's as-of date, from the two places a Track 2 card may state it.

    A card with neither is an organizer fault: the harness would issue `--asof ''` and every
    downstream cutoff comparison would silently pass.
    """
    forecast = card.get("forecast")
    asof = forecast.get("asof") if isinstance(forecast, Mapping) else None
    if not asof:
        provenance = card.get("provenance")
        asof = provenance.get("data_cutoff") if isinstance(provenance, Mapping) else None
    if not isinstance(asof, str) or not ISO_DATE_RE.match(asof):
        raise organizer_fault(
            "the trusted card declares no usable as-of date ([forecast].asof or "
            "[provenance].data_cutoff, ISO YYYY-MM-DD); every cutoff comparison downstream would "
            "pass vacuously"
        )
    return asof


def bind_metadata(meta: Mapping[str, Any], card: Mapping[str, Any], *, unit_handle: str) -> None:
    """Require `forecast_meta.json` to agree with the trusted card on identity, as-of and target.

    `unit_id` is compared against the **card**, not against the opaque C1 handle: the card is what
    the participant was handed and what their tooling copies, and the handle is deliberately
    meaningless. The handle is passed only so the operator reason can name which unit refused.
    """
    asof = trusted_asof(card)
    declared_asof = meta.get("asof")
    if not isinstance(declared_asof, str) or not ISO_DATE_RE.match(declared_asof):
        raise T2Refusal(
            FailureCode.SCHEMA_INVALID,
            "forecast_meta.json must declare asof as an ISO YYYY-MM-DD string",
        )
    if declared_asof != asof:
        raise T2Refusal(
            FailureCode.CUTOFF_VIOLATION,
            f"[{unit_handle}] forecast_meta.json declares asof={declared_asof!r}; the card's "
            f"as-of is {asof!r}. The as-of is a property of the task, not of the submission.",
            violation_count=1,
        )

    task = card.get("task")
    card_unit_id = task.get("id") if isinstance(task, Mapping) else None
    declared_unit = meta.get("unit_id")
    if not isinstance(card_unit_id, str) or not card_unit_id:
        raise organizer_fault("the trusted card declares no [task].id")
    if declared_unit != card_unit_id:
        raise T2Refusal(
            FailureCode.SCHEMA_INVALID,
            f"[{unit_handle}] forecast_meta.json declares unit_id={declared_unit!r} but was "
            f"scored against {card_unit_id!r}; a submission for another unit is not this unit's "
            "submission",
            violation_count=1,
        )

    targets = card.get("targets")
    want_target = targets.get("target_type") if isinstance(targets, Mapping) else None
    if want_target is not None:
        declared_target = meta.get("target")
        if declared_target is not None and declared_target != want_target:
            raise T2Refusal(
                FailureCode.SCHEMA_INVALID,
                f"[{unit_handle}] forecast_meta.json declares target={declared_target!r}; the "
                f"card's target is {want_target!r}. A level forecast scored as a log return is "
                "not a worse forecast, it is a different quantity.",
                violation_count=1,
            )


def check_declared_cutoff(card: Mapping[str, Any], *, unit_handle: str) -> None:
    """Every target date must strictly post-date the as-of. Organizer-side sanity on the card.

    This is the check `leakage.cutoff_ok` performs, run against the **trusted** card rather than
    against a participant declaration. A card whose target lands on or before its own as-of is
    asking the agent to forecast the past; that is a card defect, so it is an organizer fault and
    the dates never leave this function.
    """
    asof = trusted_asof(card)
    targets = card.get("targets")
    dates = targets.get("target_dates") if isinstance(targets, Mapping) else None
    if not dates:
        return  # a prospective card may not have resolved its targets yet; not this gate's job
    if not isinstance(dates, Sequence) or isinstance(dates, str | bytes):
        raise organizer_fault("card [targets].target_dates must be an array of ISO dates")
    for value in dates:
        if not isinstance(value, str) or not ISO_DATE_RE.match(value):
            raise organizer_fault(
                "card [targets].target_dates holds a value that is not an ISO YYYY-MM-DD date; "
                "the cutoff comparison is lexical and would be meaningless"
            )
    if not cutoff_ok(asof, list(dates)):
        raise organizer_fault(
            f"[{unit_handle}] the card's as-of does not strictly precede every target date. "
            "This is a card defect, not a submission defect, and the evaluation aborts rather "
            "than charging it to a participant."
        )


@dataclass(frozen=True, slots=True)
class PanelVerdict:
    """Counts only. `late_rows` is how many rows post-date the as-of; never which, never when."""

    panel_count: int
    scanned_rows: int
    late_rows: int
    late_panels: int


def scan_panel_cutoff(
    panel_root: pathlib.Path,
    asof: str,
    *,
    limits: ParseLimits = DEFAULT_LIMITS,
    date_column: str = "date",
) -> PanelVerdict:
    """Read every staged panel and count rows dated after `asof`. Organizer-side, fail closed.

    Reading the rows is the point: before the freeze the cutoff gate compared two strings out of
    metadata and never opened a panel, so a panel published with post-as-of rows would hand the
    agent the future in the file it is guaranteed to read. This is bounded exactly like a
    participant read — footer first, ceilings enforced — because an organizer file can be large by
    accident just as easily.

    A panel missing its date column, or carrying a malformed date, is a **hard failure**. "Skip
    what you cannot parse" is the fail-open branch found at three separate places in the
    staging scanner.
    """
    if not ISO_DATE_RE.match(asof):
        raise organizer_fault(f"as-of {asof!r} is not an ISO YYYY-MM-DD date")
    if not panel_root.is_dir():
        raise organizer_fault(
            f"the unit declares no readable panel directory at {panel_root.name}/; a forecasting "
            "unit without panels cannot be scored and must not be published"
        )
    import pyarrow.parquet as pq

    panels = sorted(p for p in panel_root.iterdir() if p.suffix == ".parquet")
    if not panels:
        raise organizer_fault(f"{panel_root.name}/ holds no .parquet panel")
    stray = sorted(p.name for p in panel_root.iterdir() if p.suffix != ".parquet")
    if stray:
        raise organizer_fault(
            f"{panel_root.name}/ holds {len(stray)} non-parquet entr(y/ies); the panel directory "
            "is exact, and an unrecognised file there has not been through any content check"
        )

    scanned = late = late_panels = 0
    for panel in panels:
        facts = inspect_parquet(panel, what=f"panel {panel.name}", limits=limits)
        if date_column not in facts.column_names:
            raise organizer_fault(
                f"panel {panel.name} has no {date_column!r} column, so its cutoff cannot be "
                "checked. A panel whose dates cannot be read is refused, never skipped."
            )
        table = pq.read_table(panel, columns=[date_column])
        values = table.column(date_column).to_pylist()
        scanned += len(values)
        panel_late = 0
        for raw in values:
            text = _as_iso_date(raw)
            if text is None:
                raise organizer_fault(
                    f"panel {panel.name} holds a value in {date_column!r} that is not an ISO "
                    "date; the cutoff comparison is lexical and cannot be applied to it"
                )
            if text > asof:
                panel_late += 1
        if panel_late:
            late += panel_late
            late_panels += 1
    if late:
        raise organizer_fault(
            f"{late} panel row(s) across {late_panels} panel(s) post-date the unit's as-of. The "
            "staged panels hand the agent data from after the cutoff, which invalidates the unit."
        )
    return PanelVerdict(panel_count=len(panels), scanned_rows=scanned, late_rows=0, late_panels=0)


def _as_iso_date(raw: Any) -> str | None:
    """Normalize a parquet date cell to 'YYYY-MM-DD', or None if it is not a date at all."""
    if raw is None:
        return None
    if hasattr(raw, "isoformat"):
        text = raw.isoformat()[:10]
    elif isinstance(raw, str):
        text = raw[:10]
    else:
        return None
    return text if ISO_DATE_RE.match(text) else None


@dataclass(frozen=True, slots=True)
class CorpusVerdict:
    """Counts only. Document ids and timestamps are organizer material and stay out of it."""

    indexed_documents: int
    files_on_disk: int


def scan_text_corpus_cutoff(
    corpus_root: pathlib.Path, asof: str, *, limits: ParseLimits = DEFAULT_LIMITS
) -> CorpusVerdict:
    """Require an index, require it to match the directory **both ways**, require every date.

    Three failures, each of which was found open:

    * a missing `corpus_index.json` returned clean — now it is a hard failure, because an
      unindexed corpus has had no cutoff check at all and "we could not check" is not "clean";
    * a document present on disk but absent from the index was never examined — the coverage check
      is now bidirectional, so an unindexed file is refused;
    * a document with a missing or malformed timestamp produced a violation string rather than a
      refusal, and the string named the document.

    Organizer-side throughout: the corpus is material the organizers publish, so a post-as-of
    document is an organizer fault that aborts, not a participant failure.
    """
    if not ISO_DATE_RE.match(asof):
        raise organizer_fault(f"as-of {asof!r} is not an ISO YYYY-MM-DD date")
    if not corpus_root.is_dir():
        raise organizer_fault(
            "the unit declares a text corpus that is not a readable directory; the corpus is an "
            "input to the agent and an unreadable one cannot be cleared"
        )
    index_path = corpus_root / _CORPUS_INDEX
    if not index_path.is_file():
        raise organizer_fault(
            f"the text corpus has no {_CORPUS_INDEX}. Returning 'clean' for an unindexed corpus "
            "reports the absence of a check as the absence of a problem."
        )
    index = read_json_bounded(index_path, what=_CORPUS_INDEX, max_bytes=limits.max_meta_bytes)
    documents = index.get("documents")
    if not isinstance(documents, list) or not documents:
        raise organizer_fault(f"{_CORPUS_INDEX} must carry a non-empty 'documents' array")

    on_disk = {
        p.relative_to(corpus_root).as_posix()
        for p in sorted(corpus_root.rglob("*"))
        if p.is_file() and p.name != _CORPUS_INDEX
    }
    indexed: set[str] = set()
    late = 0
    undated = 0
    for entry in documents:
        if not isinstance(entry, Mapping):
            raise organizer_fault(f"{_CORPUS_INDEX}.documents holds a non-object entry")
        path = entry.get("path") or entry.get("file")
        doc_id = entry.get("doc_id")
        if not isinstance(doc_id, str) or not doc_id:
            raise organizer_fault(f"{_CORPUS_INDEX} holds a document with no doc_id")
        if isinstance(path, str) and path:
            indexed.add(path.lstrip("./"))
        timestamp = entry.get("timestamp")
        if not isinstance(timestamp, str) or not ISO_DATE_RE.match(timestamp[:10]):
            undated += 1
            continue
        if timestamp[:10] > asof:
            late += 1
    if undated:
        raise organizer_fault(
            f"{undated} corpus document(s) carry no usable ISO timestamp, so their cutoff cannot "
            "be established. An undated document is refused, not assumed to be in range."
        )
    if late:
        raise organizer_fault(
            f"{late} corpus document(s) are timestamped after the unit's as-of. This is "
            "look-ahead leakage in organizer material and the unit must not be published."
        )
    if indexed:
        unindexed = sorted(on_disk - indexed)
        missing_files = sorted(indexed - on_disk)
        if unindexed or missing_files:
            raise organizer_fault(
                f"the text corpus and {_CORPUS_INDEX} do not cover each other exactly: "
                f"{len(unindexed)} file(s) on disk are unindexed and {len(missing_files)} "
                "indexed document(s) are absent from disk. An unindexed document reaches the "
                "agent having passed no cutoff check."
            )
    return CorpusVerdict(indexed_documents=len(documents), files_on_disk=len(on_disk))
