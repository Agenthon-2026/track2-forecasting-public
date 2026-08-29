"""Reference-scale normalization: a rankability invariant, not a convenience (T2-7).

## Executive summary (read this first)

The Track 2 composite is `0.5*marginal + 0.3*joint + 0.2*tail`, and the three components live on
different natural scales — a CPI-index CRPS and a 30-year-yield CRPS differ by orders of
magnitude. Without normalization the mean over the roster is a weighted average dominated by
whichever units happen to carry the largest numbers, so a participant's rank depends on which
instruments the organizers picked. `ref_scale.json` divides each component by the official M0
baseline's value for that unit, which puts every unit on one scale where **the baseline is 1.0 by
construction**. That is what makes `W = 4.0` mean something ("four times worse than a text-blind
random walk") and what makes clipping at 4.0 a real bound rather than an arbitrary one.

Two faults are closed here, both armed and not yet live:

* `scoring.py:413-419` built the scale from **whichever keys were present**, and
  `crps.crps_composite` then indexed `ref_scale["marginal"]` unconditionally whenever the dict was
  truthy — so `{"tail": 1.0}` raised an uncaught `KeyError` out of the scorer.
* `scoring.py:420` was `ctx.setdefault("ref_scale", None)`, so a **missing scale file silently
  produced a raw composite**, and the driver then averaged raw and normalized units together with
  nothing refusing the mix.

Both are now impossible by construction: `load_ref_scale` returns a complete scale or raises, and
`NormalizationMode` has no third value that means "whatever we found on disk".

### The firewall note that matters more than the arithmetic

`ref_scale.json` is **answer-equivalent**. It is derived from the sealed realized outcome — it is
the baseline's error against that outcome — so given the baseline's forecast it inverts to the
target. It looks innocuous (three floats, no dates, no identifiers) and it is *not* the answer
file, which is precisely why a tool classifying unit files by name will ship it as configuration.
C6 has `answer_equivalent: bool` for exactly this artifact. `assert_reference_only()` below is the
scorer-side restatement: the loader refuses to read a scale out of anything but the reference root.
"""

from __future__ import annotations

import pathlib
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from .failures import organizer_fault
from .limits import DEFAULT_LIMITS, ParseLimits, read_json_bounded

__all__ = [
    "REF_SCALE_COMPONENTS",
    "REF_SCALE_FILENAME",
    "REF_SCALE_PROVENANCE_KEYS",
    "NormalizationMode",
    "RefScale",
    "assert_reference_only",
    "load_ref_scale",
]

#: Every component the composite weights. All three are required — a partial scale is the
#: `KeyError` fault, and "normalize two of three" is not a defined metric.
REF_SCALE_COMPONENTS: tuple[str, ...] = ("marginal", "joint", "tail")

#: Keys the generator writes for provenance and the metric never reads. Named as a CLOSED set
#: rather than tolerated by a wildcard: every one of the 114 scale files in the private tree
#: carries all three, so refusing them outright would fail every legitimate unit — and a gate that
#: rejects the legitimate case makes every rejection beside it uninterpretable. Anything outside
#: the union of these and `REF_SCALE_COMPONENTS` is still refused.
REF_SCALE_PROVENANCE_KEYS: tuple[str, ...] = ("method", "seed", "generated")

REF_SCALE_FILENAME = "ref_scale.json"


class NormalizationMode(StrEnum):
    """How a unit's composite was produced. There is no `auto` and no `whatever_was_on_disk`.

    `RAW_UNRANKABLE` exists for the participant smoke path, where no evaluation plan and no sealed
    reference exist and a raw composite is the only thing computable. It is named for what it
    costs: a raw score can be *displayed*, and it can never enter a ranked aggregate. The
    aggregator refuses a mixed set, so the name is load-bearing rather than decorative.
    """

    REF_SCALE = "ref_scale"
    RAW_UNRANKABLE = "raw_unrankable"


