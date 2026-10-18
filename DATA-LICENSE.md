# Licensing — code, content, and data

This repository contains **three different kinds of material with three different rights bases.**
A single licence does not cover all of it, and this file exists to say which is which.

- **Organizer-authored material is MIT.** The code, task cards, manifests, indexes, specs, docs and
  synthetic fixtures written by the Agenthon 2026 organizers are licensed under the **MIT License**
  (see [`LICENSE`](LICENSE)). `LICENSE` is *this repository's own* licence and applies to *our own*
  work.
- **Third-party corpora and data are NOT licensed by us.** The central-bank speeches, statements,
  agency releases, corporate filings and third-party numeric panels redistributed here were not
  authored by the organizers. We hold no rights to sublicense them, and **MIT does not apply to
  them.** Each remains governed by its issuer's own terms.
- **U.S. Government material is in the public domain.** Works prepared by officers or employees of
  a U.S. federal agency in the course of their official duties carry no copyright under
  **17 U.S.C. §105**. No licence is needed and none is granted — by us or by anyone.

> **MIT is a software licence.** It grants sublicensing and commercial reuse. Asserting it over a
> speech by a non-U.S. central bank official, or over a corporate press release, purports to grant
> rights the organizers never held. That is the specific defect this file corrects.

## Rights basis by category

| Material | Rights basis | Redistributable |
|---|---|---|
| Organizer-authored code, cards, manifests, indexes, specs, docs, synthetic fixtures | **MIT** (this repo's `LICENSE`) | yes |
| U.S. Federal Reserve Board of Governors, BLS, CFTC, BEA, U.S. Treasury, the White House, the State Department, USTR — releases, statements, minutes, projections, transcripts, speeches by Board officials (including copies mirrored on bis.org) | **Public domain**, 17 U.S.C. §105 | yes |
| FRED-sourced numeric panels (H.15 rates, H.10 FX, BLS/BEA macro), including the 3-month, 6-month and 1-year Treasury yields (`DGS3MO`, `DGS6MO`, `DGS1`) that the short-horizon practice set's `rates_daily` panels add, and the matching answer files in `practice-answers/` | **Public domain** underlying data, 17 U.S.C. §105; the organizers' selection and arrangement is MIT | yes |
| ECB euro foreign exchange reference rates. **Shipped here:** the short-horizon practice set's `em_fx_ecb_daily` panels and their answer files in `practice-answers/` (historical rates of MXN, BRL, ZAR, KRW and INR). **Not shipped here:** the FX panels and targets of the cards that rank the Final. In both, the rates against the US dollar are **computed by the organizers** from the ECB's euro rates (currency per euro divided by US dollars per euro); the ECB does not publish them, and each panel's manifest `source` and `practice-answers/README.md` state that modification | **ECB terms of use** (<https://www.ecb.europa.eu/services/using-our-site/disclaimer/html/index.en.html>): free use provided the information is reproduced accurately and the ECB is cited as the source; if the information is modified, this must be stated explicitly. Source: European Central Bank | yes, with attribution and the modification stated |
| Monthly official statistics behind the data-release cards of the ranked Final (not shipped in this repository) | **Each publisher's own terms govern**; U.S. federal statistics are public domain. Each card's manifest names its publisher, source and licence | per publisher |
| Statistics South Africa (statssa.gov.za): extracts of statistical releases | **The notice printed in Stats SA releases**: users may apply, process, publish or distribute the data provided Stats SA is acknowledged as the original source. Extract wording unaltered; what was omitted is stated in the manifest `source` | yes, with acknowledgement |
| Banco de México (banxico.org.mx): monetary policy decisions and minutes | **Banco de México's usage policy** (<https://www.banxico.org.mx/footer-en/disclaimer-usage-policies-ban.html>): the general public may use and reproduce its information provided the source and Banco de México's URL are stated; the Spanish version is the official one | yes, with the source and URL |
| Banco Central do Brasil: Copom statements and minutes in Portuguese, from the BCB open-data portal (dataset "Documentos do Copom") | **Open Database License v1.0 (ODbL)**; the extract is offered under ODbL | yes, under ODbL |
| National Treasury, Republic of South Africa: Budget and Medium Term Budget Policy Statement speeches delivered by the Minister of Finance (one speech per minister) | **No copyright subsists** in speeches of a political nature, Copyright Act 98 of 1978, s.12(8)(a). Written media statements are not included, and no collection of one speaker's speeches is made (s.12(8)(b)) | yes |
| Korea Policy Briefing (korea.kr): government press releases on pages marked 공공누리 제1유형 (KOGL Type 1) | **Korea Open Government License, Type 1** (source indication), text only; photographs and captions removed | yes, with the source indicated |
| Press Information Bureau, Government of India (pib.gov.in), and the Prime Minister's Office archive (archivepmo.nic.in, 2004–14) | **Each site's published policy**: material may be reproduced free of charge without prior approval, provided it is reproduced accurately and the source is acknowledged. Tables re-laid out as plain text, which the manifest `source` states | yes, with attribution |
| Speeches by **regional** Federal Reserve Bank officials (New York, Kansas City) | **Unresolved.** The regional Reserve Banks are federally chartered corporations, not federal agencies; §105 does not clearly reach their employees' works | **undetermined** |
| Non-U.S. central banks in the original 103 practice units — ECB, Bank of Japan, Bank of England, RBA, PBoC, Bank of Canada, SNB, RBI, Bank Indonesia, Norges Bank, Sveriges Riksbank, Danmarks Nationalbank, RBNZ, Banco Central do Brasil — and the Japan Ministry of Finance | **Issuer's own terms govern.** Except for the ECB reference rates noted above, and the ECB files and the SNB press release noted below, no grant to the organizers is evidenced anywhere in this repository. (The short-horizon practice set's Banco de México and Banco Central do Brasil texts have their own rows above.) | **undetermined** |
| ECB files that print their own reuse line: in the original units, eight files (six documents) — `draghi_whatever_it_takes_2012.txt`, `bis_schnabel_2020-02-27.txt`, `bis_guindos_2019-11-06.txt` (three copies), `bis_lane_2020-02-17.txt`, `bis_lagarde_2020-09-10.txt`, `bis_panetta_2022-03-30.txt`; in the short-horizon practice set, the ECB monetary policy decision press releases | **Permission on the face of the document:** *"Reproduction is permitted provided that the source is acknowledged."* | yes, with acknowledgement |
| The SNB press release of 15 January 2015 — `snb_floor_discontinued_20150115.txt` | **The SNB's published copyright terms** (<https://www.snb.ch/en/srv/disclaimer_copyright>): the information and data the SNB provides on its website may be saved, translated (with reference to the source), transmitted or used in other ways *"for non-commercial purposes, compatible with the purpose of such information or data"*. Its manifest licence stays `LicenseRef-Source-Terms` | yes, for non-commercial use |
| HM Treasury, *The Growth Plan 2022* — `hmt_growth_plan_2022-09-23.txt` | **UK Open Government Licence v3.0** (© Crown copyright 2022). Its manifest licence stays `LicenseRef-Source-Terms`; the manifest `source` carries the attribution the licence asks for | yes, with attribution |
| Corporate exhibits to SEC Form 8-K (Pfizer, Moderna, SVB Financial Group, Apple, Lehman Brothers) | **Private corporate copyright, all rights reserved by the filer.** EDGAR is a government *dissemination* system; filing does not place a document in the public domain | **undetermined** |
| Factor panels from the Kenneth R. French Data Library and AQR Capital Management | **Providers' own terms of use.** Neither grants sublicensing or commercial reuse | **undetermined** |

