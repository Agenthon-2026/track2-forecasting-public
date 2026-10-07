# Changelog

## Executive summary (read this first)

This file records what changed in the Track 2 forecasting kit, newest first. Each entry says
whether scoring is affected. `## Still to reconcile` lists known open items. `## Unreleased`
lists changes merged for the next public update; each dated section below it is headed by the
UTC date its changes reached public `main` and the commit `main` was at afterwards, down to the
published baseline checked on 2026-09-14. Release timing follows the organizer announcement in
public issue #4.

## Still to reconcile

- A resolvable deployed-scorer identifier and the Final revision announcement (issue #7).

## Unreleased

**Scores change: every card is divided by the baseline's expected error, and the cap and failure
value are 8.0 (first entry below).** Track scorer code and evaluation cards are unchanged; that
change is carried by the normalization scale files and the signed evaluation plan. Documentation and
link corrections, the toolkit pin move and one unit document cleaned of later news change no scoring
path, gate, card or published number, and twenty practice units are renamed (ids only; entry below).
Seven further entries change practice units, each stating its own scoring effect: the second entry
below changes the card text of all 104 cards, and the third that of twenty-seven practice cards and
the worked example; the fourth, the fifth and the practice-corpus entry, seventh below, change the
text of the practice units; the monthly practice-panel entry, eighth below, changes the data and
notes of four practice units; and the entry after it changes the card text of two monthly practice
cards.

- **Every card is now divided by the text-blind baseline's expected error, and the cap and the
  failure value move from 4.0 to 8.0.** *Scoring:* every Track 2 score changes. The scorer code is
  unchanged; the change is in the normalization scale files and the signed evaluation plan.
  - **Divisor.** Each component of a card's composite (marginal CRPS, joint variogram, tail) is
    divided by the error the text-blind baseline M0 expects to make on that card: its average
    score if the outcome were drawn from its own forecast distribution, computed exactly from the
    card's inputs before the outcome exists ([`docs/M0-BASELINE.md`](docs/M0-BASELINE.md) §5).
    It used to be divided by M0's score on the realized outcome of that card.
  - **What 1.0 means now.** An error equal to the error M0 expects of itself. M0 no longer scores
    exactly 1.0; the leaderboard shows its actual score as a reference row.
  - **Cap and failure value: 8.0, both** (they were 4.0). Real per-card scores are clipped at 8.0,
    and a card that is not scored counts 8.0 and stays in the average.
  - **Development and Final.** Every finished Development submission is re-scored under the new
    rule, so all entries on the board are on one scale. The new values are not comparable with
    those shown before the change. The Final uses the same rule.
  - **Scale files.** A scale depends only on the card's inputs, so on a released card you can
    compute it from the published method. Scale files are still not shipped with any card.
  - **Documents.** `docs/M0-BASELINE.md` (§§1, 2, 3.7–3.9 and 4–7), `docs/CONCEPTS.md` (§§4 and
    13), `README.md`, `docs/CATEGORIES.md` and `baselines/README.md` describe the new rule. The
    reference-CLI comparison in `docs/M0-BASELINE.md` §7 was measured under the old rule and is
    marked for re-measurement.

- **`[metadata].difficulty` removed from all 104 cards, and `[metadata].design_note` from the 31 F4
  practice cards.** Neither key is part of the card format: `difficulty` is gone from every card in
  `units/` (the 71 validation units, the 32 other practice units and the worked example) and from
  `templates/card.toml`, `design_note` from every F4 practice card, Final input cards will not carry
  either, and `.github/validate_units.py` refuses a card that does. *Scoring:* card text only.
  Neither the reference CLI nor the scorer reads either key; targets, spec, panels, corpus,
  reference outcomes and scales are unchanged. The copies evaluated on CodaBench change at the next
  Track 2 evaluation update.

- **Text corpus role paragraphs and nine card titles: reworded on twenty-seven practice cards and
  the worked example.** The "Text corpus role" paragraph of `forecast_card.md`, and the same text in
  `card.toml` `[text].notes`, are reworded to describe the documents in each corpus on
  `t2-F1-ai-mom-2024`, `t2-F1-chf-highly-valued-2021`, `t2-F1-hawkish-cut-2024`,
  `t2-F2-aud-taper-2013`, `t2-F2-trade-war-escalation-2019`, `t2-F3-dots-vs-oil-2014`,
  `t2-F3-inversion-persistence-2019`, `t2-F3-readout-calendar-factors-2020`, `t2-F4-aud-gfc-2008`,
  `t2-F4-mkt-new-year-2016`, `t2-F4-covid-nfp-2020`, `t2-F4-covid-rates-2020`,
  `t2-F4-cpi-friday-2022`, `t2-F4-factor-stress-2008`, `t2-F4-funding-stress-2y-2008`,
  `t2-F4-funding-stress-10y-2008`, `t2-F4-ust2y-december-fomc-2021`, `t2-F4-hml-covid-2020`,
  `t2-F4-jpy-carry-2007`, `t2-F4-jpy-crowding-2024`, `t2-F4-mkt-debt-ceiling-2011`,
  `t2-F4-momentum-bank-stress-2009`, `t2-F4-nok-covid-2020`, `t2-F4-powell-december-2018`,
  `t2-F4-factor-joint-credit-2007`, `t2-F4-short-vol-2018` and `t2-F4-vaccine-timeline-2020`, and so is
  `[text].notes` on the worked example `t2-EXAMPLE-ust-curve-1m`, whose forecast card has no such
  paragraph. On most of these cards the matching sentence of `[metadata].description` is reworded
  the same way. The title, `[metadata].description` and `forecast_card.md` heading of
  `t2-F1-ai-mom-2024`, `t2-F4-aud-gfc-2008`, `t2-F4-covid-rates-2020`, `t2-F4-cpi-friday-2022`,
  `t2-F4-ust2y-december-fomc-2021`, `t2-F4-jpy-crowding-2024`, `t2-F4-momentum-bank-stress-2009`,
  `t2-F4-powell-december-2018` and `t2-F4-short-vol-2018` name the event and the date. *Scoring:*
  card text only; targets, spec, horizons, panels, corpus, reference outcomes and scales are
  unchanged. The copies evaluated on CodaBench change at the next Track 2 evaluation update.

- **Four COVID-era practice cards held a speech given in January 2021.**
  `text/bis_elderson_2020-01-25.txt` on `t2-F3-covid-curve-2020`, `t2-F4-covid-mkt-2020`,
  `t2-F4-covid-rates-2020` and `t2-F4-hml-covid-2020` is Frank Elderson's introductory statement at
  the European Parliament's ECON hearing of 25 January 2021, which the speech archive dates a year
  early; it refers to the COVID-19 pandemic. It is removed from the four cards, whose document
  counts, corpus indexes and manifests are updated, and `data/PROVENANCE.md` is re-measured (999
  text files). *Scoring:* no realized value, reference or scale changes. The text an agent reads on
  these four cards changes, so a text-using agent's outputs on them can change. The copies evaluated
  on CodaBench change at the next Track 2 evaluation update.

- **Practice-unit text corpora: each card now carries its target central bank's decisions, the
  document of the event it is built around, and unrelated documents to set aside.** *Scoring:*
  scorer code, gates, reference outcomes and normalization scales are unchanged. The text an agent
  reads on the practice units changes, so a text-using agent's outputs on those units can change.
  The copies evaluated on CodaBench change at the next Track 2 evaluation update.
  - **Why.** Many cards forecast a non-US asset but their corpus held almost only Federal Reserve
    material, and the event a card is named after was often not in its corpus. On such cards the
    text gave an agent little to use.
  - **311 files added on all 103 practice units** (237 distinct documents; 2 to 13 per unit; a unit
    now holds 5 to 20 documents, median 9):
    - **65 monetary policy decisions** of the card's target central bank, the one in force at the
      as-of date and on some cards the one before it: Bank of Japan 14, ECB 13, SNB 6, RBA 5, Bank
      of England 5, Bank of Canada 4, Norges Bank 4, Riksbank 4, Danmarks Nationalbank 2, PBoC 2,
      Banco Central do Brasil 2, RBI 2, RBNZ 2. New `doc_type`: `central_bank_decision`.
    - **41 key-event documents** (36 distinct), indexed as landmarks: FOMC Summaries of Economic
      Projections and policy-normalization statements, Chair press-conference transcripts, Board
      and joint-agency statements, U.S. Treasury, White House, State Department and USTR
      statements, ECB press conferences, two Bank of Japan speeches, two Japan Ministry of Finance
      documents (one in Japanese only, as published), HM Treasury's Growth Plan 2022 and a Lehman
      Brothers 8-K exhibit. Each is listed with its official source in `data/LANDMARKS.md`.
    - **205 speeches on unrelated topics** by Federal Reserve Board, ECB and Bank of Japan
      officials, such as payments, supervision, climate and statistics. They are there on purpose:
      part of the task is telling which documents matter.
  - **Dates.** Every added file is dated by its publication date, on or before its card's as-of
    date; press-conference transcripts carry the day the final transcript was posted.
    `cutoff.scan_text_corpus_cutoff` passes on all 104 units and
    `python3 scripts/declutter_corpus.py --check units` reports every unit text clean.
  - **Records.** `corpus_index.json`, `card.toml` `[text]` (`n_documents`, `doc_types`, `source`),
    the document count in `forecast_card.md` and `manifest.json` are updated on every practice unit.
    `data/PROVENANCE.md` is re-measured (1,003 text files); `THIRD-PARTY-NOTICES.md` and
    `DATA-LICENSE.md` list the new issuers. Six of the added files, copies of four ECB speeches,
    print the ECB's reproduction permission and are labelled
    `LicenseRef-ECB-Reproduction-Permitted`.

- **`t2-F3-scandies-stress-2022`: a document carried news from after the card's as-of date.**
  `text/boe_mpc_statement_20220922.txt`, the Bank of England statement of 22 September 2022 on a
  card whose as-of date is 23 September 2022, ended with a block of site navigation scraped in
  2026 that listed Bank Rate decisions from 2026. That block is removed and the unit's manifest
  updated. No realized value, reference or scale changes. The copy evaluated on CodaBench was
  updated on 27 September 2026 at 19:14 UTC.

- **Practice-unit text corpora: counts corrected, 59 documents added, website material removed.**
  *Scoring:* this change leaves scorer code, gates, reference outcomes and normalization scales as
  they are. The text an agent reads on the practice units changes, so an agent's outputs on those
  units can change. The copies evaluated on CodaBench were updated on 27 September 2026 at 19:14 UTC.
  - **Counts.** On 92 units `forecast_card.md` stated a document count that did not match the
    files shipped. The prose, `card.toml` `[text]` (`n_documents`, `doc_types`, `source`),
    `text/corpus_index.json`, the manifests and the files on disk now agree on every unit.
  - **59 documents added** on 42 units: 14 CPI and 16 Employment Situation releases, 19 sets of
    FOMC minutes, 5 Beige Books, 3 Bank of Japan policy statements, the SNB's 15 January 2015
    press release and the FOMC statement of 22 September 2021. Every one is dated on or before
    its card's as-of date.
  - **Website material removed** from 173 existing and 38 of the added documents by one committed
    module, `scripts/declutter_corpus.py`: menus, footers, "Return to top" separators,
    related-news lists and a trailing "Last Modified Date:" page label. Document text is kept,
    including every District report of the 2024 Beige Books, Beige Book titles, release dates and
    "prepared at" preambles, BLS release headers, and the date line of the 2007-2011 FOMC minutes.
    `python3 scripts/declutter_corpus.py --check units` confirms every unit text is clean.
  - **Post-as-of material.** The Bank of England statement's list of 2026 announcements is
    already removed (see the `t2-F3-scandies-stress-2022` entry above). Four BLS files carried a
    note that the release was reissued after its publication date (`cpi_2011-07-15.txt` on two
    units, `empsit_2020-02-07.txt` and `empsit_2020-03-06.txt` on `t2-F4-covid-nfp-2020`); the
    notes are removed and listed in `data/corpus-cleaning/reissue-notes-removed.tsv`. The tables
    in those files are still the reissued versions.
  - **Beige Book dates.** Nine `corpus_index.json` timestamps now carry the Beige Book's release
    date; four of them had been earlier than the release. No card has a Beige Book released after
    its as-of date.
  - **Docs.** New `data/LANDMARKS.md` gives the official source of the 13 landmark documents;
    `data/PROVENANCE.md` is re-measured; `THIRD-PARTY-NOTICES.md` and `DATA-LICENSE.md` list the
    SNB press release under the SNB's published copyright terms, which allow non-commercial use
    compatible with the purpose of the information.

- **Monthly practice panels now hold the data as published on each card's as-of date.** The
  `macro_monthly.parquet` panels of the four monthly practice cards (`t2-F1-cpi-glidepath-2023`,
  `t2-F1-sahm-watch-2024`, `t2-F4-covid-nfp-2020`, `t2-F4-cpi-vintage-2022`) carried today's
  revised values, not the values published by the as-of date that
  [`docs/CATEGORIES.md`](docs/CATEGORIES.md) tells you to use. Nothing in them was published after
  the as-of date; the difference was later revisions only. Each panel is now the ALFRED vintage in
  force on its card's as-of date, revisions released that day included.
  - **What changes.** Values only: rows, dates, assets, the 45-day publication-lag truncation and
    the file format are unchanged. Between 517 and 948 values change per panel: recent CPI months
    (seasonal-factor revisions), most payroll months (benchmark revisions), some
    unemployment-rate months and the PCE indexes.
  - **PCE index base.** On the three cards dated before September 2023 the PCE indexes are on the
    base then published, 2012=100, so their levels sit about 6 to 8% above the same months on
    today's 2017=100 basis. That is the published basis, not an error.
  - **Documents.** Each card's panel note, `forecast_card.md` and manifest now state the vintage,
    as does `data/PROVENANCE.md`. The pooled row count in README leakage rule 5 is updated to
    148,680 (re-run: still 0 exposed), and [`docs/M0-BASELINE.md`](docs/M0-BASELINE.md) §6 dates
    the four regenerated scales.
  - *Scoring:* targets, target months and scored values do not change.
    `t2-F1-cpi-glidepath-2023` and `t2-F1-sahm-watch-2024` are still scored on the current
    vintage, as their `value_unit` says. The organizer-side normalization scales of the four
    cards were regenerated from the new panels by the unchanged M0 procedure. All four are
    public-dev units, so none of them is part of the Final.

- **Two monthly practice cards name the month they are scored on.** `t2-F4-cpi-vintage-2022`
  and `t2-F4-covid-nfp-2020` said they forecast "the next" print; the scored month is one
  print later than the next unreleased print at the as-of date. Card text only: targets, spec,
  horizons, panels and corpus are unchanged.
- **[`docs/M0-BASELINE.md`](docs/M0-BASELINE.md) matches the monthly release.** It still
  described the cards before the 2026-09-16 monthly release. It now says what a released
  monthly card publishes, follows the reference CLI's monthly path, and gives the recipe for
  the normalization scale commitment. Documentation only.
- **[`docs/M0-BASELINE.md`](docs/M0-BASELINE.md) §3.7: a monthly cell that names its month is
  counted to that month.** Where `forecast_spec.json` names a cell's observation month, M0 walks
  one step per month from the target series' last published observation to that month, with no
  2x test. On the monthly cards of the Final phase that is one or two steps more than the months
  from the as-of month, because their series end one or two months before it; the old wording
  would have kept the declared horizon there. The organizers' scale generator makes the same
  count. No published scale changes: on the published cards, the new rule gives the same step
  count as the old one on every cell where M0 applies it. §4 adds a synthetic example.
  Documentation only.

- **Twenty practice units renamed; their ids name the event and the date.**
  `t2-F3-bear-flattener-2022` is now `t2-F3-front-loaded-hikes-2022`; `t2-F3-taper-steepener-2013`
  is now `t2-F3-taper-testimony-curve-2013`; `t2-F2-eur-parity-2022` is now
  `t2-F2-eur-energy-divergence-2022`; `t2-F3-term-premium-steepener-2023` is now
  `t2-F3-sep-dots-curve-2023`; `t2-F4-momentum-reversal-2009` is now
  `t2-F4-momentum-bank-stress-2009`; `t2-F4-mkt-selloff-2011` is now `t2-F4-mkt-debt-ceiling-2011`;
  `t2-F4-china-panic-2016` is now `t2-F4-mkt-new-year-2016`; `t2-F3-cpi-shock-cross-2022` is now
  `t2-F3-cpi-release-cross-2022`; `t2-F4-svb-whiplash-2023` is now `t2-F4-same-week-texts-2023`;
  `t2-F3-safe-haven-paradox-2011` is now `t2-F3-fiscal-risk-joint-2011`;
  `t2-F3-vaccine-rotation-2020` is now `t2-F3-readout-calendar-factors-2020`, and its title,
  `[metadata].description` and `forecast_card.md` heading name the event; `t2-F3-oil-fx-split-2022`
  is now `t2-F3-energy-escalation-fx-2022`; `t2-F4-qe1-expansion-2009` is now
  `t2-F4-ust10y-january-fomc-2009`; `t2-F4-quant-crowding-2007` is now
  `t2-F4-factor-joint-credit-2007`; `t2-F3-funding-flip-2024` is now `t2-F3-funding-carry-fx-2024`;
  `t2-F2-fragile-five-brl-2013` is now `t2-F2-brl-transfer-2013`; `t2-F2-fragile-five-inr-2013` is
  now `t2-F2-inr-transfer-2013`; `t2-F3-fragile-five-joint-2013` is now
  `t2-F3-em-transfer-joint-2013`; `t2-F4-hike-cycle-2021Q4b` is now
  `t2-F4-ust2y-december-fomc-2021`; `t2-F4-chf-floor-strain-2015` is now
  `t2-F4-chf-defended-floor-2015`. The unit directory, `[task].id`, the `card_id` of
  `forecast_spec.json` and `text/corpus_index.json`, and the manifest's `unit_id` change; card text,
  targets, panels and corpora do not. Fifteen of the twenty are validation units
  (`t2-F3-front-loaded-hikes-2022`, `t2-F3-taper-testimony-curve-2013`,
  `t2-F4-momentum-bank-stress-2009`, `t2-F4-mkt-debt-ceiling-2011`, `t2-F4-mkt-new-year-2016`,
  `t2-F3-cpi-release-cross-2022`, `t2-F3-readout-calendar-factors-2020`,
  `t2-F3-energy-escalation-fx-2022`, `t2-F4-ust10y-january-fomc-2009`,
  `t2-F4-factor-joint-credit-2007`, `t2-F3-funding-carry-fx-2024`, `t2-F2-brl-transfer-2013`,
  `t2-F2-inr-transfer-2013`, `t2-F3-em-transfer-joint-2013`, `t2-F4-ust2y-december-fomc-2021`). On
  some of these and other practice cards the title, `[metadata].description`, the "Text corpus role"
  paragraph, or the `t2c-` catalog name in `[metadata].tags` and `created_by` is reworded the same
  way. *Scoring:* none. The copies evaluated on CodaBench change at the next Track 2 evaluation
  update.

- **Toolkit pin moved to `v2.6.0` everywhere.** `.github/workflows/ci.yml`, the README install
  commands, `Dockerfile`, the hub guide links in `README.md` and `SUBMISSION_CLI.md`, and
  `docs/FORECAST-RESOLUTION-CANDIDATE.md` name `v2.6.0`. `qfbench2 card validate` from `v2.6.0`
  accepts a card without `[metadata].difficulty`. *Scoring:* none; scorer code, gates and cards are
  unchanged.

- **`docs/CATEGORIES.md`: the F2 and F4 worked examples describe the setup.** The first F2
  example of leading-indicator text, the F2 GBP/USD example, the F4 examples of foreshadowing text,
  the as-of rule and the F4 example card describe each card's inputs and window; the example card
  ids are `t2-F2-gbp-boe-2022Q3` and `t2-F4-ust-fomc-2021Q4`. Documentation only.

- **Last Development runs start by 20:00 UTC on Monday 12 October 2026.** A scheduled
  maintenance window on Tuesday 13 October 2026, 08:00–12:00 UTC stops the evaluation fleet. An
  upload that has not started by 20:00 UTC on 12 October, whenever it was made, is not run, and
  one made during the window shows `Submitting` until 12:00 UTC and is not run. Announced in
  public issue #18; now also in the README's schedule section and in `SUBMISSION_CLI.md`.
  Scoring, limits and the submission contract: unchanged.
- **Final tie-break in `SUBMISSION_CLI.md`.** Its schedule paragraph now carries the sentence the
  README has carried since 2026-09-22: if two Final submissions finish this track with the same
  ranking score, the one uploaded earlier ranks ahead. No rule change.
- **Runtime guide links moved to `main`.** The Development runtime guide links in `README.md`
  and `SUBMISSION_CLI.md` pointed at the toolkit's `v2.4.4` copy, which still states the
  withdrawn allowance of 1,000,000 input tokens per unit and lacks the tie-break and
  `Failed`-upload sentences. They now point at the guide's `main` copy, like the
  submission-limits link and the House model guide links already do. The image-submission,
  descriptor and team-claim links stay on `v2.4.4`; those guides have not changed since.
- **`docs/FORECAST-RESOLUTION-CANDIDATE.md`** said no public toolkit tag carries the module the
  opt-in candidate API needs. Toolkit `v2.4.4`, which this repository pins, carries
  `qfbench2_common.contracts.forecast_protocol`, and public CI installs `v2.4.4` and runs the
  candidate's tests. Documentation only.
- **`docs/NVIDIA-STACK.md`, "Where the tooling lives":** an "(In review)" line linked two public
  pull requests that are unrelated documentation fixes. It now links the repo-root `Dockerfile`
  (the reference submission image), the README's end-to-end run section and
  `docs/SOLVER-PLAYBOOK.md`. The playbook's composite formula now names the tail term as the
  pinball loss at the 1/5/95/99% quantiles, as `docs/CONCEPTS.md` states, instead of "PIT
  calibration".
- **House wording.** Three passages in `README.md` and `SUBMISSION_CLI.md` said the House route
  is budgeted "per run"; the budget is per unit (25 admitted requests), as rule 5 of
  `SUBMISSION_CLI.md` states. `MODEL_NAME` is now described as the runtime alias of the House
  model, with the model identity and snapshot for `models[]` in the House model guide, instead of
  "the pinned house-model id". No rule changes.
- **This file.** Sections are now dated by when their changes reached public `main`. The
  2026-09-23 changes it listed as unreleased are dated, and the missing entries for 2026-09-16 to
  2026-09-23 are added. Two rulings of 2026-09-21 that were filed under the 2026-09-14 baseline
  moved to 2026-09-22, and that baseline's House-allowance entry is restored to its published
  wording. Resolved items are removed from "Still to reconcile".

## 2026-09-24 — public `main` at `8799596`

**Track scorer code and evaluation cards: unchanged.** A CI comment and two documentation links.

- **House model guide links moved to `main`.** The two House model guide links in
  `docs/NVIDIA-STACK.md` pointed at `v2.4.3`, whose copy still lists an input-token limit among
  the House limits and lacks the note that `low_effort` and `reasoning_budget` pass through
  unchanged. They now point at the guide's `main` copy.
- **`.github/workflows/ci.yml` comment.** It said no released toolkit tag carries
  `contracts.forecast_protocol`; `v2.4.4`, the pinned tag, does. Comment only; the install is
  unchanged.

## 2026-09-23 — public `main` at `f84ad29`

**Track scorer code and evaluation cards: unchanged.** These are documentation and build-pin
corrections. They change no scoring path, no gate, no card and no published number.

- **An upload the platform marks `Failed` does not consume a Development attempt** — the
  platform's daily count excludes it. Held and cancelled uploads still count. (`README.md`,
  `SUBMISSION_CLI.md`; the latter's submission-limits link now points at the hub guide's `main`
  copy.)
