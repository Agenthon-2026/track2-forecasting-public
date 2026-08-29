"""Synthetic Track 2 fixtures. Nothing here comes from, or resembles, a sealed unit.

## Executive summary (read this first)

Every asset id is `SYN-*`, every unit handle is `u-` + hex, every date is in 2020, and every
realized value is a small round number chosen so the arithmetic in the assertions is legible. No
value, date, identifier or canary from the private tree appears in this directory, and the builders
below are the only source of test data — a test that reaches for a real unit is the firewall
breach the public suite exists to prevent.

The signing material is the Hub's **published development seed** (`contracts.fixtures.DEV_SEED`),
which exists precisely so a public test suite can build a valid signed C1 without holding a
production key. A plan signed with it verifies only against the development trust store.
"""

from __future__ import annotations

import json
import pathlib
import shutil
from collections.abc import Iterable, Sequence
from typing import Any

import numpy as np
import pytest
from qfbench2_common.contracts import (
    CONTRACT_SET,
    compute_roster_digest,
    digest_json,
    sign_payload,
)
from qfbench2_common.contracts.fixtures import DEV_KEY_ID, DEV_SEED
from qfbench2_common.contracts.plan import SCHEMA_VERSION as PLAN_SCHEMA_VERSION

SIGNED_AT = "2026-08-21T09:00:00Z"

#: Synthetic grid used by almost every test. Two assets, two horizons, four cells.
ASSETS: tuple[str, ...] = ("SYN-A", "SYN-B")
HORIZONS: tuple[int, ...] = (1, 5)
ASOF = "2020-06-30"
TARGET_DATES: tuple[str, ...] = ("2020-07-01", "2020-07-07")


# --------------------------------------------------------------------------------------------
# Parquet helpers
# --------------------------------------------------------------------------------------------


def write_parquet(path: pathlib.Path, columns: dict[str, list[Any]], **kwargs: Any) -> None:
    """Write a parquet from column arrays. Used for both valid and deliberately broken files."""
    import pyarrow as pa
    import pyarrow.parquet as pq

    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.table(columns), path, **kwargs)


def forecast_rows(
    *,
    assets: Sequence[str] = ASSETS,
    horizons: Sequence[int] = HORIZONS,
    n_draws: int = 200,
    centre: float = 1.0,
    spread: float = 0.25,
    seed: int = 7,
) -> dict[str, list[Any]]:
    """A complete, unique, finite draw-format grid. The positive control every negative case edits."""
    rng = np.random.default_rng(seed)
    draw: list[int] = []
    asset: list[str] = []
    horizon: list[int] = []
    value: list[float] = []
    for d in range(n_draws):
        shock = float(rng.standard_normal())
        for a in assets:
            for h in horizons:
                draw.append(d)
                asset.append(a)
                horizon.append(int(h))
                value.append(centre + spread * shock)
    return {"draw": draw, "asset": asset, "horizon": horizon, "value": value}


def realized_rows(
    *,
    assets: Sequence[str] = ASSETS,
    horizons: Sequence[int] = HORIZONS,
    value: float = 1.0,
) -> dict[str, list[Any]]:
    """The organizer's reference shape, INCLUDING the columns the scorer must not read.

    A real `realized.parquet` carries `draw` and `target_date` alongside the three the metric
    needs. Both are here on purpose: `target_date` is sealed, and the scorer proving it can read a
    reference file without selecting that column is part of what keeps it out of public output.
    """
    rows: dict[str, list[Any]] = {
        "draw": [],
        "asset": [],
        "horizon": [],
        "value": [],
        "target_date": [],
    }
    for a in assets:
        for i, h in enumerate(horizons):
            rows["draw"].append(0)
            rows["asset"].append(a)
            rows["horizon"].append(int(h))
            rows["value"].append(float(value))
            rows["target_date"].append(TARGET_DATES[i % len(TARGET_DATES)])
    return rows


# --------------------------------------------------------------------------------------------
# Unit / submission builders
# --------------------------------------------------------------------------------------------


CARD_TEMPLATE = """\
schema_version = "2.0"

[task]
id    = "{unit_id}"
track = "forecasting"
title = "Synthetic Track 2 unit"
split = "{split}"

[provenance]
data_cutoff = "{asof}"

[contamination]
canary_guid = "{canary}"

[scoring]
verifier = "t2.crps_composite"
metric   = "crps_composite"

[scoring.params]
tail_levels = [0.01, 0.05, 0.95, 0.99]
joint       = "variogram"

[scoring.params.weights]
marginal = 0.5
joint    = 0.3
tail     = 0.2

[environment]
cpus    = 2
memory  = "4G"
gpu     = false
network = "restricted"

[text]
path   = "text/"
cutoff = "{asof}"

[targets]
asset_ids    = {assets}
horizons     = {horizons}
target_type  = "level"
target_dates = {target_dates}
"""


