"""Resolve a unit's as-of date from its card.

Promoted from dev_tools/card_asof.py into the runtime because the Dockerfile's
default CMD carries no --asof while the flag was required=True: `docker run
<image>` exited 2 with zero files - an inadmissible run from the image's own
default invocation. The card knows the date; the agent should read it rather
than demand it.

`grep -o` over card.toml returns every date in the file - the as-of, the panel
end, the created date, the target date. The card knows which is which, but not
always under the same key: the exemplar has no `asof` field at all, it has a
panel `end_date` and a separate `target_dates`. Taking the wrong one silently
forecasts from the future, so only keys that mean "data ends here" count and
keys that describe the prediction target are skipped outright.
"""

from __future__ import annotations

ASOF_KEYS = {"asof", "as_of", "end_date", "data_end", "cutoff", "data_cutoff"}
#: Never an as-of: these describe the thing being predicted.
FORBIDDEN = {"target_date", "target_dates", "created_date",
             "public_release_date", "start_date"}


def _walk(node, found: list[str]) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            lowered = key.lower()
            if lowered in FORBIDDEN:
                continue
            if lowered in ASOF_KEYS and isinstance(value, str) and len(value) >= 10:
                found.append(value[:10])
            else:
                _walk(value, found)
    elif isinstance(node, list):
        for item in node:
            _walk(item, found)


def from_card(card: dict) -> str | None:
    """The latest date at which data is still legitimately available."""
    dates: list[str] = []
    _walk(card, dates)
    return max(dates) if dates else None
