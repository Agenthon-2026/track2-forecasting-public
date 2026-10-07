"""Reference-scale normalization: a rankability invariant, not a convenience (T2-7).

## Executive summary (read this first)

The Track 2 composite is `0.5*marginal + 0.3*joint + 0.2*tail`, and the three components live on
different natural scales — a CPI-index CRPS and a 30-year-yield CRPS differ by orders of
magnitude. Without normalization the mean over the roster is a weighted average dominated by
whichever units happen to carry the largest numbers, so a participant's rank depends on which
instruments the organizers picked. `ref_scale.json` divides each component by the error the
official M0 baseline expects to make on that unit: M0's expected value of the component under
M0's own forecast distribution, computed from the card's inputs (docs/M0-BASELINE.md §5). That
puts every unit on one scale, where **1.0 means an error equal to the error M0 expects of
itself**. It is what makes the signed plan's `W = 8.0` mean something ("eight times the error the
text-blind baseline expects of itself") and what makes clipping at 8.0 a real bound rather than an
arbitrary one.

Three faults are closed here, all armed and not yet live:

* `hydrate_ctx` built the scale from **whichever keys were present**, and `crps.crps_composite`
  then indexed `ref_scale["marginal"]` unconditionally whenever the dict was truthy — so
  `{"tail": 1.0}` raised an uncaught `KeyError` out of the scorer.
* `hydrate_ctx` ended with `ctx.setdefault("ref_scale", None)`, so a **missing scale file silently
  produced a raw composite**, and the driver then averaged raw and normalized units together with
  nothing refusing the mix.
* "complete" meant all three components positive, but the joint component does not exist on a
  1-cell variogram grid, so the correct scale (`joint: 0.0`) was unloadable — 60 of 104 public
  cards. Latent only because the generator writes a placeholder `1.0` there; it arms the moment
  the scales are regenerated honestly. `load_ref_scale` now takes the grid shape and the joint
  statistic. See `_OPTIONAL_COMPONENT`.

All three are now impossible by construction: `load_ref_scale` returns a complete scale or raises,
and `NormalizationMode` has no third value that means "whatever we found on disk".

Ranked callers additionally use `load_verified_ref_scales(plan, ref_root)` once for the entire
roster. It checks the plan's commitment to the exact file bytes and returns an immutable snapshot.
Unit verifiers parse that snapshot; they never reopen scales after verification. Staging uses
`read_ref_scale_bundle(ref_root, handles).commitment`, so both paths share the digest encoding.

### The firewall note that matters more than the arithmetic

`ref_scale.json` is **organizer reference material**, read only from the reference root. It looks
innocuous (three floats, no dates, no identifiers), which is precisely why a tool classifying unit
files by name would ship it as configuration; and a copy the participant can reach would let a
submission supply its own divisor. `assert_reference_only()` below is the scorer-side rule: the
loader refuses to read a scale out of anything but the reference root.
"""

from __future__ import annotations

import json
import os
import pathlib
import stat
import tomllib
from collections.abc import Mapping, Sequence
from contextlib import ExitStack
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType

from qfbench2_common.contracts import EvaluationPlan, OrganizerFault, RosterEntry
from qfbench2_common.contracts.digest import digest_json, sha256_bytes
from qfbench2_common.contracts.plan import validate_unit_handle

from .failures import organizer_fault
from .grid import grid_from_plan_entry
from .limits import DEFAULT_LIMITS, ParseLimits

__all__ = [
    "REF_SCALE_ALWAYS_REQUIRED",
    "REF_SCALE_COMPONENTS",
    "REF_SCALE_FILENAME",
    "REF_SCALE_PROVENANCE_KEYS",
    "NormalizationMode",
    "RefScale",
    "RefScaleBundle",
    "VerifiedRefScales",
    "VARIOGRAM",
    "assert_reference_only",
    "joint_is_structurally_zero",
    "load_ref_scale",
    "load_verified_ref_scales",
    "read_ref_scale_bundle",
]

#: Every component the composite weights.
REF_SCALE_COMPONENTS: tuple[str, ...] = ("marginal", "joint", "tail")

