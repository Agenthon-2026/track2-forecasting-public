#!/usr/bin/env python3
"""T2 scoring regression: golden fixtures in, pinned verdicts and composites out.

Modeled on track3's regression_suite. Motivation is recorded rather than implied: the CodaBench
driver's first-ever real T2 invocation (2026-08-16) crashed with KeyError 'card' and, patched,
produced a NaN leaderboard — defects that survived because nothing continuously scored a known
submission against a known unit. This suite is that something.

The sealed answer is committed under fixtures/<uid>/targets.parquet, out of the unit tree and
without an answer-shaped name, so the published repo carries no reference/ dir or realized*
file. Check 1 stages it back to reference/realized.parquet in a temp copy, so the real
_hydrate_ctx path is still what runs.

Checks, in order:
  0  no-answers     the committed tree contains no answer-shaped path (reference/, realized*,
                    outcome*) -- the firewall check the repo unit sweep (root=units/) misses
  1  golden-exact   minimal driver ctx {unit_dir, output_dir}, answer staged from fixtures/
                    -> gates all pass, composite == expected.json to 1e-9 (the golden parquet
                    is committed, so this is deterministic arithmetic; regenerating through
                    the CLI would couple the pin to numpy's RNG stream)
  2  public-smoke   committed unit has no reference/ -> admissible, score None, fixed reason
  3  g1-missing     forecast_rationale.md deleted        -> inadmissible, code no_output
  4  g1-empty       forecast_rationale.md whitespace     -> inadmissible, code schema_invalid
  5  g0-missing     forecast_meta.json deleted           -> inadmissible at g0
  6  cutoff         corpus doc dated after the as-of     -> the STAGING scan refuses it
  7  g3-thin        draws truncated below n_draws        -> inadmissible at g3
  8  cli-smoke      fresh CLI run on both units          -> gates pass (values not pinned)
  9  negative       the four measured exploits are refused: repeated asset, duplicate primary
                    key, extra grid cell, compression bomb
 10  redaction      no gate detail carries anything but an enum code and integer counts
 11  baseline-read  the published baselines read a unit panel, and read it CORRECTLY
                    (compared against the panel's own pre-as-of series, per asset)
 12  gap-guard      _diffs_without_gaps drops exactly the hole-spanning difference;
                    post-as-of rows are excluded; _extract_dates aligns with the series

### Why checks 3, 4 and 6 changed shape at the 2026-08-22 freeze

3 and 4 used to assert that the refusal *text* named the file. It cannot any more: the public
detail is enum code plus integer counts only, precisely so no free-form string can carry a sealed
value. The refusals are unchanged; what they say to a participant is bounded, and the operator
reason still names the file on the operator path.

6 moved. Under the frozen worker/scoring topology the scoring program receives `input/ref` and
`input/res` and nothing else, so the participant mount -- where the text corpus lives -- is not in
its namespace. The corpus cutoff is enforced before publication, by `cutoff.scan_text_corpus_cutoff`
in the staging gate stack, and that is what check 6 now exercises. A check placed where its inputs
do not exist is a check that silently passes.

Exit 0 only if every check passes. After an INTENTIONAL scoring change, rebuild with
`build_reference.py --regen` and review the expected.json diff.
"""
from __future__ import annotations

import json
import pathlib
import shutil
import sys
import tempfile

try:
    import tomllib  # noqa: F401
except ModuleNotFoundError:
    import tomli
    sys.modules["tomllib"] = tomli

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from qfbench2_track_forecasting import scoring  # noqa: E402

FAILURES: list[str] = []


def check(name, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))
    if not ok:
        FAILURES.append(name)


def run(unit_dir, out_dir):
    ctx = {"unit_dir": pathlib.Path(unit_dir), "output_dir": pathlib.Path(out_dir)}
    return scoring.build_verifier(ctx).run(ctx)


def tmp_copy(src):
    d = pathlib.Path(tempfile.mkdtemp())
    dst = d / src.name
    shutil.copytree(src, dst)
    return dst


def staged_unit(uid):
    """A temp copy of the committed unit with the sealed answer staged back into place.

    The answer is committed under fixtures/<uid>/targets.parquet (out of the unit tree, no
    answer-shaped name); scoring's _hydrate_ctx looks for reference/realized.parquet, so we
    put it there in the temp copy. This exercises the real hydrate path without the repo ever
    carrying an answer-shaped path.
    """
    unit = tmp_copy(HERE / "units" / uid)
    (unit / "reference").mkdir(exist_ok=True)
    shutil.copy(HERE / "fixtures" / uid / "targets.parquet",
                unit / "reference" / "realized.parquet")
    return unit


