"""Track 2 (forecasting) verifier/scorer package for QFBench 2.0.

This package fulfils the contract stated in the shared toolkit's `common/README.md`
(`Agenthon-2026/Agenthon2026-public`):
    "expose `qfbench2_track_<track>.scoring.build_verifier(ctx)` returning a
     `HierarchicalVerifier`"
so that the shared smoke runner (`qfbench2-smoke <unit> <out> --track forecasting`
and `qfbench2 smoke ... --track forecasting`) can import it. All evaluation math
comes from `qfbench2_common` — this is a track-specific wrapper only.
"""

from .scoring import SCORER_VERSION, scorer_identity

__all__ = ["SCORER_VERSION", "scorer_identity"]

# The shared scorer version (see scoring.SCORER_VERSION), so a participant can read it
# without importing the scoring module. This package previously declared 2.0.0 here while
# pyproject.toml said 2.1.0; the version is now derived, so the two cannot disagree.
__version__ = SCORER_VERSION
