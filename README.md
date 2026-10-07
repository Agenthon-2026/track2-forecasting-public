# Track 2 — Reasoning-Augmented Time-Series Forecasting (Participant Guide)

## Executive summary (read this first)

Track 2 asks one question: **can an AI agent reason over text AND time-series data to forecast financial markets better than a model that looks only at numbers?**

You submit a **Docker agent** — an LLM-powered reasoning system combined with a forecasting component — that reads two things: multivariate **time-series panels** (rates, FX, macro, factor returns) and a frozen, time-stamped **text corpus** (news headlines, FOMC statements, central-bank speeches, macro-release commentary) available up to the as-of date. It must output a full probability distribution over possible futures, expressed as Monte Carlo draws.

We score your output against sealed realized market outcomes using a **CRPS composite**:

**S = 0.5 × marginal CRPS + 0.3 × joint variogram + 0.2 × tail penalty (lower is better)**

The headline scientific question is whether adding text improves a forecast. The five named
adapters in `baselines/` are Gaussian-random-walk scaffolds, not working implementations of
Chronos, TimesFM, Lag-Llama, MOIRAI, or Theta/AutoARIMA. The published scorer reports the composite
and its components; it does not compute a separate information-uplift or text-ablation score.

**Track 2 vs. Track 4:** Track 2 = time-series data (panels indexed by time) → forecast the future. Track 4 = general tabular data (a table of entities) → predict a label or value. Both tracks add text and LLM reasoning, and both run in Docker with **no open internet**: the only network egress is model-API calls through the organizer's audited proxy. See "Network contract and submission categories" below.

**Unfamiliar terms?** See the competition-wide GLOSSARY published with the shared toolkit:
`Agenthon-2026/Agenthon2026-public`, file `docs/GLOSSARY.md`. Or read `docs/CONCEPTS.md` first.

**Track 2 is led by Polak.** Reviewers for this track are Rosenberg, Kazantsev, and Koutsoyannis.
All pull requests to this repository require Polak's approval before merge.

---

## What you get access to

### Time-series panels

Four panels of publicly sourced financial time-series data, each in Parquet format with
columns `[date: date32, asset: utf8, value: float64, panel_id: utf8]`. All panels
cover 2000-01-03 through 2024-12-31 and are business-day indexed.

| Panel | Path | Series | Unit |
|-------|------|--------|------|
| `rates/ust-daily` | `data/rates/ust_daily.parquet` | UST 2Y, 5Y, 7Y, 10Y, 20Y, 30Y | % per annum |
| `fx/g10-daily` | `data/fx/g10_daily.parquet` | EUR, GBP, JPY, CHF, AUD, CAD, NZD, SEK, NOK, DKK vs USD | spot mid |
| `macro/releases-quarterly` | `data/macro/releases_quarterly.parquet` | CPI, PCE, NFP, GDP flash × G6 + selected EM | native units |
| `factors/jkp-daily` | `data/factors/jkp_daily.parquet` | MKT, SMB, HML, MOM, BAB, QMJ | decimal daily return |

Data-pipeline scripts that reproduce these files from public sources are in `data-pipelines/`.
The canonical panels shipped in `data/` are the ones the harness uses.

### Text corpus

Each evaluation card comes with a frozen, time-stamped **text corpus** mounted at `/input/text/`.
The corpus contains only documents with timestamps on or before the card's as-of date. No document with a date after the as-of date is included — this is enforced **before publication** by the organizer's staging gates (`cutoff.scan_text_corpus_cutoff`), not by gate g2 at scoring time: the scoring program never sees `/input/text/`. Your agent may read the corpus freely; it may not fetch any text or market data from the internet at inference time. The restricted network allows model-API calls only (see the network contract below), and vendor-side tools such as web search and retrieval must be disabled in those calls.

Typical corpus contents:

- FOMC statements and meeting minutes
- Federal Reserve and ECB governor speeches (text form)
- Macro-release headlines and survey commentary (e.g., NFP surprise wording)
- COT (Commitment of Traders) analyst summaries
- News headlines tagged to the release date

The text corpus is what lets a reasoning agent beat a text-blind baseline. An agent that notices an FOMC statement shifting tone toward tightening can adjust its rate forecast accordingly, even before the numbers in the panel reflect the move.

### Practice tasks — 103 units

`units/` contains **103 practice units** with full specifications, covering all four card
families: **F1 23 · F2 27 · F3 22 · F4 31**. Every one carries its panels, its dated text
corpus, its card and its spec. By `target_type` the 103 split **87 `level` · 16 `log_return`**;
the type is stated in each unit's `card.toml` and `forecast_spec.json`, and your output must
match it.

`units/` holds **104 directories**, not 103: the extra one is the worked exemplar
`t2-EXAMPLE-ust-curve-1m`, which is referenced throughout this README and ships no
`forecast_spec.json`. It is the only unit here without one, and it is not counted as a practice
unit above.

**They carry no answers.** That is deliberate and it bounds what a local run can tell you:

| You can check locally | You cannot check locally |
|---|---|
| that your agent runs, reads the card, and writes all three output files | how accurate your forecast is |
| that it passes the admissibility gates (g0–g3) | your CRPS composite |
| that the `baselines/` scaffolds run against the same panel (their forecast is a placeholder — see below) | anything about the scored baseline, or whether you beat it |

Accuracy feedback comes from submitting: the Development leaderboard scores you on this
repository's `validation` units, against outcomes that are not shipped with them. Use the
practice units to get *admissible*, and the leaderboard to find out how good you are.