- **Toolkit pin moved to `v2.4.4` everywhere.** The 2026-09-18 bump reached the README's install
  commands but not `.github/workflows/ci.yml` or the `Dockerfile`, so CI and the reference
  submission image kept validating against `v2.4.2` — whose category enum still contains
  `byo-large` and `byo-small`, the two values the same ruling withdrew. A descriptor naming one
  of them packs cleanly under `v2.4.2`, is then held at organizer intake and never runs, and
  still costs a Development attempt, with no local signal that anything was wrong. The README
  prose also still told you to pin `v2.4.2` while the command beside it installed `v2.4.3`. The
  2026-09-21 bump to `v2.4.4` fixed `ci.yml` and that prose but again missed the `Dockerfile`. All
  three now name `v2.4.4`, and a new stdlib-only CI step fails the build if they disagree again.
- **`README.md` container-environment table corrected.** It described `MODEL_ENDPOINT` as
  already carrying `/v1` and never mentioned `MODEL_TOKEN` at all. `MODEL_ENDPOINT` is the route
  origin with no path, the OpenAI-compatible API is served under `/v1`, and a request without
  `Authorization: Bearer $MODEL_TOKEN` is refused 401 — so an agent built from that table alone
  failed every House call. The 2026-09-17 House-route correction reached `SUBMISSION_CLI.md` and
  `docs/NVIDIA-STACK.md` and missed this table. It now also states `NO_PROXY` and the House
  request allowance, and names `SUBMISSION_CLI.md` as the binding version instead of maintaining
  a second full copy that can drift.
