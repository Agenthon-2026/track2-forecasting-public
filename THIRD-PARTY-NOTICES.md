# Third-Party Notices

This project incorporates or builds on the components below. **Each retains its own license**, and
that license governs that component — it is not superseded by this repository's `LICENSE` (MIT).
The organizers' own work is MIT; third-party material is not licensed by the organizers at all.
See [`DATA-LICENSE.md`](DATA-LICENSE.md) for the rights basis by category, and
[`data/PROVENANCE.md`](data/PROVENANCE.md) for the per-file measured record of where each document
came from.

**Where no grant to the organizers is evidenced, this file says so rather than naming a licence.**
"Issuer's terms govern" is not a grant and not a denial — it means the terms have not been
established from any evidence in this repository, unless the entry quotes the issuer's published
terms, as it does for the ECB files that print the ECB's permission, the ECB euro reference rates,
the SNB press release, the HM Treasury document and every source of the short-horizon practice set
(units whose ids end in `-ps1`, and their answer files in `practice-answers/`) below.

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
  Beige Book, Summaries of Economic Projections, press-conference transcripts, press releases, and
  speeches and testimony by Board officials (Bernanke, Greenspan, Yellen, Powell, Clarida, Fischer,
  Bowman, Brainard, Cook, Kugler, Kroszner, Mishkin, Warsh, Waller, Barr, Bies, Duke, Gramlich,
  Jefferson, Quarles, Raskin, Tarullo). This includes
  copies **mirrored on bis.org**: the speaker's employer determines status, not the host site. BIS
  is a mirror and compiler here, not the author. The short-horizon practice set takes its FOMC
  documents and Beige Books from federalreserve.gov directly; it carries no Board speeches.
- **U.S. Bureau of Labor Statistics**, U.S. Department of Labor (bls.gov) — Consumer Price Index and
  Employment Situation news releases, and the CPI/payrolls/unemployment series used in the monthly
  macro panels.
- **U.S. Bureau of Economic Analysis** — PCE price index series used in the monthly macro panels.
- **U.S. Department of the Treasury** (home.treasury.gov), **The White House** (archived at
  trumpwhitehouse.archives.gov and bidenwhitehouse.archives.gov), **U.S. Department of State**
  (2021-2025.state.gov) and **Office of the U.S. Trade Representative** (ustr.gov) — statements,
  briefings, remarks and a quarterly refunding statement added as key-event documents (see
  `data/LANDMARKS.md`); in the short-horizon practice set, the Treasury's quarterly refunding
  statements, a borrowing estimate and a debt-limit letter; and the joint statement of the Treasury, FDIC, OCC, OTS and Federal Reserve
  of 23 February 2009, published on federalreserve.gov.
- **U.S. Commodity Futures Trading Commission** (cftc.gov) — Commitments of Traders reports. The
  tabular extracts shipped here are **organizer-formatted renderings** of that public-domain data,
  not verbatim CFTC documents; the formatting layer is MIT.
- **U.S. Treasury** and **Federal Reserve H.15 Selected Interest Rates** — constant-maturity
  Treasury par yields underlying the `rates_daily` panels, retrieved via FRED, including the
  3-month, 6-month and 1-year yields (`DGS3MO`, `DGS6MO`, `DGS1`) of the short-horizon practice
  set and the values in its UST answer files.
- **Federal Reserve H.10 Foreign Exchange Rates** — G10 exchange rates underlying the
  `g10_fx_daily` panels, retrieved via FRED, including the short-horizon practice set's three G10
  cards and their answer files.
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

None of the material below is a U.S. Government work, and **except for the ECB files that print the
ECB's permission, the ECB euro reference rates, the SNB press release and the short-horizon practice
set's Banco de México and Banco Central do Brasil texts, noted below, no grant to the organizers is
evidenced anywhere in this repository.** It is neither MIT nor CC-BY-4.0. Those are the only ones
whose reuse terms are established: the ECB files print them, the ECB publishes its terms for the
reference rates, the SNB publishes them on its copyright page, Banco de México in its usage policy,
and the Banco Central do Brasil on its open-data portal.
Most copies were obtained from the BIS *Central bankers' speeches* archive, which is a host and
compiler — **BIS authored none of these documents**, and a thin typesetting or compilation layer may
sit over the underlying text.

- **Bank for International Settlements** (bis.org) — *Central bankers' speeches* archive; the source
  from which most speeches below were obtained. BIS's own compilation and typesetting rights are
  reserved to BIS.
