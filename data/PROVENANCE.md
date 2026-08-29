# Provenance — Track 2 text corpus and numeric panels

Track 2 ships **631 text files (26.87 MB)** and **116 Parquet panels (13.22 MB)** inside the
repository. This file says where they came from.

**The per-file record lives in each unit's `manifest.json`**, in the `source` and `license` fields.
That is the authoritative record: it is per-file, it is machine-checked in CI, and it is what a tool
should read. This document is the human-readable summary of the same information — it groups the
files so you can see the shape of the corpus without reading 1,160 manifest entries. **Where this
summary and a manifest entry disagree, the manifest entry is the one to trust**, and the
disagreement is a bug in this file worth reporting.

Two things are worth knowing before anything else:

1. **The repository's `LICENSE` (MIT) is our licence for our own work.** It does not govern the
   third-party documents in this corpus, and we do not offer it over them. About 99% of the corpus
   was written by someone other than the organizers.
2. **A large majority of the corpus is U.S. Government work and is in the public domain** — 437 of
   the 631 files (22.84 MB). You may do essentially anything with those, including commercially.
   For most of the remaining 181 files — speeches and statements by non-US central banks, plus a
   few corporate documents — **the issuing institution's own terms govern**, and we assert no
   redistribution grant of our own. They are here as frozen evidence for an offline benchmark. See
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
the same document often appears in several units: the 631 instances are **412 distinct documents**.
Sizes are the bytes on disk.

### U.S. Government works — public domain (437 files, 22.84 MB)

| Group | Files | Distinct | Bytes | What it is |
|---|---:|---:|---:|---|
| Federal Reserve Board | 328 | 188 | 16,267,687 | FOMC statements and minutes, Beige Book, Bernanke/Powell testimony and speeches |
| Bureau of Labor Statistics | 53 | 41 | 6,557,966 | CPI and Employment Situation news releases |
| Fed Board officials via BIS | 50 | 34 | 1,095,291 | Speeches by Board of Governors officials, copy obtained from BIS |
| CFTC Commitments of Traders | 6 | 5 | 25,521 | Weekly positioning, as an organizer-formatted extract |

### Non-US central banks — issuer's terms govern (174 files, 3.42 MB)

| Group | Files | Distinct | Bytes | Principal speakers |
|---|---:|---:|---:|---|
| European Central Bank | 100 | 74 | 1,692,878 | Draghi, Trichet, Lagarde, Guindos, Praet, Schnabel, Elderson, Cœuré |
| Bank of Japan | 32 | 25 | 913,781 | Kuroda, Ueda, Wakatabe, Shirakawa, Adachi; plus 3 policy statements |
| Bank of England | 13 | 9 | 468,989 | Carney, Paul Fisher, Cunliffe; plus 1 MPC statement |
| Reserve Bank of Australia | 11 | 8 | 229,688 | Stevens, Lowe |
| People's Bank of China | 7 | 4 | 91,642 | Hu Xiaolian, Yi Gang |
| Bank of Canada | 6 | 6 | 86,243 | Poloz, Wilkins |
| Swiss National Bank | 3 | 3 | 62,061 | Jordan |
| Reserve Bank of India | 1 | 1 | 26,104 | Patra |
| Bank Indonesia | 1 | 1 | 13,870 | Martowardojo |

**Two of these 174 carry an explicit permission on the page**, in the ECB's standard press footer:
*"Reproduction is permitted provided that the source is acknowledged."* They are
`units/t2-F2-whatever-it-takes-2012/text/draghi_whatever_it_takes_2012.txt` (line 42) and
`units/t2-F3-dollar-squeeze-2020/text/bis_schnabel_2020-02-27.txt` (line 563). We reproduce them and
acknowledge the ECB as the source, and their manifest entries record that. The sentence was searched
for literally over the bytes of every text file in the tree, with a planted control to prove the
search fires; **it appears in those two files and nowhere else**, and no variant wording of it
appears anywhere.

### Other (20 files)

