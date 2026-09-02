# QFBench 2.0 — Published Submission CLI Contract (`interface_version = 2.0`)

A submission is a **Docker image**. The organizer runs it in the sealed scoring environment;
the image must implement the track verb below. The harness invokes the image, the image reads
from a read-only input mount, writes to an output mount, and **exits 0** on success.

```
docker run --rm \
  --network=none|qfb2-eval \             # "none" (simulation) or the internal eval network (agent tracks) — see "Network modes"
  --cpus=<card.cpus> --memory=<card.memory> [--gpus all] \
  -v <unit-dir>:/input:ro \              # read-only inputs — the UNIT DIRECTORY itself is mounted at /input
  -v <run>/output:/output \              # outputs (deliverables + logs); a normal read-write bind
  [-v <run>/output:/app/output] \       # T1 ONLY: the same host dir, also at the QFBench path (see invariant 8)
  <SUBMISSION_IMAGE> <verb> [args]
```

**The verb is the container command.** It arrives as the first argument after the image
reference, so your image must either resolve it from `PATH` (build with no `ENTRYPOINT` — the
Track 3 reference baseline does this, shipping `simulate` and `simulate-batch` as executables)
or consume it as a leading positional (the `ENTRYPOINT ["python", "agent.py"]` pattern, where
`agent.py` declares `parser.add_argument("verb")`). An image that does not accept the verb fails
every unit — as `127` if the verb is not on `PATH`, as `126` if it is present but not executable,
or as whatever your own argument parser exits with if it consumes and rejects it. All three are
recorded as **your** failure, not an organizer fault, and score zero on that unit.

The harness logs `sha256(image)` (anti-cheat), enforces
`card.environment.{cpus,memory,gpu,timeout,network}`, and mounts only files whose `manifest.json`
checksum matches. `LABEL qfbench2.interface_version="2.0"` is required on the image.

## Network modes (per unit card, `[environment].network`)

There are exactly two network modes; every unit card declares one. **There is never open
internet** in official scoring.

| Mode | Who | Meaning |
|---|---|---|
| `none` | **Simulation (T3)** | Fully offline (`--network=none`). Exactly the historical closed-resource behavior; any attempted outbound connection fails the run. |
| `restricted` | **Agent tracks (T1 coding, T2 forecasting, T4 analysis)** | No open internet. Egress **only** through the organizer's audited proxy to the **organizer-hosted model endpoint** given by `MODEL_ENDPOINT` (open models, free to use, per-run budget). Every connection is logged (domain, bytes, timestamps); the log is the audit artifact for the verification phase. |

> ### ⚠️ Agent tracks: there is no third-party model-API access
>
> Read this before you design your agent. (Track 3 is unaffected — it runs fully offline.)
>
> The proxy allowlist contains the organizer-hosted endpoint and **nothing else**. Calls to
> `api.anthropic.com`, `api.openai.com`, `generativelanguage.googleapis.com` or any other vendor
> API **will be refused by the proxy**, and there is no route around it: the eval network is
> `--internal`, so the proxy is the only path off the host.
>
> Your two supported options are therefore:
>
> 1. **House endpoint** — call `MODEL_ENDPOINT` with `MODEL_NAME`. Free, metered per run.
> 2. **Bring your own adapter** — ship a LoRA adapter; the organizer serves it on the house base
>    model and you still call `MODEL_ENDPOINT`. Nothing is fetched at run time. Bringing your own
>    *weights* is not a supported option — see "Bring your own model" below.
>
> **No participant API keys exist.** The harness injects none and there is no mechanism for a
> submission to supply one, so a vendor key would have nothing to reach even if you had one.

Data and text cutoffs are unchanged: enforced by the organizer's staging gates before a unit ships, with gate `g2_cutoff_resource` binding your declaration to the trusted card
in both modes — network access is for **model calls only**, never for fetching data.

### Submission categories (agent tracks only)

Track 3 (simulation) sits outside these categories: submissions are simulators and the network
stays `none`. For the agent tracks, every submission declares one category in `submission.json`:

| Category | What you bundle | Model access | Compute tier |
|---|---|---|---|
| `api` | prompts / harness / system-prompts / agents (your contribution is the scaffolding) | the **house endpoint only**, via the proxy | CPU |
| `byo-large` / `byo-small` | one LoRA adapter: `adapter_model.safetensors` + `adapter_config.json`. **Not model weights, and not a model server.** | the **house endpoint only**, via the proxy — on a BYO run `MODEL_NAME` names *your adapter* | CPU for your code; the worker's GPU serves the base model |

