"""Read the dated text corpus and turn it into one number.

Track 2's headline scientific question is the *information uplift*: does adding
text beat a text-blind forecaster. That makes the honest baseline a run with the
corpus unread, and any text contribution something that must be measured against
it rather than assumed.

So this stays deliberately small and legible. A lexicon score is not a good
reasoning system - it is a floor that can be compared against, and a shape the
model-driven version can slot into without changing the interface. What matters
architecturally is that the drift it produces is a single declared quantity, so
the uplift attributable to text is measurable rather than tangled into the
sampler.

Cutoff: a document dated after the as-of date is not evidence, it is leakage.
Gate g2 checks it; this filters before reading.
"""

from __future__ import annotations

import datetime as dt
import json
import pathlib
import re

#: Directional language, scored in units of a daily standard deviation. Small on
#: purpose: a lexicon should nudge the distribution, never relocate it.
HAWKISH = ("hike", "tighten", "tightening", "restrictive", "elevated inflation",
           "upside risk", "firmer", "raise the target range")
DOVISH = ("cut", "ease", "easing", "accommodative", "downside risk",
          "moderating", "greater confidence", "lower the target range",
          "hold the target range")

DATE_IN_NAME = re.compile(r"(20\d{2})[_-](\d{2})[_-](\d{2})")
STEP_PER_NET_HIT = 0.05
MAX_DRIFT_SIGMAS = 0.5
#: A single document's net contribution is capped so one long FOMC transcript
#: cannot saturate the whole corpus signal by repetition alone.
MAX_NET_PER_DOC = 5

#: Word-boundary patterns, compiled once. Substring counting scored
#: "in-crease" and "de-crease" as `ease` and "exe-cut-ive" as `cut` - the most
#: common words in financial prose, all landing on the dovish side - so every
#: document drifted dovish regardless of what it said, and the drift saturated
#: the cap. The signal measured typography, not policy.
_PATTERNS = {
    word: re.compile(r"\b" + re.escape(word) + r"\b")
    for word in HAWKISH + DOVISH
}


def _net_hits(body: str) -> int:
    hawkish = sum(len(_PATTERNS[w].findall(body)) for w in HAWKISH)
    dovish = sum(len(_PATTERNS[w].findall(body)) for w in DOVISH)
    net = hawkish - dovish
    return max(-MAX_NET_PER_DOC, min(MAX_NET_PER_DOC, net))


def _document_date(path: pathlib.Path, index: dict) -> dt.date | None:
    entry = index.get(path.name) if index else None
    if isinstance(entry, dict) and entry.get("date"):
        try:
            return dt.date.fromisoformat(str(entry["date"])[:10])
        except ValueError:
            pass
    match = DATE_IN_NAME.search(path.name)
    if match:
        try:
            return dt.date(*(int(g) for g in match.groups()))
        except ValueError:
            return None
    return None


def read_corpus(text_dir: pathlib.Path, asof: str) -> dict:
    if not text_dir.is_dir():
        return {"documents": [], "drift_in_sigmas": 0.0,
                "note": "no text/ directory"}

    cutoff = dt.date.fromisoformat(asof)
    index: dict = {}
    index_path = text_dir / "corpus_index.json"
    if index_path.is_file():
        try:
            raw = json.loads(index_path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                index = raw
            elif isinstance(raw, list):
                index = {e.get("filename", ""): e for e in raw if isinstance(e, dict)}
        except (ValueError, AttributeError):
            index = {}

    used, skipped, undated, net = [], [], 0, 0
    documents = sorted(p for suffix in ("*.txt", "*.md")
                       for p in text_dir.rglob(suffix))
    for path in documents:
        date = _document_date(path, index)
        if date is not None and date > cutoff:
            skipped.append(f"{path.name} (dated {date}, after as-of)")
            continue
        if date is None:
            # Read, but counted and surfaced: for a gate that can void the
            # whole run on embargo, a silently-undated document is a risk the
            # rationale must at least disclose.
            undated += 1
        body = path.read_text(encoding="utf-8", errors="replace").lower()
        hits = _net_hits(body)
        net += hits
        used.append({"file": path.name,
                     "date": date.isoformat() if date else None,
                     "net_hawkish_hits": hits})

    drift = max(-MAX_DRIFT_SIGMAS,
                min(MAX_DRIFT_SIGMAS, net * STEP_PER_NET_HIT))
    return {"documents": used, "skipped_after_cutoff": skipped,
            "undated_documents": undated,
            "net_hawkish_hits": net, "drift_in_sigmas": drift,
            "lexicon": "word-boundary hawkish/dovish counts, "
                       f"per-doc cap {MAX_NET_PER_DOC}, drift cap "
                       f"{MAX_DRIFT_SIGMAS} sigma"}