@dataclass(frozen=True, slots=True)
class RefScale:
    """A complete, positive, finite normalization scale. Constructing one is the validation."""

    marginal: float
    joint: float
    tail: float

    def __post_init__(self) -> None:
        for name in REF_SCALE_COMPONENTS:
            value = getattr(self, name)
            if not isinstance(value, float):  # pragma: no cover - constructor coerces
                raise organizer_fault(f"ref_scale.{name} must be a float")
            if value != value or value in (float("inf"), float("-inf")):
                raise organizer_fault(
                    f"ref_scale.{name} is non-finite. A non-finite intermediate statistic is an "
                    "organizer failure, and a scale that is not a number cannot normalize anything."
                )
            if value <= 0.0:
                raise organizer_fault(
                    f"ref_scale.{name}={value} is not positive. Dividing by zero or by a negative "
                    "baseline inverts the direction of the metric, which would make a worse "
                    "forecast rank better."
                )

    def as_mapping(self) -> dict[str, float]:
        """The `ref_scale` argument `crps.crps_composite` expects: all three keys, always."""
        return {"marginal": self.marginal, "joint": self.joint, "tail": self.tail}


def assert_reference_only(path: pathlib.Path, reference_root: pathlib.Path) -> None:
    """Refuse to load a scale from anywhere but the organizer's reference root.

    `ref_scale.json` inverts to the sealed target (C6 `answer_equivalent`). A scorer that would
    read it out of the participant's own output directory, or out of the mounted unit tree, is one
    misconfigured mount away from letting a submission supply its own denominator — which sets the
    composite to whatever the participant chooses.
    """
    resolved = path.resolve()
    root = reference_root.resolve()
    if not resolved.is_relative_to(root):
        raise organizer_fault(
            "refusing to load ref_scale.json from outside the reference root: the file is "
            "answer-equivalent (C6 answer_equivalent=true) and a participant-reachable copy "
            "would let the submission choose its own normalization denominator"
        )


def load_ref_scale(
    reference_root: pathlib.Path, *, limits: ParseLimits = DEFAULT_LIMITS
) -> RefScale:
    """Load and validate the unit's frozen scale. Anything short of complete is an organizer fault.

    There is no `None` return and no partial dict. The pre-freeze loader built the scale from the
    keys it happened to find; this one requires all three, refuses an unknown key, and refuses a
    non-positive or non-finite value. Every one of those refusals is an `OrganizerFault`, because a
    scale is organizer material and a participant cannot cause, detect or repair a missing one.
    """
    path = reference_root / REF_SCALE_FILENAME
    assert_reference_only(path, reference_root)
    if not path.is_file():
        raise organizer_fault(
            "this unit is rankable under normalization mode 'ref_scale' and carries no "
            f"reference/{REF_SCALE_FILENAME}. A rankable unit without a complete scale is an "
            "organizer failure, not a fallback to raw components: raw and normalized composites "
            "are not comparable and averaging them produces a leaderboard nobody can interpret."
        )
    try:
        raw: Mapping[str, Any] = read_json_bounded(
            path, what=REF_SCALE_FILENAME, max_bytes=limits.max_meta_bytes
        )
    except Exception as exc:  # noqa: BLE001 - a participant refusal here is a category error
        raise organizer_fault(
            f"reference/{REF_SCALE_FILENAME} is unreadable: {type(exc).__name__}: {exc}"
        ) from None

    allowed = set(REF_SCALE_COMPONENTS) | set(REF_SCALE_PROVENANCE_KEYS)
    unknown = sorted(set(raw) - allowed)
    if unknown:
        raise organizer_fault(
            f"reference/{REF_SCALE_FILENAME} carries unknown key(s) {unknown}; the scale is "
            f"{list(REF_SCALE_COMPONENTS)} plus the provenance keys "
            f"{list(REF_SCALE_PROVENANCE_KEYS)}, and nothing else"
        )
    missing = [k for k in REF_SCALE_COMPONENTS if k not in raw]
    if missing:
        raise organizer_fault(
            f"reference/{REF_SCALE_FILENAME} is missing {missing}. The composite weights all "
            "three components, so a partial scale normalizes some of the sum and not the rest — "
            "which is how an uncaught KeyError reached the scorer before the freeze."
        )
    values: dict[str, float] = {}
    for key in REF_SCALE_COMPONENTS:
        value = raw[key]
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise organizer_fault(
                f"reference/{REF_SCALE_FILENAME}.{key} must be a number, got {type(value).__name__}"
            )
        values[key] = float(value)
    return RefScale(**values)