# Answer-shaped paths must never be committed under the suite. This is the firewall check the
# repo's unit sweep (`.github/validate_units.py`, root=units/) does not reach; running it here
# means CI trips the moment a real answer lands in the tree.
_FORBIDDEN = ("reference", "realized")


def check_no_committed_answers():
    stray = [p.relative_to(HERE).as_posix()
             for p in HERE.rglob("*")
             if p.is_file() and (
                 "reference" in p.relative_to(HERE).parts
                 or p.name.startswith("realized")
                 or p.name.startswith("outcome"))]
    check("no answer-shaped paths committed under regression_suite/",
          not stray, f"found {stray}" if stray else "")


def _scans_clean(corpus, asof) -> bool:
    from qfbench2_common.contracts import OrganizerFault

    from qfbench2_track_forecasting.cutoff import scan_text_corpus_cutoff
    try:
        scan_text_corpus_cutoff(corpus, asof)
    except OrganizerFault:
        return False
    return True


def _negative_controls(unit):
    """Each of these was admissible before 2026-08-22 and is refused now. Measured, not theorised."""
    import pandas as pd

    golden = unit / "golden_submission"

    # 9a. Repeat an asset in the declared grid. Measured: composite 0.2327 -> 0.1659 (-29%).
    sub = tmp_copy(golden)
    meta = json.loads((sub / "forecast_meta.json").read_text())
    meta["asset_ids"] = list(meta["asset_ids"]) + [meta["asset_ids"][0]]
    (sub / "forecast_meta.json").write_text(json.dumps(meta, indent=1))
    v = run(unit, sub)
    check("9a repeated asset refused", not v.admissible, str(v.detail))

    # 9b. Duplicate a (draw, asset, horizon) key. Measured: composite 74.09 -> 0.11 (~650x).
    sub = tmp_copy(golden)
    df = pd.read_parquet(sub / "forecast.parquet")
    pd.concat([df, df.iloc[[0]]], ignore_index=True).to_parquet(
        sub / "forecast.parquet", index=False)
    v = run(unit, sub)
    check("9b duplicate primary key refused", not v.admissible, str(v.detail))

    # 9c. An extra (asset, horizon) cell outside the grid, silently dropped by `reindex` before.
    sub = tmp_copy(golden)
    df = pd.read_parquet(sub / "forecast.parquet")
    extra = df.iloc[[0]].copy()
    extra["asset"] = "NOT-IN-THE-GRID"
    pd.concat([df, extra], ignore_index=True).to_parquet(sub / "forecast.parquet", index=False)
    v = run(unit, sub)
    check("9c extra grid cell refused", not v.admissible, str(v.detail))

    # 9d. A compression bomb: 61 KiB on disk, 4,000,000 rows, 237 MB of RSS before the freeze.
    sub = tmp_copy(golden)
    rows = 2_000_000
    pd.DataFrame({"draw": [0] * rows, "asset": ["A"] * rows,
                  "horizon": [1] * rows, "value": [1.0] * rows}).to_parquet(
        sub / "forecast.parquet", index=False, compression="zstd")
    size = (sub / "forecast.parquet").stat().st_size
    v = run(unit, sub)
    check(f"9d compression bomb refused on the footer ({size} B on disk)",
          not v.admissible, str(v.detail))


def _redaction_control(unit):
    """No gate detail may carry a string other than the enum code. The counts-only projection."""
    import pandas as pd

    cases = {}
    sub = tmp_copy(unit / "golden_submission")
    (sub / "forecast_meta.json").write_text("{not json")
    cases["malformed meta"] = sub

    sub = tmp_copy(unit / "golden_submission")
    meta = json.loads((sub / "forecast_meta.json").read_text())
    meta["asof"] = "1999-01-01"
    (sub / "forecast_meta.json").write_text(json.dumps(meta, indent=1))
    cases["wrong asof"] = sub

    sub = tmp_copy(unit / "golden_submission")
    df = pd.read_parquet(sub / "forecast.parquet")
    df.iloc[:5].to_parquet(sub / "forecast.parquet", index=False)
    cases["truncated grid"] = sub

    for name, out in cases.items():
        v = run(unit, out)
        detail = v.detail
        ok = not v.admissible and all(
            key == "code" or isinstance(value, int) for key, value in detail.items()
        )
        check(f"10 {name}: detail is enum code plus integer counts", ok, str(detail))


