"""Track 2 canonical scorer — the gate stack, the metric, and the one flattening rule.

## Executive summary (read this first)

This module is the **single** Track 2 scoring implementation. The private final scorer and the
CodaBench scoring image both import it as an installed package; neither reimplements it and
neither reaches it through an ambient sibling checkout. That is T2-7/T2-17: before the freeze
`final_scorer.py` did `sys.path.insert(0, <repo>/../track2-forecasting-public/scoring)` and
`import scoring`, so whatever happened to be checked out next door became the production gate
stack, under a generic top-level module name that also shadowed any installed `scoring`.

Canonical contract, unchanged and still what the shared smoke runner imports:

    build_verifier(ctx) -> qfbench2_common.verifier.HierarchicalVerifier
    LEADERBOARD_SORT     -> "asc"   (lower composite is better)

### What changed at the freeze, and why each one is structural rather than a patch

* **g1 no longer fails open.** `except ModuleNotFoundError: pass` around `jsonschema.validate`
  meant that on a host without `jsonschema` a garbage sidecar passed — and because the 200-draw
  floor lived only in the schema, that one `pass` removed the floor entirely. A missing validator
  is now an `OrganizerFault`, and the floor is *also* enforced in code (`limits.min_draws`) so it
  survives any single point of failure.
* **`representation: parametric` is refused.** The schema advertised it and promised `cov.parquet`;
  nothing anywhere read `cov.parquet`, and the `n_draws` requirement was conditional on
  `representation == "samples"` — so `parametric` with **3 draws** was fully admissible while the
  same 3 draws under `samples` were rejected. Track 2 does not maintain a divergent copy of the
  Hub's schema, so the accepted-representation narrowing lives here until the Hub lands the schema
  change (filed as a contract request).
* **No participant-authored parse error escapes as a crash.** `json.loads` and `read_parquet` were
  unguarded and `score.py` called the verifier inside the unit loop with no `try`, so one malformed
  sidecar killed the whole submission as an organizer-shaped crash instead of producing one
  participant failure. Every read here is bounded and every parser exception becomes a `T2Refusal`.
* **The grid comes from C1, in order.** See `grid.py`.
* **There is no raw-composite fallback.** See `normalization.py`.
* **No detail carries free text.** See `failures.py`.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import tomllib
from collections.abc import Callable
from typing import Any

import numpy as np
from numpy.typing import NDArray
from qfbench2_common.contracts import FailureCode, OrganizerFault, RosterEntry
from qfbench2_common.scoring import crps
from qfbench2_common.taskcard import schema_path
from qfbench2_common.verifier import GateResult, HierarchicalVerifier

from .cutoff import bind_metadata, check_declared_cutoff
from .failures import T2Refusal, organizer_fault
from .grid import (
    REALIZED_COLUMNS,
    GridSpec,
    build_sample_matrix,
    check_declared_grid,
    flatten_realized,
    grid_from_card,
    grid_from_plan_entry,
)
from .limits import (
    DEFAULT_LIMITS,
    ParseLimits,
    inspect_parquet,
    rationale_has_content,
    read_json_bounded,
    stat_regular_file,
)
from .normalization import NormalizationMode, RefScale, load_ref_scale

__all__ = [
    "ACCEPTED_REPRESENTATIONS",
    "GATES",
    "LEADERBOARD_SORT",
    "UNSCORED_NO_REFERENCE",
    "build_verifier",
    "hydrate_ctx",
    "resolve_expected_grid",
]

LEADERBOARD_SORT = "asc"  # lower composite wins

#: The ONE reason an unranked run may report for producing no score. A fixed constant on purpose:
#: the pre-freeze `_unscored_reason` read `backfill_after` out of `reference/PENDING.json` and put
#: it in the verdict as `resolves_after` — a sealed target date on a participant-visible path. The
#: distinction it drew (prospective / unresolved / smoke) was correct and now lives in C1, where a
#: prospective unit is simply not in the committed roster.
UNSCORED_NO_REFERENCE = "no_reference_in_mounted_unit"

#: The representations this scorer actually implements. `parametric` is deliberately absent: the
#: Hub schema still lists it (contract request T2-CR-1) and a loader for it does not exist. An
#: accepted representation with no loader is a hole, not a feature.
ACCEPTED_REPRESENTATIONS: tuple[str, ...] = ("samples",)

_SCHEMA = schema_path("forecast.schema.json")

_FORECAST_PARQUET = "forecast.parquet"
_FORECAST_META = "forecast_meta.json"
_FORECAST_RATIONALE = "forecast_rationale.md"

#: Exactly three regular files at the root of the sanitized participant tree. Contributed to C3,
#: and repeated here because this is the scorer's own perimeter.
PARTICIPANT_FILES: tuple[str, ...] = (
    _FORECAST_PARQUET,
    _FORECAST_META,
    _FORECAST_RATIONALE,
)


# --------------------------------------------------------------------------------------------
# ctx hydration — every source is explicit and stamped
# --------------------------------------------------------------------------------------------


def resolve_expected_grid(ctx: dict[str, Any]) -> tuple[GridSpec, str]:
    """Return `(grid, source)` where source is `"plan"` or `"card"`, and never guess.

    `"plan"` is the only source a ranked score may use. `"card"` exists for the participant smoke
    path, where no evaluation plan is mounted; the aggregator refuses any unit whose grid came from
    a card, so the smoke path cannot become a ranked path by accident.
    """
    entry = ctx.get("plan_entry")
    if entry is not None:
        if not isinstance(entry, RosterEntry):
            raise organizer_fault(
                "ctx['plan_entry'] must be a qfbench2_common.contracts.RosterEntry; the grid is "
                "read from the signed plan, not from a look-alike dict"
            )
        return grid_from_plan_entry(entry), "plan"
    card = ctx.get("card")
    if card is None:
        raise organizer_fault(
            "ctx carries neither a C1 roster entry nor a card, so there is no grid to score "
            "against. An absent grid is an error, never an unconstrained one."
        )
    return grid_from_card(card), "card"


def hydrate_ctx(ctx: dict[str, Any]) -> None:
    """Fill the ctx keys this verifier documents, stamping the provenance of each one.

    Every value an explicit caller supplied wins. What this adds is the *smoke* path: the shared
    runner passes only `{unit_dir, output_dir}` and the gates need a card, a grid, a reference
    root and a normalization decision. Before the freeze this ended with
    `ctx.setdefault("ref_scale", None)`, which turned "no scale on disk" into "score it raw" — the
    silent fallback that makes a mixed-mode leaderboard. There is no `setdefault` here: a missing
    scale under `ref_scale` mode raises.
    """
    ctx.setdefault("limits", DEFAULT_LIMITS)
    ctx.setdefault("unit_handle", "u-unspecified")

    unit_dir = ctx.get("unit_dir")
    if unit_dir is not None:
        unit_dir = pathlib.Path(unit_dir)
        ctx["unit_dir"] = unit_dir

    if "card" not in ctx:
        if unit_dir is None:
            raise organizer_fault(
                "ctx has neither 'card' nor 'unit_dir'; the scorer cannot invent the task it is "
                "grading"
            )
        card_path = unit_dir / "card.toml"
        if not card_path.is_file():
            raise organizer_fault(
                f"cannot score {unit_dir.name}: no ctx['card'] and no readable card.toml — the "
                "reference bundle is malformed"
            )
        ctx["card"] = tomllib.loads(card_path.read_text(encoding="utf-8"))

    if "reference_root" not in ctx:
        ctx["reference_root"] = (unit_dir / "reference") if unit_dir is not None else None
    elif ctx["reference_root"] is not None:
        ctx["reference_root"] = pathlib.Path(ctx["reference_root"])

    grid, source = resolve_expected_grid(ctx)
    ctx["expected_grid"] = ctx.get("expected_grid") or grid
    ctx.setdefault("grid_source", source)

    if "normalization_mode" not in ctx:
        # The smoke path has no plan, therefore no `normalization.mode`, therefore no rankability.
        # Naming the mode `raw_unrankable` rather than defaulting to `None` is the whole point:
        # the value says out loud what it costs.
        ctx["normalization_mode"] = (
            NormalizationMode.REF_SCALE if source == "plan" else NormalizationMode.RAW_UNRANKABLE
        )
    mode = NormalizationMode(ctx["normalization_mode"])
    ctx["normalization_mode"] = mode

    if "realized" not in ctx:
        # The smoke/CLI path: load the reference vector if the mounted unit carries one, using the
        # SAME flattening rule as the official path (plan order, exact unique complete coverage).
        # Before the freeze the two entrypoints each had their own loader and their own
        # ordering, and an identical submission scored 187x apart as a result.
        ctx["realized"] = _reference_from_unit(ctx)

    if mode is NormalizationMode.REF_SCALE and ctx.get("ref_scale") is None:
        reference_root = ctx.get("reference_root")
        if reference_root is None:
            raise organizer_fault(
                "normalization mode is 'ref_scale' but no reference root was supplied, so the "
                "answer-equivalent scale cannot be located. Refusing to fall back to raw."
            )
        ctx["ref_scale"] = load_ref_scale(
            reference_root,
            cell_count=ctx["expected_grid"].cell_count,
            limits=ctx["limits"],
        )
    ctx.setdefault("ref_scale", None)


def _reference_from_unit(ctx: dict[str, Any]) -> NDArray[np.float64] | None:
    """The realized vector from `reference/realized.parquet`, or None when the unit has none.

    None here means "this mounted unit ships no answer", which is the ordinary state of a public
    smoke unit. It is NOT a licence to drop a roster unit: `_score` refuses a `None` on a
    plan-derived grid and only tolerates it on a card-derived one, which can never be aggregated.
    """
    reference_root = ctx.get("reference_root")
    if reference_root is None:
        return None
    path = pathlib.Path(reference_root) / "realized.parquet"
    if not path.is_file():
        return None
    import pyarrow.parquet as pq

    facts = inspect_parquet(path, what="realized.parquet", limits=ctx["limits"])
    missing = [c for c in REALIZED_COLUMNS if c not in facts.column_names]
    if missing:
        raise organizer_fault(f"reference/realized.parquet lacks column(s) {missing}")
    table = pq.read_table(path, columns=list(REALIZED_COLUMNS))
    return flatten_realized(
        {name: table.column(name) for name in REALIZED_COLUMNS}, ctx["expected_grid"]
    )


# --------------------------------------------------------------------------------------------
# Gates
# --------------------------------------------------------------------------------------------


def _refused(exc: T2Refusal) -> GateResult:
    """One place where a refusal becomes a `GateResult`, so no gate can forget to redact.

    `exc.detail` has already been through the Hub's `validate_public_detail`, so what lands in
    `GateResult.detail` is an enum code and non-negative integers. `exc.reason` is *not* attached:
    the verdict's detail is serialized by callers we do not control.
    """
    return GateResult(False, exc.label, dict(exc.detail))


def _g0_integrity(ctx: dict[str, Any]) -> GateResult:
    """The tree holds exactly the three expected regular files, and the sidecar parses."""
    output_dir = pathlib.Path(ctx["output_dir"])
    limits: ParseLimits = ctx["limits"]
    try:
        if not output_dir.is_dir():
            raise T2Refusal(FailureCode.NO_OUTPUT, "the submission produced no output directory")
        present = {p.name for p in output_dir.iterdir()}
        unexpected = sorted(present - set(PARTICIPANT_FILES))
        if unexpected:
            raise T2Refusal(
                FailureCode.SCHEMA_INVALID,
                f"the submission tree holds {len(unexpected)} unexpected entr(y/ies); the "
                f"contract is exactly {list(PARTICIPANT_FILES)}",
                extra_count=len(unexpected),
                expected_count=len(PARTICIPANT_FILES),
            )
        stat_regular_file(
            output_dir / _FORECAST_PARQUET,
            required=True,
            what=_FORECAST_PARQUET,
            max_bytes=limits.max_parquet_bytes,
        )
        ctx["_meta"] = read_json_bounded(
            output_dir / _FORECAST_META,
            what=_FORECAST_META,
            max_bytes=limits.max_meta_bytes,
        )
    except T2Refusal as exc:
        return _refused(exc)
    return GateResult(True)


def _g1_schema(ctx: dict[str, Any]) -> GateResult:
    """Hub schema, then the two things the schema cannot express, then the rationale bit.

    The schema validator is **required**. Skipping validation because a module is absent is the
    fail-open shape global rule 5 forbids, and it is not hypothetical: with `jsonschema` importable
    a garbage sidecar failed this gate, and with the import blocked the identical sidecar passed.
    """
    try:
        import jsonschema
    except ModuleNotFoundError as exc:  # pragma: no cover - production images pin jsonschema
        raise organizer_fault(
            "jsonschema is not importable, so the Track 2 output schema cannot be validated. "
            "Refusing to score behind a gate that did not run rather than passing the submission."
        ) from exc

    meta = ctx["_meta"]
    limits: ParseLimits = ctx["limits"]
    output_dir = pathlib.Path(ctx["output_dir"])
    try:
        try:
            jsonschema.validate(meta, json.loads(_SCHEMA.read_text(encoding="utf-8")))
        except jsonschema.ValidationError as exc:
            # `exc` renders the offending instance, i.e. participant bytes. Operator-only.
            raise T2Refusal(
                FailureCode.SCHEMA_INVALID,
                f"{_FORECAST_META} does not validate against forecast.schema.json: {exc.message}",
            ) from None

        representation = meta.get("representation")
        if representation not in ACCEPTED_REPRESENTATIONS:
            raise T2Refusal(
                FailureCode.SCHEMA_INVALID,
                f"representation={representation!r} is not implemented by this scorer; Track 2 "
                f"accepts {list(ACCEPTED_REPRESENTATIONS)}. 'parametric' is advertised by the "
                "shared schema and has no loader anywhere, which made it a route past the draw "
                "floor rather than a second submission format.",
            )

        declared = meta.get("n_draws")
        if isinstance(declared, bool) or not isinstance(declared, int):
            raise T2Refusal(
                FailureCode.SCHEMA_INVALID,
                "forecast_meta.json must declare n_draws as an integer for a draw-format forecast",
            )
        if declared < limits.min_draws or declared > limits.max_draws:
            raise T2Refusal(
                FailureCode.SCHEMA_INVALID,
                f"n_draws={declared} is outside the contract range "
                f"[{limits.min_draws}, {limits.max_draws}]",
                observed_count=max(declared, 0),
                expected_count=limits.min_draws,
            )

        # forecast_rationale.md: presence and non-emptiness ONLY. The file is required and NEVER
        # SCORED; this gate learns exactly one bit about it and no other code path may read it.
        if not rationale_has_content(output_dir / _FORECAST_RATIONALE, limits=limits):
            raise T2Refusal(
                FailureCode.SCHEMA_INVALID,
                f"{_FORECAST_RATIONALE} is present but empty (required, never scored)",
            )
    except T2Refusal as exc:
        return _refused(exc)
    return GateResult(True)


def _g2_cutoff_resource(ctx: dict[str, Any]) -> GateResult:
    """Bind the declaration to the trusted card, and check the card's own cutoff.

    The panel-row and text-corpus scans do **not** run here, and that is deliberate rather than an
    omission: under the frozen worker/scoring topology the scoring program receives `input/ref` and
    `input/res` only, so the panels and the corpus — which live in the participant *mount* — are
    not in this process's namespace at all. They are checked where they can be, before publication,
    by `cutoff.scan_panel_cutoff` and `cutoff.scan_text_corpus_cutoff` in the staging gate stack.
    A check placed where its inputs do not exist is a check that silently passes.
    """
    try:
        check_declared_cutoff(ctx["card"], unit_handle=ctx["unit_handle"])
        bind_metadata(ctx["_meta"], ctx["card"], unit_handle=ctx["unit_handle"])
    except T2Refusal as exc:
        return _refused(exc)
    return GateResult(True)


def _g3_domain_semantics(ctx: dict[str, Any]) -> GateResult:
    """The declared grid must be the committed grid, and the parquet must fill it exactly once."""
    meta = ctx["_meta"]
    spec: GridSpec = ctx["expected_grid"]
    limits: ParseLimits = ctx["limits"]
    path = pathlib.Path(ctx["output_dir"]) / _FORECAST_PARQUET
    try:
        check_declared_grid(meta, spec)
        facts = inspect_parquet(path, what=_FORECAST_PARQUET, limits=limits)
        samples = build_sample_matrix(path, facts, spec, int(meta["n_draws"]), limits=limits)
    except T2Refusal as exc:
        return _refused(exc)
    ctx["_samples"] = samples
    ctx["_parquet_facts"] = facts
    return GateResult(True)


# --------------------------------------------------------------------------------------------
# Metric
# --------------------------------------------------------------------------------------------


def _score(ctx: dict[str, Any]) -> dict[str, Any]:
    """Compute the composite. A scorable unit with no realized outcome is an organizer fault.

    Before the freeze this returned `{"score": None, **_unscored_reason(ctx)}` and the driver
    dropped the unit from the mean — the A01 exploit, measured at 15x. The taxonomy that function
    built (`prospective` / `unresolved` / `smoke`) was correct and is *not* lost: it moved to C1,
    where a prospective unit is simply not in the committed roster. What cannot happen any more is
    a unit inside the roster resolving to "no score": that raises, and the evaluation aborts,
    because the alternative is a denominator that shrinks to whatever answers happen to exist.
    """
    y = ctx.get("realized")
    if y is None:
        if ctx["grid_source"] == "plan":
            raise organizer_fault(
                f"[{ctx['unit_handle']}] the unit is in the scoring roster and no realized "
                "outcome was supplied. A roster unit with no answer is an organizer failure that "
                "aborts the evaluation; it is never a dropped unit and never a participant zero."
            )
        # Unranked: a mounted smoke unit with no answer. The gates ran and passed; there is
        # nothing to score against. The reason is a FIXED CONSTANT, not derived from the unit —
        # the pre-freeze version returned `resolves_after` read out of PENDING.json, which is a
        # sealed date, and the frozen C4 removed that key from the public allowlist for exactly
        # this reason.
        return {
            "score": None,
            "scored": False,
            "unscored_reason": UNSCORED_NO_REFERENCE,
            "normalization_mode": ctx["normalization_mode"].value,
            "grid_source": ctx["grid_source"],
        }
    samples: NDArray[np.float64] = ctx["_samples"]
    spec: GridSpec = ctx["expected_grid"]
    y = np.asarray(y, dtype=np.float64)
    if y.shape != (spec.cell_count,):
        raise organizer_fault(
            f"[{ctx['unit_handle']}] the realized vector has shape {y.shape}, the committed grid "
            f"has {spec.cell_count} cells"
        )

    params = ctx["card"].get("scoring", {}).get("params", {})
    weights = params.get("weights", {"marginal": 0.5, "joint": 0.3, "tail": 0.2})
    try:
        weight_tuple = (
            float(weights["marginal"]),
            float(weights["joint"]),
            float(weights["tail"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise organizer_fault(
            f"[{ctx['unit_handle']}] card [scoring.params.weights] is unusable: {exc}"
        ) from None

    # ---- single-cell weight renormalization (track-lead ruling, 2026-08-24) ----
    # The variogram is a between-cells statistic: on a 1-cell grid it is 0 by construction,
    # not by merit, so its weight deflates the composite and the documented anchor breaks --
    # the frozen baseline lands at exactly w_m + w_t = 0.7 instead of the 1.0 that
    # SCORING-AGGREGATION.md promises. Measured across the private tree: 40 of 71 validation
    # units and 38 of 123 private-test units are single-cell, so the leaderboard mean was
    # averaging two different scales. On a 1-cell grid the live weights are renormalized over
    # the components that structurally exist ((0.5, 0.3, 0.2) -> (0.714286, 0, 0.285714));
    # every multi-cell unit is byte-identical.
    #
    # There is ONE board. An earlier revision of this comment said single- and multi-cell units
    # additionally rank on separate boards combined by rank average; that ruling was withdrawn
    # (track-lead, 2026-08-25) because the scoring program emits one statistic and the live
    # leaderboard has nowhere to put a per-board field -- publishing it would have promised
    # participants a number the platform cannot show them. The renormalization above is what makes
    # one board fair: it puts the text-blind baseline at 1.0 on both card shapes, so a single
    # average is averaging one quantity. Ruling and measurements: the private repo's
    # docs/SCORING-AGGREGATION.md.
    if spec.cell_count == 1:
        live = weight_tuple[0] + weight_tuple[2]
        if live <= 0.0:
            raise organizer_fault(
                f"[{ctx['unit_handle']}] single-cell grid with zero marginal+tail weight; "
                "the card's weight vector cannot score this unit"
            )
        weight_tuple = (weight_tuple[0] / live, 0.0, weight_tuple[2] / live)

    mode: NormalizationMode = ctx["normalization_mode"]
    ref_scale: RefScale | None = ctx.get("ref_scale")
    if mode is NormalizationMode.REF_SCALE and ref_scale is None:  # pragma: no cover - hydrate
        raise organizer_fault(
            "normalization mode is 'ref_scale' and no scale is loaded; there is no raw fallback"
        )

    out = crps.crps_composite(
        samples,
        y,
        weights=weight_tuple,
        tail_levels=tuple(params.get("tail_levels", (0.01, 0.05, 0.95, 0.99))),
        joint=params.get("joint", "variogram"),
        ref_scale=(
            ref_scale.as_mapping(joint_weight=weight_tuple[1]) if ref_scale is not None else None
        ),
    )
    composite = float(out["composite"])
    if not np.isfinite(composite):
        # A non-finite *statistic* is an organizer failure (frozen C4), unlike a non-finite value
        # in participant data, which g3 already refused as a participant failure.
        raise organizer_fault(
            f"[{ctx['unit_handle']}] the composite statistic is non-finite on finite inputs; "
            "this is a metric or reference defect, not a submission defect"
        )
    return {
        "score": composite,
        "normalization_mode": mode.value,
        "grid_source": ctx["grid_source"],
        "cell_count": spec.cell_count,
        "rank_group": "single" if spec.cell_count == 1 else "multi",
        "weights_effective": [float(w) for w in weight_tuple],
        "n_draws": int(samples.shape[0]),
        **{k: float(v) for k, v in out.items()},
    }


#: The published gate order. Named at module scope so the CLI's gates-only path and
#: `build_verifier` cannot run different stacks -- two orderings for one contract is how dev and
#: final scoring drift.
GATES: list[tuple[str, Callable[[dict[str, Any]], GateResult]]] = [
    ("g0_integrity", _g0_integrity),
    ("g1_schema", _g1_schema),
    ("g2_cutoff_resource", _g2_cutoff_resource),
    ("g3_domain_semantics", _g3_domain_semantics),
]


def build_verifier(ctx: dict[str, Any]) -> HierarchicalVerifier:
    """The canonical contract every track exposes: hydrate `ctx`, wire g0-g3 to the metric."""
    hydrate_ctx(ctx)
    return HierarchicalVerifier(list(GATES), _score)


# --------------------------------------------------------------------------------------------
# CLI — `python -m qfbench2_track_forecasting.scoring score --card ... --forecast ...`
# --------------------------------------------------------------------------------------------


def _load_realized_vector(realized_path: pathlib.Path, spec: GridSpec) -> NDArray[np.float64]:
    """CLI-side reference loader. Same exactness rules as the official path, same ordering."""
    import pyarrow.parquet as pq

    facts = inspect_parquet(realized_path, what="realized.parquet")
    missing = [c for c in REALIZED_COLUMNS if c not in facts.column_names]
    if missing:
        raise organizer_fault(f"realized.parquet lacks column(s) {missing}")
    table = pq.read_table(realized_path, columns=list(REALIZED_COLUMNS))
    columns = {name: table.column(name) for name in REALIZED_COLUMNS}
    return flatten_realized(columns, spec)


def _cmd_score(args: argparse.Namespace) -> int:
    card_path = pathlib.Path(args.card)
    forecast_path = pathlib.Path(args.forecast)
    with card_path.open("rb") as fh:
        card = tomllib.load(fh)
    spec = grid_from_card(card)
    realized = _load_realized_vector(pathlib.Path(args.realized), spec) if args.realized else None
    ctx: dict[str, Any] = {
        "card": card,
        "output_dir": forecast_path.parent,
        "unit_dir": card_path.parent,
        "unit_handle": str(card.get("task", {}).get("id", "u-unspecified")),
        "expected_grid": spec,
        "grid_source": "card",
        "normalization_mode": NormalizationMode.RAW_UNRANKABLE,
        "ref_scale": None,
        "realized": realized,
    }
    if realized is None:
        # Gates only. `_score` refuses a roster unit with no answer, and the CLI's gates-only mode
        # is not a roster: run the gates explicitly rather than teaching the scorer a third state.
        hydrate_ctx(ctx)
        results = {}
        for name, gate in GATES:
            results[name] = gate(ctx)
            if not results[name].passed:
                break
        admissible = all(r.passed for r in results.values()) and len(results) == len(GATES)
        payload: dict[str, Any] = {
            "card_id": card.get("task", {}).get("id"),
            "admissible": admissible,
            "gates": {n: ("pass" if r.passed else "fail") for n, r in results.items()},
            "scored": False,
            "note": "no --realized supplied: gates only, no score",
        }
        if not admissible:
            failing = next(r for r in results.values() if not r.passed)
            payload["detail"] = dict(failing.detail)
        print(json.dumps(payload, indent=2))
        return 0 if admissible else 1

    verdict = build_verifier(ctx).run(ctx)
    result: dict[str, Any] = {
        "card_id": card.get("task", {}).get("id"),
        "admissible": verdict.admissible,
        "gates": {
            name: ("pass" if res.passed else "fail") for name, res in verdict.gate_results.items()
        },
        "failure_labels": [label.value for label in verdict.labels],
        "normalization_mode": NormalizationMode.RAW_UNRANKABLE.value,
        "rankable": False,
    }
    if verdict.admissible:
        detail = verdict.detail
        result.update(
            {
                "marginal_crps": detail["marginal"],
                "joint_variogram": detail["joint"],
                "tail_penalty": detail["tail"],
                "composite_score": detail["composite"],
                "n_draws": detail["n_draws"],
                "cell_count": detail["cell_count"],
            }
        )
    else:
        result["detail"] = dict(verdict.detail)
    print(json.dumps(result, indent=2))
    return 0 if verdict.admissible else 1


def _main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="qfbench2-track-forecasting-score",
        description=(
            "Track 2 reference scorer: runs the admissibility gates (g0_integrity, g1_schema, "
            "g2_cutoff_resource, g3_domain_semantics) and the CRPS composite on one forecast. "
            "This CLI is UNRANKED by construction: it scores against card.toml with no reference "
            "scale, so its composite is raw and not comparable across units."
        ),
    )
    sub = ap.add_subparsers(dest="command", required=True)
    sp = sub.add_parser("score", help="score one forecast against one card")
    sp.add_argument("--card", required=True, help="path to the unit's card.toml")
    sp.add_argument(
        "--forecast",
        required=True,
        help=f"path to {_FORECAST_PARQUET} ({_FORECAST_META} must sit next to it)",
    )
    sp.add_argument(
        "--realized",
        default=None,
        help="path to realized outcomes parquet [asset,horizon,value]; omit for gates only",
    )
    args = ap.parse_args(argv)
    try:
        return _cmd_score(args)
    except OrganizerFault as exc:
        print(json.dumps({"organizer_failure": str(exc)}, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(_main())
