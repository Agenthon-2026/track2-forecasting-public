# Track 2 — Forecast Card Authoring Guide

## Executive summary (read this first)

This guide is for **card authors** — people who design and publish the evaluation tasks that
participants compete on. It is NOT for participants building forecast agents; participants should
read `README.md` and `docs/CONCEPTS.md` instead.

A **forecast card** is a fully self-contained specification of one forecasting task: which
time-series panels the agent may see, what frozen text corpus it may read, what it must
forecast, and how it will be scored. Designing a good card requires care in seven areas:
(1) assembling the time-series panels; (2) assembling the time-stamped text corpus;
(3) setting the as-of date (the information cutoff for both panels and text);
(4) specifying target assets and horizons; (5) assigning the card to a family (F1–F4);
(6) writing the sealed realized-outcome key (which goes in `private/`, never `public/`);
and (7) running the leakage check for both panel rows and text document timestamps.

**The two most common card authoring mistakes are:**
1. Letting realized-outcome information touch the public repo.
2. Including a text corpus document dated after the as-of date (text leakage — gate g2 will catch this in production, but it is embarrassing and makes the card invalid).

---

## Step 1 — Pick and assemble the time-series panels

A **panel** is a named collection of time-series data that ends strictly at the as-of date.
Four panels are available:

| Panel ID | Source | Series | Native unit |
|----------|--------|--------|-------------|
| `rates/ust-daily` | FRED H.15 | DGS2, DGS5, DGS7, DGS10, DGS20, DGS30 | % per annum |
| `fx/g10-daily` | Fed H.10 | 10 G10 currency spots | USD per foreign unit (spot mid) |
| `macro/releases-quarterly` | FRED | CPI, PCE, NFP, GDP flash x G6 + selected EM | native units (varies) |
| `factors/jkp-daily` | JKP | MKT, SMB, HML, MOM, BAB, QMJ | decimal daily return |

**Rules for panel specification:**

1. List every series explicitly in `[panels.<id>] series`. No wildcards.
2. Set `end_date` equal to the as-of date exactly.
3. For factor returns, document the reporting lag. JKP factors for month M are typically
   available 1-2 weeks after month-end.
4. Any derived feature (e.g., yield spread = DGS10 - DGS2) must be constructible entirely
   from raw series with `date <= asof`. Document the derivation formula in `[notes]`.
5. Do not include forward-looking survey data, analyst forecasts, or any series that
   embeds future information (e.g., Fed funds futures for dates past the as-of date).

---

## Step 2 — Assemble the time-stamped text corpus

The **text corpus** is the collection of text documents the agent may read at inference time.
It is mounted at `/input/text/` in the Docker container. Every document in the corpus must
have a timestamp on or before the as-of date. This is not just a guideline — gate g2 of the
admissibility pipeline checks every document timestamp against the as-of date and will reject
any submission where the corpus contains a post-asof document.

**What belongs in the text corpus:**

| Document type | Example | Notes |
|--------------|---------|-------|
| Central bank statements | FOMC meeting statements | Use the release date as the document timestamp |
| Meeting minutes | FOMC minutes | Release date is typically ~3 weeks after the meeting |
| Governor speeches | Fed chair Jackson Hole speech | Timestamp = date of delivery |
| Macro-release commentary | BLS CPI release text, NFP press release | Timestamp = release date |
| COT analyst summaries | Commitment of Traders commentary | Timestamp = publication date |
| News headlines | Newswire snippets about market events | Timestamp = publication date |

**Assembling the corpus — required layout:**

A corpus is a directory of documents (one `.txt` or `.md` file each) **plus a
`corpus_index.json` at its root** listing every one of them. The index is not optional and it is
not one of two alternatives: `scan_text_corpus_cutoff` refuses a corpus that has no index, and
refuses one whose index and directory do not cover each other exactly in **both** directions — a
file on disk that no entry names has passed no cutoff check at all, and an entry naming a file
that is not there is a corpus that was not assembled the way it claims.

