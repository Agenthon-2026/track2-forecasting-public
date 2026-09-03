# Track 2 — Reasoning-Augmented Time-Series Forecasting (Participant Guide)

## Executive summary (read this first)

Track 2 asks one question: **can an AI agent reason over text AND time-series data to forecast financial markets better than a model that looks only at numbers?**

You submit a **Docker agent** — an LLM-powered reasoning system combined with a forecasting component — that reads two things: multivariate **time-series panels** (rates, FX, macro, factor returns) and a frozen, time-stamped **text corpus** (news headlines, FOMC statements, central-bank speeches, macro-release commentary) available up to the as-of date. It must output a full probability distribution over possible futures, expressed as Monte Carlo draws.

We score your output against sealed realized market outcomes using a **CRPS composite**:

**S = 0.5 × marginal CRPS + 0.3 × joint variogram + 0.2 × tail penalty (lower is better)**

The headline scientific question is the **information uplift**: does adding text make a forecaster better than one that ignores text entirely? Baselines are text-blind time-series foundation models (Chronos, TimesFM, Lag-Llama, MOIRAI, Theta/AutoARIMA). Beat them with reasoning.

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

Accuracy feedback comes from submitting: the Development leaderboard scores you on units you
have not seen. Use the practice units to get *admissible*, and the leaderboard to find out how
good you are.

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

The baseline your score is normalized against is a different thing: it runs organizer-side, it is
not any of these files, and you never see it directly — you see it only through the normalization,
described next.

**Their scores are not published per unit, and this is not an oversight.** A card's score is normalized by the same baseline's components, so a published per-unit baseline score plus a reproducible baseline forecast inverts to the sealed value — most sharply on single-asset cards, which are the majority here. What you get instead is the normalization itself: on every card, **1.0 means "no better than the text-blind baseline"**, so your own leaderboard number already reads as a ratio against them, with no separate table needed.

---

## Network contract and submission categories

### The two network modes

Track 2 units declare `network = "restricted"` in `card.toml [environment]`. There are two
modes you will encounter:

1. **Local development (smoke runs).** Run your container with `--network=none`. Everything
   in this repo — the example card, the scorer, the five text-blind baselines — works fully
   offline. If your agent needs a model API, local runs without network will fail those calls;
   that is expected and fine for structural smoke tests.
2. **Official scoring (`restricted`).** Your container runs on an internal eval network with
   **no open internet**. The only permitted egress is through the organizer's audited proxy to:
   - the organizer-hosted model endpoint (open models served via NIM/vLLM; free, with a
     per-run budget) — **and nothing else**.

   Vendor model APIs (`api.anthropic.com`, `api.openai.com`,
   `generativelanguage.googleapis.com`, any other) are **refused by the proxy** (policy
   2026-08-04). If you need a different model, adapt the house model: ship a LoRA adapter and
   the organizer serves it for you. See "Submission categories" below.

   Every connection is logged (domain, bytes, timestamps). These logs are the audit artifact
   for the verification phase. **Vendor-side tools — web search, code execution, retrieval —
   must be disabled in all API calls.** This is enforced by rule and by audit.

At scoring time your container receives this environment:

| Variable | Meaning |
|----------|---------|
| `HTTP_PROXY` / `HTTPS_PROXY` | Point at the organizer's audited proxy — all egress goes through it |
| `MODEL_ENDPOINT` | The organizer-hosted model endpoint (OpenAI-compatible, e.g. `http://model:8000/v1`), when available |
| `QFBENCH_NETWORK` | `restricted` (or `none` for local smoke runs) |
| `MODEL_NAME` | The model served at `MODEL_ENDPOINT` |
| Your API keys | **None exist.** The harness injects no participant API key and there is no mechanism to supply one (policy 2026-08-04) |

Data and text cutoffs are unchanged: panel and corpus timestamps are enforced by the organizer's staging gates before a unit ships, and gate g2 still binds your declaration to the trusted card. The network
contract does not weaken any leakage rule: model APIs are reachable, market data and live text
are not.

### Submission categories

| Category | What you bundle | Model access |
|----------|-----------------|--------------|
| `api` | Prompts, harness, system prompts, agent code | The house endpoint only, via the proxy |
| `byo-large` / `byo-small` | One LoRA adapter (`adapter_model.safetensors` + `adapter_config.json`) — not weights, and not a model server | The house endpoint only, via the proxy; on a BYO run `MODEL_NAME` names *your adapter* |

