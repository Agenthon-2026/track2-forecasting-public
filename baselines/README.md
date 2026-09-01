# Track 2 Baselines — adapter scaffolds

## Read this first

**These are scaffolds, not working model adapters.** Each file shows the shape a real adapter
takes — the `BaselineForecaster` interface, the request/result types, seeding, and output
validation — and then produces samples from a **Gaussian random walk**. None of them calls the
model it is named after.

The import at the top of each file is a presence check only; its result is never used. Until
2026-08-28 the metadata compounded this by reporting `"implementation": "chronos-forecasting"`
(and equivalently for the others) whenever the package happened to be installed, while still
returning placeholder samples. That field now always reads `"gaussian-rw-placeholder"` and carries
`"real_adapter_implemented": false`.

**What this means for you.** Do not treat these scores as a bar to clear, and do not read a gap
between your agent and a "baseline" as information uplift — the comparison is against noise, not
against the state of the art. Use the files for their interface, and bring your own forecaster.

Implementing any of these against the real package is a genuinely useful contribution; the
scaffold is the part that is done.

---

## The five scaffolds

| File | Interface it demonstrates | Forecast actually produced |
|------|---------------------------|----------------------------|
| `theta_arima.py` | classical statistical adapter (Theta / AutoARIMA shape) | Gaussian random walk |
| `chronos.py` | foundation-model adapter (Amazon Chronos shape) | Gaussian random walk |
| `timesfm.py` | foundation-model adapter (Google TimesFM shape) | Gaussian random walk |
| `lag_llama.py` | time-series LLM adapter (Lag-Llama shape) | Gaussian random walk |
| `moirai.py` | multi-frequency adapter (Salesforce MOIRAI shape) | Gaussian random walk |

Each uses a distinct fixed seed, so the five produce different numbers. That difference is seed
noise and nothing else — it is not a difference in method.


All five scaffolds:
- Are **Python classes, not command-line programs.** None of them ships a `__main__` or an
  argument parser; the `forecast --panels ... --text ... --asof ... --out ...` verb lives in
  `qfbench2_track_forecasting/cli.py` and is installed as the `forecast` console script. Call a
  scaffold in-process, as shown below.
- Take a `ForecastRequest` and return a `ForecastResult`. They never read `--text`, or any text.
- Respect the leakage guard: only panel rows with `date <= asof` reach the series.
- Produce sample output shaped `[n_draws, n_assets, n_horizons]` with `n_draws` from the request
  (default 500; gate g1 needs at least 200).
- Need no network at all — they make no model-API call of any kind.

Note: needing no network is a property of these text-blind scaffolds, not of Track 2 submissions
in general. Reasoning agents that call the model endpoint run at scoring time under the
**restricted** network — no open internet, model-API egress only through the organizer's
audited proxy. See the README section "Network contract and submission categories".

---

## What these names were meant to be

The five names — Theta/AutoARIMA, Chronos, TimesFM, Lag-Llama, MOIRAI — are the comparison Track 2
was designed around: strong *text-blind* time-series models, so that any improvement your agent
shows has to come from the text rather than from a better numeric model. That design is why the
scaffolds carry these names.

**None of that is implemented here.** What ships in this directory is five interfaces over one
Gaussian random walk. Read the names as a statement of intent about the interface, not as a claim
about what the code does.

---

## Baseline scores

**There are none in this repository, and none are published.** There is no `baseline-scores.csv`
here — the file does not exist and never shipped — and no per-card or aggregate baseline table is
published anywhere else either. Deliberately: a card's score is normalized by the baseline's own
components, so a published per-unit baseline score plus a reproducible baseline forecast inverts
to the sealed value. See the "Their scores are not published per unit" note in the repository
[README.md](../README.md).

**So you cannot calibrate against a baseline number locally, and you should not try.** What you
can do locally is check that your agent runs, that it is admissible under g0-g3, and that its
distribution is self-consistent. Accuracy feedback comes from submitting: on the leaderboard the
normalization does the comparison for you — **1.0 means "no better than the text-blind
baseline"** — so your own score already reads as a ratio, with no baseline table needed.

