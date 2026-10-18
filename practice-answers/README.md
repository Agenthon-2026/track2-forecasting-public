# Practice answers — the short-horizon practice set

## Executive summary (read this first)

This folder holds the **realized values of the 22 units of the short-horizon practice set**, one
Parquet file per unit, so that you can score a forecast for those cards on your own machine. The
units themselves are in `units/`; their ids end in `-ps1`.

These are the only answers in the repository. The original 103 practice units, the validation
units and every Final card have no answer file in this repository. The unit directories
stay answer-free, exactly as an agent sees them at `/input`.

Every value is historical: every target date is in 2022 or earlier, so none of them is the outcome
of a ranked Final card. Scores you compute with these files are **raw**: they are not divided by
the error the text-blind baseline expects on the card, so they are not on the leaderboard's scale.

---

## The files

- **`<unit_id>.parquet`**, one per short-horizon practice unit. One row per target asset and
  horizon of the card's `[targets]`, asset by asset, then horizon by horizon:

  | Column | Type | Meaning |
  |---|---|---|
  | `draw` | int64 | Always 0: there is one realization. |
  | `asset` | string | The asset id, as in the card's `[targets] asset_ids`. |
  | `horizon` | int64 | The card's horizon key, unchanged: business days after the as-of. |
  | `value` | float64 | The realized value, in the card's `value_unit`. |
  | `target_date` | string | An ISO date: the business day the value is for. |

  Every value is finite, and every cell of the card's grid has exactly one row, which is what the
  scorer requires of a `--realized` file.
- **`SHA256SUMS`**: the SHA-256 of every answer file in this folder. From inside `practice-answers/`,
  check them with `sha256sum -c SHA256SUMS` (on macOS, `shasum -a 256 -c SHA256SUMS`).

## Scoring a forecast locally

Install the toolkit and this repository as the README's "Running the scorer locally" describes,
run your agent on a unit, then:

```bash
python scoring/scoring.py score \
  --card units/<unit_id>/card.toml \
  --forecast out/forecast.parquet \
  --realized practice-answers/<unit_id>.parquet
```

`forecast_meta.json` and `forecast_rationale.md` must sit next to `forecast.parquet`, as for any
scorer run. After `pip install .` the same command is also installed as `qfbench2-t2-score`.

The output carries `"normalization_mode": "raw_unrankable"` and `"rankable": false`. That is
expected: the composite is in the units of what the card forecasts, so it is not comparable across
cards or with the leaderboard. To put a card on the leaderboard's scale, compute the baseline's
expected error from the card's inputs as [`docs/M0-BASELINE.md`](../docs/M0-BASELINE.md) (§3 and
§5) describes, and divide each component by it.

Tuning on these values is fine. The README's "No cross-unit lookup" rule still applies to a run of
a unit: don't carry that unit's answer into it. Doing so would only spoil your own practice score.

## Where the values come from

Each value comes from the same official series as the card's panel. The unit id tells you which:

| Unit ids | Cards | Values | Source and terms |
|---|---:|---|---|
| `t2-F*-curve-…-ps1` | 8 | UST yields in % per annum on the target date: the Treasury's par yields, Federal Reserve H.15, retrieved via FRED (`DGS3MO`, `DGS6MO`, `DGS1`, `DGS2`) | U.S. Government work, public domain (17 U.S.C. §105). |
| `t2-F*-fx-…-ps1` on EUR, JPY or CHF | 3 | Federal Reserve H.10 rates on the target date, retrieved via FRED, quoted as in the card's panel | U.S. Government work, public domain (17 U.S.C. §105). |
| `t2-F*-fx-…-ps1` on MXN, BRL, ZAR, KRW or INR | 11 | Units of the currency per US dollar on the target date. **Modified data:** computed by the organizers from the ECB's euro foreign exchange reference rates as currency per euro divided by US dollars per euro, in full float64 precision, without rounding. The ECB does not publish these rates. | ECB terms of use (<https://www.ecb.europa.eu/services/using-our-site/disclaimer/html/index.en.html>): free use provided the information is reproduced accurately and the ECB is cited as the source; a modification must be stated, as it is here. Source: ECB. |

Every value was checked against its source before publication.

**Licensing.** The values belong to their sources, under the terms above. This repository's MIT
`LICENSE` covers only the organizers' selection and arrangement of them in these files, not the
values; do not relabel a file as if the organizers licensed it. See
[`DATA-LICENSE.md`](../DATA-LICENSE.md), [`THIRD-PARTY-NOTICES.md`](../THIRD-PARTY-NOTICES.md) and
[`data/PROVENANCE.md`](../data/PROVENANCE.md).

If you find a value that does not match its source, please open an issue.