- **European Central Bank** (ecb.europa.eu) — monetary policy decisions, press-conference
  statements, one statement after an ad hoc Governing Council meeting, and speeches and hearings by
  ECB officials (Draghi, Trichet, Lagarde, de Guindos, Praet, Schnabel, Elderson, Cœuré, Constâncio,
  Lane, Mersch, Bini Smaghi, Hernández de Cos, Buch, Papademos, Panetta, Lautenschläger,
  Tumpel-Gugerell, González-Páramo, Cipollone, McCaul, Duisenberg), including material derived from
  the ECB's published speech corpus. The ECB applies its own reuse terms. **Six of these documents,
  in eight files, print those terms on the page**: the ECB's standard footer, *"Reproduction is
  permitted provided that the source is acknowledged."* They are
  `draghi_whatever_it_takes_2012.txt`, `bis_schnabel_2020-02-27.txt`, `bis_guindos_2019-11-06.txt`
  (three copies), `bis_lane_2020-02-17.txt`, `bis_lagarde_2020-09-10.txt` and
  `bis_panetta_2022-03-30.txt`; their manifest entries use `LicenseRef-ECB-Reproduction-Permitted`.
  We reproduce them and acknowledge the ECB. The sentence was searched for literally over every text
  file of the original 103 units and the worked example and appears in **those eight files and no
  others**. The short-horizon practice set adds ECB monetary policy decision press releases from
  ecb.europa.eu, each keeping the same printed line, with the same manifest label; their manifests
  state that media-contact details and page navigation were removed. One further speech,
  `bis_elderson_2022-12-01.txt`, ends with "Copyright 2022, European Central Bank" and no
  permission; the ECB's terms govern it.