def write_card(
    unit_dir: pathlib.Path,
    *,
    unit_id: str = "t2-SYN-0001",
    split: str = "validation",
    asof: str = ASOF,
    assets: Sequence[str] = ASSETS,
    horizons: Sequence[int] = HORIZONS,
    target_dates: Sequence[str] = TARGET_DATES,
    canary: str = "00000000-0000-4000-8000-000000000001",
) -> pathlib.Path:
    unit_dir.mkdir(parents=True, exist_ok=True)
    path = unit_dir / "card.toml"
    path.write_text(
        CARD_TEMPLATE.format(
            unit_id=unit_id,
            split=split,
            asof=asof,
            canary=canary,
            assets=json.dumps(list(assets)),
            horizons=json.dumps([int(h) for h in horizons]),
            target_dates=json.dumps(list(target_dates)),
        ),
        encoding="utf-8",
    )
    return path


def write_text_corpus(
    unit_dir: pathlib.Path, *, asof: str = ASOF, extra_unindexed: bool = False
) -> pathlib.Path:
    corpus = unit_dir / "text"
    corpus.mkdir(parents=True, exist_ok=True)
    (corpus / "doc-1.md").write_text("Synthetic dated snippet.\n", encoding="utf-8")
    (corpus / "corpus_index.json").write_text(
        json.dumps(
            {"documents": [{"doc_id": "doc-1", "path": "doc-1.md", "timestamp": "2020-06-01"}]},
            indent=2,
        ),
        encoding="utf-8",
    )
    if extra_unindexed:
        (corpus / "doc-2.md").write_text("Unindexed snippet.\n", encoding="utf-8")
    return corpus


def write_panels(
    unit_dir: pathlib.Path, *, asof: str = ASOF, late_row: bool = False
) -> pathlib.Path:
    panels = unit_dir / "panels"
    dates = ["2020-06-01", "2020-06-15", asof]
    if late_row:
        dates.append("2020-12-31")
    write_parquet(
        panels / "syn_daily.parquet",
        {
            "asset": ["SYN-A"] * len(dates),
            "date": dates,
            "panel_id": ["syn_daily"] * len(dates),
            "value": [1.0] * len(dates),
        },
    )
    return panels


def write_reference(
    unit_dir: pathlib.Path,
    *,
    assets: Sequence[str] = ASSETS,
    horizons: Sequence[int] = HORIZONS,
    value: float = 1.0,
    ref_scale: dict[str, float] | None = None,
) -> pathlib.Path:
    reference = unit_dir / "reference"
    reference.mkdir(parents=True, exist_ok=True)
    write_parquet(
        reference / "realized.parquet",
        realized_rows(assets=assets, horizons=horizons, value=value),
    )
    scale = ref_scale if ref_scale is not None else {"marginal": 1.0, "joint": 1.0, "tail": 1.0}
    (reference / "ref_scale.json").write_text(json.dumps(scale, indent=2), encoding="utf-8")
    return reference


def build_unit(
    root: pathlib.Path,
    *,
    unit_id: str = "t2-SYN-0001",
    assets: Sequence[str] = ASSETS,
    horizons: Sequence[int] = HORIZONS,
    realized_value: float = 1.0,
    ref_scale: dict[str, float] | None = None,
    with_reference: bool = True,
) -> pathlib.Path:
    """A complete organizer-side unit: card, panels, text corpus, reference."""
    root.mkdir(parents=True, exist_ok=True)
    write_card(root, unit_id=unit_id, assets=assets, horizons=horizons)
    write_panels(root)
    write_text_corpus(root)
    if with_reference:
        write_reference(
            root, assets=assets, horizons=horizons, value=realized_value, ref_scale=ref_scale
        )
    return root