"Undetermined" means exactly that: **we have not established the terms, and we are not asserting
any.** It is not a grant, and it is not a denial. See `THIRD-PARTY-NOTICES.md` for the per-issuer
detail and for the express copyright notices some of these documents carry on their face.

### The `license` identifiers used in `manifest.json`

| Identifier | Meaning |
|---|---|
| `MIT` | Organizer-authored. This repository's `LICENSE` applies. |
| `LicenseRef-US-Gov-Public-Domain` | U.S. Government work, 17 U.S.C. §105. No copyright, no licence needed. |
| `LicenseRef-US-Gov-Public-Domain AND MIT` | Public-domain data in an organizer-authored presentation (e.g. the CFTC extracts). |
| `LicenseRef-Source-Terms` | Third-party. **The issuing institution's own terms govern; the organizers grant nothing.** For the SNB press release, the HM Treasury document and the short-horizon practice set's files under this label (Banco de México, South Africa's National Treasury, Statistics South Africa, korea.kr, PIB and the PMO archive), whose published terms this repository records, the manifest `source` states them. |
| `LicenseRef-ECB-Reproduction-Permitted` | The ECB permits reproduction provided the source is acknowledged. Either the document prints its own reuse line, *"Reproduction is permitted provided that the source is acknowledged."* (eight files, six documents, of the original units and the ECB decision press releases of the short-horizon practice set; see `data/PROVENANCE.md`), or, for the `em_fx_ecb_daily` panels, the ECB's published terms of use grant it, on condition that a modification is stated, which their manifest `source` does. |
| `ODbL-1.0` | Open Database License v1.0 (its SPDX identifier): the Banco Central do Brasil Copom texts of the short-horizon practice set, from the BCB open-data portal. |
| `LicenseRef-Unverified` | Rights basis **not established**. Not a grant and not a denial. |

The `LicenseRef-` values are **not** OSI licences. Three of them confer no permissions and are
honest records of a rights position, including the position "we do not know";
`LicenseRef-ECB-Reproduction-Permitted` records a permission the ECB grants: printed on the document
itself, or, for the `em_fx_ecb_daily` panels, in the ECB's published terms of use.

## The manifests are authoritative

Each unit's `manifest.json` records a `license` and a `source` for **every file in that unit**.
**That per-file record is the authoritative one.** It is per-file rather than per-category, and it is
checked in CI against the bytes on disk, so it is the record a tool should read and the record that
wins where anything else disagrees with it.

Two documents summarise the same information for humans, and neither overrides a manifest entry:

- [`data/PROVENANCE.md`](data/PROVENANCE.md) — where each group of documents came from, and what we
  could not establish. Read this first if you want the shape of the corpus.
- [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md) — the per-issuer notices and the express
  copyright lines some of these documents carry on their face.

The answer files of the short-horizon practice set, in `practice-answers/`, are not in any unit's
manifest. Their record is `practice-answers/README.md`, which gives each file's source and rights
basis, and `practice-answers/SHA256SUMS`, which pins their bytes.

Each unit's `card.toml` also carries a short `[provenance]` block. It is a summary too, and **where
it differs from that unit's `manifest.json`, the manifest is correct.**

> **⚠ Organizers — before publishing:** confirm the `[provenance]` blocks in `units/*/card.toml` have
> been brought into line with their manifests. A card is checksummed by its own `manifest.json`, so
> the two have to be updated together.

The issuing institution for each document is established; the exact retrieval URL generally is
**not**. Where a source is recorded as `unverified`, that is a truthful statement that we could not
establish it — not an oversight to be filled in with a plausible guess.

## Vendor data is not covered

Commercial vendor data is **not** redistributed here and is **not** covered by this license. It is
referenced by checksum and access instructions only, and remains governed by the vendor's own
agreement.
