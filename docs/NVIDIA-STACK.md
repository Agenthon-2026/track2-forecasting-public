# The NVIDIA stack and Track 2

How the NVIDIA technology stack maps to Track 2, and how participants should (and should not) use
it. Track 2 asks your agent to turn a frozen numeric panel plus a dated official-document corpus
into a **calibrated probabilistic forecast**, scored offline against realized outcomes
([CONCEPTS.md](CONCEPTS.md)). The NVIDIA stack enters this track through exactly one door: the
**organizer-hosted house-model endpoint** — an open model from the sponsor's Nemotron family,
served behind `$MODEL_ENDPOINT`. Nothing GPU-shaped in the stack affects your rank.

## Framing: leveled by the model, not the metal

Track 2 is leveled the opposite way from Track 3. There, every submission gets identical hardware
and no runtime LLM; here, the LLM is the centerpiece of the loop and the GPU never touches your
rank: no scored component measures hardware. Since the 2026-08 caps change every T2 card grants
the same generous sandbox — 16 vCPU / 128G / `gpu = true`. Neither category needs that GPU for
its own code: an `api` submission has no use for it, and on a BYO run the worker's GPU is what
serves the base model. Using or ignoring it moves no score. The network mode is `restricted` — model calls through the audited eval proxy
only, **never data fetching** ([SUBMISSION_CLI.md](../SUBMISSION_CLI.md), "Network modes") — and
official scoring happens organizer-side against sealed realized outcomes, with a scorer that
needs no network at all (local smoke runs use `--network=none`). The house endpoint is free and
identical for everyone (exposed as `$MODEL_ENDPOINT` when available), so what separates
submissions is **elicitation and calibration skill** — how much verifiable predictive signal you
extract from the corpus, and how honestly you spread your uncertainty. Bring-your-own is **adapter-only**: a BYO team
trains one LoRA adapter (rank ≤ 64) **off-cluster, before submission** against the house base
model, ships `adapter_model.safetensors` + `adapter_config.json` in its image, and the organizer
serves the adapter on that base — the image never carries model weights and never runs a model
server. See "Bring your own model: adapter-only, rank ≤ 64" in
[SUBMISSION_CLI.md](../SUBMISSION_CLI.md).

## Per-tool fit

| Tool | Fit for T2 | How to use it | Caveat |
|---|---|---|---|
| **Nemotron behind `$MODEL_ENDPOINT`** | **Core — the one NVIDIA component in your loop** | An OpenAI-compatible chat endpoint; the pinned house-model id is published and arrives as `$MODEL_NAME`. Use it as your **text-reader**: extract stance, dates, revisions and surprises from the corpus, then let them adjust a statistical prior ([CONCEPTS.md](CONCEPTS.md) on information uplift) | If the pin is a reasoning variant, thinking toggles via the system prompt (`detailed thinking on\|off`) and responses may omit the opening `<think>` tag — parse tolerantly. And do not build a strategy on the model's *memory* of famous market episodes: the organizers will publish closed-book recall baselines (the house model queried with no panel and no corpus) alongside the text-blind baselines, so recall of an outcome earns no credit |
| **NeMo (customization / fine-tuning)** | **Off-cluster only — and this is the BYO path** | PEFT/LoRA adapter training against the house base model for macro-text conditioning, before you submit. Rank ≤ 64; ship the adapter, not the merged weights | No tuning or training path can execute in the T2 sandbox, and the NeMo customization stack ships in no T2 image |
| **Megatron-LM** | **No fit** | — | It is a full-weight training stack, and full fine-tuning is not a permitted BYO submission: BYO ships one LoRA adapter. GPU-mandatory with a multi-GB dependency closure and no time-series or forecasting code; it is never part of a T2 image |
| **CUDA / RAPIDS / cuDF** | **No fit** | — | T2's scored pipeline has no GPU surface: solving is file I/O + endpoint calls + sampling, and scoring is CPU CRPS arithmetic. That holds for BYO too — your code calls `$MODEL_ENDPOINT` like an `api` submission does — so vendoring GPU libraries only bloats your image |
| **Nsight / DCGM** | **No fit** | — | T2 has no throughput or efficiency component — nothing to profile, nothing to meter (these are Track 3 concerns) |
| **NeMo Guardrails** | **No fit** | — | A participant-side self-check rail relevant only to Track 4's citation surface; T2's admissibility gates are numeric and schema-level, and the rationale review reads your reasoning, not your I/O |

## What this means concretely

- **To be admissible:** pass the deterministic gates — g0 integrity, g1 schema (including a
  non-empty `forecast_rationale.md`: required, never scored), g2 cutoff/resource, g3 domain
  semantics. No NVIDIA tool helps or hurts here.
- **To rank well:** lower the composite — 50 % marginal CRPS + 30 % joint variogram + 20 % tail
  penalty, lower is better ([CONCEPTS.md](CONCEPTS.md)). The house endpoint is your only lever
  beyond your own statistics: better elicitation of the corpus, better-calibrated spread.
- **What is actually measured:** **information uplift** — your composite against the best
  text-blind baseline on the same cards ([CONCEPTS.md](CONCEPTS.md)). A separate integrity
  measurement keeps memory from masquerading as skill: the planned closed-book recall baselines
  make "the model simply remembered the episode" visible. Design your agent to beat the
  baselines, not to out-recall them.

## Where the tooling lives

- Endpoint contract (`MODEL_ENDPOINT`, `MODEL_NAME`), network modes, and the
  submission-categories table: [SUBMISSION_CLI.md](../SUBMISSION_CLI.md); network modes and
  categories are also summarized in the repo [README.md](../README.md).
- Scoring semantics and the composite: [CONCEPTS.md](CONCEPTS.md); task families:
  [CATEGORIES.md](CATEGORIES.md).
- The rationale requirement and how reviewers read it: [RATIONALE-REVIEW.md](RATIONALE-REVIEW.md).
- *(In review)* a reference end-to-end submission — baseline CLI + gate-passing image
  ([#10](https://github.com/Agenthon-2026/track2-forecasting-public/pull/10)) — and a solver
  playbook distilling what measurably works
  ([#11](https://github.com/Agenthon-2026/track2-forecasting-public/pull/11)); both will be
  linked here once merged.