An earlier revision of this section recommended "one JSON file per document" as the primary
format, with the index as an alternative. Measured 2026-08-27, a corpus built that way is
refused:

```
one JSON file per document, no index -> OrganizerFault: the text corpus has no
                                        corpus_index.json. Returning 'clean' for an unindexed
                                        corpus reports the absence of a check as the absence
                                        of a problem.
documents + corpus_index.json        -> CorpusVerdict(indexed_documents=1, files_on_disk=1)
```

Each entry needs a `doc_id`, an ISO `YYYY-MM-DD` `timestamp`, and the file it names under either
`path` or `file`. `source` and `doc_type` are conventional and carried by every shipped corpus.
`units/t2-EXAMPLE-ust-curve-1m/text/corpus_index.json` is the worked example:

```json
{
  "documents": [
    {
      "doc_id": "fomc-statement-2021-09-22",
      "path": "fomc_statement_2021_09_22.txt",
      "timestamp": "2021-09-22",
      "source": "Federal Reserve",
      "doc_type": "fomc_statement"
    }
  ]
}
```

**Enforcing the text cutoff:**

After assembling the corpus, verify every document timestamp against the as-of date.
`qfbench2_track_forecasting.cutoff.scan_text_corpus_cutoff` is the canonical implementation. It
takes the **corpus directory** and the as-of date, and it does not return violations: it either
returns a `CorpusVerdict` of counts, or **raises `OrganizerFault`** — an undated document, a
post-as-of document, a missing index and an index that does not match the directory are all
refusals. The as-of comes from the card's `[forecast].asof` or `[provenance].data_cutoff`, which
is what `trusted_asof` reads; it is **not** `[targets].target_dates[0]`, which is the date being
forecast, not the date the corpus is cut at.

```python
import pathlib, tomllib

from qfbench2_common.contracts import OrganizerFault
from qfbench2_track_forecasting.cutoff import scan_text_corpus_cutoff, trusted_asof

unit_dir = pathlib.Path("units/t2-EXAMPLE-ust-curve-1m")
card = tomllib.loads((unit_dir / "card.toml").read_text())
asof = trusted_asof(card)
corpus_root = unit_dir / card.get("text", {}).get("path", "text/")

try:
    verdict = scan_text_corpus_cutoff(corpus_root, asof)
except OrganizerFault as exc:
    raise SystemExit(f"corpus is not publishable: {exc}")
print("asof:", asof)
print("clean:", verdict)
# asof: 2024-06-28
# clean: CorpusVerdict(indexed_documents=2, files_on_disk=2)
```

The previous revision of this snippet imported `_check_text_corpus_cutoff` from
`scoring.scoring`. That name was removed at the 2026-08-22 freeze and the import now raises
`ImportError`, so the snippet could not be run as published.

**This scan does not run at scoring time.** `_g2_cutoff_resource` binds the declared as-of to
the trusted card; the panel and corpus scans run in the **staging gate stack before a unit is
published**, because under the frozen scoring topology the corpus is not in the scoring process's
namespace at all. A post-as-of document in organizer material is therefore an organizer fault that
stops publication — not a participant DNF that shows up on a leaderboard. Document the result in
`card.toml` under `[text] cutoff_checked = true`, and re-run whenever you add or change documents
in the corpus.

**The role of text in each family (what corpus to build):**

| Family | What text signals to include |
|--------|----------------------------|
| F1 | FOMC/MPC statements around the as-of date; macro-release commentary |
| F2 | Pre-shift central bank communications showing tone change; policy announcements |
| F3 | Multi-market commentary; communications about one asset that imply another |
| F4 | Shock-foreshadowing text: urgency language, record-level commentary, risk warnings |

For F4, the corpus should include documents that explicitly foreshadow the shock, published
before the shock, and available to an informed observer on the as-of date. Do not include
any post-shock commentary — that would be leakage.

---

## Step 3 — Set the as-of date and held-out window