#: The only component that can be structurally absent, and the only statistic that makes it so.
#: See `joint_is_structurally_zero`.
_OPTIONAL_COMPONENT = "joint"
VARIOGRAM = "variogram"

#: Required on every grid shape. Derived, so it cannot drift out of `REF_SCALE_COMPONENTS`.
REF_SCALE_ALWAYS_REQUIRED: tuple[str, ...] = tuple(
    c for c in REF_SCALE_COMPONENTS if c != _OPTIONAL_COMPONENT
)

#: Stand-in for a `joint` slot that does not exist, because `crps_composite` indexes
#: `ref_scale["joint"]` unconditionally. Safe only because the joint WEIGHT is a literal `0.0`
#: there — the numerator is not necessarily zero — so `as_mapping` refuses to emit it otherwise.
_JOINT_PLACEHOLDER: float = 1.0


def joint_is_structurally_zero(cell_count: int | None, joint_statistic: str) -> bool:
    """Does this grid's joint term have no value to normalize by?

    True only for the variogram on one cell, where it is 0 by construction. `energy_score` on one
    cell equals the marginal CRPS, so its scale genuinely exists. Both the scale loader and the
    weight renormalization in `scoring.py` branch on this, and they must agree.
    """
    return cell_count == 1 and joint_statistic == VARIOGRAM


#: Keys the generator writes for provenance and the metric never reads. Named as a CLOSED set
#: rather than tolerated by a wildcard: every scale file the generator has written carries all
#: three, so refusing them outright would fail every legitimate unit — and a gate that
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
    """A finite, positive normalization scale for every component the grid HAS.

    `joint` is `None` exactly when the component does not exist — see `_OPTIONAL_COMPONENT`.

    Constructing one validates every component that is present. It does NOT validate that an
    absent `joint` is legitimate: that pairs the scale with the composite's joint weight, which is
    card material and not in scope here. `as_mapping` settles it, as an `OrganizerFault` that
    `official.py` does not catch and that therefore aborts the evaluation rather than being charged
    to a participant.
    """

    marginal: float
    joint: float | None
    tail: float

    def __post_init__(self) -> None:
        for name in REF_SCALE_COMPONENTS:
            value = getattr(self, name)
            if value is None and name == _OPTIONAL_COMPONENT:
                continue
            if not isinstance(value, float):  # pragma: no cover - constructor coerces
                raise organizer_fault(f"ref_scale.{name} must be a float")
            if value != value or value in (float("inf"), float("-inf")):
                raise organizer_fault(
                    f"ref_scale.{name} is non-finite. A non-finite intermediate statistic is an "
                    "organizer failure, and a scale that is not a number cannot normalize anything."
                )
            if value <= 0.0:
                raise organizer_fault(
                    f"ref_scale.{name} is not positive. Dividing by zero or by a negative "
                    "baseline inverts the direction of the metric, which would make a worse "
                    "forecast rank better."
                )

    def as_mapping(self, *, joint_weight: float) -> dict[str, float]:
        """The `ref_scale` argument `crps.crps_composite` expects: all three keys, always.

        `joint_weight` is the composite's live weight on the joint term. A `None` joint is only
        representable when that weight is zero; asking for it otherwise is an organizer fault
        rather than a silent placeholder.
        """
        if self.joint is None:
            if joint_weight != 0.0:
                raise organizer_fault(
                    "ref_scale.joint does not exist for this unit but the composite weights the "
                    f"joint term at {joint_weight}. A scale that normalizes some of the sum and "
                    "not the rest is not a defined metric."
                )
            joint = _JOINT_PLACEHOLDER
        else:
            joint = self.joint
        return {"marginal": self.marginal, "joint": joint, "tail": self.tail}


def assert_reference_only(path: pathlib.Path, reference_root: pathlib.Path) -> None:
    """Refuse to load a scale from anywhere but the organizer's reference root.

    `ref_scale.json` is organizer reference material. A scorer that would
    read it out of the participant's own output directory, or out of the mounted unit tree, is one
    misconfigured mount away from letting a submission supply its own denominator — which sets the
    composite to whatever the participant chooses.
    """
    resolved = path.resolve()
    root = reference_root.resolve()
    if not resolved.is_relative_to(root):
        raise organizer_fault(
            "refusing to load ref_scale.json from outside the reference root: the file is "
            "organizer reference material and a participant-reachable copy "
            "would let the submission choose its own normalization denominator"
        )


