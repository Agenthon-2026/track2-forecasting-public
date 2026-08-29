"""Back-compat shim — the canonical module is `qfbench2_track_forecasting.scoring`.

Kept so existing references keep working unchanged:
- `python scoring/scoring.py score --card ... --forecast ... [--realized ...]`
- `sys.path` imports of `scoring.scoring` (e.g. docs/AUTHORING-GUIDE.md's
  `_check_text_corpus_cutoff` snippet)

All public and underscore-prefixed symbols are re-exported.
"""

from __future__ import annotations

import pathlib
import sys

# Allow running this file directly from a repo checkout without installing the
# package: put the repo root (which contains qfbench2_track_forecasting/) first.
_repo_root = str(pathlib.Path(__file__).resolve().parents[1])
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from qfbench2_track_forecasting import scoring as _impl  # noqa: E402

# Static re-exports of the public contract so type checkers can follow them
# (the globals().update below re-exports everything dynamically, which mypy cannot see).
from qfbench2_track_forecasting.scoring import (  # noqa: E402
    LEADERBOARD_SORT as LEADERBOARD_SORT,
)
from qfbench2_track_forecasting.scoring import (
    build_verifier as build_verifier,
)

globals().update(
    {
        k: v
        for k, v in vars(_impl).items()
        if k
        not in {
            "__name__",
            "__file__",
            "__package__",
            "__loader__",
            "__spec__",
            "__builtins__",
            "__doc__",
            "__annotations__",
        }
    }
)

if __name__ == "__main__":
    raise SystemExit(_impl._main())
