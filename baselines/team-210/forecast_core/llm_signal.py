"""Read the text corpus with an LLM, into the same declared drift slot.

The architecture rule stands: whatever reads the text produces a SMALL number
of bounded, declared quantities - a global drift and optional per-asset tilts,
in units of one daily standard deviation - and the sampler consumes them
without knowing who wrote them. That keeps the information uplift measurable:
floor (--no-text) vs lexicon vs LLM differ only in this module's output.

Failure discipline: any problem - no endpoint, refused call, malformed reply -
falls back to the lexicon signal with a note. A forecast must never die, or
even change shape, because the reader had a bad minute.

Values are clamped HERE, not trusted from the model: the prompt asks for
[-0.5, 0.5] and the code enforces it, because a reader that can relocate the
distribution by ten sigmas is not a signal, it is a failure mode.
"""

from __future__ import annotations

import http.client
import json
import os
import pathlib
import re
import time
import urllib.error
import urllib.request

from . import text_signal

MODEL_RETRIES = 2
RETRY_BACKOFF_SEC = (2.0, 5.0)
#: Per-document and total character budgets for the prompt.
DOC_CHAR_BUDGET = 1500
TOTAL_CHAR_BUDGET = 7000

SYSTEM = (
    "You are a macro and rates analyst. You read time-stamped central-bank "
    "and market text and translate it into a small directional tilt for a "
    "distributional forecast. You never restate the documents; you output "
    "STRICT JSON only, no markdown, of the form:\n"
    '{"drift_in_sigmas": <float in [-0.5, 0.5]>, '
    '"per_asset": {"<asset>": <float in [-0.5, 0.5]>, ...}, '
    '"reasons": ["<short reason>", "..."]}\n'
    "Positive drift means the target quantity moves UP relative to a "
    "no-information random walk; negative means DOWN. Stay near zero unless "
    "the text is clearly directional - an unjustified tilt is worse than "
    "none. per_asset may be empty; include only assets you have a view on.")


def _clamp(value, limit: float) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return 0.0
    if v != v:  # NaN
        return 0.0
    return max(-limit, min(limit, v))


def _extract_json(text: str) -> dict | None:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        payload = json.loads(match.group(0))
    except ValueError:
        return None
    return payload if isinstance(payload, dict) else None


def _prompt(signal: dict, text_dir: pathlib.Path, assets: list[str],
            horizons: list[int], target: str, asof: str) -> str:
    parts = [
        f"AS-OF DATE: {asof} (nothing after this date exists for you)",
        f"TARGET: {target} of assets {assets} at horizon(s) {horizons} "
        "business days.",
        "DOCUMENTS (name | date | body, truncated):",
    ]
    used = 0
    for doc in signal.get("documents", []):
        body = ""
        try:
            body = (text_dir / doc["file"]).read_text(
                encoding="utf-8", errors="replace")[:DOC_CHAR_BUDGET]
        except OSError:
            pass
        block = f"--- {doc['file']} | {doc.get('date') or 'undated'} ---\n{body}"
        if used + len(block) > TOTAL_CHAR_BUDGET:
            parts.append("--- (further documents omitted for budget) ---")
            break
        used += len(block)
        parts.append(block)
    parts.append("Return the JSON now.")
    return "\n".join(parts)


def _call(endpoint: str, model: str, prompt: str,
          notes: list[str]) -> dict | None:
    try:
        max_tokens = int(os.environ.get("MODEL_MAX_TOKENS", 600))
    except ValueError:
        max_tokens = 600
    try:
        timeout = float(os.environ.get("MODEL_TIMEOUT_SEC", 120.0))
    except ValueError:
        timeout = 120.0

    payload = json.dumps({
        "model": model, "temperature": 0.0, "seed": 0,
        "max_tokens": max_tokens,
        "messages": [{"role": "system", "content": SYSTEM},
                     {"role": "user", "content": prompt}],
    }).encode()
    headers = {"Content-Type": "application/json",
               "User-Agent": "agenthon-t2-agent/1.0"}
    api_key = os.environ.get("MODEL_API_KEY")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(
        endpoint.rstrip("/") + "/chat/completions", data=payload,
        headers=headers)

    for attempt in range(1 + MODEL_RETRIES):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = json.loads(response.read())
            choices = body.get("choices") or []
            content = (choices[0].get("message") or {}).get("content") if choices else None
            if not content:
                notes.append("llm reader: empty completion; lexicon fallback")
                return None
            parsed = _extract_json(str(content))
            if parsed is None:
                notes.append("llm reader: reply was not JSON; lexicon fallback")
                return None
            usage = body.get("usage") or {}
            parsed["_usage"] = {"prompt_tokens": usage.get("prompt_tokens"),
                                "completion_tokens": usage.get("completion_tokens")}
            return parsed
        except urllib.error.HTTPError as error:
            if attempt >= MODEL_RETRIES:
                notes.append(f"llm reader: HTTP {error.code} after retries; "
                             "lexicon fallback")
                return None
            time.sleep(25.0 if error.code in (413, 429)
                       else RETRY_BACKOFF_SEC[min(attempt, 1)])
        except (OSError, http.client.HTTPException, ValueError) as error:
            if attempt >= MODEL_RETRIES:
                notes.append(f"llm reader: {type(error).__name__}; "
                             "lexicon fallback")
                return None
            time.sleep(RETRY_BACKOFF_SEC[min(attempt, 1)])
    return None


def read_corpus(text_dir: pathlib.Path, asof: str, assets: list[str],
                horizons: list[int], target: str) -> dict:
    """The lexicon signal, upgraded by an LLM reading when one is reachable.

    The lexicon pass runs first regardless: it carries the cutoff filtering,
    the document census and the fallback drift. The LLM only ever *replaces
    the numbers*, so a dead endpoint degrades to exactly the shipped floor.
    """
    signal = text_signal.read_corpus(text_dir, asof)
    notes: list[str] = []

    endpoint = os.environ.get("MODEL_ENDPOINT")
    model = os.environ.get("MODEL_NAME")
    if not endpoint or not model:
        signal["reader"] = "lexicon (no model endpoint)"
        return signal
    if not signal.get("documents"):
        signal["reader"] = "lexicon (no documents to read)"
        return signal

    parsed = _call(endpoint, model,
                   _prompt(signal, text_dir, assets, horizons, target, asof),
                   notes)
    if parsed is None:
        signal["reader"] = "lexicon (llm fallback)"
        signal["reader_notes"] = notes
        return signal

    limit = text_signal.MAX_DRIFT_SIGMAS
    drift = _clamp(parsed.get("drift_in_sigmas"), limit)
    per_asset_raw = parsed.get("per_asset")
    per_asset = {}
    if isinstance(per_asset_raw, dict):
        per_asset = {str(k): _clamp(v, limit)
                     for k, v in per_asset_raw.items() if str(k) in assets}
    reasons = [str(r)[:200] for r in (parsed.get("reasons") or [])[:3]
               if isinstance(r, str)]

    signal["drift_in_sigmas"] = drift
    signal["per_asset_drift"] = per_asset
    signal["reader"] = f"llm ({model})"
    signal["llm"] = {"reasons": reasons, "usage": parsed.get("_usage")}
    if notes:
        signal["reader_notes"] = notes
    return signal
