# Landmarks index

Some practice units ship one or more **landmark documents**: a single official statement, speech,
testimony or set of minutes that the card's text corpus is built around. In each unit's
`text/corpus_index.json` these entries have `doc_type = "landmark"` and the source
`official (see landmarks index)`, and the unit's `card.toml` names that source in `[text]`. This
file is that index.

The track ships 49 distinct landmark documents, as 68 copies across 50 units: the 13 below, and the
36 key-event documents added on 2026-09-28 in the second table. For each one the table gives the
document's own date, its title as printed on the document, and the official source URL. For the
first 13 the URL is the one recorded by the organizers' landmark fetcher and the retrieval date was
not recorded.

| File (under `units/<unit>/text/`) | Document date | Title on the document | Official source |
|---|---|---|---|
| `draghi_whatever_it_takes_2012.txt` | 2012-07-26 | Speech by Mario Draghi at the Global Investment Conference in London | <https://www.ecb.europa.eu/press/key/date/2012/html/sp120726.en.html> |
| `bernanke_jec_testimony_2013.txt` | 2013-05-22 | Bernanke, "The Economic Outlook", before the Joint Economic Committee | <https://www.federalreserve.gov/newsevents/testimony/bernanke20130522a.htm> |
| `fomc_minutes_20130619_released_2013-07-10.txt` | meeting 2013-06-19, released 2013-07-10 | Minutes of the Federal Open Market Committee, June 18-19, 2013 | <https://www.federalreserve.gov/monetarypolicy/fomcminutes20130619.htm> |
| `snb_floor_discontinued_20150115.txt` | 2015-01-15 | Swiss National Bank discontinues minimum exchange rate and lowers interest rate to –0.75% (press release) | <https://www.snb.ch/public/asset/en/www-snb-ch/publications/communication/press-releases/2015/pre_20150115/publications0_en/pre_20150115.en.pdf> |
| `fomc_statement_20200315.txt` | 2020-03-15 | Federal Reserve issues FOMC statement | <https://www.federalreserve.gov/newsevents/pressreleases/monetary20200315a.htm> |
| `fomc_statement_20210922.txt` | 2021-09-22 | Federal Reserve issues FOMC statement | <https://www.federalreserve.gov/newsevents/pressreleases/monetary20210922a.htm> |
| `fomc_statement_20211215.txt` | 2021-12-15 | Federal Reserve issues FOMC statement | <https://www.federalreserve.gov/newsevents/pressreleases/monetary20211215a.htm> |
| `powell_jackson_hole_2022.txt` | 2022-08-26 | Powell, "Monetary Policy and Price Stability" (Jackson Hole symposium) | <https://www.federalreserve.gov/newsevents/speech/powell20220826a.htm> |
| `boe_mpc_statement_20220922.txt` | 2022-09-22 | Bank Rate increased to 2.25% - September 2022 Monetary Policy Summary and minutes of the Monetary Policy Committee meeting | <https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2022/september-2022> |
| `boj_ycc_20221220.txt` | 2022-12-20 | Statement on Monetary Policy | <https://www.boj.or.jp/en/mopo/mpmdeci/mpr_2022/k221220a.pdf> |
| `boj_ycc_20230728.txt` | 2023-07-28 | Statement on Monetary Policy | <https://www.boj.or.jp/en/mopo/mpmdeci/mpr_2023/k230728a.pdf> |
| `boj_ycc_20240319.txt` | 2024-03-19 | Changes in the Monetary Policy Framework | <https://www.boj.or.jp/en/mopo/mpmdeci/mpr_2024/k240319a.pdf> |
| `boj_ycc_20240731.txt` | 2024-07-31 | Change in the Guideline for Money Market Operations and Decision on the Plan for the Reduction of the Purchase Amount of Japanese Government Bonds | <https://www.boj.or.jp/en/mopo/mpmdeci/mpr_2024/k240731a.pdf> |

### Key-event documents added on 2026-09-28

Each practice card was re-read for the event it is built around (a policy decision, a projection
change, a government announcement, a failure). Where that event's own official document was
missing from the card's corpus, it was fetched on 2026-09-27 and 2026-09-28 and added, dated by its
publication date. Every copy is dated on or before its card's as-of date.

