"""Track 2 (forecasting) verifier/scorer package for QFBench 2.0.

This package fulfils the contract stated in the shared toolkit's `common/README.md`
(`Agenthon-2026/Agenthon2026-public`):
    "expose `qfbench2_track_<track>.scoring.build_verifier(ctx)` returning a
     `HierarchicalVerifier`"
so that the shared smoke runner (`qfbench2-smoke <unit> <out> --track forecasting`
and `qfbench2 smoke ... --track forecasting`) can import it. All evaluation math
comes from `qfbench2_common` — this is a track-specific wrapper only.
"""

__version__ = "2.0.0"

# The shared scorer version (see scoring.SCORER_VERSION). Re-exported so a
# participant can read it without importing the scoring module.
from .scoring import SCORER_VERSION, scorer_identity  # noqa: E402

__version__ = SCORER_VERSION
