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