The held-out evaluation units are sealed in the private repository and are a different, later
window — nothing in this practice data reaches them.

**These cards are practice, and the Development leaderboard is a practice board — not a
ranking.** Because the cards share underlying series and each panel is cut at its own as-of
date, most of this set is readable from itself (see "Leakage rules", rule 5). We are telling
you this rather than letting the teams who work it out compete against the teams who don't.
Use the board the way it is useful — to check that your agent runs, parses, and calibrates —
and read your per-card scores rather than your position. **The ranking that decides the
competition is the Final phase**, on the sealed set — a different, later window that nothing in
this practice data reaches.

### Scoring code

`scoring/scoring.py` is the reference implementation of all three score components plus all admissibility gates. The production harness runs this exact code. Run it locally to verify your output before submitting.

### `baselines/` — five adapter scaffolds, not five working models

`baselines/` contains five files named after text-blind time-series models. **None of them runs the
model it is named after.** Each demonstrates the adapter interface — the `BaselineForecaster` shape,
the request/result types, seeding, output validation — and then returns samples from a Gaussian
random walk. The import at the top of each file is a presence check whose result is never used.

| File | Interface it demonstrates | Forecast actually produced |
|------|---------------------------|----------------------------|
| `theta_arima` | classical statistical adapter (Theta / AutoARIMA shape) | Gaussian random walk |
| `chronos` | foundation-model adapter (Amazon Chronos shape) | Gaussian random walk |
| `timesfm` | foundation-model adapter (Google TimesFM shape) | Gaussian random walk |
| `lag_llama` | time-series LLM adapter (Lag-Llama shape) | Gaussian random walk |
| `moirai` | multi-frequency adapter (Salesforce MOIRAI shape) | Gaussian random walk |

They say so themselves: every result carries `"implementation": "gaussian-rw-placeholder"` and
`"real_adapter_implemented": false` in its metadata. The five use different fixed seeds, so they
produce different numbers; that difference is seed noise, not method.

**These are not a bar to clear.** Do not calibrate against them and do not read a gap between your
agent and one of them as information uplift — the comparison would be against noise. Take the files
for their interface and bring your own forecaster. Details and the scoring consequences are in
[`baselines/README.md`](baselines/README.md).

The baseline your score is normalized against is a different thing: it runs organizer-side and it
is not any of these files. You see it through the normalization, described next, and as a
reference row on the leaderboard.

**The organizer baseline's per-unit normalization values are not shipped.** Each one is the error
that baseline expects to make on that card, computed from the card's inputs before the outcome
exists ([docs/M0-BASELINE.md](docs/M0-BASELINE.md), §5). A normalized score of **1.0** means your
error equals that expected error; lower is better. The baseline's own score is shown on the
leaderboard as a reference row. This comparison is against the organizer baseline, not the five
named scaffolds, and it does not isolate how much of an improvement came from text.

---

## Network contract and submission categories

### The two network modes

Track 2 units declare `network = "restricted"` in `card.toml [environment]`. There are two
modes you will encounter:

1. **Local development (smoke runs).** Run your container with `--network=none`. The reference
   forecast CLI, local scorer, and five adapter scaffolds work offline. If your agent needs
   a model API, local runs without network will fail those calls;
   that is expected and fine for structural smoke tests.
2. **Official scoring (`restricted`).** Your container runs on an internal eval network with
   **no open internet**. The only permitted egress is through the organizer's audited proxy to:
   - the organizer-hosted model endpoint (open models served via NIM/vLLM; free, with a
     per-unit request budget) — **and nothing else**.

   Vendor model APIs (`api.anthropic.com`, `api.openai.com`,
   `generativelanguage.googleapis.com`, any other) are **refused by the proxy** (policy
   2026-08-04). There is no other language model: bring-your-own models and adapters are not
   part of this competition (ruling of 2026-09-18). See "Submission categories" below.

   Every connection is logged (domain, bytes, timestamps). These logs are the audit artifact
   for verification within the joint Final + Verification phase. **Vendor-side tools — web search, code execution, retrieval —
   must be disabled in all API calls.** This is enforced by rule and by audit.

At scoring time your container receives this environment:

| Variable | Meaning |
|----------|---------|
| `HTTP_PROXY` / `HTTPS_PROXY` | The organizer's audited proxy — all egress goes through it. Read them from the environment; never hardcode a proxy host, the address has changed before |
| `NO_PROXY` | Hosts that must bypass the proxy |
| `MODEL_ENDPOINT` | The **origin** of the House route — `scheme://host:port`, **no path**. The OpenAI-compatible API is served under `/v1`: `POST $MODEL_ENDPOINT/v1/chat/completions`. `$MODEL_ENDPOINT/chat/completions` (no `/v1`) is refused with 403 |
| `MODEL_TOKEN` | The per-unit bearer credential. Send `Authorization: Bearer $MODEL_TOKEN` on every request; without it the route answers 401 |
| `MODEL_NAME` | The runtime alias of the House model — use it as the `model` field of every request. The model identity and snapshot you disclose in `models[]` are in the [House model guide](https://github.com/Agenthon-2026/Agenthon2026-public/blob/main/docs/HOUSE-MODEL.md) |
| `QFBENCH_NETWORK` | `restricted` (or `none` for local smoke runs) |
| Your API keys | **None exist.** The harness injects no participant API key and there is no mechanism to supply one (policy 2026-08-04) |

With the OpenAI client that is
`OpenAI(base_url=os.environ["MODEL_ENDPOINT"].rstrip("/") + "/v1", api_key=os.environ["MODEL_TOKEN"])`.
Budget the calls: the House allowance is **25 admitted requests per unit** with at most **4,000
output tokens per call**; there is no per-unit token allowance. A request is charged at
admission, so an upstream failure is not refunded and a retry costs another slot. This table is
a summary; the binding version, with the full charging rules, is
[`SUBMISSION_CLI.md`](SUBMISSION_CLI.md#container-environment-contract-restricted-mode-set-by-the-harness).

Data and text cutoffs are unchanged: panel and corpus timestamps are enforced by the organizer's staging gates before a unit ships, and gate g2 still binds your declaration to the trusted card. The network
contract does not weaken any leakage rule: model APIs are reachable, market data and live text
are not.

### Submission categories

A Track 2 forecaster may use permitted numerical code without calling the House model. Use `category: "api"`; House calls are optional. Use `models: []` only when the submission contains no learned model. Disclose any packaged fitted model with `access: "local"`, its immutable revision and training cutoff; include the House disclosure when used. The existing artifact, data-cutoff and resource rules still apply.

| Category | What you bundle | Model access |
|----------|-----------------|--------------|
| `api` | Prompts, harness, agent code and permitted local numerical artifacts | Optional House calls, via the proxy |

`api` is the only category on this track. **Bring-your-own models and adapters are not part of
this competition** (ruling of 2026-09-18): the former `byo-large` / `byo-small` values are
invalid since toolkit 2.4.3, `qfbench2 submission pack` refuses them, and an upload that still
carries one is held by the organizer's intake and never run.

The [Track 2 artifact policy](docs/ARTIFACT-POLICY.md) specifies which fitted non-neural
models, calibration parameters and static retrieval assets are allowed, with cutoff and
provenance requirements. Additional pretrained neural checkpoints need separate approval. These
permissions do not change the task resource limits.

Every entry is tagged with its category, the models it used (pinned versions), and their
training cutoffs.

**There is one ranking: the equal-weight mean of your normalized scores across every card,
lower is better.** On each card, each score component is divided by the error the text-blind
baseline expects to make on that card, a value computed from the card's inputs before the outcome
exists. A normalized score of 1.0 therefore means your error equals that expected error. Because
the divisor does not depend on the outcome, the honest forecast is the best strategy. The
baseline's own score is shown on the leaderboard as a reference row.

Each card counts the same regardless of its shape. That is fair because of a fix one level down.
Some cards ask for a single number (one asset at one horizon); others ask for several at once.
The joint-variogram term measures relationships *between* the numbers you forecast, so on a
single-number card it is 0 no matter how good your forecast is — its weight is redistributed over
the terms that do exist (0.714 x CRPS + 0.286 x tail), so that 1.0 means the same thing on both
shapes. With both on the same footing, one average is averaging one quantity.

**Every card is in the denominator, and a card you do not score counts against you.** A card
that is inadmissible, errors, or is never attempted takes a pre-committed worst-case value
(**8.0** — eight times the error the text-blind baseline expects of itself), and real scores are
clipped at that same value. So failing a hard card can at best *tie* the worst possible attempt at
it, never beat it: there is no card you are better off skipping. The value is not ours to pick per
card — it is the worst end of the declared metric domain in the signed evaluation plan that
governs ranking. See [CONCEPTS.md](docs/CONCEPTS.md) for the scoring detail and
[docs/M0-BASELINE.md](docs/M0-BASELINE.md) for how the baseline and its expected error are
computed.

### Reproducibility rules

- Model versions MUST be pinned (dated snapshots).
- The training cutoff of every model MUST be disclosed in your submission metadata.
- Temperature and seed MUST be pinned where the API supports it.
- Entries are verified statistically (bootstrap-CI overlap on rerun).

### House API allocation

The model budget is **requests per unit**: **25 admitted requests per unit**, with **at most
4,000 output tokens per request**, both counted by the House route. There is no per-unit token
allowance — the earlier figure of 1,000,000 input plus 100,000 output tokens per unit is withdrawn
and nothing replaces it. See the
[model-API rules](SUBMISSION_CLI.md#rules-for-model-api-use-restricted-mode) for the accounting of
failed or retried requests. Model calls use the organizer-supplied endpoint; participant vendor
API keys are not supported. Platform availability and deployed enforcement will be announced
separately.

---

## Submission format

### The `forecast` verb

Your Docker agent must implement:

```bash
forecast --panels /input/panels --text /input/text --asof YYYY-MM-DD --out /output/forecast.parquet
```

`forecast` is the **container command**: the harness runs
`docker run <image> forecast --panels … --text … --asof … --out …`, so it arrives as the first
argument after the image reference. Your image must either expose `forecast` as an executable on
`PATH` (build with no `ENTRYPOINT`), or, if you set an `ENTRYPOINT`, have the program it names
accept `forecast` as a leading positional argument. An image that ignores the verb exits 2 on
every unit before reading any input. The full contract is [`SUBMISSION_CLI.md`](SUBMISSION_CLI.md).

> **Status (2026-08-27): the reference implementation ships in this repo — and its image does not
> run yet.** The paragraph that used to sit here said there was no reference `forecast` CLI, no
> `argparse` entry point, no `__main__`, no `[project.scripts]` and no `Dockerfile`. All five were
> true when it was written and none of them is true now, so do not start from scratch:
>
> - `qfbench2_track_forecasting/cli.py` implements the verb above, with a `__main__` guard;
> - `pyproject.toml` declares `[project.scripts] forecast = "qfbench2_track_forecasting.cli:main"`;
> - the repo-root `Dockerfile` builds an image that puts `forecast` on `PATH`.
>
> Run it locally and it works end to end. Measured 2026-08-27 against the exemplar unit:
>
> ```bash
> python -m qfbench2_track_forecasting.cli \
>   --panels units/t2-EXAMPLE-ust-curve-1m/panels/ \
>   --text   units/t2-EXAMPLE-ust-curve-1m/text/ \
>   --asof 2024-06-28 --out out/forecast.parquet
> # wrote forecast.parquet, forecast_meta.json and forecast_rationale.md to out
> #   4 asset(s) x 1 horizon(s), 500 draws
> ```
>
> then `python scoring/scoring.py score --card units/t2-EXAMPLE-ust-curve-1m/card.toml --forecast
> out/forecast.parquet` reports `"admissible": true` with g0-g3 all `"pass"`.
>
> That `--panels` path does not exist: the exemplar keeps its panel at the unit root
> (`rates_daily.parquet`) rather than under `panels/`. The reference CLI falls back to the parent
> directory when `--panels` holds no `.parquet`, which is why the command above still runs — but a
> staged unit really does ship `panels/`, so keep passing `/input/panels/`.
>
> The image installs the shared toolkit itself, so `docker build` followed by
> `docker run --rm <image> forecast --help` works with no extra steps. If you build your own image
> from scratch, carry a `qfbench2-common` line into it — `qfbench2_track_forecasting.limits`
> imports the toolkit, so an image without it builds cleanly and then fails at run time. Note that
> `python:*-slim` images ship no `git`, so the `git+https://` form used above needs
> `apt-get install git` first; the `Dockerfile` here uses the tarball URL instead.
> `units/t2-EXAMPLE-ust-curve-1m/run_example.sh` drives the same pipeline through the Python API
> and also runs offline.

- `--panels /input/panels` — read-only mount of Parquet panel files; no row with `date > asof` is accessible
- `--text /input/text` — read-only mount of the text corpus; all documents have timestamp ≤ asof
- `--asof` — the information cutoff date; your agent may not use any data or text after this date
- `--out` — output path for the forecast file

The agent may use any combination of LLM reasoning over text and time-series forecasting component (statistical or neural). The agent's reasoning is internal — only the forecast output file is scored.

The reference CLI reads `[targets].target_type` from the card. For `level`, it keeps the last
observed level as the forecast centre. For `log_return`, panel rows are decimal daily simple returns
`r`, and the target is the cumulative future log return, `sum(log(1 + r))`, over the horizon.
The walk starts at zero, its centre is the historical mean of `log(1 + r)` multiplied by the horizon,
and its spread uses those log-return steps, scaled by the square root of the horizon. It retains
the estimated dependence across assets. The generated
rationale records the anchor, drift and spread. Earlier CLI revisions applied the level rule to
both target types; regenerate reference outputs for return cards when updating from those revisions.

### Output file: forecast.parquet

| Column | Type | Description |
|--------|------|-------------|
| `draw` | int32 | Sample index, 0-indexed |
| `asset` | string | Asset ID exactly matching `card.toml [targets] asset_ids` |
| `horizon` | int32 | Authored horizon key, unchanged (e.g., 21); see monthly periods below |
| `value` | float64 | Forecasted value in stated unit (e.g., % per annum for yields) |

**Monthly targets:** use the task's explicit observation period to determine monthly steps,
including the gap from the last available panel observation. Preserve the output horizon key.
See [Monthly target periods](docs/MONTHLY-HORIZONS.md) for the mapping and synthetic example.

Minimum `n_draws` is **200**. Recommend 500+. For F4 (tail-from-text) cards: recommend 1,000+
for reliable tail quantile estimates.

For joint cards (F3, F4), every draw index must have rows for ALL target assets and horizons.
Do not submit draws generated independently per asset — the joint score checks for co-movement.

### Required metadata file: forecast_meta.json

```json
{
  "unit_id": "t2-F3-ust-curve-2024Q1",
  "asof": "2024-01-02",
  "asset_ids": ["UST_2Y", "UST_5Y", "UST_10Y", "UST_30Y"],
  "horizons": [21, 63],
  "representation": "samples",
  "n_draws": 500
}
```

`unit_id` and `asof` must match the card's `card.toml` exactly — `unit_id` is compared against
`[task].id`. Gate g1 (schema check) fails immediately if they do not.

The key is **`unit_id`**, not `card_id`. `forecast.schema.json` lists `unit_id` among its
required keys and `bind_metadata` reads `meta["unit_id"]`; a sidecar that spells it `card_id`
is read as declaring no unit at all and is refused with `SCHEMA_INVALID` on every unit. The
scorer's *output* does use `card_id` (see the example further down) — that is a different
document, written by us, and the two names are not interchangeable.

### Required deliverable: forecast_rationale.md

Write `forecast_rationale.md` next to your `forecast.parquet`. It is **required** — gate g1
fails a submission that omits it or ships it blank — and it is **never scored**.

The gate learns exactly one bit about the file: whether it contains any non-whitespace
character. It never reads what you wrote, and no other gate or scoring path touches it. Nothing
in this file can move your composite score or your rank.

It exists for a human reviewer. Say what your forecast is, what drove it — in particular what
the text corpus contributed, if anything — and what would change it. There is no length
requirement and length is not evidence of anything: see [`docs/RATIONALE-REVIEW.md`](docs/RATIONALE-REVIEW.md)
for what reviewers do and do not treat as a signal.

`units/t2-EXAMPLE-ust-curve-1m/run_example.sh` writes a worked example of all three files.

### Output folder rules

Everything your agent leaves in `/output` is checked, not only the three files above. After your
process exits, the organizers' output checker reads the whole tree and refuses it if it has any
of these:

- more than 256 files, more than 4,096 files and folders together, or a folder nested 8 or more
  levels deep, even an empty one (a file can sit at most seven folders down, as in
  `/output/a/b/c/d/e/f/g/file.txt`);
- a symbolic link (even one pointing inside the folder), a hard link, or a special file such as a
  named pipe or socket;
- a file with a setuid, setgid or sticky bit;
- a file larger than 64 MiB, more than 64 MiB in total, or a file more than 64 times larger than
  the disk space it occupies (a heavily sparse file);
- two file paths that differ only in letter case or Unicode form (`Notes.txt` and `notes.txt`), a
  name that is not valid UTF-8 or not in Unicode NFC form, a name with a backslash or a control
  character, or a name directly in `/output` that starts with a letter and a colon (such as
  `C:data`);
- no files at all (empty folders do not count).

In Development, a refused tree scores the unit `no_output` when your process exited 0. A non-zero
exit is scored `container_crashed`, or `resource_timeout` / `resource_oom` if the run was stopped
for time or memory, whatever the tree holds. The 64 MiB limits are the same in the Final.

---

## How the scoring works

### 1 — Marginal CRPS (50 % weight)

For each (asset, horizon) pair, the CRPS (Continuous Ranked Probability Score — a number
that rewards being both accurate *and* honest about uncertainty; lower is better) is computed
from your draws against the single realized value. The average across all pairs is the
marginal CRPS.

CRPS penalizes both overconfidence (too narrow — draws cluster away from the realized value)
and over-dispersion (too wide — draws spread so far that the score suffers from the second
term of CRPS). See `docs/CONCEPTS.md` for a worked numerical example.

### 2 — Joint variogram score (30 % weight)

Measures whether your draw matrix captures relationships between assets. If you sample each
asset independently, the pairwise distances between asset draws will be systematically too
large compared to the pairwise distances between realized values. The variogram detects this
mismatch. Lower is better. Most important for F3 (cross-asset reasoning) cards.

### 3 — Tail penalty (20 % weight)

Mean pinball loss at the 1st, 5th, 95th, and 99th percentiles. A model that misses a rate
shock or macro surprise will pay a massive tail penalty. Lower is better. Most important
for F4 (tail/shock-from-text) cards.

### Text ablation (a separate experiment, not scorer output)

A **text ablation** compares your agent with and without its text input, keeping the numerical
method and evaluation conditions the same. On a labeled development dataset you are permitted
to use, compare both forecasts against the same known outcomes. A lower composite for the full
agent is evidence that text helped on that dataset; beating a different numeric baseline alone
does not isolate the contribution of text.

The published scorer does not emit `information_uplift` or `text_ablation_delta`, and the
submission interface has no separate ablated-forecast slot. Treat ablation as an experiment you
run and report separately. The public practice units do not provide realized references: on
those inputs, local checks can establish admissibility and changes in predictions, not accuracy.

### Running the scorer locally

```bash
# 1. The shared toolkit, pinned.
# Pin toolkit v2.6.0 for the current submission commands and model-free fixture.
# The installed package reports version 2.6.0.
pip install "qfbench2-common[data] @ git+https://github.com/Agenthon-2026/Agenthon2026-public.git@v2.6.0#subdirectory=common"

# 2. This track's package, from the repository root. Without it neither the reference CLI nor
#    the smoke scorer can import `qfbench2_track_forecasting`, and both stop at an ImportError
#    before they parse a single argument. It also brings in pandas and pyarrow.
pip install .

# Gates only -- this is what a participant can run. Realized outcomes are sealed and are
# NOT shipped in this repository, so there is no --realized file to point at locally.
python scoring/scoring.py score \
  --card units/t2-EXAMPLE-ust-curve-1m/card.toml \
  --forecast /path/to/your/forecast.parquet
```

The scorer expects `forecast_meta.json` and `forecast_rationale.md` next to your
`forecast.parquet`. Passing `--realized <parquet>` adds the score, but you supply that file:
nothing under `data/realized/` exists here, and `units/t2-EXAMPLE-ust-curve-1m/run_example.sh`
states the reason -- "no realized outcomes are shipped publicly". Without it you get the
admissibility gates only (no score), which is the check that matters before submitting.

This is what the command above actually prints — no metrics, and two keys that say so. Reproduced
verbatim 2026-08-27 against the exemplar unit:

```json
{
  "card_id": "t2-EXAMPLE-ust-curve-1m",
  "admissible": true,
  "gates": {
    "g0_integrity": "pass",
    "g1_schema": "pass",
    "g2_cutoff_resource": "pass",
    "g3_domain_semantics": "pass"
  },
  "scored": false,
  "note": "no --realized supplied: gates only, no score"
}
```

Supplying `--realized` replaces `scored` and `note` with the metrics. The numbers below come from
one run against a hand-made reference file and mean nothing on their own; the **keys** are the
point, because an earlier revision of this block advertised `assets_scored` and `horizons_scored`,
which the scorer has never emitted, and omitted `normalization_mode`, `rankable` and `cell_count`,
which it always does:

```json
{
  "card_id": "t2-EXAMPLE-ust-curve-1m",
  "admissible": true,
  "gates": {
    "g0_integrity": "pass",
    "g1_schema": "pass",
    "g2_cutoff_resource": "pass",
    "g3_domain_semantics": "pass"
  },
  "failure_labels": [],
  "normalization_mode": "raw_unrankable",
  "rankable": false,
  "marginal_crps": 0.15974256368939124,
  "joint_variogram": 0.37771455294457157,
  "tail_penalty": 0.03721824163617158,
  "tail_metric": "pinball",
  "composite_score": 0.2006292960553014,
  "n_draws": 500,
  "cell_count": 4
}
```

`"rankable": false` is not a defect in your submission: this CLI grades against `card.toml` with
no reference scale, so its composite is raw and not comparable across units. The identity key in
**both** of these outputs is `card_id` — that is the scorer's own vocabulary for its own report,
and it is not the `unit_id` your `forecast_meta.json` must declare.

---

## Smoke scorer (quick sanity check)

Run the smoke scorer before the full end-to-end test. It needs both installs from
[Running the scorer locally](#running-the-scorer-locally) — the toolkit **and** `pip install .`
for this repository:

```bash
qfbench2-smoke units/t2-EXAMPLE-ust-curve-1m/ out/ --track forecasting
```

This runs admissibility gates g0–g3 without requiring realized outcomes. A green smoke run
means your submission will not DNF on structural grounds.

The output directory is `out/`, which is where the reference CLI above writes. Pointing it at a
directory nothing has written — `output/`, as this line used to read — reports
`admissible=False labels=['shared.schema.invalid_output']` and creates nothing, which looks like
a failing submission rather than a mistyped path.

---

## Running your Docker agent end-to-end

The command below is the **local smoke run** (`--network=none`; fully offline — model-API
calls will fail, which is fine for a structural test). At official scoring time the harness
runs the same container on the internal eval network instead, with the proxy environment
described in "Network contract and submission categories" above.

```bash
docker build -t my-reasoning-agent:latest .

# The harness grants 16 vCPU / 128G per unit. Docker refuses a --cpus value above the
# cores your machine actually has, so lower both for a local smoke run — they are limits,
# not reservations, and nothing about the forecast depends on them.
docker run --rm \
  --network=none \
  --cpus=4 \
  --memory=16g \
  -v $(pwd)/units/t2-EXAMPLE-ust-curve-1m:/input:ro \
  -v $(pwd)/output:/output \
  my-reasoning-agent:latest \
  forecast --panels /input/panels --text /input/text --asof 2024-06-28 --out /output/forecast.parquet

python scoring/scoring.py score \
  --card units/t2-EXAMPLE-ust-curve-1m/card.toml \
  --forecast output/forecast.parquet
```

**The unit directory itself is mounted at `/input`** — that is the harness contract
([`SUBMISSION_CLI.md`](SUBMISSION_CLI.md): `-v <unit-dir>:/input:ro`), so `/input/panels/` and
`/input/text/` are subdirectories of the mounted unit, not separate mounts. Earlier revisions of
this block mounted `units/t2-EXAMPLE-ust-curve-1m/input/panels` and `.../input/text`; no unit in
this repository has an `input/` directory, so Docker created the missing sources rather than
erring and the container saw two empty mounts. Measured 2026-08-27: with those two mounts the
reference image exits with `card.toml not found in /input/panels or /input`; with the single
`-v <unit-dir>:/input:ro` above it writes a forecast that passes g0-g3.

For local smoke runs, `--network=none` is the recommended flag: it guarantees your agent
cannot accidentally depend on live data. Production scoring uses the restricted network —
model APIs reachable through the audited proxy, everything else blocked — so an agent that
passes offline structurally and only adds model-API calls on top will behave identically.

---

## Inheriting the shared toolkit

Install the `qfbench2-common` package (schemas, scoring, leakage guard) from the public
repository that publishes it, `Agenthon-2026/Agenthon2026-public`:

```bash
pip install "qfbench2-common[data] @ git+https://github.com/Agenthon-2026/Agenthon2026-public.git@v2.6.0#subdirectory=common"
```

The toolkit is half of what you need. Running the scorer or the exemplar also requires this
repository itself — `pip install .` from the repository root — which is what brings in pandas and
the rest. See the Quick-start checklist, step 0.

**Pin the tag, and pin this one.** `v2.6.0` is the tag whose descriptor contract matches what the
evaluation verifier accepts. Two earlier tags fail in opposite directions. `v2.3.1` carries
`qfbench2_common.contracts` — earlier tags predate it entirely — but it **refuses a descriptor the
verifier accepts**: it demands at least one `models` entry, while the current contract allows
`"models": []`. Building against it means your own tools reject work that would have scored.
`v2.4.2` has the quieter failure: its category enum still contains `byo-large` and `byo-small`, so
it **packs a descriptor the 2026-09-18 ruling made invalid** — nothing warns you, the upload is
held at intake, it never runs, and it still costs you one of your Development attempts. Tags from
`v2.4.4` on close that enum to `api` and `simulator`, and `v2.6.0` validates a card without
`[metadata].difficulty`. `v2.6.0` is also the tag `.github/workflows/ci.yml` installs and the tag
the reference image in `Dockerfile` builds on, so what you verify locally is what CI verifies.

Do not install from a branch. An unpinned toolkit is how a local result and a scored result come
to disagree without either side noticing.

Everything in this repository that does not need the toolkit — `units/`, `baselines/`,
`templates/`, the card and schema documentation — is usable without it.

---

## Firewall: what is sealed

The following are NOT available to participants during the competition:

- **Realized outcomes for the held-out evaluation window (H2 2025 – Q2 2026).** Scores are
  computed server-side. Results are released after the competition closes.
- **The official baseline's per-card normalization scale files** (`reference/ref_scale.json`).
  Each one holds the error that the text-blind baseline expects to make on that card, computed
  from the card's inputs before the outcome exists, so it says nothing about the outcome. No card
  released to participants carries one, and the scorer refuses to read a scale from anywhere but a
  card's `reference/` directory. The **method** that produces them is published in full, so on a
  released card you can compute the values yourself: see [docs/M0-BASELINE.md](docs/M0-BASELINE.md).
  A sealed card's inputs are sealed, so its scale is too.
- **The exact card IDs, as-of dates, and asset combinations for the sealed evaluation set.**
  You know the four families and the four panels, but not which specific cards appear.
- **The EM FX panel** used for F2 (Text-cued regime shift with transfer) cards. G10 FX is in
  training; EM FX is the transfer target and is absent from all input panels.
- **Regime event labels for F4 cards.** The harness knows which cards are tail/shock cards,
  but specific event dates are not pre-announced.

Sealed means the *values*, not the *procedure*. Everything about how the baseline is built — the
window, the differencing, the gap and alignment rules, the horizon conversion, the covariance
structure, the draw count, the per-card seed and the exact formulas for its expected error — is
specified in [docs/M0-BASELINE.md](docs/M0-BASELINE.md), so the denominator of your score is not a
black box.

---

## Leakage rules

Leakage — using information from after the as-of date — is the most common reason for DNF.
Four rules are enforced by the harness, at three independent levels:

1. **Panel timestamp rule.** Every panel you are handed is truncated at the as-of date **before it is published**: the organizers read every row of every staged panel and refuse the unit if any row is dated after the as-of. There is no runtime interceptor and there never was — earlier revisions of this document described a `LeakageViolation` exception that exists in no repository, and a guard that does not exist is worse than an acknowledged gap, because you would have planned around it. What protects the cutoff is the publication gate, not your process.
2. **Text corpus timestamp rule.** Every document in the text corpus has a timestamp ≤ the card's as-of date; the organizer's staging gates (`cutoff.scan_text_corpus_cutoff`) enforce it before a unit ships, and gate g2 at scoring time binds your declaration to the trusted card and checks the card's own cutoff — it does not rescan the corpus. A unit whose corpus carried a post-as-of document would never ship. Your agent may not fetch new text at inference time — the restricted network permits model-API calls only, and vendor-side tools (web search, retrieval) must be disabled.
3. **No external data at inference time.** The restricted network blocks everything except the audited model-API proxy; every connection is logged and audited. Local smoke runs use `--network=none`, which blocks all network calls outright.
4. **Weight freeze.** Model weights must be frozen at image build time. The harness records the Docker image digest.
### One more rule, and it is not one of the enforced ones

**No cross-unit lookup.** Your agent must forecast each unit from the inputs it is handed **for
that unit**. You may not bake into your image — as a table, as weights, or in any other form — a
value for one unit's target that you obtained from another unit's panel, or from any source that
reveals a target. Training or tuning on the published practice data is fine; **carrying a specific
unit's answer into the run is not.**

**Nothing detects this, and we are saying so rather than letting you assume otherwise.** The gate
stack is g0–g3; there is no g4, and none of the four gates above looks for it. Treat it as a rule
of the competition that we are asking you to keep, not as one the harness enforces — and read it
knowing your competitors are reading the same paragraph.

The rule exists because the practice cards are not mutually independent. They are drawn from the
same few underlying series and each panel is truncated only at **its own** as-of date, so a card
with a later as-of can carry a value that is another card's target. Dropping the answer files does
not help, because the exposure is in the panels, not in the answers.

Measured 2026-08-28, at full strength — the sealed `realized.parquet` value matched exactly
against another unit's published panel row at the same `(asset, target_date)`:

| | |
|---|---|
| public units shipping a panel | 103 |
| of those, units whose **every** realized value appears exactly in a sibling unit's panel | **75** |
| splits affected | 52 `validation`, 23 `public-dev` |

The mechanism, without the worked example: a practice unit's target is an `(asset, target_date)`
pair, and a sibling practice unit's published panel often carries a row for that same asset on that
same date, to the same precision. Nothing has to be inferred — the value is simply present in the
other folder.

Nor is the sibling panel the only route: these are historical series, so the same figures are
reachable from public data sources without touching the kit at all. That is the deeper reason a
practice score is a pipeline check rather than a skill signal.

The consequence is under "Practice tasks" above: **the Development leaderboard is practice, not a
ranking.** The sealed evaluation set is a different, later window. **No practice panel reaches any
target in it.** That is a measurement, not an assurance: we run it at every strength — does a
practice panel carry the asset far enough to touch the target date, does it hold a row at exactly
that (asset, date), does that row's value equal the sealed one — and we re-run it as the sealed set
is finalized, rather than treating one clean result as settled.

The current run: **0 exposed**, pooling all 148,680 `(asset, date, value)` rows from every
published panel against every sealed answer that exists today. The honest scope of that number is
that only a small fraction of the sealed units have a resolved outcome yet; the rest resolve in
the
future and cannot be checked until they do. The re-run before the Final bundle is the one that
covers them, and it is the run that matters. So a lookup table built from the
practice data is worth exactly zero on it, and the Final phase gives you one submission to discover
that.
Within the joint Final + Verification phase, organizers rerun the top of the Final board on
fresh seeds and resamples with reproducibility and disclosure checks. This does not require
a separate participant Verification submission.

---

## Resource limits

Development applies each card's CPU, memory, GPU and network settings. The cards supply no
per-unit timeout, so the launcher uses its 1,800-second fallback.

| Resource | Development setting per unit |
|----------|-------------------------------|
| CPU quota | 16 CPUs; not exclusive cores |
| Memory | 128 GiB (`memory = "128G"`); swap disabled |
| GPU | `gpu = true`, available for permitted local code |
| Container clock | 1,800 seconds, including creation and an image pull when needed |
| Network | `restricted` — the organizer's model route only, never data fetching |

The platform gives the ingestion stage **43,200 seconds (12 hours)** to run the units
sequentially; scoring has its own stage clock. The per-unit clock, platform clock or House
window can end a run first. The planned House timing release activates each unit once when the organizer begins that unit's execution setup. Queue waiting and earlier units do not spend its own
window; setup/provisioning and container creation/execution after activation can. Its fixed end
is capped by the card/fallback unit ceiling and the remaining actual ingestion-stage time.
Restarting or retrying under the same allocation resets neither that window nor request counters.
Deployment and verification remain required before opening. No compute allowance grows, and
these Development settings do not certify Final resources or promise every unit its full ceiling.

The `api` category denotes House model access; it does not remove the card's GPU grant for
permitted local code. A GPU grant does not authorize an additional model server. Service
availability is announced separately.

Include dependencies and permitted artifacts in the image before submission. Cold image pulls
consume the unit clock; previously reported pull timings are historical observations, not a
current startup guarantee. See the
[Development runtime guide](https://github.com/Agenthon-2026/Agenthon2026-public/blob/main/docs/DEVELOPMENT-RUNTIME.md)
for process, temporary-space and output limits, and the
[image submission guide](https://github.com/Agenthon-2026/Agenthon2026-public/blob/v2.6.0/docs/IMAGE-SUBMISSIONS.md)
for anonymous public pulls and organizer-confirmed private mirrors. The writable image layer,
temporary filesystem and output mount are separate; do not infer an image-size quota or a
writable workspace allowance from a card's memory or disk field.

The Final cannot run an image that declares a Docker `VOLUME`, including one inherited from its base
image. Such an upload is marked Failed when its run starts and does not use an attempt; remove the
`VOLUME` (or choose another base image) and upload again.

---

## Quick-start checklist

0. **Install both packages first.** The toolkit alone is not enough — this repository's own
   dependencies (pandas among them) come from `pip install .`, and without it step 3 fails with
   `ModuleNotFoundError: No module named 'pandas'`:
   ```bash
   pip install "qfbench2-common[data] @ git+https://github.com/Agenthon-2026/Agenthon2026-public.git@v2.6.0#subdirectory=common"
   pip install .
   ```
1. Read `docs/CONCEPTS.md` — understand CRPS, variogram, tail penalty, text ablation, and leakage.
2. Read `docs/CATEGORIES.md` — understand what each card family (F1–F4) tests and the role of text in each.
3. Run the exemplar end-to-end:
   ```bash
   cd units/t2-EXAMPLE-ust-curve-1m && bash run_example.sh
   ```
4. Build your agent image; verify it writes a valid `forecast.parquet`, `forecast_meta.json`
   and a non-blank `forecast_rationale.md`.
5. Run the smoke scorer against the exemplar card.
6. Run your agent on the validation cards in `units/` and check that every output is admissible.
   They carry no answers, so this checks form, not accuracy (see "They carry no answers" above).
7. Optionally build a text-ablated variant too. How it compares with your agent shows only on
   the Development leaderboard, after you submit both.
8. Pack and upload: `qfbench2 submission pack --descriptor submission.json --team-number <N> --out submission.zip`,
   then upload `submission.zip` on the track's CodaBench competition page (see
   ["How an upload is made"](SUBMISSION_CLI.md#how-an-upload-is-made)).

## Competition schedule and submission limits

Development runs through **October 12, 2026**. The joint **Final + Verification phase runs
October 13–25, 2026**. Each team makes **one final submission per track**; organizers perform
verification within that same phase, with no separate participant Verification submission.
If two Final submissions finish this track with the same ranking score, the tie is broken in
favour of the one uploaded earlier.
Registration and Development close together on October 12, 2026 at **23:59 Anywhere on Earth (AoE, UTC−12)**. The joint Final + Verification phase closes on October 25, 2026 at **23:59 AoE**. Other competition dates and task/data cutoffs are unchanged.

**Last Development runs start by 20:00 UTC on Monday 12 October 2026.** A scheduled
maintenance window on **Tuesday 13 October 2026, 08:00–12:00 UTC** stops the evaluation fleet,
and new Development runs stop starting twelve hours before it so that every run started by
then keeps its full 12-hour stage clock. The 23:59 AoE close on 12 October is 11:59 UTC on
13 October, inside that window. An upload that has not started by 20:00 UTC on 12 October,
whenever it was made, is not run; a run starts only when a worker is free, so upload well
before that evening. An upload made during the window shows `Submitting` until 12:00 UTC and
is not run. The window changes nothing about scoring, limits or the submission contract
([issue #18](https://github.com/Agenthon-2026/track2-forecasting-public/issues/18)).

At the participant Development opening, Track 2 allows **5 uploads per team per day**
and **20 total uploads per team for this track during Development**. Use your team's single
designated CodaBench account. Local validation and packaging use no attempts; held or cancelled
uploads still count. An upload the platform marks `Failed` does not consume an attempt — the platform's
daily count excludes it. See [submission limits](SUBMISSION_CLI.md#development-submission-limits).
