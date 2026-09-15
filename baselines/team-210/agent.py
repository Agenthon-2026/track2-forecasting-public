#!/usr/bin/env python3
"""Agenthon 2026 Track 2 submission - `forecast`.

    forecast --panels /input/panels/ --text /input/text/ \
             [--asof YYYY-MM-DD] --out /output/forecast.parquet

Three deliverables, and the third is the one people lose a run on:

    forecast.parquet        long form: draw, asset, horizon, value
    forecast_meta.json      bound to the card by g2 - unit_id, asof and target
                            must EQUAL the card's, not merely resemble them
    forecast_rationale.md   REQUIRED and NEVER SCORED. g1 checks it exists and
                            is non-empty. Omitting it makes an otherwise good
                            forecast inadmissible.

The grid is read from card.toml rather than restated. --asof is optional: the
default CMD ships without it, and the card's own end-of-data date is the
authority when the flag is absent.

Survival contract (mirrors the Track 1 agent): whatever happens inside, all
three files exist when this process exits, and it exits 0. A SystemExit that
left zero files behind was this agent's own g1 failure mode - a degraded
forecast scores badly; no files scores nothing and says nothing.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from forecast_core import (asof as asof_mod, llm_signal, panel_loader,  # noqa: E402
                           rationale, scenario_mixture, self_check)

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None


def read_card(unit_dir: pathlib.Path, notes: list[str]) -> dict:
    card_path = unit_dir / "card.toml"
    if not card_path.is_file() or tomllib is None:
        notes.append(f"no readable card.toml under {unit_dir}")
        return {}
    try:
        return tomllib.loads(card_path.read_text(encoding="utf-8",
                                                 errors="replace"))
    except Exception as error:
        notes.append(f"card.toml unparseable ({type(error).__name__})")
        return {}


def read_grid(card: dict, unit_dir: pathlib.Path, notes: list[str]) -> dict:
    """asset_ids, horizons and target_type come from the card. Never restate.

    unit_id is hunted across the spellings cards actually use: g2 binds
    forecast_meta.json to the card by EQUALITY, and a fallback to the
    directory name is a guess that happens to hold on the exemplar only.
    """
    unit_id = (card.get("task", {}).get("id")
               or card.get("unit", {}).get("id")
               or card.get("id") or card.get("unit_id"))
    if unit_id is None:
        unit_id = unit_dir.name
        notes.append("unit_id not found in card; using directory name")

    targets = card.get("targets") or card.get("task", {}).get("targets") or {}
    grid = {"unit_id": unit_id,
            "asset_ids": list(targets.get("asset_ids") or []),
            "horizons": list(targets.get("horizons") or []),
            "target": targets.get("target_type", "level")}
    if not grid["asset_ids"] or not grid["horizons"]:
        notes.append("card declares no usable [targets] grid")
    return grid


def write_outputs(out_path: pathlib.Path, draws, meta: dict,
                  rationale_text: str) -> None:
    out_dir = out_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    draws.to_parquet(out_path, index=False)
    (out_dir / "forecast_meta.json").write_text(
        json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    (out_dir / "forecast_rationale.md").write_text(
        rationale_text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("verb", nargs="?", default="forecast")
    parser.add_argument("--panels", default="/input/panels/")
    parser.add_argument("--text", default="/input/text/")
    parser.add_argument("--asof", default=None,
                        help="YYYY-MM-DD; defaults to the card's data-end date")
    parser.add_argument("--out", default="/output/forecast.parquet")
    parser.add_argument("--unit-dir", default="/input")
    parser.add_argument("--n-draws", type=int, default=500)
    parser.add_argument("--no-text", action="store_true",
                        help="statistical floor only; the text corpus is left unread")
    args, unknown = parser.parse_known_args()

    started = time.time()
    out_path = pathlib.Path(args.out)
    notes: list[str] = []
    if unknown:
        notes.append(f"ignored unrecognised arguments: {unknown}")

    unit_dir = pathlib.Path(args.unit_dir)
    if not (unit_dir / "card.toml").is_file() and (pathlib.Path(args.panels).parent / "card.toml").is_file():
        unit_dir = pathlib.Path(args.panels).parent
    card = read_card(unit_dir, notes)
    grid = read_grid(card, unit_dir, notes)

    asof = args.asof or asof_mod.from_card(card)
    if asof is None:
        asof = "2100-01-01"  # read everything rather than nothing
        notes.append("no --asof and no data-end date in card; cutoff disabled")

    try:
        panels, loader_notes = panel_loader.load(
            pathlib.Path(args.panels), unit_dir, asof)
        notes += loader_notes

        assets = grid["asset_ids"] or sorted(panels.get("asset", []).unique())[:4]
        horizons = grid["horizons"] or [1, 5, 21]

        # llm_signal upgrades the lexicon reading when MODEL_ENDPOINT is
        # reachable and degrades to it when not - so the three uplift
        # conditions (floor / lexicon / llm) share every other code path.
        # Text drift is OPT-IN (T2_TEXT=1). Measured 2026-09-05 on the
        # organizer's own composite against their random-walk baseline
        # (16 units x 6 origins, median normalised composite): raw block
        # bootstrap 0.982 (57% of origins beat the walk); + lexicon drift
        # 0.998 (50%); + EWMA vol adjust 1.014; + self-correct widening 1.075.
        # Every widening layer lost to the walk. The corpus is still read
        # for the rationale; only the drift injection is gated.
        use_text = (not args.no_text) and os.environ.get("T2_TEXT") == "1"
        signal = ({} if not use_text
                  else llm_signal.read_corpus(pathlib.Path(args.text), asof,
                                              assets, horizons,
                                              grid["target"]))
        if not use_text and not args.no_text:
            notes.append("text drift disabled by default (T2_TEXT=1 enables); "
                         "measured to lose to the random-walk baseline on the "
                         "official composite")
        if signal.get("reader"):
            notes.append(f"text reader: {signal['reader']}")
        # Verifier-first, T1-style: try to falsify the distribution against
        # the recent past before shipping it; only ever widen. Measured twice
        # on 16 public units and DISABLED by default (crps 0.5115 -> 0.5255,
        # then 0.5205 after retuning: the public panels are calm and the
        # guardrail only paid rent as insurance). Env-gated for sealed-unit
        # regimes where that insurance may be worth its premium.
        correction = 1.0
        if os.environ.get("T2_SELF_CORRECT") == "1":
            correction, check_notes = self_check.dispersion_correction(
                panels, assets, horizons)
            notes += check_notes

        # log_return cards: the panel holds per-period returns and the graded
        # target is their SUM over the horizon anchored at 0. Cumulate first,
        # forecast the cumulative level, then remove the as-of anchor.
        anchors: dict = {}
        if grid["target"] == "log_return":
            panels, anchors = panel_loader.cumulative_from_returns(panels)
            notes.append("log_return target: forecasting cumulative returns "
                         "anchored at 0 (per-period returns cumulated)")

        draws, mix_notes = scenario_mixture.build(
            panels, assets, horizons, n_draws=args.n_draws, signal=signal,
            vol_adjust=os.environ.get("T2_VOL_ADJUST") == "1",
            extra_widen=correction)
        notes += mix_notes
        if anchors:
            draws["value"] = draws["value"] - draws["asset"].map(anchors).fillna(0.0)

        meta = {
            "unit_id": grid["unit_id"],
            "asof": asof,
            "representation": "samples",
            "asset_ids": assets,
            "horizons": horizons,
            "n_draws": args.n_draws,
            "target": grid["target"],
            "rationale": {"file": "forecast_rationale.md",
                          "method": scenario_mixture.METHOD_NAME},
        }
        write_outputs(out_path, draws, meta,
                      rationale.write(grid, asof, signal, args.n_draws,
                                      draws=draws, notes=notes))
        print(json.dumps({
            "unit": grid["unit_id"], "rows": len(draws),
            "assets": len(assets), "horizons": horizons,
            "text_documents_used": len(signal.get("documents", [])),
            "notes": notes,
            "wall_sec": round(time.time() - started, 2),
        }))
    except BaseException as error:  # noqa: BLE001 - survival contract
        import pandas as pd
        notes.append(f"unhandled {type(error).__name__}: {str(error)[:200]}")
        stub = pd.DataFrame(columns=["draw", "asset", "horizon", "value"])
        meta = {"unit_id": grid["unit_id"], "asof": asof,
                "representation": "samples",
                "asset_ids": grid["asset_ids"], "horizons": grid["horizons"],
                "n_draws": 0, "target": grid["target"],
                "rationale": {"file": "forecast_rationale.md",
                              "method": "stub after internal failure"}}
        try:
            write_outputs(out_path, stub, meta,
                          "# Forecast rationale - degraded\n\n"
                          "The pipeline failed before producing draws. "
                          "Diagnostics:\n\n"
                          + "\n".join(f"- {n}" for n in notes) + "\n")
        except BaseException:
            pass
        print(json.dumps({"unit": grid["unit_id"], "rows": 0, "notes": notes}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
