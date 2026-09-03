# AGENTS.md — Track 2 public repo rules for AI agents

## Executive summary (read this first)

This file tells an AI coding agent — or a new human contributor — how to work in the
**Track 2 public repository** (`track2-forecasting-public`). Three rules are absolute:
(1) the public/private firewall must never be broken — no realized outcome or answer key
may be placed here; (2) the `qfbench2-common` toolkit must be imported, never reimplemented;
(3) every file must open with an executive summary in plain English before going into detail.

Track 2 is **Reasoning-Augmented Time-Series Forecasting**: agents forecast the future of
time-series data (rates, FX, macro, factors) by combining a time-series forecasting component
with LLM reasoning over a frozen, time-stamped text corpus. This distinguishes it from
Track 4 (general tabular data → predict a label/value). Both tracks add text and run in
Docker with no open internet: unit cards declare `network = "restricted"`, meaning the only
egress is model-API calls through the organizer's audited proxy (see README "Network
contract and submission categories"). Local smoke runs use `--network=none`.

**Track 2 is led by Polak.** Reviewers for this track are Rosenberg, Kazantsev, and
Koutsoyannis. Every pull request to this repository must be reviewed and approved by Polak
before it merges.

> **Status of that rule.** It is a project rule, not an enforced control, and `.github/CODEOWNERS`
> is a proposal rather than a live gate. This file used to claim the rule was "enforced via
> CODEOWNERS + branch protection"; a documented control that does not exist is worse than an
> acknowledged gap, because everyone downstream plans around it.

Read `Agenthon-2026/Agenthon2026-public`, file `AGENTS.md` first: it covers the shared
`qfbench2-common` toolkit and the local gate loop every track uses.
This file only adds Track 2 specifics.

---

## Hard rules for this repo

1. **Firewall.** Nothing that reveals a realized market outcome, card answer, or solved
   scoring result may exist in this repo. Forbidden file names and patterns include:
   `reference/`, `realized.parquet`, `oracle_*`, `answer_key*`, `solution/`, `expected*`,
   any numeric value described as "the realized outcome for card X". The checker
   `qfbench2_common.manifest.assert_public_safe` must pass on every PR.

2. **No new scoring math.** The CRPS composite, variogram score, and tail penalty formulas
   live only in the `qfbench2-common` toolkit, `Agenthon-2026/Agenthon2026-public`,
   `common/qfbench2_common/scoring/`.
   Do not rewrite them here. If you need a new scoring variant, add it to the toolkit
   first, then call it from
   `scoring/scoring.py` here.

3. **Family strings are locked.** Card families must be exactly `T2-F1`, `T2-F2`, `T2-F3`,
   or `T2-F4`. Gate names must be exactly `g0_integrity`, `g1_schema`, `g2_cutoff_resource`,
   `g3_domain_semantics`. Submission verb is `forecast`. Do not invent new names.

4. **canary_guid is unique per card.** Every card.toml must have a unique UUIDv4 in
   `[contamination] canary_guid`. Never reuse an existing GUID and never copy the exemplar
   GUID `f3a1c2e8-4b7d-4e9f-a2c1-8d3e7b5f9a0c`.

5. **Horizons in business days.** All horizon values in `[targets] horizons` and in the
   output `forecast.parquet` column `horizon` are in business days. Never calendar days.

6. **n_draws minimum is 200.** No card spec or example output should use fewer than 200
   draws. For F3 and F4 guidance, recommend >= 500 and >= 1000 respectively.

7. **Text corpus timestamps are enforced.** Every document in a card's `text/` corpus must
   have a timestamp on or before the card's as-of date. Gate g2 checks this. Do not include
   any document with a post-asof date in the text corpus stub or example. When adding text
   snippets to a card, always annotate them with a clear date.

---

## File layout — what lives where

```
public/
├── README.md               ← participant quick-start (exec summary first)
├── AGENTS.md               ← this file
├── TASK-CATEGORIES.md      ← stub pointer → docs/CATEGORIES.md
├── docs/
│   ├── CONCEPTS.md         ← plain-English explainer of all scoring + text concepts
│   ├── CATEGORIES.md       ← deep guide to all four card families (F1–F4)
│   └── AUTHORING-GUIDE.md  ← step-by-step card design guide (for organizers)
├── units/                  ← example and validation forecast cards (no realized outcomes)
│   └── t2-EXAMPLE-ust-curve-1m/
│       ├── card.toml       ← includes [text] section
│       ├── text/           ← tiny frozen text corpus stub (dated snippets)
│       └── ...
├── scoring/scoring.py      ← reference scorer (calls qfbench2-common; g2 binds the declaration to the card — corpus dates are checked at staging)
├── baselines/              ← five adapter SCAFFOLDS (all return a Gaussian random walk) + README
│   └── README.md           ← says plainly what they do and do not provide
└── templates/
    └── card.toml           ← includes [text] section template
```

Do NOT create `reference/` or `realized/` directories here. Those belong in
`private/units/<card_id>/reference/`.

---

## Writing standard

- Every new file opens with `## Executive summary (read this first)`.
- Define every technical term the first time it appears. When in doubt, add
  "(see the GLOSSARY published with the shared toolkit: Agenthon-2026/Agenthon2026-public,
  docs/GLOSSARY.md)".
- Show a concrete example before the abstract definition.
- Short sentences. One idea per sentence.

---

## Quick checks before calling work done

```bash
# Verify no realized-outcome files leaked into public.
# Takes ONE unit directory, and this repo has no `public/`. The bare dotted name above
# was not a command at all -- pasted into a shell it is `command not found`, and this
# block ends with "If any check fails, do not merge."
# `|| break` would be wrong here: it stops at the first bad unit AND the loop exits 0,
# which is the same "guard that cannot fail" this line was fixed to remove.
fail=0; for u in units/*/; do qfbench2 manifest assert-public-safe "$u" || fail=1; done; exit $fail

# Smoke-score the exemplar card
qfbench2-smoke units/t2-EXAMPLE-ust-curve-1m/ output/ --track forecasting

# Run shared toolkit tests. They live in the toolkit's own repository
# (Agenthon-2026/Agenthon2026-public); run this from a checkout of it, not from here.
python -m pytest common
```

If any check fails, do not merge.