- **`docs/ARTIFACT-POLICY.md` aligned with the 2026-09-18 ruling.** Its executive summary still
  said Track 2 permits artifacts "in both submission categories" and that "the adapter-only rule
  governs language-model serving", and a later paragraph still asserted a one-adapter limit on a
  bring-your-own language-model path — each contradicting the ruling stated in the same file and
  in `README.md`. This was the last file in the tree carrying the withdrawn regime, and it is the
  file `README.md` designates as the authority on what may be packaged. The permitted-artifact
  table is unchanged; what changes is the description of the regime around it. Policy revision
  stamp moved to 2026-09-21.1. The category sentence this file shares with `README.md` and
  `SUBMISSION_CLI.md` also loses its leftover "for this non-adapter path", in all three files.

## 2026-09-22 — public `main` at `8da3c76`

**Scoring formula and scores: unchanged.**

- **House model budget: requests per unit** (ruling of 2026-09-21). 25 admitted requests per
  unit and at most 4,000 output tokens per call, both counted by the House route. The allowance
  of 1,000,000 input tokens per unit that `README.md` and `SUBMISSION_CLI.md` stated from
  2026-09-16 is withdrawn and **nothing replaces it**: there is no per-unit token allowance. An
  admitted request is charged before forwarding, so an upstream failure, a lost response or a
  retry can spend a slot; a request refused before admission costs nothing. (`README.md` "House
  API allocation", `SUBMISSION_CLI.md` rule 5, `docs/NVIDIA-STACK.md`.) (Answers the last open
  item of issue #2.)
- **Ties in the ranking score** (ruling of 2026-09-21): if two Final submissions finish this
  track with the same ranking score, the one uploaded earlier is ranked ahead. The ruling covers
  the Final ranking. (`README.md`.)

## 2026-09-21 — public `main` at `4a14af5`

Reached public `main` in two pushes: `4ee4069` at 01:18 UTC and `4a14af5` at 15:36 UTC.

**Track scorer code changed; scores unchanged for a valid organizer bundle.** Evaluation cards
unchanged.

- **`docs/M0-BASELINE.md` specifies M0**, the text-blind baseline every card's score is
  normalized against: the procedure end to end and the per-card seed, with a worked example on
  `t2-EXAMPLE-ust-curve-1m`. The generator source and the per-card scale values stay sealed. The
  README's "Firewall: what is sealed" now names `reference/ref_scale.json` as answer-equivalent.
  Scoring unaffected. (Answers part of issue #3.)
- **How an upload is made:** an upload is the zip written by `qfbench2 submission pack`,
  uploaded on the track's CodaBench page, not an image reference. New `SUBMISSION_CLI.md` section
  "How an upload is made" and README checklist step 8. Scoring unaffected.
- **Scale-commitment check on the official scoring path.** `score_roster` now reads every card's
  `reference/ref_scale.json` once, before any participant gate, checks those bytes against the
  evaluation plan's `ref_scale_commitment`, and scores from the verified bytes. A missing,
  linked, malformed or mismatched scale file, a set of reference directories that differs from
  the plan's roster, or a plan without an expanded `ref_scale` normalization aborts the run as
  an organizer fault. For a valid organizer bundle nothing changes: the same bytes are parsed by
  the same rules and the scoring arithmetic is untouched. This was checked by re-scoring
  synthetic evaluations with the scorer before and after the change (identical results), and the
  regression suite's pinned composites are unchanged; that is a check, not a proof for every
  input. Package version stays `3.1.0`.
- **Opt-in candidate forecast-resolution API** (`qfbench2_track_forecasting.resolution`,
  `docs/FORECAST-RESOLUTION-CANDIDATE.md`), with opt-in precise-cutoff and strict-coverage
  options in `cutoff.py` that only this module uses. Nothing on the live scoring path imports
  it, and every result it returns is non-rankable. No scoring change.
- **Toolkit pin `v2.4.4`** in CI, in the README install commands and in the tag-pinned hub guide
  links of `README.md` and `SUBMISSION_CLI.md`; the `Dockerfile` was missed and fixed on
  2026-09-23. `v2.4.4` adds organizer-side contracts, including
  `qfbench2_common.contracts.forecast_protocol`, which the candidate API above needs. The
  toolkit's `starter-packs/CHANGELOG.md` says when an existing `v2.4.3` install has to move.

## 2026-09-18 — public `main` at `46f40a4`

**Scoring formula: unchanged.**

- **Bring-your-own models and adapters are out of scope** (ruling of 2026-09-18, announced on
  issue #5): `api` is the only submission category on this track. Toolkit `v2.4.3` and later
  refuse to pack a `byo-large` or `byo-small` descriptor, and an upload that still carries one is
  held at the organizer's intake and never run. `README.md`, `SUBMISSION_CLI.md` and
  `docs/NVIDIA-STACK.md` no longer offer a BYO route; `docs/ARTIFACT-POLICY.md` was finished on
  2026-09-23. The README install commands and the tag-pinned hub links moved to `v2.4.3`;
  `ci.yml` and the `Dockerfile` did not, and were fixed on 2026-09-21 and 2026-09-23.

## 2026-09-17 — public `main` at `72ae1f0`

**Scoring: unchanged.** Out-of-cycle correction, announced on issue #4.

- **House route contract.** `MODEL_ENDPOINT` is the route origin with no path; the
  OpenAI-compatible API is served under `/v1` (`POST $MODEL_ENDPOINT/v1/chat/completions`); every
  request needs `Authorization: Bearer $MODEL_TOKEN`. The container-environment table in
  `SUBMISSION_CLI.md` and the House row of `docs/NVIDIA-STACK.md` now say so and link the hub
  guide's "Calling the House route". The README table was missed and fixed on 2026-09-23.

## 2026-09-16 — toolkit `v2.4.2` release, public `main` at `53a414c`

**Track scorer code: unchanged.** These changes updated toolkit install pins, the reference
image, the reference forecast producer, documentation, the four monthly practice specs and
synthetic regression tests. They did not update the deployed scorer. The local toolkit
correction inherited by the pin is noted below. The same release also published the Development
schedule, resource and submission-limit sections of `README.md` and `SUBMISSION_CLI.md`, and
stated a House input allowance of 1,000,000 input tokens per unit there (withdrawn on
2026-09-22, see above).

- **Toolkit installation:** align the reference Docker image, README and CI at `v2.4.2`,
  including the current submission-packaging command and corrected model-free simulation
  fixture. The image previously installed `v2.3.1`, which refuses an empty `models` array even
  when the evaluation verifier accepts it. (Superseded: see the `v2.4.4` entry above — the
  `v2.4.3` bump reached the README and not `ci.yml` or the `Dockerfile`.) The pin also includes
  the local CRPS correction already released in toolkit `v2.4.1`: a component with zero weight
  and exactly zero reference scale contributes zero instead of poisoning the composite with
  `NaN`. See the toolkit starter-pack changelog; this patch adds no scoring implementation.
- **Diagnostic documentation:** remove remaining claims that the scorer reports information
  uplift, text-ablation results, PIT or interval coverage. The scorer reports the composite
  and its components; participants can run separate diagnostics on labeled data they may use.
- **Log-return regression tests:** extend the existing synthetic fixture to 21- and 127-day
  horizons. Check both the CLI and shared baseline against cumulative `log(1 + r)` returns,
  an exact zero anchor, and the complete history window. This changes the synthetic fixture's
  expected result, not scoring code or the daily/monthly regression expectations.
- **Monthly target periods** (answers issue #2, horizon semantics): the four monthly practice
  specs carry explicit `observation_periods`; the horizon integer stays the submission's grid
  key. The reference CLI and reasoning example count monthly steps from the last available panel
  observation, including publication lag (`docs/MONTHLY-HORIZONS.md`). The example card and the
  card template now set `target_frequency = "daily"`, the cadence of target observations rather
  than the forecast lead time. The scorer joins on `(asset, horizon)` and never converts a
  horizon, so scoring is unaffected.

## Published baseline — checked 2026-09-14

The following changes are already in public commit `1c6fdb6`. Scorer version is `3.1.0`.
All 104 shipped `units/*/card.toml` declare `joint = "variogram"`, so the single-cell guard
below does not change their scoring output.

### Reference forecast producer

- **Cumulative log-return cards** (the 16 practice units with `target_type = "log_return"`):
  the reference `forecast` CLI and shared baseline fallback read the card's `target_type`.
  Panel rows are decimal daily simple returns; the walk starts at 0, centres at
  `horizon × mean(log(1 + r))` and spreads by `sd(log(1 + r)) × sqrt(horizon)`, keeping
  cross-asset correlation. Earlier revisions anchored these cards at the last panel row and
  differenced the returns, inflating the spread by about 1.4×. **Regenerate reference outputs
  made with those earlier revisions for return cards.** `forecast_meta.json` records
  `target_type`; the step transform lives in `qfbench2_track_forecasting/targets.py`.
  `level` cards are unaffected. (Answers issue #2.)
- The synthetic `reg-t2-logreturn` fixture checks both producers. It used a 21-day horizon at
  that point; the 127-day horizon was added in the 2026-09-16 release above.

### Scoring code

- The single-cell `ref_scale` relaxation uses the card's joint statistic: the joint term is
  dropped on a one-cell grid only for the variogram, which is zero by construction. A one-cell
  card declaring another joint statistic is refused as an organizer fault instead of silently
  discarding a defined component.

### Rules and documentation

- **House API allowance:** 25 requests per unit, at most 4,000 output tokens per call.
  Participant vendor API keys are not supported. The earlier "1,000,000 input + 100,000
  output tokens per unit" wording is withdrawn. Operational input limits and failed-request
  or retry handling are separate from this kit changelog; this entry makes no change to them.
- **Artifact policy** (`docs/ARTIFACT-POLICY.md`, revision 2026-09-10.1): fitted non-neural
  models, calibration parameters and static retrieval assets may ship under the information
  cutoff, provenance and disclosure rules stated there; additional pretrained neural
  checkpoints need separate approval. No change to resource limits, the descriptor schema or
  scoring formulas. (Answers issue #5.)
- **Baselines and ablation:** the five files in `baselines/` are Gaussian-random-walk interface
  scaffolds, not implementations of the models they are named after. There is no separate
  ablated-forecast slot. Text ablation is an experiment you run and report yourself.
  (Answers issue #3.)
- **Reasoning baseline:** `baselines/reasoning_agent.py` reaches the model through the
  authenticated House proxy (`MODEL_ENDPOINT`, `MODEL_NAME`, `MODEL_TOKEN`, `http_proxy`),
  one request per call, no retries, redirects or direct fallback; missing configuration yields
  the labelled statistical fallback (`reasoning_applied: false`).