def main():
    expected = json.loads((HERE / "expected.json").read_text())

    print("0. no committed answer-shaped paths")
    check_no_committed_answers()

    print("1. golden-exact (driver-shaped minimal ctx, answer staged from fixtures/)")
    for uid, exp in expected["units"].items():
        unit = staged_unit(uid)
        v = run(unit, HERE / "units" / uid / "golden_submission")
        check(f"{uid}: admissible", v.admissible, str(v.labels) if not v.admissible else "")
        if v.admissible:
            drift = abs(v.score - exp["composite"])
            check(f"{uid}: composite pinned", drift < 1e-9,
                  f"got {v.score:.9f} expected {exp['composite']:.9f} (drift {drift:.2e})")
            # Single-cell weight renormalization (track-lead ruling, 2026-08-24). The monthly
            # unit is 1-cell on purpose: its variogram is 0 by construction, so the live
            # weights renormalize over marginal+tail and the baseline anchor stays at 1.0.
            # The daily unit is 2-cell and must keep the card weights byte-identical --
            # that pairing is what pins the rule in BOTH directions.
            cells = v.detail.get("cell_count")
            want_group = "single" if cells == 1 else "multi"
            check(f"{uid}: rank_group is {want_group!r}",
                  v.detail.get("rank_group") == want_group,
                  f"got {v.detail.get('rank_group')!r}")
            w = v.detail.get("weights_effective")
            if cells == 1:
                ok = (w is not None and abs(w[0] - 0.5 / 0.7) < 1e-12
                      and w[1] == 0.0 and abs(w[2] - 0.2 / 0.7) < 1e-12)
                check(f"{uid}: weights renormalized over live components", ok, f"got {w}")
            else:
                check(f"{uid}: card weights untouched", w == [0.5, 0.3, 0.2], f"got {w}")

    print("2. public-smoke (committed unit has no reference/ -> score None, FIXED reason)")
    unit = HERE / "units" / "reg-t2-daily"
    v = run(unit, unit / "golden_submission")
    check("admissible with score None", v.admissible and v.score is None,
          f"admissible={v.admissible} score={v.score}")
    # The reason is a constant, not a value read out of the unit. The pre-freeze version returned
    # `resolves_after` from reference/PENDING.json -- a sealed target date on a participant path.
    check("unscored reason is the fixed constant",
          v.detail.get("unscored_reason") == scoring.UNSCORED_NO_REFERENCE,
          str(v.detail))

    daily = HERE / "units" / "reg-t2-daily"

    print("3. g1-missing rationale")
    sub = tmp_copy(daily / "golden_submission")
    (sub / "forecast_rationale.md").unlink()
    v = run(daily, sub)
    # A DELETED rationale is `no_output`: the file the contract requires is not there. The detail
    # carries the code and nothing else -- naming the file would be free-form text.
    check("inadmissible, code no_output",
          not v.admissible and v.detail.get("code") == "no_output", str(v.detail))

    print("4. g1-empty rationale")
    sub = tmp_copy(daily / "golden_submission")
    (sub / "forecast_rationale.md").write_text("   \n\n")
    v = run(daily, sub)
    # An EMPTY rationale is `schema_invalid`: the file is present and does not satisfy the contract.
    check("inadmissible, code schema_invalid",
          not v.admissible and v.detail.get("code") == "schema_invalid", str(v.detail))

    print("5. g0-missing meta")
    sub = tmp_copy(daily / "golden_submission")
    (sub / "forecast_meta.json").unlink()
    v = run(daily, sub)
    check("inadmissible at g0",
          not v.admissible and not v.gate_results["g0_integrity"].passed)

    print("6. post-as-of corpus document (refused by the STAGING scan, not by g2)")
    from qfbench2_common.contracts import OrganizerFault

    from qfbench2_track_forecasting.cutoff import scan_text_corpus_cutoff, trusted_asof
    unit = tmp_copy(daily)
    card = tomllib.loads((unit / "card.toml").read_text())
    asof = trusted_asof(card)
    check("clean corpus scans clean", _scans_clean(unit / "text", asof))
    idx = json.loads((unit / "text" / "corpus_index.json").read_text())
    (unit / "text" / "doc_99.txt").write_text("a document from the future\n")
    idx["documents"].append({"doc_id": "doc_99", "timestamp": "2099-01-01",
                             "source": "synthetic", "doc_type": "cb_speech",
                             "path": "doc_99.txt"})
    (unit / "text" / "corpus_index.json").write_text(json.dumps(idx, indent=1))
    refused = False
    try:
        scan_text_corpus_cutoff(unit / "text", asof)
    except OrganizerFault:
        refused = True
    check("post-as-of document refused before publication", refused)

    print("7. g3-thin draws")
    import pandas as pd
    sub = tmp_copy(daily / "golden_submission")
    df = pd.read_parquet(sub / "forecast.parquet")
    df[df["draw"] < 50].to_parquet(sub / "forecast.parquet", index=False)
    v = run(daily, sub)
    check("inadmissible at g3",
          not v.admissible and not v.gate_results["g3_domain_semantics"].passed)

    print("8. cli-smoke (fresh run, gates only)")
    from qfbench2_track_forecasting import cli
    for uid in expected["units"]:
        unit = HERE / "units" / uid
        card = tomllib.loads((unit / "card.toml").read_text())
        out = pathlib.Path(tempfile.mkdtemp())
        cli.main(["--panels", str(unit), "--text", str(unit / "text"),
                  "--asof", card["provenance"]["data_cutoff"],
                  "--out", str(out / "forecast.parquet")])
        v = run(unit, out)
        check(f"{uid}: fresh CLI output admissible", v.admissible,
              str(v.labels) if not v.admissible else "")

    print("9. negative controls: the four measured exploits")
    _negative_controls(daily)

    print("10. redaction: every gate detail is enum code plus integer counts")
    _redaction_control(daily)

    print("11. published baselines read the panel, and read it correctly")
    # Non-vacuous on purpose. An earlier draft asserted only `size > 0`, which four separate
    # mutants of _extract_series survived: dropping the asset filter (both assets interleaved),
    # dropping the as-of mask (leakage), and returning a constant array all still "passed".
    import numpy as _np
    import pandas as _pd

    from baselines.base import BaselineForecaster, ForecastRequest

    for uid in expected["units"]:
        unit = HERE / "units" / uid
        card = tomllib.loads((unit / "card.toml").read_text())
        asof = card["provenance"]["data_cutoff"]
        panels = {q.stem: _pd.read_parquet(q) for q in unit.glob("*.parquet")}
        req = ForecastRequest(
            panels=panels,
            asof=asof,
            asset_ids=card["targets"]["asset_ids"],
            horizons=card["targets"]["horizons"],
            n_draws=8,
        )
        for asset in card["targets"]["asset_ids"]:
            got = BaselineForecaster._extract_series(req, asset)
            want = None
            for fr in panels.values():
                acol = next((c for c in ("asset", "asset_id") if c in fr.columns), None)
                if acol is None:
                    continue
                sub = fr[(fr[acol].astype(str) == asset)
                         & (_pd.to_datetime(fr["date"]) <= _pd.Timestamp(asof))]
                if len(sub):
                    want = sub.sort_values("date")["value"].to_numpy(dtype=float)
                    break
            check(
                f"{uid}/{asset}: baseline reads the panel's own pre-as-of series",
                want is not None and got.shape == want.shape and _np.allclose(got, want),
                f"got {got.shape} want {None if want is None else want.shape}",
            )

    # The fixtures stop at their as-of, so nothing in them can prove the leakage guard still
    # fires. Build a frame that deliberately carries post-as-of rows and assert they are cut,
    # and that _extract_dates lines up with _extract_series (if it returns None the gap guard
    # quietly stops working).
    leak = _pd.DataFrame({
        "date": ["2020-01-01", "2020-01-02", "2020-01-03", "2020-06-01"],
        "asset": ["X", "X", "X", "X"],
        "value": [1.0, 2.0, 3.0, 99.0],
    })
    lreq = ForecastRequest(panels={"p": leak}, asof="2020-01-03", asset_ids=["X"],
                           horizons=[1], n_draws=4)
    lseries = BaselineForecaster._extract_series(lreq, "X")
    check("post-as-of rows are excluded from the series",
          lseries.shape == (3,) and float(lseries[-1]) == 3.0, f"got {lseries.tolist()}")
    ldates = BaselineForecaster._extract_dates(lreq, "X")
    check("_extract_dates returns an index aligned with the series",
          ldates is not None and ldates.size == lseries.size,
          f"dates {None if ldates is None else ldates.size} vs series {lseries.size}")

    print("12. the gap guard drops exactly the hole, and only the hole")
    # Neither fixture has a hole, so without these asserts _diffs_without_gaps and
    # _extract_dates can both be deleted outright with the suite still green.
    daily = _pd.to_datetime(
        [f"2020-01-{d:02d}" for d in range(1, 8)] + ["2030-01-01"]
    ).to_numpy()
    vals = _np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 500.0])
    kept = BaselineForecaster._diffs_without_gaps(vals, daily)
    check("daily series: the one gap-spanning difference is dropped",
          kept.size == 6 and _np.allclose(kept, 1.0),
          f"kept {kept.tolist()}")

    monthly = _pd.to_datetime([f"2020-{m:02d}-01" for m in range(1, 13)]).to_numpy()
    mvals = _np.arange(12.0)
    mkept = BaselineForecaster._diffs_without_gaps(mvals, monthly)
    check("monthly series: nothing is dropped", mkept.size == 11, f"kept {mkept.size}")

    nodates = BaselineForecaster._diffs_without_gaps(vals, None)
    check("no dates available: falls back to raw diffs unchanged", nodates.size == 7,
          f"kept {nodates.size}")

    print()
    if FAILURES:
        print(f"REGRESSION: {len(FAILURES)} failure(s): {FAILURES}")
        return 1
    print("ALL REGRESSION CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