def load_ref_scale(
    reference_root: pathlib.Path,
    *,
    cell_count: int | None = None,
    joint_statistic: str = VARIOGRAM,
    limits: ParseLimits = DEFAULT_LIMITS,
) -> RefScale:
    """Load and validate the unit's frozen scale. Any defect is an organizer fault.

    There is no `None` return and no partial dict: this requires every component the grid HAS,
    refuses an unknown key, and refuses a non-positive or non-finite value. A scale is organizer
    material, so every refusal is an `OrganizerFault`.

    Where `joint_is_structurally_zero`, the joint is dropped whatever the file says — including
    the `1.0` the generator writes — so `joint is None` means "the grid has no joint" rather than
    "the file was honest". The emitted mapping is unchanged either way. Every other shape keeps
    the strict rule, including `cell_count=None`, meaning the caller did not say.
    """
    raw_bytes = _read_scale_bytes(reference_root, (), limits)
    return _parse_ref_scale(raw_bytes, cell_count=cell_count, joint_statistic=joint_statistic)


def _parse_ref_scale(raw_bytes: bytes, *, cell_count: int | None, joint_statistic: str) -> RefScale:
    """Parse the exact immutable bytes that were read (and, for ranking, committed)."""
    try:
        raw = json.loads(raw_bytes.decode("utf-8"))
    except (ValueError, RecursionError):
        raise organizer_fault("reference/ref_scale.json is not valid UTF-8 JSON") from None
    if not isinstance(raw, dict):
        raise organizer_fault(
            "reference/ref_scale.json must hold an object; repair the organizer bundle"
        )

    allowed = set(REF_SCALE_COMPONENTS) | set(REF_SCALE_PROVENANCE_KEYS)
    unknown = sorted(set(raw) - allowed)
    if unknown:
        raise organizer_fault(
            f"reference/{REF_SCALE_FILENAME} carries unknown keys; the scale is "
            f"{list(REF_SCALE_COMPONENTS)} plus the provenance keys "
            f"{list(REF_SCALE_PROVENANCE_KEYS)}, and nothing else"
        )
    no_joint = joint_is_structurally_zero(cell_count, joint_statistic)
    required = REF_SCALE_ALWAYS_REQUIRED if no_joint else REF_SCALE_COMPONENTS
    missing = [k for k in required if k not in raw]
    if missing:
        raise organizer_fault(
            f"reference/{REF_SCALE_FILENAME} is missing {missing}. The composite weights every "
            "component the grid has, so a partial scale normalizes some of the sum and not the "
            "rest — which is how an uncaught KeyError reached the scorer before the freeze."
        )

    def _number(key: str) -> float:
        value = raw[key]
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise organizer_fault(
                f"reference/{REF_SCALE_FILENAME}.{key} must be a number, got {type(value).__name__}"
            )
        try:
            return float(value)
        except OverflowError:
            raise organizer_fault(
                f"reference/{REF_SCALE_FILENAME}.{key} is outside the supported numeric range"
            ) from None

    joint: float | None
    if no_joint:
        # Dropped, but validated first: a negative or non-finite joint is a corrupt file whatever
        # the grid, and dropping it silently would lose that detector. Absent, `0.0` and any
        # finite positive are all tolerated.
        if raw.get("joint") is not None:
            probe = _number("joint")
            if probe != probe or probe in (float("inf"), float("-inf")) or probe < 0.0:
                raise organizer_fault(
                    f"reference/{REF_SCALE_FILENAME}.joint is not a scale. A negative or "
                    "non-finite value is a corrupt file, not a grid property."
                )
        joint = None
    else:
        joint = _number("joint")
    return RefScale(marginal=_number("marginal"), joint=joint, tail=_number("tail"))


def _open_dir(stack: ExitStack, path: str | pathlib.Path, *, dir_fd: int | None = None) -> int:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=dir_fd)
    stack.callback(os.close, fd)
    return fd


