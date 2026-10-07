# Provenance — Track 2 text corpus and numeric panels

Track 2 ships **999 text files (34.41 MB)** and **116 Parquet panels (13.22 MB)** inside the
repository. This file says where they came from.

**The per-file record lives in each unit's `manifest.json`**, in the `source` and `license` fields.
That is the authoritative record: it is per-file, it is machine-checked in CI, and it is what a tool
should read. This document is the human-readable summary of the same information — it groups the
files so you can see the shape of the corpus without reading 1,526 manifest entries. **Where this
summary and a manifest entry disagree, the manifest entry is the one to trust**, and the
disagreement is a bug in this file worth reporting.

Two things are worth knowing before anything else:

1. **The repository's `LICENSE` (MIT) is our licence for our own work.** It does not govern the
   third-party documents in this corpus, and we do not offer it over them. About 99% of the corpus
   was written by someone other than the organizers.
2. **Most of the corpus is U.S. Government work and is in the public domain** — 605 of the 999
   files (27.77 MB). You may do essentially anything with those, including commercially. For 379 of
   the remaining 394 files — speeches and statements by non-US central banks, three documents of
   two non-US finance ministries, and a few corporate documents — **the issuing institution's own
   terms govern**, and we assert no redistribution grant of our own. They are here as frozen
   evidence for an offline benchmark. See
   [What we do not know](#what-we-do-not-know).

---

## Why the corpus ships with the repository at all

Track 2 units run **with no network access**. Local smoke runs use `--network=none`, and in the
graded environment the only egress is model-API calls through the organizer's audited proxy — no web
fetch, no retrieval, no data downloads at inference time. An agent cannot go and get a speech while
it is being scored.

That is a scoring-integrity requirement, not a convenience: the corpus is frozen and cut at each
card's as-of date so that every agent sees exactly the same evidence, and so that no document dated
after the as-of date can leak in. A corpus fetched at evaluation time would satisfy neither
condition.

The consequence is that the text is **redistributed inside the repository**, which is why the
position below is stated explicitly rather than left to a link.

---

## What is here

Counts are file **instances** on disk. Units each carry their own copy of the documents they use, so
the same document often appears in several units: the 999 instances are **683 distinct documents**.
Sizes are the bytes on disk.

### U.S. Government works — public domain (605 files, 27.77 MB)

| Group | Files | Distinct | Bytes | What it is |
|---|---:|---:|---:|---|
| Federal Reserve Board | 373 | 219 | 16,335,625 | FOMC statements, minutes and Summaries of Economic Projections, Beige Book, Bernanke/Powell testimony, speeches and press-conference transcripts, Board press releases (one of them, of 25 February 2009, joint with the FDIC, OCC and OTS) |
| Fed Board officials via BIS | 133 | 94 | 2,739,269 | Speeches by Board of Governors officials, copy obtained from BIS |
| Bureau of Labor Statistics | 83 | 60 | 9,879,581 | CPI and Employment Situation news releases |
| Other U.S. Government | 10 | 8 | 141,910 | U.S. Treasury, White House, State Department and USTR statements, among them the joint statement of the Treasury, FDIC, OCC, OTS and Federal Reserve of 23 February 2009 |
| CFTC Commitments of Traders | 6 | 5 | 25,521 | Weekly positioning, as an organizer-formatted extract |

### Non-US central banks — issuer's terms govern (368 files, 5.90 MB)

| Group | Files | Distinct | Bytes | Principal speakers, and other documents |
|---|---:|---:|---:|---|
| European Central Bank | 220 | 158 | 3,551,822 | Draghi, Trichet, Lagarde, Guindos, Praet, Schnabel, Elderson, Cœuré, Mersch, Lautenschläger, Panetta; plus 12 monetary policy decisions (13 copies), 4 press-conference statements and 1 statement after an ad hoc Governing Council meeting |
| Bank of Japan | 67 | 53 | 1,360,534 | Kuroda, Ueda, Wakatabe, Shirakawa, Adachi, Nakaso, Uchida, Takata; plus 18 policy statements (20 copies) |
| Bank of England | 18 | 14 | 500,937 | Carney, Paul Fisher, Cunliffe; plus 6 MPC statements |
| Reserve Bank of Australia | 16 | 13 | 249,425 | Stevens, Lowe; plus 5 monetary policy decisions |
| Bank of Canada | 10 | 10 | 99,441 | Poloz, Wilkins; plus 4 interest-rate announcements |
| Swiss National Bank | 10 | 10 | 95,393 | Jordan; plus 1 press release (15 January 2015) and 6 monetary policy assessments |
| People's Bank of China | 9 | 6 | 95,281 | Hu Xiaolian, Yi Gang; plus 2 policy announcements |
| Norges Bank | 4 | 4 | 8,813 | 4 policy-rate decisions |
| Sveriges Riksbank | 4 | 4 | 22,009 | 4 repo-rate decisions |
| Reserve Bank of India | 3 | 2 | 174,016 | Patra; plus 1 monetary policy statement (2 copies) |
| Danmarks Nationalbank | 2 | 2 | 3,131 | 2 interest-rate decisions |
| Reserve Bank of New Zealand | 2 | 2 | 13,046 | 2 Official Cash Rate decisions |
| Banco Central do Brasil | 2 | 1 | 2,688 | 1 Copom statement (2 copies) |
| Bank Indonesia | 1 | 1 | 13,870 | Martowardojo |

**Eight of these 368 files, six documents, carry an explicit permission on the page**, in the
ECB's standard press footer: *"Reproduction is permitted provided that the source is
acknowledged."* They are `units/t2-F2-whatever-it-takes-2012/text/draghi_whatever_it_takes_2012.txt`
(line 42), `units/t2-F3-dollar-squeeze-2020/text/bis_schnabel_2020-02-27.txt` (line 563), and four
speeches added on 2026-09-28: `bis_guindos_2019-11-06.txt` (three copies, line 87),
`bis_lane_2020-02-17.txt` (line 256), `bis_lagarde_2020-09-10.txt` (line 146) and
`bis_panetta_2022-03-30.txt` (line 169). We reproduce them and acknowledge the ECB as the source,
and their manifest entries record that (`LicenseRef-ECB-Reproduction-Permitted`). The sentence was
searched for literally over the bytes of every text file in the tree; **it appears in those eight
files and nowhere else**.

### Other (26 files)

| Group | Files | Distinct | Bytes | What it is |
|---|---:|---:|---:|---|
| Corporate SEC 8-K exhibits | 8 | 6 | 469,193 | Pfizer, Moderna, SVB Financial Group, Apple, Lehman Brothers earnings/announcement exhibits |
| Non-US finance ministries | 3 | 3 | 89,375 | HM Treasury, *The Growth Plan 2022* (Open Government Licence v3.0); Japan Ministry of Finance FX intervention report and a joint MoF/FSA/Bank of Japan statement |
| Regional Federal Reserve Banks | 8 | 5 | 207,061 | Dudley, Hoenig, Potter, Williams (New York, Kansas City) |
| Organizer-written text | 7 | 3 | 2,969 | 1 exemplar stub in the example unit, 6 synthetic regression fixtures |

### Numeric panels (116 Parquet files, 13.22 MB)

| Panel | Files | Contents | Basis |
|---|---:|---|---|
| `rates_daily` | 51 | UST 2Y/5Y/7Y/10Y/20Y/30Y constant-maturity par yields | Federal Reserve H.15 via FRED — public domain |
| `g10_fx_daily` | 40 | 10 G10 currencies vs USD | Federal Reserve H.10 via FRED — public domain |
| `factors_daily` | 16 | MKT, SMB, HML, MOM, BAB, QMJ | **Kenneth R. French Data Library and AQR — see below** |
| `em_transfer_early` | 5 | CNY, INR, BRL | **Source not established — see below** |
| `macro_monthly` | 4 | CPI, PCE, NFP, unemployment rate | BLS and BEA via FRED, as the ALFRED vintage published on each card's as-of date (index base as then published) — public domain |

All five panel types carry **raw published values redistributed as-is** — yields in percent, quoted
FX rates, raw CPI index levels, raw daily factor returns. They are not derived series we own. The
organizers' contribution is the container only: renaming to canonical asset IDs, a business-day
calendar filter, gap-fill, truncation at the as-of date, and reprojection to long format. The
repository states this itself: *"No derived features (no spreads, no rolling statistics) are
pre-computed."* Because the numbers are raw, **the upstream terms still govern them** — which is why
`factors_daily` is a real question and not a formality.

---

## Where each group came from

### U.S. Government works

**Groups:** Federal Reserve Board, Bureau of Labor Statistics, CFTC, Fed Board officials whose
speeches we obtained via BIS, and the U.S. Treasury, White House, State Department and USTR
documents added on 2026-09-28 as key-event documents (see `data/LANDMARKS.md`).

Works prepared by officers and employees of a U.S. federal agency in the course of their official
duties carry no copyright under **17 U.S.C. §105**. No permission is needed, no attribution is owed,
and commercial reuse is fine. Attribution is still good scholarly practice.

Two points of precision:

- **The host is not the author.** 133 of these files sit behind a `bis_` filename because BIS
  reproduces central-bank speeches. BIS did not write them. Bernanke, Powell, Yellen, Waller,
  Bowman, Fischer and the other Board officials in this group wrote them in their official capacity,
  and that is what puts them in the public domain. The BIS copy is a typeset reproduction, so a thin
  typesetting layer may sit over public-domain text; the underlying speech is unambiguously PD.
- **The CFTC files are a derived extract, not a CFTC document.** All six share an organizer-composed
  header and a fixed-width table we generated. The underlying positioning data is public domain; the
  presentation is ours. Do not cite them as verbatim CFTC releases.

### Non-US central bank speeches

**Institutions:** the European Central Bank, the Bank of Japan, the Bank of England, the Reserve
Bank of Australia, the People's Bank of China, the Bank of Canada, the Swiss National Bank, the
Reserve Bank of India, Bank Indonesia, and, for monetary policy decisions only, Norges Bank,
Sveriges Riksbank, Danmarks Nationalbank, the Reserve Bank of New Zealand and the Banco Central do
Brasil. Copies were obtained from the issuing institutions and from the BIS *Central bankers'
speeches* collection.

Plainly: these 368 files are here **for non-commercial academic research**, as frozen evidence for an
offline benchmark. Apart from the ECB files noted above and the SNB press release noted below,
whose issuers state reuse terms, **we do not assert a redistribution grant over them** and the MIT
`LICENSE` does not convey one. Any use beyond reading them inside this benchmark — redistribution,
mirroring, commercial use, inclusion in another published dataset — is between you and the issuing
institution.

All fourteen institutions are named in `THIRD-PARTY-NOTICES.md`, and that file and this one are kept
consistent with each other.

Three specific facts inside this set, each read off the documents themselves:

- **One Swiss National Bank file carries an SNB copyright notice on its face.**
  `units/t2-F1-chf-highly-valued-2021/text/bis_jordan_2021-04-30.txt` carries `© Swiss National Bank`
  at lines 16 and 154, alongside a release embargo line. **The other two SNB speeches do not** —
  read end to end, `bis_jordan_2014-11-23.txt` and `bis_jordan_2014-12-01.txt` contain no copyright
  notice of any kind, and their manifest entries say so. Neither does the SNB press release of
  15 January 2015, `units/t2-F1-chf-highly-valued-2021/text/snb_floor_discontinued_20150115.txt`: it
  shows the SNB Communications contact lines and no copyright or permission notice. Its manifest
  entry records the SNB's terms as governing (`LicenseRef-Source-Terms`). **Those terms are on the
  SNB's copyright page, not on the document:** <https://www.snb.ch/en/srv/disclaimer_copyright>
  allows the information and data the SNB provides on its website to be saved, translated (with
  reference to the source), transmitted or used in other ways "for non-commercial purposes,
  compatible with the purpose of such information or data". The benchmark uses the release on that
  basis and names the SNB as its source.
- **Six Bank of Japan files carry a fourth-party commercial right.** Five copies of
  `bis_wakatabe_2020-02-05.txt` and one of `bis_kuroda_2018-05-10.txt` embed IHS Markit chart data
  marked with IHS Markit's copyright and database right. **Even permission from the Bank of Japan
  would not clear these files**, because the IHS Markit layer is a separate right nested inside the
  document.
- **The People's Bank of China files are the one group with recorded retrieval provenance.** Six of
  the seven carry a live `bis.org` PDF URL in their own first line, e.g.
  `# source: BIS central bankers' speeches (https://www.bis.org/review/r100729e.pdf)`. Those URLs are
  evidence, not reconstruction. `bis_gang_2018-06-14.txt` has no such header.

### Monetary policy decisions, key events and other speeches added on 2026-09-28

311 files, 237 distinct documents, were added to the 103 practice units so that each card's corpus
holds the evidence its question turns on, alongside material an agent should learn to set aside.
Each unit's `corpus_index.json`, `card.toml` `[text]`, `forecast_card.md` and `manifest.json` were
updated with them.

- **Decisions of the card's target central bank** (65 files, 62 distinct): for each card whose
  forecast target is tied to a central bank other than the Federal Reserve, the bank's own
  monetary policy decision statement in force at the as-of date, and on some cards the one before
  it. Taken from the issuing bank's website; the Reserve Bank of Australia and Reserve Bank of New
  Zealand statements from Internet Archive captures of the official pages. New `doc_type`:
  `central_bank_decision`.
- **Key-event documents** (41 files, 36 distinct): the official document of the event a card is
  built around, when the card did not already carry it. They are indexed as landmarks; each is
  listed with its official source in `data/LANDMARKS.md`.
- **Speeches on unrelated topics** (205 files) from the BIS *Central bankers' speeches* archive, by
  Federal Reserve Board, ECB Executive Board or Supervisory Board, and Bank of Japan officials, on
  subjects such as payments, supervision, climate, statistics and financial literacy. Each speaker's
  employer was read from the speech's own byline, not from the archive's institution label, which
  names the host institution of the event for some speeches: speeches by regional Reserve Bank,
  national central bank and other speakers were excluded.
- **Dates.** Each file's `corpus_index.json` timestamp is its publication date, on or before the
  card's as-of date. Press-conference transcripts are dated by the day the final transcript was
  posted.

### Non-US finance ministries

**Files:** 3 instances, 3 distinct. HM Treasury's *The Growth Plan 2022* carries "© Crown copyright
2022" and is published under the UK Open Government Licence v3.0; its manifest `source` carries the
attribution statement that licence asks for. The Japan Ministry of Finance's monthly report of
foreign exchange intervention (31 May 2024) and the joint Ministry of Finance / Financial Services
Agency / Bank of Japan statement of 10 June 2022 are governed by the Ministry's terms. The joint
statement is in Japanese, as published; the official link is dead, and the copy is from the National
Diet Library's WARP archive of mof.go.jp.

### Corporate SEC 8-K exhibits

**Files:** 8 instances, 6 distinct — Pfizer, Moderna, SVB Financial Group (×2), Apple, Lehman
Brothers.

These are **not** U.S. Government works and are **not** in the public domain. EDGAR is a government
*dissemination system*; filing a document with the SEC does not transfer copyright. The owners are
the filing companies, and two of the six say so on their face: `© 2020 Apple Inc. All rights
reserved.` and `© 2023 SVB Financial Group. All rights reserved.` Same position as the non-US
speeches: present as frozen research evidence, upstream rights unaffected.

### Regional Federal Reserve Bank speeches — unresolved, deliberately

**Files:** 8 instances, 5 distinct — Dudley and Potter (New York), Hoenig (Kansas City), Williams
(New York).

The twelve regional Reserve Banks are **federally chartered corporations, not federal agencies**, and
their employees are not federal employees, so §105 does not reach their works the way it reaches the
Board of Governors'. We have deliberately not folded these into the public-domain group, because
doing so would manufacture a claim we cannot support. **Unresolved; needs an owner decision.**

### Organizer-authored material

Our own work is covered by the repository's `LICENSE` (MIT):

- the **7 organizer-written text files** — 1 exemplar stub in the example unit and 6 synthetic
  regression fixtures;
- the **104 `manifest.json`**, **104 `card.toml`**, **104 `forecast_card.md`**, **103
  `forecast_spec.json`** and **104 `text/corpus_index.json`** files, plus the example unit's
  `panel_description.md` and `run_example.sh`;
- the **selection, arrangement, cutting and formatting** of every panel and corpus, as distinct from
  the underlying data.

**The example unit's two "exemplar stubs" are not the same kind of thing, and only one of them is
ours.** Measured over the bytes:

- `units/t2-EXAMPLE-ust-curve-1m/text/fomc_statement_2024_06_12.txt` is **real Federal Reserve
  text**, abridged. All 8 of its sentences occur verbatim in the retrieved FOMC releases already in
  this tree, and the same 2024-06-12 statement sits in full at
  `units/t2-F3-funding-carry-fx-2024/text/fomc_statement_20240612.txt`. The stub only drops sentences and
  rewraps. It is a U.S. Government work in the public domain, not organizer-authored, and its
  manifest entry now records that.
- `units/t2-EXAMPLE-ust-curve-1m/text/fomc_minutes_excerpt_2024_05_22.txt` **is** ours: none of its 6
  sentences occurs in any retrieved document in this tree, and its longest verbatim run shared with
  the real 2024-05-01 minutes is 11 words of stock phrasing. It is an organizer-written paraphrase in
  the style of FOMC minutes. Note that the file's own trailer calls itself a "representative public
  excerpt", which overstates it — treat the manifest entry, not the trailer, as the record.

## How the text was cleaned

Most documents were saved from web pages, and the saved text carried the site around the document:
menus, search boxes, "Return to top" links, footers, and lists of related news filled in on the
day the page was fetched. Those lists can name events after the document's own date. The unit
texts have therefore been passed through **one committed module, `scripts/declutter_corpus.py`**
(standard library only). Its docstring states every rule; nothing was removed by hand.

- **What it removes:** site navigation before the document body and after it, page footers, inline
  "Return to top" / "Back to top" separators, the ECB "SEE ALSO" related-content block, the
  Bank of England related-news blocks, and a bare "Last Modified Date:" page label (with its date)
  left at the very end of a BLS release. Line endings become LF.
- **What it keeps:** the document itself, including its front matter. A Beige Book keeps its title,
  release date and "This report was prepared at the Federal Reserve Bank of ... based on
  information collected on or before ..." preamble; a BLS release keeps its release header and
  dateline; the FOMC minutes of 2007-2011 keep the date line the page prints just above its
  footer (for example "February 18, 2009"). The 2024 Beige Books are 13 web pages saved into one
  file; the module cleans each page on its own, so every District report is kept.
- **Guards:** a file whose prose would fall below half of what it was, or a multi-page file with a
  page left almost empty, is refused and left untouched. None was refused.
- **Reissued BLS releases.** Four BLS files carried a note that the release was reissued *after*
  its publication date: `cpi_2011-07-15.txt` (reissued 18 August 2011, in 2 units) and
  `empsit_2020-02-07.txt` and `empsit_2020-03-06.txt` (reissued 23 September 2020, in
  `t2-F4-covid-nfp-2020`). The module removes such a note by an explicit rule, and every removal
  is listed in [`corpus-cleaning/reissue-notes-removed.tsv`](corpus-cleaning/reissue-notes-removed.tsv)
  (paths relative to `units/`). **The tables in those four files are still the reissued versions.**
  Per the removed notes, the 2011 reissue corrected the April-June 2011 data in Table 7 (the
  chained CPI, C-CPI-U) and did not change the text; the 2020 reissue corrected a limited number of
  series in household-survey tables A-8, A-9, A-13 and A-14 and did not affect the official
  unemployment rate. Notes about a same-day reissue are kept. (The same rule also removes a
  numbered table footnote saying a table was reissued after the release date; no unit text has
  one.)

To check a unit's text, run `python3 scripts/declutter_corpus.py --check units`; it exits 0 when
every file is already clean and writes nothing.

Beige Book timestamps in `text/corpus_index.json` are never earlier than the Beige Book's public
release date (read off the document's own dateline), and every one is on or before its card's as-of
date. Many are the last day of the release month rather than the release day itself; a timestamp
later than the release is conservative for the cutoff gate.

---

## What we do not know

These are gaps, not formalities, and none of them is filled with a guess.

**1. We cannot say where 649 of the 999 text files were retrieved from.**

We can establish the **issuing institution for 999 of 999 files** by reading the documents — that
is what the rights question turns on, and it is solid. A **source URL** is recorded for 344 files:
the 6 PBoC files carrying inline `bis.org` URLs; the 27 copies of the 13 original landmark documents
listed with their URLs in [`LANDMARKS.md`](LANDMARKS.md); and the 311 files added on 2026-09-28 — the
106 decision and key-event files carry the official URL in their own first line (the key events are
also in `LANDMARKS.md`), and the 205 other speeches record their BIS page in their manifest
`source`. The 106 decision and key-event files were fetched between 26 and 28 September 2026; the
205 other speeches were taken from the organizers' copy of the BIS speech archive, held since July
2026. The 6 synthetic fixtures have no external source. For the other 649 files we **cannot**
establish the **exact retrieval URL**, and no retrieval date is recorded for them. **No URL or date
has been invented to fill that gap**, and none should be added later without evidence.

**2. The reuse terms for 369 files are not established.**

For 359 of the 368 non-US central bank files, the 2 Japan Ministry of Finance files and the 8
corporate exhibits, we know **who issued them** with certainty and we do **not** know **what the
terms permit**. No evidence exists anywhere in this repository that any grant was ever obtained from
those institutions or companies. The exceptions are the eight ECB files described above, whose
permission is printed on the document, the SNB press release, whose terms the SNB publishes on its
copyright page, and the HM Treasury document, published under the Open Government Licence v3.0.

**3. The rights basis for 8 regional Federal Reserve Bank files is genuinely unsettled.**

See above. Not resolved, not silently rounded to public domain.

**4. Five `em_transfer_early.parquet` files have no recorded source.**

They carry CNY, INR and BRL series. Unlike every other panel type, **the cards declare no `series`
list** for this panel — a search for `series` under `panels.em_transfer_early` across all 104 cards
returns **0** — so **no FRED series ID for these three currencies is recorded anywhere in the
repository**. The card claims `"official (FRED/H.10)"`. If they are H.10 series they are public
domain like `g10_fx_daily`; the repository does not say so, and the IDs have not been inferred.
**Unverified until whoever built the panel confirms them.**

**5. One panel's own labels contradict each other.**

`units/t2-EXAMPLE-ust-curve-1m/rates_daily.parquet` was labelled **synthetic** in its `manifest.json`
while the same unit's `panel_description.md` and `card.toml` document a **real FRED download**
("Raw series downloaded from FRED: DGS2, DGS5, DGS10, DGS30"), and its values are consistent with
actual mid-2024 Treasury levels. One of the two statements is false and we have not determined which.
The manifest entry now records the contradiction rather than picking a side.

**6. `factors_daily` is a live question in the numeric data.**

The 16 `factors_daily.parquet` files (2,426,152 bytes) carry Mkt-RF, SMB, HML and Mom from the **Kenneth R.
French Data Library** and BAB and QMJ from **AQR Capital Management** — named explicitly in all 16
cards. Both are private-party libraries distributed under their own terms of use, and **neither
grants sublicensing or commercial reuse**. Naming both providers in `THIRD-PARTY-NOTICES.md` records
the dependency; it does not obtain a grant. **Unresolved.**

**7. The generator code is not in this repository.**

103 manifests cite `scripts/make_public_dev_copy.py`, but **that script is not in this repository**:
the `scripts/` directory here holds only `check_public_sync.sh` and `declutter_corpus.py`. The
"raw, not derived" conclusion for the panels therefore rests on the panel documentation plus the
measured value ranges, **not** on reading the code that built them.

**8. The landmarks pointer now resolves.**

`"see landmarks index"` appears **118** times across 100 unit files (50 `card.toml`, 50
`text/corpus_index.json`). Until the 2026-09-25 revision no landmarks index existed anywhere in the
tree; it is now [`data/LANDMARKS.md`](LANDMARKS.md), which lists all 49 landmark documents with
their official source URLs. (The other two pointer classes were already gone: `"see PROVENANCE.md
chain"` no longer appears anywhere under `units/`, and the `data/PROVENANCE.md` that 340 references
in 212 files under `units/` point to is this file.)

---

## How to report a problem

**If you are a rights holder** — a central bank, an agency, a company, or a data provider — and you
believe material of yours is included here in error, mis-attributed, or redistributed beyond what
your terms allow, please contact us:

> **`qfbench@neurips2026.org`**

Tell us the file path or document title and what you would like done. **We will act on a well-founded
request from a rights holder without requiring a formal notice**, and we would rather correct an entry
than argue about it. If material must be withdrawn, we will withdraw it and reissue the affected
units.

> **⚠ FLAG FOR THE ORGANIZERS — confirm before publishing.** `qfbench@neurips2026.org` is the only
> role address that appears anywhere in this repository, and its **single** occurrence is as an
> `author_email` field in one example card — not as a published, monitored contact channel. Confirm
> that this mailbox exists and is being read before this file goes public; if it is not, replace it
> with a monitored role address. It must not be replaced with any individual's personal address.

**If you are a participant** and you spot an error in this file — a misattributed speaker, a wrong
institution, a group that does not match what you find in the data — please open an issue. The
classification here was derived by reading documents, and reading can be wrong.

---

## How this was established

Everything above was **measured on this tree**, not inferred from filenames.

- **Enumeration.** 999 `.txt` files totalling 36,080,910 bytes and 116 unit Parquet panels
  totalling 13,860,758 bytes, from the working tree of this revision. Five paths contain non-ASCII
  characters (`bis_cœuré_*` ×3,
  `bis_constâncio_*` ×2) and are handled with Unicode NFC normalisation.
- **Classification by content, not filename.** Every speech document had its byline read to identify
  the issuing institution. **This matters: the filename lies for 375 of 999 files.** Every
  `bis_*` file carries a filename implying BIS, and **BIS authored none of them** — behind that
  prefix sit 133 U.S. Fed Board works, 8 regional Reserve Bank works, and 234 foreign works from 9
  institutions. The BIS archive's own institution label is not reliable either: among the speeches
  considered on 2026-09-28 it named the Federal Reserve for speeches by New York Fed, Reserve Bank of India and
  Reserve Bank of New Zealand officials, and the ECB for speeches by national central bank
  governors, because it follows the host of the event. Those speeches were excluded.
- **Traps caught by reading, which filename or keyword matching would have got wrong:**
  - `bis_martowardojo_2016-08-01.txt` — an automated scan called this a U.S. Government work because
    "Federal Reserve Bank of New York" appears in the byline. It is the **co-host of the seminar**.
    The speaker is the **Governor of Bank Indonesia**.
  - `bis_fisher_*` — **Paul Fisher, Bank of England**, not Richard Fisher of the Dallas Fed.
  - `bis_patra_2024-10-21.txt` — delivered **at** the New York Fed; the speaker works for the
    **Reserve Bank of India**.
  - Venue is never the employer: Kuroda and Draghi at Jackson Hole, Shirai at the San Francisco Fed,
    Dudley at the Central Bank of Brazil.
  - The example unit's two "stubs" — one is verbatim Fed text and one is ours. Reading the trailer
    would have got both wrong; only sentence-level comparison against the real releases separates
    them.
- **Path rules verified.** The figures of the 2026-09-25 revision came from an ordered set of
  file-name rules in which every `bis_*` speaker is mapped to the institution read off the byline.
  It classified all 692 paths of that tree, **stopped with an error on any path or speaker it did
  not know**, and reconciled exactly to 31,174,771 bytes; run on the tree before the cleaning pass,
  it reproduced every text-file figure of the first version of this file. The figures of this
  revision come from each file's manifest `license` and `source`, which record the institution read
  off the byline; the rules stop with an error on any entry they cannot place. Run on the
  2026-09-25 tree, they reproduce every group's files, distinct documents and bytes of that
  revision exactly. Distinct documents are counted by file name, as in earlier revisions, with one
  exception: `bis_bowman_2024-06-25.txt` names two different speeches given that day, the remarks
  at Policy Exchange in London (an earlier copy) and the opening remarks at the Midwest Cyber
  Workshop (added on 2026-09-28), and they count as two. `bis_schnabel_2024-02-16.txt` ships in
  two formattings of one speech, an earlier copy and one added on 2026-09-28, and counts once.
- **Detectors proved before use.** Every search was positive-controlled before a clean result was
  accepted. Three census claims were corrected this way: the IHS Markit files number **6, not 4**; an
  over-strict pattern produced a **false negative** on the Apple copyright notice, which a second
  check confirmed is genuinely present; and the SNB copyright notice, first recorded against all
  three `bis_jordan_*` files, is present in **one**.
- **Integrity.** sha256 and length were recomputed for all **1,526** manifest entries against disk:
  **1,526 OK, 0 mismatches.** Apart from the cleaning pass described in
  [How the text was cleaned](#how-the-text-was-cleaned), no file bytes were modified in establishing
  any of this; the other corrections are to manifest metadata and to this document.

*Counts describe this tree as re-measured on 2026-10-01, after the target-central-bank decisions,
key-event documents and other speeches were added; the unit Parquet total was re-measured on
2026-09-27, after the monthly practice panels were rebuilt. Re-measure before publishing if the tree
has changed since.*