**`byo-large` and `byo-small` mean the same thing.** They are legacy enum names from before the
adapter rule. The `submission.json` schema still accepts both and will not reject either, so the
descriptor stays valid whichever you write — but **there is no small-weights tier**, and both
select the same contract: one adapter, rank ≤ 64, served on the organizer's base.

### Bring your own model: adapter-only, rank ≤ 64

**The shape.** Your submission ships **only a LoRA adapter** — never model weights, and never a
model server. The organizer runs the base for you: when your submission is evaluated, a dedicated
server is started *for that submission*, on the same base model that sits behind `MODEL_ENDPOINT`,
with your adapter loaded at launch, and it is destroyed when your submission finishes.

1. **Ship the adapter as `adapter_model.safetensors` + `adapter_config.json`** in your image.
   **Exactly one adapter per submission.** Keep the two files together in one directory you can
   relocate with a single line; the directory the pair must sit in arrives with the submission
   instructions. Your image never runs a model server, and gets much smaller for it.
2. **Extraction is static.** The adapter is copied out of your image without executing any of your
   code, and the server starts with it already loaded. Before any unit runs, the server must list
   your adapter as a served model — an adapter that fails to load fails the submission right
   there, cheaply and with a named reason. An over-cap adapter is refused at load:
   `LoRA rank 128 is greater than max_lora_rank 64`.
3. **At run time your code sees the same contract as an `api` submission:** call `MODEL_ENDPOINT`
   (OpenAI-compatible) with `MODEL_NAME`, which on a BYO run names *your adapter*, so every call
   routes through it. There is nothing for you to start, configure, or connect to; no server
   lifecycle is yours.
4. **Teardown is automatic.** The server and the extracted adapter are destroyed with your
   submission's run. Nothing persists between submissions.

**Build rules:**

- **Rank ≤ 64.** Enforced by the server at load, not penalised later.
- **Declare `target_modules` accurately** in `adapter_config.json`; it is read.
- **Full fine-tuning is not permitted.** A full fine-tune cannot be verified as derived from the
  base model by any available means, so the choice is between a rule that is enforceable and one
  that is decorative.
- **There is no small-weights tier.** `byo-small` / `byo-large` are legacy descriptor enum names;
  BYO means bring your own **adapter**.
- **During a BYO run the worker's GPU serves the base model.** Plan your own code as CPU plus API
  calls — your GPU use *is* the model serving.

**Testing your adapter locally** — this is the one place you run a server yourself:

```
vllm serve <base> --enable-lora --max-lora-rank 64 --lora-modules mine=<adapter-dir>
```

vLLM 0.28.0 accepts exactly `(1, 8, 16, 32, 64, 128, 256, 320, 512)` for `--max-lora-rank`, and
the **default is 16** — without the flag you will hit a much tighter cap and may conclude your
adapter is broken when it is not.

**Why rank is the number that matters:** it sets how much an adapter can change the base. On a
4096-wide layer, rank 64 carries about 3 % as many parameters as the matrix it adapts, against
100 % for a full fine-tune — low enough that the model underneath is unambiguously the house base
model, high enough for real domain adaptation.

### Container environment contract (`restricted` mode, set by the harness)

| Variable | Value |
|---|---|
| `HTTP_PROXY` / `HTTPS_PROXY` | the audited egress proxy. **Read these from the environment; never hardcode a proxy host** — the address is an operational detail and it has changed. Most HTTP clients honour them automatically |
| `NO_PROXY` | hosts that must bypass the proxy |
| `MODEL_ENDPOINT` | the organizer-hosted OpenAI-compatible endpoint. This is the **only** model API you can reach |
| `MODEL_NAME` | the pinned house-model id served at `MODEL_ENDPOINT` (use it in your client calls; published with the model pin) |
| `QFBENCH_NETWORK` | `restricted` (or `none` for simulation / local fallback) |

### Rules for model-API use (`restricted` mode)

1. **Vendor-side tools OFF.** Web search, code execution, retrieval, and any other vendor-side
   tool MUST be disabled in every API call. Enforced by rule + audit of the proxy logs.