The **as-of date** is the single most important parameter of a card. It is the strict
information cutoff for both panels and text. Everything the agent sees must have
`date <= asof`. Everything it is asked to forecast must have `date > asof`.

**The as-of date applies to BOTH the numeric panel and the text corpus.** A card where
the panel ends on 2021-10-01 but the text corpus contains a document dated 2021-11-03 is
invalid. Gate g2 checks both.

**Minimum gap rules:**

| Family | Minimum gap | Reason |
|--------|------------|--------|
| F1 Continuation-with-context | asof >= 6 calendar months before first target | Long-horizon level forecasting |
| F2 Text-cued regime shift | asof >= 3 calendar months before first target | Medium-horizon; text is the key signal |
| F3 Cross-asset reasoning | asof >= 1 calendar month before first target | Dependence structure, not horizon, is the test |
| F4 Tail/shock-from-text | asof must precede the shock by >= forecast horizon | Agent must not know the shock has started |

**Leakage check (mandatory) — panels:**

`cutoff_ok` RETURNS a bool (it does not raise); assert on it. ISO `YYYY-MM-DD` strings
compare chronologically, so pass dates as strings:

```python
from qfbench2_common.leakage import cutoff_ok

asof = "2023-07-03"
target_dates = ["2024-01-03", "2024-04-03"]

assert cutoff_ok(asof, target_dates)   # True iff every target_date strictly post-dates asof
```

**Leakage check (mandatory) — text corpus:**

```python
import tomllib, pathlib
from scoring.scoring import _check_text_corpus_cutoff  # public/scoring/scoring.py

unit_dir = pathlib.Path("units/my-card")
card = tomllib.loads((unit_dir / "card.toml").read_text())
violations = _check_text_corpus_cutoff(unit_dir, card, asof)
assert not violations, violations  # empty list = no document timestamp > asof
```

Document both outputs in `card.toml` under `[targets] leakage_checked = true` and
`[text] cutoff_checked = true`. Re-run both whenever you change the as-of date, the
target dates, or the corpus contents.

---

## Step 4 — Specify target assets and horizons

### Required fields

```toml
[targets]
asset_ids        = ["UST_2Y", "UST_10Y"]        # exact IDs; must match panel asset_ids
horizons         = [21, 63]                      # in BUSINESS DAYS, not calendar days
target_type      = "level"                       # "level", "log_return", or "spread"
target_frequency = "monthly"                     # "daily" or "monthly"
target_dates     = ["2024-01-03", "2024-04-03"]  # the actual calendar dates being measured
value_unit       = "percent_per_annum"           # document units for the realized-outcome author
leakage_checked  = true                          # set after running cutoff_ok
```

**Business days vs. calendar days:** 21 business days is approximately 1 calendar month
but is NOT exactly 21 calendar days. Use `pandas.offsets.BDay` to find the exact target
calendar date from the as-of date.

**Choosing horizons:**
- F1 cards: typically 21, 63, or 126 BD (1, 3, or 6 months).
- F2 cards: typically 21 and 63 BD (medium range; text is the key signal).
- F3 cards: typically 21 and 63 BD; the dependence structure is the focus.
- F4 cards: horizon determined by the shock event window.

---

## Step 5 — Assign the card to a family

Pick exactly one family. Wrong family assignment changes which score component is primary,
which breaks comparability with other cards in the same family.

| Family | When to use |
|--------|------------|
| F1 | Target assets are all present in the training panel through the as-of date; testing whether text adds incremental signal |
| F2 | Text signals a regime change before the panel numbers move; or the target asset is absent from the panel |
| F3 | Multiple target assets; cross-asset dependence (text about one implies moves in others) is the test |
| F4 | The held-out window spans a shock that the text corpus foreshadows; tail calibration is the test |

A card can have characteristics of multiple families. Use these tie-breaking rules:
- If the target series is absent from the panel → F2 (the exclusion rule dominates)
- If the window spans a shock AND assets are multi-variate → F4 (tails dominate)
- If multi-asset joint but no shock → F3
- Otherwise → F1

