"""A minimal REASONING agent: the mechanism the track is named for, and nothing more.

## Why this file exists

`baselines/` holds five text-blind adapters. Every one of them reports
`real_adapter_implemented: False` and returns a Gaussian random walk, and each says in its own
metadata that it never opens the corpus. They are the floor a reasoning agent has to beat, and
they are honest about being placeholders -- but between them and a submission there was nothing
showing how a forecast is supposed to USE `/input/text/` at all.

This is that missing example. It is deliberately the smallest thing that demonstrates the loop:

    read the dated corpus  ->  ask the house model for two numbers  ->  move the distribution

It is NOT a competitive method and is not tuned. If it beats the statistical floor, that gap is
the quantity the track exists to measure; if it does not, that is a real result about this prompt
and this model, not a bug in the harness.

## What it does, precisely

The numeric half is the joint Gaussian random walk from
`qfbench2_track_forecasting/cli.py` -- correlated across assets from the empirical covariance of
daily changes, because the composite puts 0.3 on the joint variogram term and independently drawn
marginals are penalised there by design. That part is imported, not reimplemented.

The reasoning half asks the model for exactly two scalars per asset:

    drift_bp    a directional shift, in basis points of the MAGNITUDE of the as-of level,
                applied to the mean and clamped to +-3 horizon standard deviations
    vol_scale   a multiplier on the standard deviation, clamped to [0.5, 2.0]

Two scalars rather than a distribution because they are auditable: a reviewer can read them in
`forecast_rationale.md`, compare them against the documents, and disagree. A model asked for 500
draws directly would produce numbers nobody can check.

`drift_bp` is stated against the level's MAGNITUDE, not the signed level, and both the level and
the horizon standard deviation go into the prompt. Track 2 panels are not all prices: 11 of the
169 shipped asset-series have a negative as-of anchor, and against the signed level "up 250 bp"
moved those distributions DOWN. A further 14 have an anchor small enough that 250 bp of it is
under 2% of the forecast's own width, which is why the model is told that width and the drift is
bounded in units of it. Everything the model sends is still checked before it is used: `NaN` and
`Infinity` are legal JSON literals to `json.loads` and an unguarded one produces an all-NaN
parquet that `g3_domain_semantics` refuses, so a non-finite scalar drops that asset's adjustment
and says so in the ledger.

## The cutoff is enforced here, not assumed

`corpus_index.json` carries a `timestamp` per document and the harness gates on it (g2), but a
submission that reads a file the index dates after `--asof` has already leaked before any gate
runs. This filters on the index and refuses to read anything later, and records how many documents
that excluded. `note` in the shipped indexes is explicit that minutes and COT timestamps are
PUBLIC RELEASE dates, which is what makes them usable at all.

## Failure is labelled, never silent

If `MODEL_ENDPOINT` is unset, or the call fails, or the reply does not parse, the forecast is the
unadjusted statistical floor and both `forecast_meta.json` and `forecast_rationale.md` say so:

    reasoning_applied: false
    reasoning_skipped_reason: "<why>"

Those two keys are machine-readable in the sidecar, not prose only: a reviewer counting how many
submissions actually reached a model should not have to parse markdown to find out.

The five placeholder adapters were corrected once for claiming a provenance they did not have
(`theta_arima.py:134-141`). The same rule applies here: an agent that silently degrades to the
floor while reporting itself as a reasoning run makes every uplift number downstream meaningless.

## Usage

    MODEL_ENDPOINT=https://... MODEL_NAME=... \
      python3 -m baselines.reasoning_agent \
        --panels /input/panels --text /input/text --asof 2024-05-31 \
        --card /input/card.toml --out /output/forecast.parquet

Reads only `/input`, writes only `/output`, and calls nothing but `MODEL_ENDPOINT`.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import pathlib
import sys
import urllib.error
import urllib.request
from typing import Any

import numpy as np
import pandas as pd

_TIMEOUT_SEC = 60
_MAX_DOC_CHARS = 6000
_MAX_DOCS = 8
_VOL_CLAMP = (0.5, 2.0)
#: Ceiling on the drift, expressed in horizon standard deviations rather than in the target's own
#: units, because Track 2 panels span yields (~4), FX (~1) and factor returns (~0.006) and no
#: absolute ceiling is meaningful across all three.
_DRIFT_SD_CLAMP = 3.0
#: `qfbench2_track_forecasting.limits.ParseLimits.min_draws`. The scorer refuses a submission
#: below it, and `cli.py` already floors on it -- an example that quietly emits an inadmissible
#: parquet when a participant passes a smaller `--n-draws` teaches the wrong lesson.
_MIN_DRAWS = 200


# --------------------------------------------------------------------------- corpus
def read_corpus(text_dir: pathlib.Path, asof: str) -> tuple[list[dict[str, Any]], int, int]:
    """Documents dated at or before `asof`, newest first.

    Returns `(kept, excluded_by_date, dropped_by_prompt_budget)`. The two counts are reported
    separately because they mean opposite things: the first is the cutoff doing its job, the
    second is this file's own `_MAX_DOCS` prompt budget throwing away admissible evidence. Nine
    of the shipped units index more than `_MAX_DOCS` documents, so on those the second count is
    non-zero and a reader who saw only a single "excluded" number would misread the ledger.

    Filtering happens on `corpus_index.json`, which is the organizer's dated manifest. A file on
    disk with no index entry is NOT read: an unindexed document has no timestamp, and a document
    whose date cannot be established cannot be shown to predate the cutoff.
    """
    index_path = text_dir / "corpus_index.json"
    if not index_path.is_file():
        return [], 0, 0
    index = json.loads(index_path.read_text(encoding="utf-8"))
    kept: list[dict[str, Any]] = []
    excluded = 0
    for doc in index.get("documents", []):
        ts = str(doc.get("timestamp", ""))[:10]
        if not ts or ts > asof:
            excluded += 1
            continue
        path = text_dir / doc.get("file", "")
        if not path.is_file():
            excluded += 1
            continue
        kept.append(
            {
                "doc_id": doc.get("doc_id"),
                "timestamp": ts,
                "doc_type": doc.get("doc_type"),
                "source": doc.get("source"),
                "text": path.read_text(encoding="utf-8", errors="replace")[:_MAX_DOC_CHARS],
            }
        )
    kept.sort(key=lambda d: str(d["timestamp"]), reverse=True)
    return kept[:_MAX_DOCS], excluded, max(0, len(kept) - _MAX_DOCS)


# --------------------------------------------------------------------------- the model call
def build_prompt(
    assets: list[str],
    horizons: list[int],
    asof: str,
    target_type: str,
    last: dict[str, float],
    sd_h: dict[str, float],
    docs: list[dict[str, Any]],
) -> str:
    """The prompt states BOTH the as-of level and the horizon standard deviation.

    Stating the level alone is not enough to size `drift_bp`. Track 2 panels are not all prices:
    across the 104 shipped units, 25 of 169 asset-series carry an as-of level small enough that a
    250 bp move of it is under 2% of the horizon standard deviation -- on `t2-F1-ai-mom-2024` the
    MOM anchor is -0.0065 and 250 bp of it moves the distribution by 0.1% of its own width. The
    model cannot ask for a meaningful drift without knowing the width it is being compared to, so
    both numbers go in and the reply is bounded in units of that width.
    """
    lines = [
        "You are adjusting a statistical forecast using dated documents.",
        f"As-of date: {asof}. Nothing after this date is known to you.",
        f"Target type: {target_type}. Horizons (business days): {horizons}.",
        "",
        "Per asset: the level at the as-of date, and the statistical standard deviation of the",
        f"forecast at the longest horizon ({max(horizons)} business days):",
    ]
    lines += [f"  {a}: level {last[a]:.6f}, horizon sd {sd_h[a]:.6f}" for a in assets]
    lines += ["", f"Documents ({len(docs)}), newest first:"]
    for d in docs:
        lines += [f"--- {d['doc_id']} ({d['timestamp']}, {d['doc_type']}) ---", d["text"], ""]
    lines += [
        "For EACH asset, give two numbers:",
        "  drift_bp  : expected directional shift over the longest horizon, in basis points of",
        "              the MAGNITUDE of the current level. Positive means up regardless of the",
        "              sign of that level. Use 0 if the documents say nothing. The resulting",
        f"              shift is clamped to +-{_DRIFT_SD_CLAMP:.0f} horizon standard deviations.",
        "  vol_scale : multiplier on the statistical standard deviation, in [0.5, 2.0].",
        "              >1 if the documents imply more uncertainty than usual, <1 if less.",
        "",
        "Both must be finite numbers. NaN and Infinity are rejected and the adjustment dropped.",
        "",
        "Reply with JSON only, no prose:",
        '{"assets": {"<asset>": {"drift_bp": <float>, "vol_scale": <float>,',
        '  "because": "<one sentence citing a doc_id>"}}}',
    ]
    return "\n".join(lines)


def call_model(prompt: str) -> tuple[dict[str, Any] | None, str]:
    """(parsed, reason_if_skipped). The ONLY network call this module makes."""
    endpoint = os.environ.get("MODEL_ENDPOINT", "").strip()
    model = os.environ.get("MODEL_NAME", "").strip()
    if not endpoint:
        return None, "MODEL_ENDPOINT is unset"
    if not model:
        return None, "MODEL_NAME is unset"

    body = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "max_tokens": 1200,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        endpoint.rstrip("/") + "/chat/completions",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    token = os.environ.get("MODEL_API_KEY", "").strip()
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT_SEC) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
        return None, f"{type(exc).__name__}: {exc}"

    try:
        content = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return None, "reply had no choices[0].message.content"
    start, end = content.find("{"), content.rfind("}")
    if start < 0 or end <= start:
        return None, "reply contained no JSON object"
    try:
        return json.loads(content[start : end + 1]), ""
    except ValueError as exc:
        return None, f"reply JSON did not parse: {exc}"


def apply_adjustment(
    samples: np.ndarray,
    assets: list[str],
    last: dict[str, float],
    sd_h: dict[str, float],
    parsed: dict[str, Any],
) -> tuple[np.ndarray, dict[str, dict[str, Any]]]:
    """Shift the mean and scale the spread, per asset. Clamped, and reported.

    Applied to the DRAWS rather than re-sampling, so the cross-asset correlation the statistical
    half established is preserved exactly -- the reasoning half moves the distribution, it does
    not replace it.

    Three things the model can send that must not reach the parquet:

    * **Non-finite numbers.** `json.loads` accepts the bare literals `NaN` and `Infinity`, so a
      model that emits either produces an all-NaN forecast -- measured: 500 of 500 rows invalid,
      `g3_domain_semantics` fails, `admissible: false`. Silently writing a submission that is
      guaranteed to be refused is the same silent-degradation failure this file exists to avoid,
      so a non-finite scalar drops that asset's adjustment and records why.
    * **A negative as-of level.** `drift_bp` is basis points of the anchor, and 11 of the 169
      shipped asset-series have a NEGATIVE anchor (`t2-F1-ai-mom-2024` MOM is -0.0065). Against
      the raw anchor, "up 250 bp" moved those distributions DOWN. The magnitude is used, so the
      documented meaning -- positive is up -- holds on every card.
    * **An unbounded drift.** `drift_bp` had no ceiling: a reply of 1e12 moved the mean to 1e8
      and still passed every gate. The shift is clamped to a few horizon standard deviations,
      which is the only scale on which "large" means anything across yields, FX and factors.
    """
    out = samples.copy()
    applied: dict[str, dict[str, Any]] = {}
    per_asset = (parsed or {}).get("assets", {})
    for i, a in enumerate(assets):
        spec = per_asset.get(a) or {}
        note = ""
        try:
            drift_bp = float(spec.get("drift_bp", 0.0))
            vol = float(spec.get("vol_scale", 1.0))
        except (TypeError, ValueError):
            drift_bp, vol, note = 0.0, 1.0, "unreadable drift_bp/vol_scale; adjustment dropped"
        if not math.isfinite(drift_bp) or not math.isfinite(vol):
            drift_bp, vol, note = 0.0, 1.0, "non-finite drift_bp/vol_scale; adjustment dropped"
        vol = min(max(vol, _VOL_CLAMP[0]), _VOL_CLAMP[1])
        # Magnitude, not the signed level: see the docstring. Then clamp on the one scale that is
        # comparable across panels -- the width of the forecast this drift is moving.
        shift = abs(last[a]) * drift_bp / 10_000.0
        ceiling = _DRIFT_SD_CLAMP * sd_h[a]
        if abs(shift) > ceiling:
            note = f"drift clamped from {shift:+.6g} to {ceiling:+.6g} ({_DRIFT_SD_CLAMP} sd)"
            shift = math.copysign(ceiling, shift)
        centre = out[:, i, :].mean(axis=0, keepdims=True)
        out[:, i, :] = centre + (out[:, i, :] - centre) * vol + shift
        applied[a] = {
            "drift_bp": drift_bp,
            "vol_scale": vol,
            "shift": shift,
            "note": note,
            "because": str(spec.get("because", ""))[:300],
        }
    return out, applied


def main(argv: list[str] | None = None) -> int:
    import tomllib

    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--panels", required=True)
    ap.add_argument("--text", required=True)
    ap.add_argument("--asof", required=True)
    ap.add_argument("--card", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n-draws", type=int, default=500)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args(argv)

    # The statistical half, imported rather than reimplemented.
    from qfbench2_track_forecasting.cli import _draw, _read_panels

    card = tomllib.loads(pathlib.Path(a.card).read_text(encoding="utf-8"))
    t = card["targets"]
    assets, horizons = list(t["asset_ids"]), [int(h) for h in t["horizons"]]
    panels = _read_panels(pathlib.Path(a.panels))
    # `_draw` returns (samples, meta); meta already carries the as-of level per asset, so the
    # drift below is expressed against the same number the statistical half used rather than a
    # second, independently derived one.
    n_draws = max(a.n_draws, _MIN_DRAWS)
    if n_draws != a.n_draws:
        print(f"note: --n-draws {a.n_draws} raised to the contract floor {_MIN_DRAWS}")
    samples, draw_meta = _draw(panels, assets, horizons, a.asof, n_draws, a.seed)
    last = {x: float(draw_meta["last"][x]) for x in assets}
    # sd of the forecast at the LONGEST horizon: sqrt(h) x the daily sd the statistical half fit.
    # This is the scale the drift is stated against and clamped on, and it goes in the prompt.
    sd_h = {x: float(draw_meta["daily_sd"][x]) * math.sqrt(max(horizons)) for x in assets}

    docs, excluded, truncated = read_corpus(pathlib.Path(a.text), a.asof)
    if not docs:
        parsed, reason = None, "no corpus document is dated at or before the as-of date"
    else:
        parsed, reason = call_model(
            build_prompt(assets, horizons, a.asof, t["target_type"], last, sd_h, docs)
        )

    applied: dict[str, dict[str, Any]] = {}
    if parsed is None:
        reasoning_applied = False
    else:
        samples, applied = apply_adjustment(samples, assets, last, sd_h, parsed)
        reasoning_applied, reason = True, ""

    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {"draw": d, "asset": x, "horizon": h, "value": float(samples[d, i, j])}
        for d in range(samples.shape[0])
        for i, x in enumerate(assets)
        for j, h in enumerate(horizons)
    ]
    pd.DataFrame(rows).to_parquet(out, index=False)
    (out.parent / "forecast_meta.json").write_text(
        json.dumps(
            {
                "unit_id": card["task"]["id"],
                "asof": a.asof,
                "representation": "samples",
                "asset_ids": assets,
                "horizons": horizons,
                "n_draws": n_draws,
                "target": t["target_type"],
                # The docstring promises these two keys in the metadata, so they are IN the
                # metadata, not only in the prose rationale. `forecast.schema.json` sets no
                # `additionalProperties: false`, and `rationale` is a declared optional key
                # whose own object is open, so both are valid sidecar content -- verified by
                # running the emitted file through g1_schema.
                "reasoning_applied": reasoning_applied,
                "reasoning_skipped_reason": reason if not reasoning_applied else "",
                "rationale": {
                    "file": "forecast_rationale.md",
                    "method": (
                        "joint gaussian random walk + model-supplied drift_bp/vol_scale"
                        if reasoning_applied
                        else "joint gaussian random walk, unadjusted (reasoning skipped)"
                    ),
                    "documents_read": len(docs),
                    "documents_excluded_by_cutoff": excluded,
                    "documents_over_prompt_budget": truncated,
                },
            },
            indent=2,
        )
    )

    (out.parent / "forecast_rationale.md").write_text(
        "\n".join(
            [
                f"# Forecast rationale — {card['task']['id']}",
                "",
                f"**As of {a.asof}. Assets: {', '.join(assets)}. Horizons: {horizons}.**",
                "",
                "## Statistical half",
                "",
                "Joint Gaussian random walk from `qfbench2_track_forecasting.cli._draw`:",
                "innovations are drawn from the empirical correlation of daily changes, so curve",
                "shape is preserved rather than assembled from independent marginals.",
                "",
                "## Reasoning half",
                "",
                f"- documents read: **{len(docs)}** (dated <= {a.asof})",
                f"- documents excluded by the cutoff or a missing index entry: **{excluded}**",
                f"- documents dropped by this file's {_MAX_DOCS}-document prompt budget: "
                f"**{truncated}**",
                f"- adjustment applied: **{reasoning_applied}**",
                *([f"- skipped because: {reason}"] if not reasoning_applied else []),
                "",
                *(
                    [
                        "| asset | drift_bp | vol_scale | shift | because | note |",
                        "|---|---|---|---|---|---|",
                    ]
                    + [
                        f"| {k} | {v['drift_bp']:+.1f} | {v['vol_scale']:.2f} | "
                        f"{v['shift']:+.6g} | {v['because']} | {v['note']} |"
                        for k, v in applied.items()
                    ]
                    if applied
                    else [
                        "No per-asset adjustment was applied; the numbers above are the",
                        "statistical floor.",
                    ]
                ),
                "",
                "## What would change this",
                "",
                "A document dated at or before the as-of date that contradicts the cited",
                "ones. Anything after that date is not knowable here and was not read.",
            ]
        )
        + "\n"
    )

    print(f"wrote {out.name} + sidecars to {out.parent}")
    print(f"  {len(assets)} asset(s) x {len(horizons)} horizon(s), {n_draws} draws")
    print(
        f"  corpus: {len(docs)} read, {excluded} excluded, {truncated} over budget"
        f" · reasoning_applied={reasoning_applied}"
        + (f" ({reason})" if not reasoning_applied else "")
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