| Group | Files | Distinct | Bytes | What it is |
|---|---:|---:|---:|---|
| Corporate SEC 8-K exhibits | 7 | 5 | 431,707 | Pfizer, Moderna, SVB Financial Group, Apple earnings/announcement exhibits |
| Regional Federal Reserve Banks | 8 | 5 | 207,061 | Dudley, Hoenig, Potter, Williams (New York, Kansas City) |
| Organizer-written text | 5 | 3 | 2,403 | 1 exemplar stub in the example unit, 4 synthetic regression fixtures |

### Numeric panels (116 Parquet files, 13.22 MB)

| Panel | Files | Contents | Basis |
|---|---:|---|---|
| `rates_daily` | 51 | UST 2Y/5Y/7Y/10Y/20Y/30Y constant-maturity par yields | Federal Reserve H.15 via FRED — public domain |
| `g10_fx_daily` | 40 | 10 G10 currencies vs USD | Federal Reserve H.10 via FRED — public domain |
| `factors_daily` | 16 | MKT, SMB, HML, MOM, BAB, QMJ | **Kenneth R. French Data Library and AQR — see below** |
| `em_transfer_early` | 5 | CNY, INR, BRL | **Source not established — see below** |
| `macro_monthly` | 4 | CPI, PCE, NFP, unemployment rate | BLS and BEA via FRED — public domain |

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

**Groups:** Federal Reserve Board, Bureau of Labor Statistics, CFTC, and Fed Board officials whose
speeches we obtained via BIS.

Works prepared by officers and employees of a U.S. federal agency in the course of their official
duties carry no copyright under **17 U.S.C. §105**. No permission is needed, no attribution is owed,
and commercial reuse is fine. Attribution is still good scholarly practice.

Two points of precision:

- **The host is not the author.** 50 of these files sit behind a `bis_` filename because BIS
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
Reserve Bank of India, and Bank Indonesia. Copies were obtained from the issuing institutions and
from the BIS *Central bankers' speeches* collection.

Plainly: these 174 files are here **for non-commercial academic research**, as frozen evidence for an
offline benchmark. Apart from the two ECB files noted above, **we do not assert a redistribution
grant over them** and the MIT `LICENSE` does not convey one. Any use beyond reading them inside this
benchmark — redistribution, mirroring, commercial use, inclusion in another published dataset — is
between you and the issuing institution.

All nine institutions are named in `THIRD-PARTY-NOTICES.md`, and that file and this one are kept
consistent with each other.

Three specific facts inside this set, each read off the documents themselves:

- **One Swiss National Bank file carries an SNB copyright notice on its face.**
  `units/t2-F1-chf-highly-valued-2021/text/bis_jordan_2021-04-30.txt` carries `© Swiss National Bank`
  at lines 16 and 154, alongside a release embargo line. **The other two SNB files do not** — read
  end to end, `bis_jordan_2014-11-23.txt` and `bis_jordan_2014-12-01.txt` contain no copyright notice
  of any kind, and their manifest entries say so.
- **Six Bank of Japan files carry a fourth-party commercial right.** Five copies of
  `bis_wakatabe_2020-02-05.txt` and one of `bis_kuroda_2018-05-10.txt` embed IHS Markit chart data
  marked with IHS Markit's copyright and database right. **Even permission from the Bank of Japan
  would not clear these files**, because the IHS Markit layer is a separate right nested inside the
  document.
- **The People's Bank of China files are the one group with recorded retrieval provenance.** Six of
  the seven carry a live `bis.org` PDF URL in their own first line, e.g.
  `# source: BIS central bankers' speeches (https://www.bis.org/review/r100729e.pdf)`. Those URLs are
  evidence, not reconstruction. `bis_gang_2018-06-14.txt` has no such header.

### Corporate SEC 8-K exhibits

**Files:** 7 instances, 5 distinct — Pfizer, Moderna, SVB Financial Group (×2), Apple.