**Bring-your-own is adapter-only.** You ship one LoRA adapter, rank ≤ 64 (enforced by the server
at load), and the organizer starts a server on the house base model with your adapter loaded, then
tears it down when your run ends. Full fine-tuning is not permitted, and **there is no
small-weights tier** — `byo-large` and `byo-small` are legacy enum names the descriptor schema
still accepts, and both select this same contract. The full rules, including the local
`vllm serve` recipe for testing your adapter, are under "Bring your own model: adapter-only,
rank <= 64" in [`SUBMISSION_CLI.md`](SUBMISSION_CLI.md).

Every entry is tagged with its category, the models it used (pinned versions), and their
training cutoffs. All categories compete together — there is no separate board per category.

**There is one ranking: the equal-weight mean of your normalized scores across every card,
lower is better.** Each card counts the same regardless of its shape. That is fair because of
a fix one level down. Some cards ask for a single number (one asset at one horizon); others
ask for several at once. The joint-variogram term measures relationships *between* the numbers
you forecast, so on a single-number card it is 0 no matter how good your forecast is — its
weight is redistributed over the terms that do exist (0.714 x CRPS + 0.286 x tail), which puts
the text-blind baseline at 1.0 on both shapes. With both anchored in the same place, one
average is averaging one quantity.

**Every card is in the denominator, and a card you do not score counts against you.** A card
that is inadmissible, errors, or is never attempted takes a pre-committed worst-case value
(**4.0** — four times as bad as ignoring the text entirely, since 1.0 is the text-blind
baseline), and real scores are clipped at that same value. So failing a hard card can at best
*tie* the worst possible attempt at it, never beat it: there is no card you are better off
skipping. The value is not ours to pick — it is the worst end of the declared metric domain in
the signed evaluation plan that governs ranking. See [CONCEPTS.md](docs/CONCEPTS.md) for the
scoring detail.

### Reproducibility rules

- Model versions MUST be pinned (dated snapshots).
- The training cutoff of every model MUST be disclosed in your submission metadata.
- Temperature and seed MUST be pinned where the API supports it.
- `api` entries are verified statistically (bootstrap-CI overlap on rerun); BYO entries
  bit-reproducibly.

### Model-API budget (FINAL, ruled 2026-08-28)

A uniform per-unit model-API budget applies to every submission. The figure is
**1,000,000 input + 100,000 output tokens per unit**, enforced via proxy logs and spot audit.
Whether API keys are sponsor-provisioned or team-provided is TBD pending sponsorship — the
mechanics are identical either way, and both modes are supported.

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

### Output file: forecast.parquet

| Column | Type | Description |
|--------|------|-------------|
| `draw` | int32 | Sample index, 0-indexed |
| `asset` | string | Asset ID exactly matching `card.toml [targets] asset_ids` |
| `horizon` | int32 | Horizon in business days (e.g., 21) |
| `value` | float64 | Forecasted value in stated unit (e.g., % per annum for yields) |

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

### Text uplift (scientific diagnostic, not the ranking)

We also report the **information uplift**: the best text-blind baseline's composite score
minus your composite score on the same cards (lower composite is better). Positive uplift
means your agent extracted useful signal from the text corpus. This is a scientific diagnostic,
not a leaderboard dimension — the ranking uses composite scores only, aggregated as described
above.

We encourage teams to also submit a **text-ablated forecast** (your agent with the text
corpus replaced by an empty corpus). Comparing ablated vs. full scores shows the marginal
value of text within your own system.

### Running the scorer locally

```bash
pip install "qfbench2-common @ git+https://github.com/Agenthon-2026/Agenthon2026-public.git@v2.3.1#subdirectory=common"

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

Run the smoke scorer before the full end-to-end test:

```bash
qfbench2-smoke units/t2-EXAMPLE-ust-curve-1m/ output/ --track forecasting
```

This runs admissibility gates g0–g3 without requiring realized outcomes. A green smoke run
means your submission will not DNF on structural grounds.

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
pip install "qfbench2-common @ git+https://github.com/Agenthon-2026/Agenthon2026-public.git@v2.3.1#subdirectory=common"
```

