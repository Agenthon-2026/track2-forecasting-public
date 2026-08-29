# Third-Party Notices

This project incorporates or builds on the components below. **Each retains its own license**, and
that license governs that component — it is not superseded by this repository's `LICENSE` (MIT).
The organizers' own work is MIT; third-party material is not licensed by the organizers at all.
See [`DATA-LICENSE.md`](DATA-LICENSE.md) for the rights basis by category, and
[`data/PROVENANCE.md`](data/PROVENANCE.md) for the per-file measured record of where each document
came from.

**Where no grant to the organizers is evidenced, this file says so rather than naming a licence.**
"Issuer's terms govern" is not a grant and not a denial — it means the terms have not been
established from any evidence in this repository.

## Software

- **ABIDES** (organizer-maintained fork) — **BSD-3-Clause**. Used by Track 3. The original ABIDES
  code remains under BSD-3-Clause and may be used commercially from upstream; **only the organizers'
  additions** (scenarios, regression harness, stylized-fact checker, throughput timer) are licensed
  under this repository's `LICENSE` (MIT).
- **Python dependencies** of `qfbench2-common` (NumPy, SciPy, jsonschema, pandas, PyArrow,
  transformers, PyTorch, and others) — each under its own license (BSD / Apache-2.0 / MIT / PSF).
  These are *installed*, not redistributed in this repository.

## U.S. Government sources — public domain (17 U.S.C. §105)

Works prepared by officers or employees of a U.S. federal agency in the course of their official
duties carry no copyright. No permission is required and no attribution is obligatory.

- **U.S. Federal Reserve Board of Governors** (federalreserve.gov) — FOMC statements and minutes,
  Beige Book, and speeches and testimony by Board officials (Bernanke, Greenspan, Yellen, Powell,
  Clarida, Fischer, Bowman, Brainard, Cook, Kugler, Kroszner, Mishkin, Warsh, Waller). This includes
  copies **mirrored on bis.org**: the speaker's employer determines status, not the host site. BIS
  is a mirror and compiler here, not the author.
- **U.S. Bureau of Labor Statistics**, U.S. Department of Labor (bls.gov) — Consumer Price Index and
  Employment Situation news releases, and the CPI/payrolls/unemployment series used in the monthly
  macro panels.
- **U.S. Bureau of Economic Analysis** — PCE price index series used in the monthly macro panels.
- **U.S. Commodity Futures Trading Commission** (cftc.gov) — Commitments of Traders reports. The
  tabular extracts shipped here are **organizer-formatted renderings** of that public-domain data,
  not verbatim CFTC documents; the formatting layer is MIT.
- **U.S. Treasury** and **Federal Reserve H.15 Selected Interest Rates** — constant-maturity
  Treasury par yields underlying the `rates_daily` panels, retrieved via FRED.
- **Federal Reserve H.10 Foreign Exchange Rates** — G10 exchange rates underlying the
  `g10_fx_daily` panels, retrieved via FRED.
- **FRED / ALFRED** (Federal Reserve Bank of St. Louis) — retrieval mechanism for the numeric
  panels above. The underlying series are the issuing agencies' public-domain data.
- **SEC EDGAR** (incl. EDGAR-CORPUS / EDGAR-CRAWLER) — the SEC's filing and dissemination system.
  **The system is a U.S. Government work; the documents filed through it are not.** See the
  corporate filings entry below.

The organizers' *curation, selection, labels, questions and arrangement* built from these sources
are original organizer work under this repository's `LICENSE` (MIT).

## Regional Federal Reserve Banks — status unresolved

- **Federal Reserve Bank of New York** and **Federal Reserve Bank of Kansas City** — speeches by
  Bank officials (Dudley, Hoenig, Potter, Williams), obtained via BIS. The twelve regional Reserve
  Banks are **federally chartered corporations, not federal agencies**, and their employees are not
  federal employees, so 17 U.S.C. §105 does not clearly reach their works the way it reaches the
  Board of Governors'. **The organizers make no public-domain claim over this material** pending a
  rights determination.

## Non-U.S. central banks — the issuing institution's terms govern

None of the material below is a U.S. Government work, and **no grant to the organizers is evidenced
anywhere in this repository.** It is neither MIT nor CC-BY-4.0. Most copies were obtained from the
BIS *Central bankers' speeches* archive, which is a host and compiler — **BIS authored none of these
documents**, and a thin typesetting or compilation layer may sit over the underlying text.

- **Bank for International Settlements** (bis.org) — *Central bankers' speeches* archive; the source
  from which most speeches below were obtained. BIS's own compilation and typesetting rights are
  reserved to BIS.
- **European Central Bank** (ecb.europa.eu) — speeches and hearings by ECB officials (Draghi,
  Trichet, Lagarde, de Guindos, Praet, Schnabel, Elderson, Cœuré, Constâncio, Lane, Mersch, Bini
  Smaghi, Hernández de Cos, Buch, Papademos), including material derived from the ECB's published
  speech corpus. The ECB applies its own reuse terms. **Two of these files print those terms on the
  page** — `draghi_whatever_it_takes_2012.txt` (line 42) and `bis_schnabel_2020-02-27.txt`
  (line 563) both carry the ECB's standard footer, *"Reproduction is permitted provided that the
  source is acknowledged."* We reproduce them and acknowledge the ECB. The sentence was searched for
  literally over every text file in the tree and appears in **those two and no others**.