Set the family in `card.toml`:
```toml
[metadata]
category = "T2-F3"   # exactly one of T2-F1, T2-F2, T2-F3, T2-F4
```

---

## Step 6 — Build the sealed realized-outcome key (PRIVATE ONLY)

The realized-outcome file is what the scorer compares participant forecasts against. It
contains the actual market values that occurred on the target dates.

**Where it lives:**
```
private/units/<card_id>/reference/realized.parquet
```

**Schema:**

| Column | Type | Notes |
|--------|------|-------|
| `draw` | int32 | Always 0 (single realization) |
| `asset` | string | Must match asset IDs in `card.toml [targets] asset_ids` |
| `horizon` | int32 | Business-day horizon (must match `[targets] horizons`) |
| `value` | float64 | Realized value in the stated `value_unit` |
| `target_date` | date | The actual calendar date of observation |

**Critical rules — read carefully:**
- Do NOT include this file in any `public/` folder or any public commit.
- Do NOT reference realized values in any public card description or example output.
- The `final_scorer.py` in `private/scoring/` is the ONLY process that reads this file.
- The file must cover ALL asset x horizon combinations in `[targets]`.

---

## Step 7 — Set the predictive-distribution format

Specify what output format participants must produce. Two formats are supported:

**Format A: Samples (preferred)**

```toml
[scoring.params]
representation = "samples"
n_draws_min    = 200
```

**Format B: Parametric — WITHDRAWN, do not author a card that asks for it**

`representation = "parametric"` was advertised by the shared output schema and implemented by
nothing. No code in any repository read the `cov.parquet` it promised, and because the schema made
`n_draws` conditional on `representation == "samples"`, declaring `parametric` was a route past the
200-draw floor: three draws under `parametric` were fully admissible while the same three draws
under `samples` were rejected. The scorer now refuses any representation but `samples`, and the
schema change is filed with the Hub, which owns `forecast.schema.json`.

Draw-format samples are the only accepted representation. `require_samples` is therefore
redundant: every card requires samples, whatever it says. It is left in existing cards rather than
mass-edited, and it is read by nothing.

---

## Review checklist before publishing any card

Work through this list in order. All boxes must be checked before the card enters `public/`.

**Card structure:**
- [ ] `card.toml` exists and all `TEMPLATE_` placeholders have been replaced
- [ ] `card.toml` has a `[text]` section with `source`, `path`, `cutoff` fields
- [ ] `forecast_card.md` explains the task clearly to a junior participant
- [ ] `manifest.json` is the per-file CHECKSUM manifest (`manifest_version` `"2.0"`, `unit_id`, `files[]` with sha256 per committed file — validated by `qfbench2_common.manifest.verify_manifest`)
- [ ] The forecasting data-spec (panels, text corpus, targets, scoring parameters) lives in `forecast_spec.json`, NOT in `manifest.json`
- [ ] `[metadata].category` is exactly one of `T2-F1`, `T2-F2`, `T2-F3`, `T2-F4`
- [ ] `canary_guid` is a unique UUIDv4

**Panel and data:**
- [ ] All panels specify `end_date = asof` exactly
- [ ] No panel series contains any observation after the as-of date
- [ ] Factor lags are documented in `[notes]`

**Text corpus:**
- [ ] Text corpus directory exists at the path specified in `[text] path`
- [ ] Every document in the corpus has a timestamp on or before the as-of date
- [ ] `_check_text_corpus_cutoff(unit_dir, card, asof)` returns an empty violation list
- [ ] `[text] cutoff_checked = true` is set in card.toml
- [ ] No post-asof documents are present in any text corpus file
- [ ] Corpus index (`corpus_index.json` or equivalent) lists all documents with timestamps

**As-of date and targets:**
- [ ] Minimum gap rule for the declared family is satisfied
- [ ] The as-of date is no later than 2024-12-31 (to ensure target dates are finalized)
- [ ] `cutoff_ok(asof, target_dates)` returns `True`
- [ ] `[targets] leakage_checked = true` is set
- [ ] Horizons are in business days; calendar target dates are documented

