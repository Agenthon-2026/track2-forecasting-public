"""Track-2 reference submission CLI.

Implements the `forecast` verb from the shared submission contract:

    forecast --panels /input/panels/ --text /input/text/ --asof YYYY-MM-DD \
             --out /output/forecast.parquet

and writes the three deliverables the contract requires next to `--out`:

    forecast.parquet         the scored artifact — joint draws [draw, asset, horizon, value]
    forecast_meta.json       the sidecar g1_schema validates
    forecast_rationale.md    required, NEVER scored — the derivation, for human review

This is the statistical floor, not a worked example of using text. It reads the panels and
ignores `--text` entirely, which is stated plainly in the rationale it writes: a submission that
does this is doing the thing Track 2 exists to measure agents beating. It is here so that a
participant has something that provably builds, runs offline and passes g0-g3, and can be edited
into a real agent one step at a time.

Run offline. No network, no model weights, numpy + pandas only.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any

import numpy as np
import pandas as pd

from .limits import ParseLimits

DEFAULT_DRAWS = 500
_RATIONALE_NAME = "forecast_rationale.md"


def _read_panels(panels_dir: pathlib.Path) -> dict[str, pd.DataFrame]:
    """Every parquet under --panels, keyed by filename stem.

    Accepts the contract layout (`/input/panels/*.parquet`) and also tolerates a unit that keeps
    its panels one level up, which is how the shipped exemplar was laid out before this CLI
    existed. Tolerating it here means a card authored either way still runs.
    """
    found = sorted(panels_dir.glob("*.parquet"))
    if not found and panels_dir.parent.is_dir():
        found = sorted(panels_dir.parent.glob("*.parquet"))
    if not found:
        raise SystemExit(f"no .parquet found under {panels_dir} (or its parent)")
    return {p.stem: pd.read_parquet(p) for p in found}


#: Both spellings occur in the shipped cards — the exemplar unit uses `asset_id`, the pilot and
#: prospective batches use `asset`. A reference implementation has to read either, or it works on
#: some cards and not others for a reason that has nothing to do with forecasting.
_ASSET_COLS = ("asset", "asset_id")


def _asset_col(df: pd.DataFrame) -> str | None:
    return next((c for c in _ASSET_COLS if c in df.columns), None)


def _diff_without_gaps(s: pd.Series) -> pd.Series:
    """First differences, with any difference that spans a hole in the data dropped.

    A transfer card ships its target asset as an early window plus a single row at the as-of
    date, with the years between deliberately withheld (the card says so, and says not to
    difference across it). Differenced naively, that hole reads as one day in which the asset
    moved a decade's worth -- on the CNY card it inflated the 5-95% band from under a percent
    to +-7%. The threshold adapts to the panel's own spacing (10x its typical step), so daily
    and monthly panels are both handled and a gapless panel is untouched.
    """
    d = s.diff()
    when = pd.to_datetime(pd.Series(s.index, index=s.index), errors="coerce")
    step = when.diff().dt.days
    if step.notna().sum() == 0:
        return d
    return d.where(step <= max(float(step.median()) * 10.0, 5.0))


def _series(panels: dict[str, pd.DataFrame], asset: str, asof: str) -> pd.Series:
    """The history of one asset up to and including the as-of, from whichever panel holds it."""
    for df in panels.values():
        col = _asset_col(df)
        if col is None:
            continue
        sub = df[df[col].astype(str) == asset]
        if sub.empty:
            continue
        sub = sub.copy()
        # Dates arrive as either strings or datetimes depending on how the panel was written.
        sub["date"] = sub["date"].astype(str).str.slice(0, 10)
        sub = sub[sub["date"] <= asof].sort_values("date")
        if not sub.empty:
            return sub.set_index("date")["value"].astype(float)
    seen = sorted(
        {
            str(v)
            for df in panels.values()
            if (c := _asset_col(df)) is not None
            for v in df[c].unique()
        }
    )
    raise SystemExit(
        f"asset {asset!r} not present in any panel at or before {asof}. "
        f"Panels carry: {', '.join(seen) if seen else '(no asset column found)'}"
    )


def _draw(
    panels: dict[str, pd.DataFrame],
    assets: list[str],
    horizons: list[int],
    asof: str,
    n_draws: int,
    seed: int,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Joint Gaussian random walk, correlated ACROSS ASSETS via their historical daily changes.

    Drawing each asset independently would score badly on purpose: the composite puts 0.3 on the
    joint variogram term precisely to catch marginals that were stapled together. So the shared
    innovation is drawn from the empirical correlation of daily changes and scaled by sqrt(h).
    """
    rng = np.random.default_rng(seed)
    hist = {a: _series(panels, a, asof) for a in assets}
    diffs = pd.DataFrame({a: _diff_without_gaps(s) for a, s in hist.items()}).dropna()
    if len(diffs) < 30:
        raise SystemExit(f"not enough history to estimate covariance ({len(diffs)} rows)")

    last = np.array([hist[a].iloc[-1] for a in assets], dtype=float)
    sd = diffs.std().to_numpy(dtype=float)
    corr = diffs.corr().to_numpy(dtype=float)
    corr = np.nan_to_num(corr, nan=0.0)
    np.fill_diagonal(corr, 1.0)
    # Nearest-PSD nudge: an empirical correlation can be indefinite after nan_to_num.
    w, v = np.linalg.eigh(corr)
    corr = v @ np.diag(np.clip(w, 1e-8, None)) @ v.T
    chol = np.linalg.cholesky(corr)

    out = np.empty((n_draws, len(assets), len(horizons)), dtype=float)
    for hi, h in enumerate(horizons):
        z = rng.standard_normal((n_draws, len(assets))) @ chol.T
        out[:, :, hi] = last + z * (sd * np.sqrt(h))
    meta = {
        "last": {a: float(last[i]) for i, a in enumerate(assets)},
        "daily_sd": {a: float(sd[i]) for i, a in enumerate(assets)},
        "n_history_rows": int(len(diffs)),
    }
    return out, meta