- **European Central Bank, euro foreign exchange reference rates** (ecb.europa.eu, the
  `eurofxref-hist.zip` history) — source of the short-horizon practice set's `em_fx_ecb_daily`
  panels and their answer files, which are shipped here, and of the FX panels and targets of the
  cards that rank the Final, which are not. **The rates against the US dollar are modified data:**
  the organizers compute them as currency per euro divided by US dollars per euro, in full
  precision; the ECB does not publish them. The ECB's published terms permit use provided the
  information is reproduced accurately and the ECB is cited as the source, and require a
  modification to be stated explicitly (<https://www.ecb.europa.eu/services/using-our-site/disclaimer/html/index.en.html>).
  Each panel's manifest `source` and `practice-answers/README.md` state it. Source: ECB.
- **Bank of Japan** (boj.or.jp) — statements on monetary policy and speeches (Kuroda, Ueda,
  Wakatabe, Shirakawa, Adachi, Nakaso, Noguchi, Masai, Shirai, Sato, Iwata, Uchida, Takata, Fukui).
- **Bank of England** (bankofengland.co.uk) — Monetary Policy Committee statements and Monetary
  Policy Summaries, and speeches
  (Carney, Paul Fisher, Cunliffe, Gieve, Shafik, Cleland). *Note: Paul Fisher of the Bank of England
  is a different person from Richard Fisher of the Dallas Fed, and Stanley Fischer of the Federal
  Reserve Board is a third.*
- **Reserve Bank of Australia** (rba.gov.au) — speeches by Stevens and Lowe, and monetary policy
  decision statements. The decision statements were copied from Internet Archive captures of the
  official rba.gov.au pages.
- **People's Bank of China** (pbc.gov.cn) — speeches and articles by Hu Xiaolian and Yi Gang,
  reproduced in the BIS archive (these files carry verbatim bis.org PDF URLs in their own first
  line), and two policy announcements.
- **Bank of Canada** (bankofcanada.ca) — speeches by Poloz and Wilkins, and interest-rate
  announcements. Canadian **Crown copyright** and the Bank's own terms apply.
- **Swiss National Bank** (snb.ch) — three speeches by Thomas Jordan, one press release, and six
  monetary policy assessments (added 2026-09-28; the same copyright page governs them).
  **One of the speeches, `bis_jordan_2021-04-30.txt`, carries an express "© Swiss National Bank"
  notice on its face** (lines 16 and 154), which rules out any MIT or CC-BY-4.0 label for it. The
  other two, `bis_jordan_2014-11-23.txt` and `bis_jordan_2014-12-01.txt`, carry **no copyright
  notice at all**; the SNB's own terms still govern them, but no notice should be attributed to
  them. The press release of 15 January 2015 announcing the end of the minimum exchange rate
  (`snb_floor_discontinued_20150115.txt`, in `t2-F1-chf-highly-valued-2021`) likewise shows no
  copyright or permission notice. **The SNB states its terms on its copyright page**,
  <https://www.snb.ch/en/srv/disclaimer_copyright>: the information and data the SNB provides on
  its website may be saved, translated (with reference to the source), transmitted or used in
  other ways "for non-commercial purposes, compatible with the purpose of such information or
  data". We reproduce the release on those terms, for non-commercial research, and name the SNB
  as its source.
- **Reserve Bank of India** (rbi.org.in) — address by Deputy Governor Michael Debabrata Patra, and
  one monetary policy statement.
- **Norges Bank** (norges-bank.no), **Sveriges Riksbank** (riksbank.se) and **Danmarks
  Nationalbank** (nationalbanken.dk) — monetary policy decision announcements.
- **Reserve Bank of New Zealand** (rbnz.govt.nz) — Official Cash Rate
  announcements, copied from Internet Archive captures of the official pages.
- **Banco Central do Brasil** (bcb.gov.br) — one Copom decision statement in the original units,
  whose terms are not established. The short-horizon practice set's Copom statements and minutes, in
  the Portuguese original, come from the BCB open-data portal (Portal de Dados Abertos do BCB,
  dataset "Documentos do Copom"), and those extracts are offered under the **Open Database License
  (ODbL) v1.0**; their manifest label is `ODbL-1.0`.
- **Banco de México** (banxico.org.mx) — monetary policy decisions and minutes, in the short-horizon
  practice set. Banco de México's usage policy
  (<https://www.banxico.org.mx/footer-en/disclaimer-usage-policies-ban.html>) authorizes the general
  public to use and reproduce its information provided the source and Banco de México's URL are
  stated; the Spanish version is the official one. Each manifest `source` names the document's URL
  and states the title and publisher/date lines the organizers added above the text.
- **Bank Indonesia** (bi.go.id) — welcoming remarks by Governor Agus D W Martowardojo.

### Non-U.S. finance ministries

- **HM Treasury** (gov.uk) — *The Growth Plan 2022* (CP 743), `hmt_growth_plan_2022-09-23.txt`. The
  document carries "© Crown copyright 2022" and is published under the **UK Open Government Licence
  v3.0**. As that licence asks: contains public sector information licensed under the Open
  Government Licence v3.0.
- **Ministry of Finance, Japan** (mof.go.jp) — one monthly report of foreign exchange intervention
  operations, and one joint statement of the Ministry of Finance, the Financial Services Agency and
  the Bank of Japan (10 June 2022, Japanese original, copied from the National Diet Library's WARP
  archive of mof.go.jp). The Ministry's terms of use govern.

### Non-U.S. governments (short-horizon practice set)

- **National Treasury, Republic of South Africa** (treasury.gov.za) — Budget and Medium Term Budget
  Policy Statement speeches **delivered** by the Minister of Finance, one speech per minister. Under
  the Copyright Act 98 of 1978, s.12(8)(a), no copyright subsists in speeches of a political nature;
  s.12(8)(b) keeps the right to make a collection of a speaker's speeches with the speaker, which is
  why no card carries more than one speech by the same minister. Written media statements are not
  included. In one speech, quotations of copyrighted third-party works (an opening epigraph and five
  longer quotations in the text) are removed with the sentences that carry or introduce them, and its
  manifest states each removal.
- **Korea Policy Briefing** (korea.kr) — government press releases, taken only from pages marked
  공공누리 제1유형, the **Korea Open Government License Type 1** (source indication). Text only:
  photographs, captions and contact details are removed, and each manifest names the item page.
- **Press Information Bureau, Government of India** (pib.gov.in) and the **Prime Minister's Office
  archive** (archivepmo.nic.in, the 2004–14 website) — releases. Both sites allow their material to
  be reproduced free of charge without prior approval, provided it is reproduced accurately and the
  source is acknowledged (PIB: <https://pib.gov.in/Content/102_2_Copyright-Policy.aspx>). Tables are
  re-laid out as plain text and a header line is set above the text; the manifest `source` says so.
- **Statistics South Africa** (statssa.gov.za) — extracts of statistical releases (cover and key
  findings), wording unaltered, under the notice printed in Stats SA releases, which lets users apply,
  process, publish or distribute the data provided Stats SA is acknowledged as the original source.

None of these licences is the organizers' to grant: the manifest label is `LicenseRef-Source-Terms`,
with the publisher's licence named in `source`.

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
- **Lehman Brothers Holdings Inc.** — 8-K Exhibit 99.1 of 10 September 2008 (preliminary third
  quarter results and strategic restructuring press release).

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

## Official statistics behind the ranked Final's data-release cards

The data-release cards of the ranked Final each forecast a monthly official statistic first released
between 27 and 30 October 2026. Those cards are not shipped in this repository. Each statistic comes
from its official publisher under that publisher's terms (U.S. federal statistics are public
domain), and each card's manifest names its publisher, source and licence.

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