**Realized outcome:**
- [ ] `private/units/<card_id>/reference/realized.parquet` exists
- [ ] realized.parquet covers all asset x horizon combinations
- [ ] realized.parquet is NOT under any `public/` path
- [ ] No public file references or echoes any realized value

**Scoring and format:**
- [ ] `n_draws_min = 200` (at minimum)
- [ ] `require_samples = true` for F3 and F4 cards
- [ ] Scoring weights sum to 1.0 (default: 0.5 / 0.3 / 0.2)
- [ ] `scoring.verifier = "t2.crps_composite"` is set

**Smoke test:**
- [ ] Run the card through the smoke scorer locally:
  ```bash
  qfbench2-smoke units/<card_id>/ output/ --track forecasting
  ```
- [ ] Gate g2 passes: text corpus timestamps all <= asof (verify in smoke output)
- [ ] Gate g0 through g3 all pass green for a valid test submission

---

## Why these rules exist (the "why" behind the checklist)

**Why sealed realized outcomes?** If participants can see the actual market outcome, they can
trivially "forecast" it. The entire scoring system depends on outcomes being unknown.

**Why the text corpus cutoff?** The whole scientific question is whether an agent can extract
useful signal from text that was available before the forecast date. Allowing post-asof text
would let the agent "read" the future — defeating the purpose and inflating scores unfairly.

**Why gate g2 checks text timestamps?** The gate's name is g2_cutoff_resource — it enforces
both the panel data cutoff (no rows with `date > asof`) and the text corpus cutoff (no
document with timestamp > asof). These two checks are bundled because they share the same
purpose: ensuring the agent sees only information available on the as-of date.

**Why the minimum gap?** A 1-day forecasting horizon would be trivially predictable. The gaps
chosen (1-6 months by family) target the range where models genuinely differentiate.

**Why `require_samples = true` for F3 and F4?** A Gaussian mean + covariance matrix can
represent any linear correlation structure, but it cannot represent fat tails (F4) or
non-Gaussian copulas (F3). Requiring samples ensures the submission's distribution is
actually fat-tailed.

---

## Common mistakes in card authoring

1. **Post-asof text in the corpus.** The most common new mistake under the text-framing.
   An author includes an FOMC statement that was released one week after the as-of date —
   perhaps by accident, because they were copying from a broader data dump. Gate g2 will
   reject the submission, but the real cost is invalidating the card. Always run
   `_check_text_corpus_cutoff` before publishing.

2. **As-of date set too recently.** As-of = 2025-01-01 for a card that targets Q2 2026.
   The realized values for Q2 2026 may not yet be finalized. Keep the as-of date in 2024
   or earlier unless you are certain all target observations are published.

3. **Realized values in the public forecast_card.md.** Authors sometimes write "the 10-year
   yield on 2024-07-31 was 4.35 %" in the card description. Even this is leakage — remove
   any realized values from all public files.

4. **Wrong canary_guid.** Copying a card template without replacing the `canary_guid` means
   two cards share the same GUID. Always generate a fresh UUID4 for every card:
   `python -c "import uuid; print(uuid.uuid4())"`.

5. **Horizon in calendar days, not business days.** "21 days" after July 3 is July 24 in
   calendar days, but the 21st business day from July 3 is approximately August 2. Use
   `pandas.offsets.BDay(21)` to compute the correct calendar target date.

6. **Forgetting that T2-F2 (transfer-configuration) requires the target series to be absent
   from the panel.** An F2 card where BRL/USD appears in the FX panel is actually an F1 card.
   Remove the target series from the panel spec explicitly.

7. **No corpus index.** The text corpus directory exists but has no machine-readable index
   of timestamps. Gate g2 cannot verify the cutoff without timestamps. Always include a
   `corpus_index.json` or equivalent.
