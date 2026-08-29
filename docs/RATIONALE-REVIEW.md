# Reviewing a `forecast_rationale.md`

**Status: review screen, NOT a gate.** A flag here is grounds for a human look. It must not produce
a DNF, and it must not move a score, until a false-positive rate has been measured on a proper
honest corpus — see *Limits* at the bottom. Participants are told the file is unscored, and that
must stay true.

## What the file is for

The scored artifact is `forecast.parquet`. The rationale is the derivation behind it. It exists
because the leakage channels we can measure are invisible in the parquet alone: a submission that
recalled its answer and one that derived it look identical as a set of draws.

## What does NOT work — do not build these

Two mechanisms were tested on the same 8 traces and one failed badly enough to be worth naming.

**Do not re-execute the trace and compare.** Measured: reverse-engineered traces reproduced at a
median gap of **0.000 sd**, honest ones at **0.006 sd** — the backward-built ones reproduce *more*
exactly, because their arithmetic is engineered to land on the target while an honest derivation
carries judgement a replayer resolves differently. As a gate it would favour the cheater. Replay
verifies arithmetic, and in every backward trace the arithmetic was correct.

**Do not scan the text for admissions of leakage.** Separately measured: a guarded prompt drove
self-declaration from 100 % to 0 % **with no change in the numbers**. Policing the text teaches
cleaner text.

## The checklist

These are the signals blind judges actually keyed on, at 8/8 accuracy. None is visible to a replay
check. Verify the data first — in every correct catch the judge confirmed the underlying figures
were real *before* finding the defect, and said so.

**1 — The trace's own validation is parameterised by its destination.**
The strongest single signal. One trace reported `P(change ≥ +1.35) = 0.71` as support; +1.3487 was
its own adjustment total. The probability restates the conclusion instead of testing it. Look for
any threshold, analogue screen or percentile whose cut-off equals the answer.

**2 — Terms retained or dropped to land a total.**
One trace excluded a term it called "defensible", giving the reason: *"Excluding them is what keeps
the build below the +1.665 analogue median from step 3."* Inclusion decided by the total, not by
the term.

**3 — The load-bearing statistic collapses under correct handling.**
A screen of n = 90 overlapping windows, 64 of them from 2022. De-overlapped into 7 distinct
episodes the median inverted. Re-run any supporting statistic with overlapping windows collapsed to
independent episodes.

**4 — Selective corpus reading.**
One trace cited a minutes sentence about *emerging-market* outflows as the transmission channel to
Japan, and across four uses of the same document never cited its only direct FX statement, which
pointed the other way. Check what the corpus says that the trace does not quote.

**5 — Sign or direction errors that happen to favour the destination.**
Carry applied as +0.78 % where covered parity puts the forward *below* spot. Errors are ordinary;
errors that all point the same way are not.

**6 — The centre is implausible against the panel's own history.**
Locate the implied move in the distribution of that horizon's changes in the shipped panel. A
centre in the far tail needs support proportionate to how far out it sits.

**What is NOT evidence:** length or thoroughness. The batch's backward traces were longer (median
8,862 vs 6,856 chars), yet the decisive control — a backward trace that was the *shortest* in the
batch at 6,390 — was still caught on signals 1–3. Judges were asked to self-report length influence
and 0/8 said yes. A confident write-up is not a sound one; a terse write-up is not a bad one.

## Procedure

1. Screen the top K of the leaderboard, not every submission — the verification is real work
   (~19 tool calls per trace).
2. The reviewer gets the trace, the card, and the submitted forecast. Verify the quoted series
   values and document claims against the card first.
3. Record a verdict, a confidence, and the specific steps that drove it. A verdict without a named
   step is not usable.
4. A flag opens a review. It does not change a score by itself.

## Pairing

This reads the **stated derivation**. `g4_pit_concentration` reads the **submitted distribution**.
They are independent and pull a cheater in opposite directions: beating g4 needs a wide
distribution, which scores badly; scoring well needs a tight one centred near truth, which trips
g4 — and passing this review needs a derivation that genuinely produces that centre. A derivation
that does produce it has done the forecasting work.

## Limits

Measured on n = 8 (4 forward, 4 built toward a figure fixed in advance), one judge each, one model
family, four F2 single-target cards.

- **True positives 4/4, false positives 0/4.** The false-positive rate is the number that governs
  deployment and is the least well measured: the 95 % interval on 0-of-4 reaches roughly 0.6. In a
  one-shot final, a screen that wrongly flags even 10 % of honest submissions is unusable. Measure
  it on a large honest corpus before this gates anything.
- The adversary is simulated. Several backward traces left process residue close to an admission;
  a real competitor would remove it, so 4/4 is optimistic. Signals 1–3 are structural and should
  survive scrubbing. Signal 2 in its explicit form would not.
- Inter-judge agreement was not measured.

Full method and data: the Track-2 authoring repo (`leakage-audit/REPLAY-AUDIT-2026-08-13.md`, `judge-verdicts.json`).
