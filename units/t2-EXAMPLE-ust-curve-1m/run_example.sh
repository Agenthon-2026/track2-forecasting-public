#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Quick-start runner for the Track-2 worked exemplar t2-EXAMPLE-ust-curve-1m.
#
# It runs end to end with ONLY numpy + pandas + the shared qfbench2_common toolkit
# (no foundation-model weights, no network):
#   1. loads the synthetic input panel rates_daily.parquet (as-of 2024-06-28);
#   2. runs the theta_arima baseline (statistical Gaussian random-walk fallback)
#      to produce a schema-valid joint forecast over UST_2Y/5Y/10Y/30Y @ horizon 21;
#   3. writes forecast.parquet + forecast_meta.json into ./output/;
#   4. runs the public smoke scorer (gates g0-g3); no realized outcomes are shipped
#      publicly, so the score is reported as None ("public smoke") — gates still run.
#
# Usage:
#   bash run_example.sh                       # uses the pip-installed qfbench2-common
#   COMMON=/path/to/common bash run_example.sh # or point at a checkout of the toolkit
# ---------------------------------------------------------------------------
set -euo pipefail

UNIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PUBLIC_DIR="$(cd "${UNIT_DIR}/../.." && pwd)"
# COMMON is OPTIONAL. If you pip-installed qfbench2-common (the normal path -- see the README's
# "Inheriting the shared toolkit"), leave it unset. The old default pointed at
# ${PUBLIC_DIR}/../../../main/common, which is the organizers' internal monorepo layout; in a
# participant's checkout that directory does not exist, so under `set -e` this line aborted the
# script on line 22 before anything ran. Measured 2026-08-24.
COMMON="${COMMON:-}"
OUT_DIR="${UNIT_DIR}/output"
mkdir -p "${OUT_DIR}"

echo "Unit:    ${UNIT_DIR}"
echo "Common:  ${COMMON}"
echo "Output:  ${OUT_DIR}"

PYTHONPATH="${COMMON:+${COMMON}:}${PUBLIC_DIR}" python3 - "$UNIT_DIR" "$OUT_DIR" <<'PY'
import json, pathlib, sys
import pandas as pd

unit_dir = pathlib.Path(sys.argv[1])
out_dir = pathlib.Path(sys.argv[2])

from baselines.base import ForecastRequest
from baselines.theta_arima import ThetaARIMABaseline

# Read the grid from the card rather than restating it. The card is the contract, and a
# hard-coded copy drifts: this script used to declare target="yield" while the card says
# target_type="level", and g2 refused the run with "A level forecast scored as a log return is
# not a worse forecast, it is a different quantity." Measured 2026-08-24 -- and invisible until
# the COMMON default above was fixed, because the script aborted on line 22 before reaching it.
import tomllib
_card = tomllib.loads((unit_dir / "card.toml").read_text())
_targets = _card["targets"]

ASSETS = list(_targets["asset_ids"])
HORIZONS = list(_targets["horizons"])
TARGET = _targets["target_type"]
ASOF = "2024-06-28"
N_DRAWS = 500

panel = pd.read_parquet(unit_dir / "rates_daily.parquet")
req = ForecastRequest(
    panels={"rates_daily": panel},
    asof=ASOF,
    asset_ids=ASSETS,
    horizons=HORIZONS,
    n_draws=N_DRAWS,
)
res = ThetaARIMABaseline().forecast(req)
print("baseline impl:", res.metadata.get("implementation"))

# samples [n_draws, n_assets, n_horizons] -> long forecast.parquet [draw,asset,horizon,value]
rows = []
for di in range(res.samples.shape[0]):
    for ai, a in enumerate(ASSETS):
        for hi, h in enumerate(HORIZONS):
            rows.append({"draw": di, "asset": a, "horizon": h,
                         "value": float(res.samples[di, ai, hi])})
pd.DataFrame(rows).to_parquet(out_dir / "forecast.parquet", index=False)

meta = {
    "unit_id": "t2-EXAMPLE-ust-curve-1m",
    "asof": ASOF,
    "representation": "samples",
    "asset_ids": ASSETS,
    "horizons": HORIZONS,
    "n_draws": N_DRAWS,
    "target": TARGET,
}
(out_dir / "forecast_meta.json").write_text(json.dumps(meta, indent=2))

# forecast_rationale.md is a REQUIRED deliverable (gate g1) and is NEVER SCORED — the gate
# checks only that it exists and is not blank. It is written for a human reviewer, so this
# exemplar shows the shape: what the forecast is, what drove it, and what would change it.
(out_dir / "forecast_rationale.md").write_text(f"""\
# Forecast rationale — {meta["unit_id"]}

**As of {ASOF}. Target: joint distribution over {", ".join(ASSETS)} at horizon {HORIZONS[0]}
business days.**

## Method

Theta/AutoARIMA per tenor, with a Gaussian random-walk fallback when `statsforecast` is absent
(this run: `{res.metadata.get("implementation")}`). {N_DRAWS} draws. The draws are generated
jointly across tenors, so curve shape is preserved rather than assembled from independent
marginals — the joint variogram term penalises independently drawn assets.

## What the text corpus contributed

Nothing in this run. This is the statistical baseline: it reads the numeric panel only, and the
text corpus at `/input/text/` is left unread. It is included as the floor a reasoning agent has
to beat, not as an example of using text.

A reasoning agent would read the two dated FOMC documents in this unit's corpus and adjust the
level and spread — the June 2024 statement's rate-hold language and the "greater confidence"
framing bear directly on the front end, and should move 2Y more than 30Y.

## What would change this forecast

A shift in the FOMC's characterisation of inflation progress, or a payrolls surprise large
enough to reprice the front end. Neither is observable at the as-of date.
""")
print("wrote", out_dir / "forecast.parquet", ", forecast_meta.json and forecast_rationale.md")

# Run the public smoke scorer (gates g0-g3 + scorer; no realized outcomes in public).
from scoring.scoring import build_verifier

ctx = {"card": _card, "output_dir": out_dir, "unit_dir": unit_dir,
       "realized": None, "ref_scale": None}
verdict = build_verifier(ctx).run(ctx)
print("admissible:", verdict.admissible)
print("gate_results:", {k: v.passed for k, v in verdict.gate_results.items()})
print("score:", verdict.score, "(None => public smoke: realized outcomes are sealed)")
assert verdict.admissible, f"gates failed: {verdict.labels}"
print("OK: quick-start ran end to end.")
PY
