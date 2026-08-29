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
| U.S. Federal Reserve Board of Governors, BLS, CFTC, BEA, U.S. Treasury — releases, statements, minutes, speeches by Board officials (including copies mirrored on bis.org) | **Public domain**, 17 U.S.C. §105 | yes |
| FRED-sourced numeric panels (H.15 rates, H.10 FX, BLS/BEA macro) | **Public domain** underlying data, 17 U.S.C. §105; the organizers' selection and arrangement is MIT | yes |
| Speeches by **regional** Federal Reserve Bank officials (New York, Kansas City) | **Unresolved.** The regional Reserve Banks are federally chartered corporations, not federal agencies; §105 does not clearly reach their employees' works | **undetermined** |
| Non-U.S. central banks — ECB, Bank of Japan, Bank of England, RBA, PBoC, Bank of Canada, SNB, RBI, Bank Indonesia | **Issuer's own terms govern.** Except for the two ECB files noted below, no grant to the organizers is evidenced anywhere in this repository | **undetermined** |
| Two ECB files that print their own reuse line — `draghi_whatever_it_takes_2012.txt` and `bis_schnabel_2020-02-27.txt` | **Permission on the face of the document:** *"Reproduction is permitted provided that the source is acknowledged."* | yes, with acknowledgement |
| Corporate exhibits to SEC Form 8-K (Pfizer, Moderna, SVB Financial Group, Apple) | **Private corporate copyright, all rights reserved by the filer.** EDGAR is a government *dissemination* system; filing does not place a document in the public domain | **undetermined** |
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
| `LicenseRef-Source-Terms` | Third-party. **The issuing institution's own terms govern; the organizers grant nothing.** |
| `LicenseRef-ECB-Reproduction-Permitted` | The document prints its own reuse line: *"Reproduction is permitted provided that the source is acknowledged."* Two files carry it; see `data/PROVENANCE.md`. |
| `LicenseRef-Unverified` | Rights basis **not established**. Not a grant and not a denial. |

The `LicenseRef-` values are **not** OSI licences. Three of them confer no permissions and are
honest records of a rights position, including the position "we do not know";
`LicenseRef-ECB-Reproduction-Permitted` records a permission printed on the document itself.

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