**Pin the tag, and pin this one.** `v2.3.1` is the first toolkit release that carries
`qfbench2_common.contracts`, which `qfbench2_track_forecasting.scoring` imports at module scope —
earlier tags predate it, so a submission built against one of those dies before it runs a single
gate. It is also the tag `.github/workflows/ci.yml` installs, so what you verify locally is what
CI verifies.

Do not install from a branch. An unpinned toolkit is how a local result and a scored result come
to disagree without either side noticing.

Everything in this repository that does not need the toolkit — `units/`, `baselines/`,
`templates/`, the card and schema documentation — is usable without it.

---

## Firewall: what is sealed

The following are NOT available to participants during the competition:

- **Realized outcomes for the held-out evaluation window (H2 2025 – Q2 2026).** Scores are
  computed server-side. Results are released after the competition closes.
- **The exact card IDs, as-of dates, and asset combinations for the sealed evaluation set.**
  You know the four families and the four panels, but not which specific cards appear.
- **The EM FX panel** used for F2 (Text-cued regime shift with transfer) cards. G10 FX is in
  training; EM FX is the transfer target and is absent from all input panels.
- **Regime event labels for F4 cards.** The harness knows which cards are tail/shock cards,
  but specific event dates are not pre-announced.

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

The current run: **0 exposed**, pooling all 146,692 `(asset, date, value)` rows from every
published panel against every sealed answer that exists today. The honest scope of that number is
that only **12 of the 123** sealed units have a resolved outcome yet; the rest resolve in the
future and cannot be checked until they do. The re-run before the Final bundle is the one that
covers them, and it is the run that matters. So a lookup table built from the
practice data is worth exactly zero on it, and the Final phase gives you one submission to discover
that.
The Verification phase reruns the top of the Final board on fresh seeds and resamples with
reproducibility and disclosure checks.

---

## Resource limits

Caps are per unit and come from each card's `[environment]` block, which the harness
enforces. Cards are organizer-authored, so there is no tier to request — but since the
2026-08 caps change **every Track 2 card grants the same sandbox**, and there is no
separate "typical" case:

| Resource | Every Track 2 card grants |
|----------|---------------------------|
| CPUs | 16 |
| Memory | 128 GB (`memory = "128G"`) |
| GPU | `gpu = true` (see below) |
| Wall time | 1800 s per unit — but see the phase budget below |
| Network | `restricted` — the audited model-API proxy only, never data fetching |

Exceeding wall time or memory causes DNF.

**1800 s is a per-unit ceiling, not a budget you can spend.** Units run strictly one after
another inside a single submission, and the *phase* has its own clock that binds first: the
Development phase allows **43 200 s (12 h) for the whole submission**, Final and Verification
86 400 s (24 h). Over ~100 units that averages a little over **400 s per unit** on Development
— design against the phase budget divided by the unit count, not against 1800 s per card, or
you will be cut off partway through the set with the remaining units unscored.

**The clock starts at `docker create`, so it covers pulling your image**, not just process
start-up. On this fleet a cold pull has measured 90–187 s against roughly 15 s warm, and it is
billed to the same per-unit budget as your solve. Keep your image small: under the adapter-only
BYO rule it carries a LoRA adapter, not model weights, so there is no reason for it to be large.

**On the GPU.** Every card declares `gpu = true`, but your own code has no use for it in either
category: an `api` submission does not touch it, and on a BYO run the worker's GPU is what serves
the base model your adapter is loaded onto — your code still calls `MODEL_ENDPOINT` over the
proxy. Whether a physical device is attached is a property of the worker your submission lands on,
not of the card, so **make sure your image still starts when no device is present**. No scored
component of Track 2 measures hardware ([docs/NVIDIA-STACK.md](docs/NVIDIA-STACK.md)).

---

## Quick-start checklist

1. Read `docs/CONCEPTS.md` — understand CRPS, variogram, tail penalty, text uplift, and leakage.
2. Read `docs/CATEGORIES.md` — understand what each card family (F1–F4) tests and the role of text in each.
3. Run the exemplar end-to-end:
   ```bash
   cd units/t2-EXAMPLE-ust-curve-1m && bash run_example.sh
   ```
4. Build your agent image; verify it writes a valid `forecast.parquet`, `forecast_meta.json`
   and a non-blank `forecast_rationale.md`.
5. Run the smoke scorer against the exemplar card.
6. Score your model against the validation cards in `units/`.
7. Optionally run the text-ablated variant and compare scores.
8. Submit your image digest to the leaderboard portal.