2. **Pin model versions.** The house endpoint serves a pinned model id (`MODEL_NAME`). Floating
   aliases (`*-latest`) are not reproducible and are rejected at verification. A BYO submission
   inherits the pinned base and adds its own adapter, which must be a fixed artifact in the image.
3. **Disclose training cutoffs.** The training cutoff of every model used MUST be declared in
   submission metadata (`models[].training_cutoff` in `submission.json`). For a BYO submission
   that is the base model's cutoff; declare your adapter's training data separately.
4. **Pin temperature/seed** where the API supports it. `api`-category entries are verified
   *statistically* (bootstrap-CI overlap on organizer rerun); BYO entries bit-reproducibly.
5. **Budget (FINAL, ruled 2026-08-28).** A uniform per-unit budget applies
   to every submission — **1,000,000 input + 100,000 output tokens per unit**
   — enforced via proxy logs and spot audit. It applies to every submission in the same way,
   `api` and BYO alike: a BYO run's calls go to `MODEL_ENDPOINT` too, so there is no locally-run
   path outside the budget.

**One leaderboard.** All categories rank on a single board; every entry is tagged with its
category, the models used (pinned versions), and their training cutoffs.

| Track | Verb | Inputs (under `/input`) | Required output (under `/output`) |
|---|---|---|---|
| **T1 Coding** | `solve --task-dir /input --out /app/output` | task spec + environment files | task-specified deliverables written to **`/app/output`** (QFBench/Harbor convention); the `checks/` step asserts correctness and writes **both** `reward.txt` and `reward.json` (see T1 note below) |
| **T2 Time-Series Forecasting** | `forecast --panels /input/panels/ --text /input/text/ --asof <YYYY-MM-DD> --out /output/forecast.parquet` | `panels/` — multivariate time-series parquet files; `text/` — time-stamped text corpus (news, FOMC, macro releases); all timestamps must be ≤ `--asof` (enforced by the organizer's staging gates before the unit ships) | joint predictive distribution conforming to `forecast.schema.json`; sidecar `forecast_meta.json` required; **`forecast_rationale.md` required and never scored** (see T2 note below) |
| **T3 Simulation** (single scenario) | `simulate --config /input/scenario.json --out /output/trace.parquet` | scenario config + ABIDES environment | message-level trace conforming to `sim_scenario.schema.json` + `events.json` (counts/timing) |
| **T3 Simulation** (batched, family GB) | `simulate-batch --batch-dir /input/scenarios --out-dir /output` | `batch.json` — the sub-scenario roster; `scenarios/` — one config per sub-scenario. These units have **no** top-level `scenario.json`. | one output subdir per sub-scenario, each with `trace.parquet` + `events.json`, plus `batch_events.json` at the root of `--out-dir` |
| **T4 Tabular Prediction** | `analyze --task /input/task.json --corpus /input/corpus/ --out /output/answer.json` | `task.json` — tabular dataset (rows = entities) + target column spec + `target_type` (classification/regression/ranking); `corpus/` — frozen evidence corpus | prediction + interval + citations per row conforming to `analysis.schema.json`; `target_type` in output must match card |

> **T2 status (2026-08-20).** The unit-layout half of this is closed: `--panels` names the STAGED
> unit's `panels/` directory. `stage_bundle.py` relocates root panels into `panels/` and its S6
> gate refuses to emit a unit whose `panels/` is empty, and participant containers mount the
> staged tree, never the raw repo. Verified by execution: `--panels /input/` dies with "no
> .parquet found"; `/input/panels/` scores the full chain. The interface half ships in `track2-forecasting-public` — a `forecast`
> CLI, a console-script entry point and a `Dockerfile`, built and run on linux/arm64 (GH200) and
> admitted by g0–g3 against the exemplar unit under `--network=none`.

> **T2 note — `forecast_rationale.md`.** Alongside `forecast.parquet` a submission writes
> `forecast_rationale.md` to `/output`: the derivation behind the distribution. Numbered steps —
> the anchor, each adjustment with its size and what supports it, then the scale and shape —
> naming the series and dates computed from and the documents cited, and ending with an
> adjustment ledger so the arithmetic can be followed.
>
> **It is required and it is never scored.** No submission is ranked higher or lower because of
> this file; `g1_schema` checks only that it exists and is non-empty, and no scoring code reads
> its content. It exists because a submission that recalled its answer and one that derived it
> are indistinguishable as a set of draws, so the parquet alone cannot support any review at all.
>
> It is read as a **screen over the top of the leaderboard**, not a gate: a flag opens a human
> review and cannot by itself produce a DNF or move a score. That restriction stands until a
> false-positive rate has been measured on a large honest corpus — the current measurement is
> 4/4 true positives and 0/4 false positives, and 0-of-4 carries a 95 % interval reaching ~0.6.
> Two alternative mechanisms were tested and rejected: re-executing the trace (backward-built
> traces reproduced *more* exactly than honest ones, so as a gate it favours the cheater) and
> scanning the text for leakage admissions (a guarded prompt drove self-declaration from 100 % to
> 0 % with no change in the numbers). Method and data:
> `track2-forecasting-public/docs/RATIONALE-REVIEW.md`.

**Your image must implement BOTH Track 3 verbs.** The harness picks the verb per unit, from the
unit's contents: a unit carrying `batch.json` + `scenarios/` is dispatched to `simulate-batch`,
everything else to `simulate`. Six of the public dev units (`t3-gbatch-*`) are batched.

**Contract invariants (enforced by gate `g0_integrity` / `g1_schema` / `g2_cutoff_resource`):**

1. The image must honor the card's network mode: `none` (simulation) means fully offline — any
   attempted outbound connection fails the run; `restricted` (agent tracks) means egress only
   through the audited proxy to the house model endpoint — any connection outside that allowlist
   fails the run, and no vendor model API is on it.
2. Output must validate against the track output schema *before* any scoring (`g1_schema`).
3. The image must not read any path outside `/input` and `/output`; the canary registry and held-out
   targets are never mounted.
4. Determinism: the harness sets `QFBENCH_SEED`; verification phase reruns on fresh seeds/resamples and
   compares against the final-phase result (reproducibility gate).
5. Wall-clock and resource caps are per-track (`card.environment`); exceeding them is a `g2` failure.
6. **T2 text cutoff:** every document in `/input/text/` has a timestamp field ≤ `--asof`, enforced by the organizer's staging gates before a unit ships (gate g2 at scoring time binds your declaration to the trusted card; it does not rescan the corpus).
   The staging gates check text timestamps in addition to panel data timestamps; a unit with a
   post-as-of document does not ship. The `shared.leakage.cutoff_violation` label
   (`FailureLabel.LEAKAGE_CUTOFF` in `qfbench2_common.failure_labels`) is what g2 emits when your
   declaration's cutoff disagrees with the trusted card.
7. **T4 target type:** the `target_type` field in `/input/task.json` (and matching `card.toml`) declares
   the task as `classification`, `regression`, or `ranking`. The `answer.json` output must include a
   matching `target_type` field. Mixed task types within one unit are not allowed.
8. **T1 deliverable dir + dual reward (QFBench heritage):** Track 1 *is* QFBench, so it inherits
   QFBench's conventions. The agent writes its deliverables to **`/app/output`**, which is what
   `--out` is set to and what the units' `instruction.md` and `checks/test_outputs.py` say. The
   harness binds the run's output directory at **both** `/app/output` and `/output`, so the
   minority of units phrased against a bare `/output` are captured identically — writing to
   either path is safe, and neither is silently discarded.
   `checks/test.sh` runs **offline** via `python -m pytest` and writes **both**
   Harbor's `/logs/verifier/reward.txt` (1/0) **and** `<output>/reward.json` + `pytest_report.json`
   for the Agenthon g0–g3 verifier and DI failure-label overlay. The same unit therefore runs under
   **both** Harbor (`harbor run --path units ...`) and the Agenthon harness
   (`qfbench2 smoke <unit> <out> --track coding`). See
   `tracks/track1-coding/public/docs/QFBENCH-HERITAGE.md`. (T2/T3/T4 keep the generic `/output`
   contract above.)


## Open Division tag

Do **not** add `house_endpoint_only` -- or any key the descriptor schema does not list -- to
`submission.json`: the schema refuses unknown keys, so a submission carrying it is rejected
before it runs. Whether every model call used the house endpoint exclusively is read from
the audited egress-proxy logs during the verification phase; it drives an "Open Division"
display filter of the single leaderboard (never a separate ranking) and needs nothing
from you.