These are **not** U.S. Government works and are **not** in the public domain. EDGAR is a government
*dissemination system*; filing a document with the SEC does not transfer copyright. The owners are
the filing companies, and two of the five say so on their face: `© 2020 Apple Inc. All rights
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

- the **5 organizer-written text files** — 1 exemplar stub in the example unit and 4 synthetic
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
  `units/t2-F3-funding-flip-2024/text/fomc_statement_20240612.txt`. The stub only drops sentences and
  rewraps. It is a U.S. Government work in the public domain, not organizer-authored, and its
  manifest entry now records that.
- `units/t2-EXAMPLE-ust-curve-1m/text/fomc_minutes_excerpt_2024_05_22.txt` **is** ours: none of its 6
  sentences occurs in any retrieved document in this tree, and its longest verbatim run shared with
  the real 2024-05-01 minutes is 11 words of stock phrasing. It is an organizer-written paraphrase in
  the style of FOMC minutes. Note that the file's own trailer calls itself a "representative public
  excerpt", which overstates it — treat the manifest entry, not the trailer, as the record.

---

## What we do not know

These are gaps, not formalities, and none of them is filled with a guess.

**1. We cannot say where 621 of the 631 text files were retrieved from.**

We can establish the **issuing institution for 631 of 631 files** by reading the documents — that is
what the rights question turns on, and it is solid. We **cannot** establish the **exact retrieval URL
or retrieval date** for all but 10: the 6 PBoC files carrying inline `bis.org` URLs and the 4
synthetic fixtures, which have no external source. **No URL or date has been invented to fill that
gap**, and none should be added later without evidence.

**2. The reuse terms for 179 files are not established.**

For 172 of the 174 non-US central bank files and the 7 corporate exhibits, we know **who issued
them** with certainty and we do **not** know **what the terms permit**. No evidence exists anywhere in
this repository that any grant was ever obtained from those institutions or companies. The two ECB
files described above are the exception: their permission is printed on the document.

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

103 manifests cite `scripts/make_public_dev_copy.py`, but **no `scripts/` directory exists here**.
The "raw, not derived" conclusion for the panels therefore rests on the panel documentation plus the
measured value ranges, **not** on reading the code that built them.

**8. There is still one dangling pointer class.**

`"see landmarks index"` appears **40** times across 38 unit files, and **no landmarks index exists
anywhere in the tree**. (The other two classes are gone: `"see PROVENANCE.md chain"` no longer appears
anywhere under `units/`, and the `data/PROVENANCE.md` that 237 pointers under `units/` refer to is
this file.)

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

- **Enumeration.** 631 `.txt` files totalling 28,172,892 bytes and 116 unit Parquet panels totalling
  13,861,919 bytes, via a bytes-safe walk. Five paths contain non-ASCII characters (`bis_cœuré_*` ×3,
  `bis_constâncio_*` ×2) and are handled with Unicode NFC normalisation.
- **Classification by content, not filename.** Every speech document had its byline read to identify
  the issuing institution. **This matters: the filename lies for 174 of 631 files.** Every `bis_*`
  file carries a filename implying BIS, and **BIS authored none of them** — behind that prefix sit 50
  U.S. Fed Board works, 8 regional Reserve Bank works, and 116 foreign works from 9 institutions.
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
- **Path rules verified.** 17 mutually exclusive rules were compiled and run against all 631 paths:
  **0 files matched more than one rule, 0 matched none**, and byte totals reconcile exactly to
  28,172,892. A planted `bis_UNKNOWNPERSON_*.txt` control matched nothing — the rules **fail safe**.
- **Detectors proved before use.** Every search was positive-controlled before a clean result was
  accepted. Three census claims were corrected this way: the IHS Markit files number **6, not 4**; an
  over-strict pattern produced a **false negative** on the Apple copyright notice, which a second
  check confirmed is genuinely present; and the SNB copyright notice, first recorded against all
  three `bis_jordan_*` files, is present in **one**.
- **Integrity.** sha256 and length were recomputed for all **1,160** manifest entries against disk:
  **1,160 OK, 0 mismatches.** No file bytes were modified in establishing any of this; the corrections
  described above are to manifest metadata and to this document.

*Counts describe the `release-20260828` staging tree as measured against it directly. Re-measure
before publishing if the tree has changed since.*