| File (under `units/<unit>/text/`) | Document date | Title on the document | Official source |
|---|---|---|---|
| `bernanke_testimony_mpr_2007-07-18.txt` | 2007-07-18 | Semiannual Monetary Policy Report to the Congress | <https://www.federalreserve.gov/newsevents/testimony/bernanke20070718a.htm> |
| `frb_discount_rate_action_2007-08-17.txt` | 2007-08-17 | Federal Reserve Board discount rate action | <https://www.federalreserve.gov/newsevents/pressreleases/monetary20070817a.htm> |
| `ecb_pressconf_2008-06-05.txt` | 2008-06-05 | Introductory statement with Q&A | <https://www.ecb.europa.eu/press/press_conference/monetary-policy-statement/2008/html/is080605.en.html> |
| `frb_bernanke_gse_statement_2008-09-07.txt` | 2008-09-07 | Statement by Chairman Bernanke on Fannie Mae and Freddie Mac | <https://www.federalreserve.gov/newsevents/pressreleases/other20080907a.htm> |
| `ust_paulson_gse_2008-09-07.txt` | 2008-09-07 | Statement by Secretary Henry M. Paulson, Jr. on Treasury and Federal Housing Finance Agency Action to Protect Financial Markets and Taxpayers | <https://home.treasury.gov/news/press-releases/hp1129> |
| `lehman_8k_ex991_2008-09-10.txt` | 2008-09-10 | Lehman Brothers Announces Preliminary Third Quarter Results and Strategic Restructuring (Form 8-K, Exhibit 99.1) | <https://www.sec.gov/Archives/edgar/data/806085/000110465908057829/a08-22764_2ex99d1.htm> |
| `joint_statement_treasury_fdic_occ_ots_frb_2009-02-23.txt` | 2009-02-23 | Joint Statement by the Treasury, FDIC, OCC, OTS, and the Federal Reserve | <https://www.federalreserve.gov/newsevents/pressreleases/bcreg20090223a.htm> |
| `bernanke_testimony_mpr_2009-02-24.txt` | 2009-02-24 | Semiannual Monetary Policy Report to the Congress | <https://www.federalreserve.gov/newsevents/testimony/bernanke20090224a.htm> |
| `frb_fdic_occ_ots_scap_assessments_2009-02-25.txt` | 2009-02-25 | Agencies to Begin Forward-Looking Economic Assessments | <https://www.federalreserve.gov/newsevents/pressreleases/bcreg20090225a.htm> |
| `ust_geithner_debt_limit_2011-05-16.txt` | 2011-05-16 | As US Reaches Debt Limit, Geithner Implements Additional Extraordinary Measures to Allow Continued Funding of Government Obligations | <https://home.treasury.gov/as-us-reaches-debt-limit-geithner-implements-additional-extraordinary-measures-to-allow-continued-funding-of-government-obligations> |
| `ecb_pressconf_2014-05-08.txt` | 2014-05-08 | Introductory statement to the press conference (with Q&A) | <https://www.ecb.europa.eu/press/press_conference/monetary-policy-statement/2014/html/is140508.en.html> |
| `ecb_pressconf_2014-12-04.txt` | 2014-12-04 | Introductory statement to the press conference (with Q&A) | <https://www.ecb.europa.eu/press/press_conference/monetary-policy-statement/2014/html/is141204.en.html> |
| `fomc_sep_2014-12-17.txt` | 2014-12-17 | FOMC Projections Materials (Chair's press conference projections materials), December 17, 2014 | <https://www.federalreserve.gov/monetarypolicy/files/fomcprojtabl20141217.pdf> |
| `fomc_sep_2015-03-18.txt` | 2015-03-18 | FOMC Projections Materials (Chair's press conference projections materials), March 18, 2015 | <https://www.federalreserve.gov/monetarypolicy/files/fomcprojtabl20150318.pdf> |
| `fomc_normalization_addendum_2017-06-14.txt` | 2017-06-14 | Addendum to the Policy Normalization Principles and Plans | <https://www.federalreserve.gov/monetarypolicy/files/FOMC_PolicyNormalization.20170613.pdf> |
| `ecb_pressconf_2017-09-07.txt` | 2017-09-07 | Introductory statement to the press conference | <https://www.ecb.europa.eu/press/pressconf/2017/html/ecb.is170907.en.html> |
| `fomc_sep_2018-06-13.txt` | 2018-06-13 | FOMC Projections Materials, June 13, 2018 | <https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20180613.htm> |
| `ustr_section301_tariff_list_2018-06-15.txt` | 2018-06-15 | USTR Issues Tariffs on Chinese Products in Response to Unfair Trade Practices | <https://ustr.gov/about-us/policy-offices/press-office/press-releases/2018/june/ustr-issues-tariffs-chinese-products> |
| `fomc_balance_sheet_statement_2019-01-30.txt` | 2019-01-30 | Statement Regarding Monetary Policy Implementation and Balance Sheet Normalization | <https://www.federalreserve.gov/newsevents/pressreleases/monetary20190130c.htm> |
| `fomc_sep_2019-06-19.txt` | 2019-06-19 | FOMC Projections Materials, June 19, 2019 | <https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20190619.htm> |
| `wh_trump_remarks_china_tariffs_2019-08-01.txt` | 2019-08-01 | Remarks by President Trump Before Marine One Departure | <https://trumpwhitehouse.archives.gov/briefings-statements/remarks-president-trump-marine-one-departure-56/> |
| `powell_presser_2019-07-31.txt` | press conference 2019-07-31, final transcript posted 2019-08-08 | Transcript of Chair Powell's Press Conference, July 31, 2019 (FINAL) | <https://www.federalreserve.gov/mediacenter/files/FOMCpresconf20190731.pdf> |
| `fomc_sep_2021-12-15.txt` | 2021-12-15 | Summary of Economic Projections, December 15, 2021 (FOMC projections materials) | <https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20211215.htm> |
| `wh_psaki_sullivan_briefing_2022-02-11.txt` | 2022-02-11 | Press Briefing by Press Secretary Jen Psaki and National Security Advisor Jake Sullivan, February 11, 2022 | <https://bidenwhitehouse.archives.gov/briefing-room/press-briefings/2022/02/11/press-briefing-by-press-secretary-jen-psaki-and-national-security-advisor-jake-sullivan-february-11-2022/> |
| `state_blinken_unsc_2022-02-17.txt` | 2022-02-17 | Secretary Antony J. Blinken on Russia's Threat to Peace and Security at the UN Security Council | <https://2021-2025.state.gov/secretary-antony-j-blinken-on-russias-threat-to-peace-and-security-at-the-un-security-council/> |
| `powell_presser_2022-05-04.txt` | press conference 2022-05-04, final transcript posted 2022-05-20 | Transcript of Chair Powell's Press Conference, May 4, 2022 (FINAL) | <https://www.federalreserve.gov/mediacenter/files/FOMCpresconf20220504.pdf> |
| `mof_fsa_boj_threeparty_statement_2022-06-10.txt` | 2022-06-10 | 国際金融資本市場に係る情報交換会合の声明 (statement after the Ministry of Finance / Financial Services Agency / Bank of Japan meeting on international financial markets; Japanese only) | <https://www.mof.go.jp/policy/international_policy/gaitame_kawase/press_release/20220610_statement.pdf> |
| `ecb_adhoc_statement_2022-06-15.txt` | 2022-06-15 | Statement after the ad hoc meeting of the ECB Governing Council | <https://www.ecb.europa.eu/press/pr/date/2022/html/ecb.pr220615~2aa3900e0a.en.html> |
| `hmt_growth_plan_2022-09-23.txt` | 2022-09-23 | The Growth Plan 2022 (CP 743) | <https://www.gov.uk/government/publications/the-growth-plan-2022-documents/the-growth-plan-2022-html> |
| `ust_quarterly_refunding_2023-08-02.txt` | 2023-08-02 | Quarterly Refunding Statement of Assistant Secretary for Financial Markets Josh Frost | <https://home.treasury.gov/news/press-releases/jy1671> |
| `fomc_sep_2023-09-20.txt` | 2023-09-20 | Summary of Economic Projections, September 20, 2023 (FOMC projections materials) | <https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20230920.htm> |
| `boj_uchida_speech_2024-02-08.txt` | 2024-02-08 | Japan's Economy and Monetary Policy (Speech at a Meeting with Local Leaders in Nara, UCHIDA Shinichi, Deputy Governor) | <https://www.boj.or.jp/en/about/press/koen_2024/ko240208a.htm> |
| `boj_takata_speech_2024-03-06.txt` | 2024-03-06 | Economic Activity, Prices, and Monetary Policy in Japan (Speech at a Meeting with Local Leaders in Shiga, TAKATA Hajime, Member of the Policy Board) | <https://www.boj.or.jp/en/about/press/koen_2024/ko240306a.htm> |
| `mof_fx_intervention_monthly_2024-05-31.txt` | 2024-05-31 | Foreign Exchange Intervention Operations (April 26, 2024 – May 29, 2024) | <https://www.mof.go.jp/english/policy/international_policy/reference/feio/monthly/20240531e.html> |
| `fomc_sep_2024-06-12.txt` | 2024-06-12 | FOMC Projections Materials: Summary of Economic Projections, June 12, 2024 | <https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20240612.htm> |
| `fomc_sep_2024-12-18.txt` | 2024-12-18 | FOMC Projections Materials: Summary of Economic Projections, December 18, 2024 | <https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20241218.htm> |

Notes on individual documents:
- **Press-conference transcripts** (`powell_presser_*`) are dated by the day the final transcript
  was posted, not the day of the press conference, because the transcript was not public before
  then.
- **Summaries of Economic Projections** (`fomc_sep_*`) are the full projections materials released
  at 2:00 p.m. on the FOMC decision day; the dot plot is written out as a count table.
- `ecb_pressconf_2017-09-07.txt` holds the introductory statement only: the Q&A was not yet on the
  ECB page on the day. The other three ECB press conferences include the Q&A, which was public
  within two days and before the card's as-of date.
- `mof_fsa_boj_threeparty_statement_2022-06-10.txt` is in **Japanese only**, as published; no
  official English version exists. The official PDF link now returns 404, so the copy comes from the
  National Diet Library's WARP archive of mof.go.jp, and is byte-identical to the Internet Archive
  capture of the official URL taken on 10 June 2022.
- `wh_trump_remarks_china_tariffs_2019-08-01.txt` is the White House transcript of the President's
  remarks of 1 August 2019 announcing the 10% tariff on a further $300 billion of Chinese imports.
  The announcement itself was first posted on social media, which is not an official record.
- `ust_quarterly_refunding_2023-08-02.txt`: the auction-size table on the Treasury page is an
  image; its 48 numbers were typed in as plain text.
- `lehman_8k_ex991_2008-09-10.txt` is a corporate filing, not a government document (see
  `THIRD-PARTY-NOTICES.md`).

The rights position of each document is in its manifest entry and in
[`THIRD-PARTY-NOTICES.md`](../THIRD-PARTY-NOTICES.md): the Federal Reserve, U.S. Treasury, White
House, State Department and USTR documents are U.S. Government works in the public domain; the ECB
speech prints its own reproduction permission; the HM Treasury Growth Plan is published under the
UK Open Government Licence v3.0; for the Bank of England, Bank of Japan, Swiss National Bank, other
ECB and Japan Ministry of Finance documents the issuer's terms govern (for the SNB press release,
its copyright page, <https://www.snb.ch/en/srv/disclaimer_copyright>, allows non-commercial use
compatible with the purpose of the information); the Lehman Brothers exhibit is the issuer's
private copyright.

Every copy has been passed through `scripts/declutter_corpus.py` like the rest of the corpus (see
`data/PROVENANCE.md`); only the ECB and Bank of England pages had website material to remove.
`boe_mpc_statement_20220922.txt` no longer carries the "Other Monetary
Policy Committee news" list that the web page showed at retrieval time; that list named 2026
announcements, years after the statement.