- **Bank of Japan** (boj.or.jp) — policy statements and speeches (Kuroda, Ueda, Wakatabe,
  Shirakawa, Adachi, Nakaso, Noguchi, Masai, Shirai, Sato, Iwata).
- **Bank of England** (bankofengland.co.uk) — Monetary Policy Committee statements and speeches
  (Carney, Paul Fisher, Cunliffe, Gieve, Shafik, Cleland). *Note: Paul Fisher of the Bank of England
  is a different person from Richard Fisher of the Dallas Fed, and Stanley Fischer of the Federal
  Reserve Board is a third.*
- **Reserve Bank of Australia** (rba.gov.au) — speeches by Stevens and Lowe.
- **People's Bank of China** — speeches and articles by Hu Xiaolian and Yi Gang, reproduced in the
  BIS archive. These files carry verbatim bis.org PDF URLs in their own first line.
- **Bank of Canada** (bankofcanada.ca) — speeches by Poloz and Wilkins. Canadian **Crown copyright**
  and the Bank's own terms apply.
- **Swiss National Bank** (snb.ch) — three speeches by Thomas Jordan. **One of the three,
  `bis_jordan_2021-04-30.txt`, carries an express "© Swiss National Bank" notice on its face**
  (lines 16 and 154), which rules out any MIT or CC-BY-4.0 label for it. The other two,
  `bis_jordan_2014-11-23.txt` and `bis_jordan_2014-12-01.txt`, carry **no copyright notice at all**;
  the SNB's own terms still govern them, but no notice should be attributed to them.
- **Reserve Bank of India** (rbi.org.in) — address by Deputy Governor Michael Debabrata Patra.
- **Bank Indonesia** (bi.go.id) — welcoming remarks by Governor Agus D W Martowardojo.

### Embedded fourth-party rights

Several Bank of Japan speech files (copies of `bis_wakatabe_2020-02-05.txt` and
`bis_kuroda_2018-05-10.txt`) reproduce chart data attributed to **IHS Markit**, carrying
"© and database right IHS Markit Ltd. All rights reserved." **A permission from the Bank of Japan
would not clear these**: the chart data is a separate commercial right nested inside the document.

## Corporate filings — private copyright, all rights reserved

Exhibits to SEC Form 8-K filings retrieved via EDGAR. **These are private corporate works, not U.S.
Government works.** Filing a document with the SEC does not transfer copyright or place it in the
public domain. The issuer authored and owns each document; the SEC only hosts it.

- **Apple Inc.** — 8-K exhibit; carries "© 2020 Apple Inc. All rights reserved." on its face.
- **SVB Financial Group** — 8-K exhibits; carry "© 2023 SVB Financial Group. All rights reserved."
- **Pfizer Inc.** — 8-K exhibit (Q3 2020 results press release).
- **Moderna, Inc.** — 8-K exhibit (Q3 2020 financial results press release).

## Factor libraries — providers' terms of use

The `factors_daily` panels contain **raw published factor returns redistributed as-is**, not
organizer-derived series. Neither provider grants sublicensing or commercial reuse.

- **Kenneth R. French Data Library** (Dartmouth / Tuck) — daily `Mkt-RF`, `SMB`, `HML`, `Mom`.
- **AQR Capital Management** public factor libraries — daily `BAB USA` (Betting Against Beta) and
  `QMJ USA` (Quality Minus Junk).

## Source not established

- **`em_transfer_early` panels** (CNY, INR, BRL) — the unit cards declare only
  `official (FRED/H.10)` and record **no series identifiers anywhere in this repository**, and
  `data/PROVENANCE.md` cannot supply them either. The underlying source is therefore **unverified**.
  It is not labelled public domain on the strength of the card's unsupported claim.
- **`units/t2-EXAMPLE-ust-curve-1m/rates_daily.parquet`** — the manifest labels this file
  `synthetic`, while the same unit's `panel_description.md` and `card.toml` document a real FRED
  H.15 download. **The repository contradicts itself**; one of the two records is wrong and the
  question is unresolved.

## Other datasets referenced by the Agenthon 2026 program

Listed for completeness across the competition. **These are not present in Track 2 data** and no
Track 2 file depends on them.

- **QF-Bench** (Track 1 practice pool) — **CC BY-NC 4.0**, redistributed under those terms with
  attribution.
- **JKP Global Factor Data** (jkpfactors.com) — per the providers' terms (academic use).
- **Global Macro Database** (globalmacrodata.com) — per the providers' terms.
- **Open Source Bond Asset Pricing / OSBAP** (openbondassetpricing.com; Dickerson, Mueller &
  Robotti; Dickerson, Nozawa & Robotti) — per the site's terms; **pin a specific release**.
  Only openly-posted factor / ML-panel files are used; **WRDS-gated panels are not redistributed**.

## Vendor data — referenced, NOT redistributed

- **Databento** (Track 3 limit-order-book data) and **Bloomberg** — commercial vendor data under
  their respective agreements. **Not committed** to these repositories; referenced by checksum and
  access instructions only. Any derived statistics are used strictly per the vendor's terms.

---

If you believe a component is mis-attributed or a license has changed, contact the Agenthon 2026
organizers before redistributing.