Running a scaffold in this directory tells you nothing about accuracy either. Its output is a
Gaussian random walk; a score against it is a score against noise.

---

## How to run a scaffold locally

**There are no per-baseline Dockerfiles.** `baselines/chronos.Dockerfile` and its four siblings do
not exist; the repository ships one `Dockerfile`, at the root, and it builds the `forecast` CLI.
Earlier revisions of this section told you to build `baselines/<name>.Dockerfile` against
`units/t2-EXAMPLE-ust-curve-1m/input/panels` — neither path exists. The exemplar unit has no
`input/` subdirectory, and the harness mounts **the unit directory itself** at `/input`
(`-v <unit-dir>:/input:ro`), so a unit's panel parquets sit directly at `/input/` (for example
`/input/rates_daily.parquet`) and its corpus at `/input/text/`. No unit has a `panels/`
subdirectory.
See the container section of the repository [README.md](../README.md).

Call a scaffold in-process instead — that is what it is for:

```python
from baselines.chronos import ChronosBaseline
from baselines.base import ForecastRequest

result = ChronosBaseline().forecast(request)   # request: ForecastRequest
print(result.metadata["implementation"])       # -> 'gaussian-rw-placeholder'
print(result.metadata["real_adapter_implemented"])  # -> False
```

For an end-to-end local run of the real submission path — CLI, admissibility gates and the
unranked local scorer — use `units/t2-EXAMPLE-ust-curve-1m/run_example.sh` and the quick-start in
the repository [README.md](../README.md).

---

## The agentic baseline — not shipped

`baselines/agentic_baseline.py` **does not exist in this repository.** It is a specification, and
the five scaffolds above are the only code in this directory. Do not plan around it.

What it is meant to be, if it lands: a deliberately simple reasoning agent — a time-series
component plus a minimal LLM component that retrieves the most recent corpus documents, extracts a
directional signal, and nudges the forecast mean. A floor for reasoning-agent performance, not a
ceiling, demonstrating the minimum viable integration of text and time series. Until it ships
there is nothing here to run or compare against.

---

## Comparing your agent to the baselines

**The baseline half of this comparison cannot be run here.** No baseline scores are published, and
the scaffolds in this directory produce noise, so any local "uplift" number computed against them
is meaningless. Do not put one in your report.

What you *can* run locally, and what is worth reporting:

1. **Run your agent** on the practice cards.
2. **Run your agent with an empty text corpus** (text ablation). The gap between the ablated and
   the full run isolates the marginal contribution of text *within your own system* — no baseline
   is involved, so this measurement is sound locally.
3. **Read the baseline comparison off the leaderboard**, where the normalization already performs
   it: your submitted score is a ratio against the text-blind baseline, and 1.0 means no better
   than it.

Report your full score, your ablated score, and the gap. The text ablation is the part of the
Track 2 contribution you can establish yourself.

---

## Implementation notes

Each scaffold subclasses `BaselineForecaster` from `base.py`. That is the real interface — an
earlier revision of this section documented a `BaseForecaster` class with a
`forecast(panels_dir, text_dir, asof, output_path)` signature and an `accepts_text()` method;
none of those three exist:

```python
class BaselineForecaster(abc.ABC):
    @property
    @abc.abstractmethod
    def model_name(self) -> str: ...

    @abc.abstractmethod
    def forecast(self, request: ForecastRequest) -> ForecastResult: ...
```

**Text never enters this interface.** `ForecastRequest` carries `panels`, `asof`, `asset_ids`,
`horizons` and `n_draws` — there is no text field, which is what makes these scaffolds text-blind.
Reading the corpus is your agent's job and happens outside this class, in your own code behind the
`forecast` CLI.

`base.py` also provides `_gaussian_rw_samples()` (the placeholder every scaffold returns) and
`validate_output()`, which checks that `samples` is an ndarray of shape
`(n_draws, n_assets, n_horizons)` and that the asset and horizon axes match the request — that one
is worth reusing.
