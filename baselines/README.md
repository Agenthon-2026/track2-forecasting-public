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


All five baselines:
- Implement the standard `forecast --panels /input/panels --text /input/text --asof YYYY-MM-DD --out /output/forecast.parquet` CLI (they receive the `--text` argument but ignore it)
- Pass the leakage guard (no panel rows with `date > asof`)
- Produce valid sample-based output with `n_draws = 500`
- Run fully offline with `--network=none` — they need no model-API access, so a plain
  no-network container is all they require

Note: `--network=none` is a property of these text-blind baselines, not of Track 2
submissions in general. Reasoning agents that call model APIs run at scoring time under the
**restricted** network — no open internet, model-API egress only through the organizer's
audited proxy. See the README section "Network contract and submission categories".

---

## Why these are the right baselines

Track 2 is a time-series forecasting track. The natural text-blind comparison is the current
best time-series foundation models, not naive models. This is a deliberate design choice:

- If the baselines were trivial (e.g., a random walk), beating them would not demonstrate
  that LLM reasoning helps — it might just show that any statistical model beats random.
- By using strong text-blind TS foundation models, we ensure that any improvement your
  reasoning agent achieves must come from the text, not from a better numeric model.

**If your agent beats Chronos and MOIRAI on F4 (tail/shock-from-text) cards but not on F1
(continuation-with-context) cards**, that is a meaningful result: it shows text helps most
for shock detection, not for in-distribution continuation.

---

## Baseline scores

Baseline scores on the validation split are in `baseline-scores.csv` at the root of this
repository. The file reports per-card and aggregate composite scores for all five baselines.

Use these to calibrate your own model's performance before submitting:
- If your model scores worse than Theta/AutoARIMA on F1 cards, your marginal distribution
  is poorly calibrated — fix that before worrying about the text corpus.
- If your model scores worse than Chronos on F3 cards, your joint distribution has problems —
  you are likely generating independent marginals rather than joint draws.
- If your model scores worse than all baselines on F4 cards but uses text, your LLM is not
  successfully translating the shock-foreshadowing text into tail-widening.

---

## How to run a baseline locally

```bash
# Build the baseline image (example: Chronos)
docker build -f baselines/chronos.Dockerfile -t t2-baseline-chronos:latest .

# Run against the exemplar card (baselines are text-blind and fully offline,
# so --network=none is appropriate here)
# The harness grants 16 vCPU / 128G per unit. Docker refuses a --cpus value above the
# cores your machine actually has, so lower both for a local smoke run — they are limits,
# not reservations, and nothing about the forecast depends on them.
docker run --rm \
  --network=none \
  --cpus=4 \
  --memory=16g \
  -v $(pwd)/units/t2-EXAMPLE-ust-curve-1m/input/panels:/input/panels:ro \
  -v $(pwd)/units/t2-EXAMPLE-ust-curve-1m/input/text:/input/text:ro \
  -v $(pwd)/output:/output \
  t2-baseline-chronos:latest \
  forecast --panels /input/panels --text /input/text --asof 2024-06-28 --out /output/forecast.parquet

# Score it
python scoring/scoring.py score \
  --card units/t2-EXAMPLE-ust-curve-1m/card.toml \
  --forecast output/forecast.parquet \
  --realized units/t2-EXAMPLE-ust-curve-1m/realized_public_example.parquet
```

---

## The agentic baseline

In addition to the five text-blind models, we provide a reference **agentic baseline**:
a simple reasoning agent that combines a time-series foundation model (Chronos) with a
minimal LLM component that retrieves the three most recent text corpus documents and
extracts a directional signal (bullish / bearish / neutral) to nudge the forecast mean.

The agentic baseline is intentionally simple — it is a floor for reasoning-agent performance,
not a ceiling. It demonstrates the minimum viable integration of text and time-series models.

Source: **not shipped.** `baselines/agentic_baseline.py` is a specification only; the five
text-blind baselines above (`chronos`, `lag_llama`, `moirai`, `theta_arima`, `timesfm`) are
the code that exists here. The comparison described below cannot be run until it lands.

**Why include an agentic baseline?** It answers the question: "does even a trivial use of
text help vs. text-blind models?" If the agentic baseline beats all five text-blind models
on F2 and F4 cards, that is strong evidence that text carries real signal. If it does not,
the card families or text corpus may need redesign.

---

## Comparing your agent to the baselines

The recommended comparison protocol:

1. **Run your agent** on the validation split cards.
2. **Run the five text-blind baselines** on the same cards (scores already in `baseline-scores.csv`).
3. **Compute the information uplift**: the best baseline's composite score minus your composite
   score (composites are lower-better). Positive uplift = your agent extracted useful signal
   from the text corpus.
4. **Run your agent with an empty text corpus** (text ablation). The gap between ablated and
   full agent scores isolates the marginal contribution of text within your system.

Report all four numbers (full score, ablated score, best-baseline score, uplift) in your
technical report. This is the scientific contribution of Track 2.

---

## Implementation notes

Each baseline adapter inherits from `base.py` which defines:

```python
class BaseForecaster:
    def forecast(self, panels_dir, text_dir, asof, output_path):
        raise NotImplementedError

    def accepts_text(self) -> bool:
        return False  # All text-blind baselines return False here
```

The `text_dir` argument is passed through but ignored by all five text-blind baselines.
The `accepts_text()` method returns `False` to make this explicit. Your reasoning agent
should override `accepts_text()` to return `True` and implement actual text processing.