def _read_scale_bytes(
    root: pathlib.Path, parts: tuple[str, ...], limits: ParseLimits, *, root_fd: int | None = None
) -> bytes:
    """Read through pinned directory descriptors without following links or reopening bytes."""
    return _read_metadata_bytes(root, parts, REF_SCALE_FILENAME, limits, root_fd=root_fd)


def _read_metadata_bytes(
    root: pathlib.Path,
    parts: tuple[str, ...],
    filename: str,
    limits: ParseLimits,
    *,
    root_fd: int | None = None,
) -> bytes:
    """Bounded no-follow read of organizer metadata, with no path or content in errors."""
    try:
        with ExitStack() as stack:
            fd = root_fd if root_fd is not None else _open_dir(stack, root)
            for part in parts:
                fd = _open_dir(stack, part, dir_fd=fd)
            scale_fd = os.open(filename, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
            with os.fdopen(scale_fd, "rb") as stream:
                facts = os.fstat(stream.fileno())
                if (
                    not stat.S_ISREG(facts.st_mode)
                    or facts.st_nlink != 1
                    or facts.st_size > limits.max_meta_bytes
                ):
                    raise organizer_fault(
                        "normalization metadata must be a bounded regular file with one link; "
                        "repair the organizer bundle"
                    )
                raw = stream.read(limits.max_meta_bytes + 1)
            if len(raw) > limits.max_meta_bytes:
                raise organizer_fault("normalization metadata exceeds the metadata byte limit")
            return raw
    except OSError:
        raise organizer_fault(
            "normalization metadata is missing, unreadable or linked outside its location; "
            "repair the organizer bundle before scoring; there is no raw fallback"
        ) from None


@dataclass(frozen=True, slots=True)
class RefScaleBundle:
    """Immutable roster bytes and the canonical staging/scoring commitment.

    The commitment is JCS over {handle: sha256(exact file bytes)}, matching the existing
    CodaBench stage_native_development.py encoding. This object alone does not authorize ranking.
    """

    reference_root: pathlib.Path = field(repr=False)
    scales: Mapping[str, bytes] = field(repr=False)
    commitment: str = field(init=False, repr=False)

    def __post_init__(self) -> None:
        # Copy even a caller-created bundle: a frozen dataclass alone does not freeze its dict.
        snapshot = dict(self.scales)
        if any(not isinstance(raw, bytes) for raw in snapshot.values()):
            raise organizer_fault("normalization snapshot must contain immutable file bytes")
        object.__setattr__(self, "reference_root", pathlib.Path(self.reference_root).absolute())
        object.__setattr__(self, "scales", MappingProxyType(snapshot))
        object.__setattr__(
            self,
            "commitment",
            digest_json({handle: sha256_bytes(raw) for handle, raw in snapshot.items()}),
        )


def read_ref_scale_bundle(
    reference_root: pathlib.Path, handles: Sequence[str], *, limits: ParseLimits = DEFAULT_LIMITS
) -> RefScaleBundle:
    """One canonical roster-to-file-digest helper for staging and scoring; read each file once."""
    handles = tuple(handles)
    try:
        for handle in handles:
            validate_unit_handle(handle, phase="dev")
    except (TypeError, ValueError, OrganizerFault):
        raise organizer_fault("invalid normalization roster handle; repair the plan") from None
    if len(set(handles)) != len(handles) or not handles:
        raise organizer_fault("normalization roster must contain unique handles")
    root = pathlib.Path(reference_root).absolute()
    try:
        with ExitStack() as stack:
            root_fd = _open_dir(stack, root)
            observed = {
                name
                for name in os.listdir(root_fd)
                if stat.S_ISDIR(os.stat(name, dir_fd=root_fd, follow_symlinks=False).st_mode)
                or stat.S_ISLNK(os.stat(name, dir_fd=root_fd, follow_symlinks=False).st_mode)
            }
            if observed != set(handles):
                raise organizer_fault(
                    "normalization reference directories do not match the committed roster; "
                    "repair missing or unexpected organizer inputs"
                )
            scales = {
                handle: _read_scale_bytes(root, (handle, "reference"), limits, root_fd=root_fd)
                for handle in handles
            }
    except OSError:
        raise organizer_fault("normalization reference root is unavailable or linked") from None
    return RefScaleBundle(root, scales)


@dataclass(frozen=True, slots=True)
class VerifiedRefScales:
    """A roster snapshot bound to the supplied plan; callers still verify its signature."""

    plan_digest: str
    bundle: RefScaleBundle
    joint_statistics: Mapping[str, str] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        # An annotation does not stop a mutable look-alike from claiming any commitment.
        # Reconstruct even a genuine bundle so its commitment always derives from its bytes.
        if type(self.bundle) is not RefScaleBundle:
            raise organizer_fault("verified normalization requires a canonical immutable bundle")
        object.__setattr__(
            self,
            "bundle",
            RefScaleBundle(
                self.bundle.reference_root,
                self.bundle.scales,
            ),
        )
        statistics = dict(self.joint_statistics)
        if any(statistic not in (VARIOGRAM, "energy") for statistic in statistics.values()):
            raise organizer_fault("normalization has an unsupported joint statistic")
        object.__setattr__(self, "joint_statistics", MappingProxyType(statistics))

    def load_scale(
        self,
        plan: EvaluationPlan,
        entry: RosterEntry,
        reference_root: pathlib.Path,
        *,
        cell_count: int,
        joint_statistic: str = VARIOGRAM,
    ) -> RefScale:
        """Validate context binding and parse committed bytes, never reopen a mutable file."""
        if (
            self.plan_digest != plan.plan_digest
            or plan.normalization is None
            or self.bundle.commitment != plan.normalization["ref_scale_commitment"]
            or tuple(self.bundle.scales) != tuple(plan.expected_handles)
            or entry not in plan.expected_units
            or cell_count != grid_from_plan_entry(entry).cell_count
            or self.joint_statistics.get(entry.unit_handle) != joint_statistic
            or pathlib.Path(reference_root).absolute()
            != self.bundle.reference_root / entry.unit_handle / "reference"
        ):
            raise organizer_fault(
                "verified normalization does not match this plan, roster or reference root"
            )
        return _parse_ref_scale(
            self.bundle.scales[entry.unit_handle],
            cell_count=cell_count,
            joint_statistic=joint_statistic,
        )


def load_verified_ref_scales(
    plan: EvaluationPlan, reference_root: pathlib.Path, *, limits: ParseLimits = DEFAULT_LIMITS
) -> VerifiedRefScales:
    """Verify the entire roster once before any participant gate or score can run.

    Signature verification remains with the entrypoint's trust store. A malformed file or a
    commitment mismatch is always an organizer fault, without values, identifiers or digests.
    """
    if (
        not isinstance(plan, EvaluationPlan)
        or plan.track != "forecasting"
        or plan.is_public_commitment
        or plan.normalization is None
        or plan.normalization.get("mode") != NormalizationMode.REF_SCALE.value
    ):
        raise organizer_fault("normalization requires an expanded forecasting ref_scale plan")
    bundle = read_ref_scale_bundle(reference_root, plan.expected_handles, limits=limits)
    if bundle.commitment != plan.normalization["ref_scale_commitment"]:
        raise organizer_fault(
            "normalization scale commitment mismatch; restore the signed organizer bundle "
            "before ranking"
        )
    statistics = {}
    for entry in plan.expected_units:
        spec = grid_from_plan_entry(entry)
        raw = _read_metadata_bytes(
            bundle.reference_root,
            (entry.unit_handle,),
            "card.toml",
            limits,
        )
        try:
            card = tomllib.loads(raw.decode("utf-8"))
            statistic = card.get("scoring", {}).get("params", {}).get("joint", VARIOGRAM)
        except (ValueError, AttributeError, RecursionError):
            raise organizer_fault("normalization card metadata is malformed") from None
        if not isinstance(statistic, str) or statistic not in (VARIOGRAM, "energy"):
            raise organizer_fault("normalization card has an unsupported joint statistic")
        _parse_ref_scale(
            bundle.scales[entry.unit_handle], cell_count=spec.cell_count, joint_statistic=statistic
        )
        if spec.cell_count == 1 and statistic != VARIOGRAM:
            raise organizer_fault("single-cell normalization requires the variogram statistic")
        statistics[entry.unit_handle] = statistic
    return VerifiedRefScales(plan.plan_digest, bundle, statistics)