def _rationale(
    unit_id: str,
    asof: str,
    assets: list[str],
    horizons: list[int],
    n_draws: int,
    stats: dict[str, Any],
    text_dir: pathlib.Path,
) -> str:
    n_docs = len(list(text_dir.glob("*.txt"))) if text_dir.is_dir() else 0
    ladder = "\n".join(
        f"| {a} | {stats['last'][a]:.4f} | {stats['daily_sd'][a]:.4f} | "
        f"{stats['daily_sd'][a] * np.sqrt(h):.4f} | {h} |"
        for a in assets
        for h in horizons
    )
    return f"""# Forecast rationale — {unit_id}

As of **{asof}**, joint distribution over {", ".join(assets)} at horizon(s)
{", ".join(str(h) for h in horizons)} business days. {n_draws} draws.

## Anchor

The last observed value of each series at the as-of, taken from the shipped panels
({stats["n_history_rows"]} rows of overlapping daily history used for the covariance).

## Adjustments

**None.** This is a driftless random walk: the centre is the anchor, unadjusted. Every
adjustment is zero and is listed as such rather than omitted, so the ledger below sums.

## Scale and shape

Per-asset daily standard deviation of first differences, scaled by sqrt(horizon). Gaussian
shape — deliberately not fat-tailed, since nothing here justifies a tail view.

The draws are **joint**: a single innovation vector is drawn per draw from the empirical
correlation of daily changes across assets, so cross-asset structure is preserved rather than
assembled from independent marginals. The composite's variogram term scores exactly that.

## Adjustment ledger

| asset | anchor | daily sd | sd at horizon | horizon (BD) |
|---|---|---|---|---|
{ladder}

Centre = anchor + 0 for every asset and horizon.

## What the text corpus contributed

**Nothing.** {n_docs} document(s) were present at the text path and none was read. This is the
statistical floor a reasoning agent has to beat, not an example of using text — the whole point
of Track 2 is the gap between this and an agent that reads the corpus. A real submission would
use the documents to move the centre, skew the distribution, or widen the tails, and would say
here which document drove which adjustment and by how much.

## What would change this forecast

Any evidence at all. It currently uses none beyond the panel's own volatility.
"""


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="forecast",
        description="QFBench 2.0 Track-2 reference submission (statistical floor).",
    )
    p.add_argument("--panels", type=pathlib.Path, required=True)
    p.add_argument("--text", type=pathlib.Path, required=True)
    p.add_argument("--asof", required=True)
    p.add_argument(
        "--out",
        type=pathlib.Path,
        required=True,
        help="path to forecast.parquet; the sidecars are written beside it",
    )
    p.add_argument(
        "--card",
        type=pathlib.Path,
        default=None,
        help="card.toml; defaults to <panels>/../card.toml. Supplies assets/horizons.",
    )
    p.add_argument("--n-draws", type=int, default=None)
    p.add_argument("--seed", type=int, default=0)
    a = p.parse_args(argv)

    # --panels names the unit root (contract) but a card may still keep a panels/ subdir, so look
    # in the panels dir first and only then one level up. Deriving it as parent/ unconditionally
    # resolves to "/" when --panels is /input/, which is how this was wrong the first time.
    card_path = a.card
    if card_path is None:
        for cand in (a.panels / "card.toml", a.panels.parent / "card.toml"):
            if cand.exists():
                card_path = cand
                break
    if card_path is None or not card_path.exists():
        raise SystemExit(
            f"card.toml not found in {a.panels} or {a.panels.parent}; pass --card explicitly"
        )
    import tomllib

    card = tomllib.loads(card_path.read_text())
    tgt = card["targets"]
    assets = list(tgt["asset_ids"])
    horizons = [int(h) for h in tgt["horizons"]]
    unit_id = card["task"]["id"]
    # The card's `n_draws_min` is AUTHORITATIVE and was previously advisory: the reference
    # producer read it, the scorer never did, and the scorer instead compared the submission
    # against the participant's own declared `n_draws`. It is now a floor on both sides — this
    # producer honours it, and `limits.min_draws` enforces the contract floor in the scorer, in
    # code no missing module can skip.
    card_floor = int(card.get("scoring", {}).get("params", {}).get("n_draws_min", 0) or 0)
    floor = max(card_floor, DEFAULT_DRAWS, ParseLimits().min_draws)
    n_draws = max(a.n_draws or floor, floor)
    if n_draws > ParseLimits().max_draws:
        raise SystemExit(
            f"--n-draws {n_draws} exceeds the contract ceiling {ParseLimits().max_draws}; the "
            "scorer refuses a submission above it"
        )

    panels = _read_panels(a.panels)
    samples, stats = _draw(panels, assets, horizons, a.asof, n_draws, a.seed)

    out_dir = a.out.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {"draw": d, "asset": asset, "horizon": h, "value": float(samples[d, ai, hi])}
            for d in range(n_draws)
            for ai, asset in enumerate(assets)
            for hi, h in enumerate(horizons)
        ]
    ).to_parquet(a.out, index=False)

    (out_dir / "forecast_meta.json").write_text(
        json.dumps(
            {
                "unit_id": unit_id,
                "asof": a.asof,
                "representation": "samples",
                "asset_ids": assets,
                "horizons": horizons,
                "n_draws": n_draws,
                "target": tgt.get("target_type", "level"),
                "rationale": {
                    "file": _RATIONALE_NAME,
                    "method": "joint gaussian random walk, no text",
                },
            },
            indent=2,
        )
        + "\n"
    )

    (out_dir / _RATIONALE_NAME).write_text(
        _rationale(unit_id, a.asof, assets, horizons, n_draws, stats, a.text)
    )

    print(f"wrote {a.out.name}, forecast_meta.json and {_RATIONALE_NAME} to {out_dir}")
    print(f"  {len(assets)} asset(s) x {len(horizons)} horizon(s), {n_draws} draws")
    return 0


if __name__ == "__main__":
    sys.exit(main())