def build_submission(
    output_dir: pathlib.Path,
    *,
    unit_id: str = "t2-SYN-0001",
    asof: str = ASOF,
    assets: Sequence[str] = ASSETS,
    horizons: Sequence[int] = HORIZONS,
    n_draws: int = 200,
    representation: str = "samples",
    centre: float = 1.0,
    spread: float = 0.25,
    seed: int = 7,
    rows: dict[str, list[Any]] | None = None,
    meta_overrides: dict[str, Any] | None = None,
    rationale: str | None = "Synthetic rationale.\n",
    parquet_kwargs: dict[str, Any] | None = None,
) -> pathlib.Path:
    """A complete, admissible participant tree. Every negative test edits one thing about it."""
    output_dir.mkdir(parents=True, exist_ok=True)
    table = (
        rows
        if rows is not None
        else forecast_rows(
            assets=assets,
            horizons=horizons,
            n_draws=n_draws,
            centre=centre,
            spread=spread,
            seed=seed,
        )
    )
    write_parquet(output_dir / "forecast.parquet", table, **(parquet_kwargs or {}))
    meta: dict[str, Any] = {
        "unit_id": unit_id,
        "asof": asof,
        "representation": representation,
        "asset_ids": list(assets),
        "horizons": [int(h) for h in horizons],
        "n_draws": n_draws,
        "target": "level",
    }
    meta.update(meta_overrides or {})
    (output_dir / "forecast_meta.json").write_text(
        json.dumps(meta, indent=2) + "\n", encoding="utf-8"
    )
    if rationale is not None:
        (output_dir / "forecast_rationale.md").write_text(rationale, encoding="utf-8")
    return output_dir


# --------------------------------------------------------------------------------------------
# C1 builder
# --------------------------------------------------------------------------------------------


def make_plan(
    handles: Sequence[str],
    *,
    grids: dict[str, tuple[Sequence[str], Sequence[int]]] | None = None,
    phase: str = "dev",
    clip: bool = True,
    failure_score: float | None = None,
    domain: tuple[float, float] = (0.0, 4.0),
) -> dict[str, Any]:
    """A signed, expanded forecasting C1 with `W = 4.0` and `ref_scale` normalization.

    Signed with the Hub's published development seed. `phase="dev"` keeps the readable synthetic
    handles legible; the sealed-phase opacity rule is the Hub's and is tested there.
    """
    low, high = domain
    body: dict[str, Any] = {
        "schema_version": PLAN_SCHEMA_VERSION,
        "contract_set": CONTRACT_SET,
        "competition_id": "comp-synthetic-forecasting",
        "track": "forecasting",
        "phase": phase,
        "plan_id": "plan-synthetic-forecasting-0001",
        "metric": {
            "direction": "asc",
            "domain": {"min": low, "max": high},
            "statistic": "mean",
            "unit_scope": "per_unit",
        },
        "roster": {
            "count": len(handles),
            "digest": compute_roster_digest(list(handles)),
            "expected_units": [],
        },
        "participant_failure": {
            "policy": "fixed_worst_case",
            "score": high if failure_score is None else failure_score,
            "by_code": {},
            "clip_real_scores_to_domain": clip,
        },
        "organizer_failure": {"policy": "abort_whole_evaluation"},
        "scorer": {
            "package": "qfbench2_track_forecasting",
            "digest": digest_json("synthetic:scorer"),
            "interface_version": "2.0",
        },
        "required_evidence": {"c2": True, "c3": True, "telemetry": False, "judge": False},
        "normalization": {
            "mode": "ref_scale",
            "ref_scale_commitment": digest_json("synthetic:ref-scale"),
        },
    }
    for handle in handles:
        assets, horizons = (grids or {}).get(handle, (ASSETS, HORIZONS))
        body["roster"]["expected_units"].append(
            {
                "unit_handle": handle,
                "grid": {
                    "assets": list(assets),
                    "horizons": [int(h) for h in horizons],
                    "cell_count": len(assets) * len(horizons),
                    "digest": digest_json(
                        {"assets": list(assets), "horizons": [int(h) for h in horizons]}
                    ),
                },
            }
        )
    body["signature"] = sign_payload(
        body, seed=DEV_SEED, key_id=DEV_KEY_ID, signed_at=SIGNED_AT
    ).to_mapping()
    return body


@pytest.fixture()
def unit_dir(tmp_path: pathlib.Path) -> pathlib.Path:
    return build_unit(tmp_path / "unit")


@pytest.fixture()
def submission_dir(tmp_path: pathlib.Path) -> pathlib.Path:
    return build_submission(tmp_path / "out")


@pytest.fixture()
def clean_tmp(tmp_path: pathlib.Path) -> Iterable[pathlib.Path]:
    yield tmp_path
    shutil.rmtree(tmp_path, ignore_errors=True)
