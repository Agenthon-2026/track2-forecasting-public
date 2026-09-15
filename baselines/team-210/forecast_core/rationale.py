"""Write forecast_rationale.md.

Required by g1, never scored. Nothing is ranked higher or lower for it, and no
scoring code reads its content - the gate checks only that it exists and is not
blank. It exists so a submission that recalled its answer and one that derived
it can be told apart by a human, which is why it names the series, the dates and
the size of every adjustment rather than gesturing at a method.
"""

from __future__ import annotations

from . import scenario_mixture, text_signal


def _draws_table(draws) -> list[str]:
    """Per-asset, per-horizon quantiles of the distribution actually shipped.

    The old rationale carried exactly one number derived from this unit (the
    drift); everything else was a constant template. A document meant to let
    a human tell a derived forecast from a recalled one has to show the
    derived numbers.
    """
    if draws is None or len(draws) == 0:
        return []
    lines = ["", "| asset | horizon | q05 | median | q95 |", "|---|---:|---:|---:|---:|"]
    grouped = draws.groupby(["asset", "horizon"])["value"]
    for (asset, horizon), values in grouped:
        q05, q50, q95 = (values.quantile(0.05), values.quantile(0.5),
                         values.quantile(0.95))
        lines.append(f"| {asset} | {horizon} | {q05:.6g} | {q50:.6g} | {q95:.6g} |")
    return lines


def write(grid: dict, asof: str, signal: dict, n_draws: int,
          draws=None, notes: list[str] | None = None) -> str:
    assets = ", ".join(grid["asset_ids"])
    horizons = ", ".join(str(h) for h in grid["horizons"])
    documents = signal.get("documents", [])
    drift = float(signal.get("drift_in_sigmas", 0.0))

    lines = [
        f"# Forecast rationale - {grid['unit_id']}",
        "",
        f"**As of {asof}. Joint distribution over {assets} at horizon(s) "
        f"{horizons} business days. Target: `{grid['target']}`.**",
        "",
        "## 1. The anchor",
        "",
        f"The last observed level at or before {asof}, per asset. Nothing after "
        "the as-of date is read: the panel loader filters on date before any "
        "statistic is computed, and documents dated later are excluded by name "
        "or corpus index.",
        "",
        "## 2. The shape",
        "",
        f"{scenario_mixture.METHOD_NAME}, {n_draws} draws, "
        f"{scenario_mixture.BLOCK_DAYS}-day blocks.",
        "",
        "Blocks rather than single days because the CRPS composite carries a "
        "0.2 tail penalty, and independent daily resampling narrows the tails "
        "the history actually had. Blocks are drawn across all assets at once "
        "rather than per asset, because the 0.3 joint variogram term penalises "
        "a curve assembled from independent marginals - the covariance has to "
        "come from real slices of history, not from an assumption.",
        "",
        "## 3. The adjustments",
        "",
    ]

    if not documents:
        reason = ("was not read in this run" if not signal
                  else "was read and contained no usable documents")
        lines += [
            f"**None. The text corpus {reason}.**",
            "",
            "This is the text-blind floor - the number a reasoning agent has to "
            "beat for the information-uplift claim to mean anything. Reporting "
            "it separately is the only way the uplift is attributable.",
        ]
    else:
        net = signal.get("net_hawkish_hits", 0)
        lines += [
            "| document | date | net hawkish hits |",
            "|---|---|---:|",
        ]
        for doc in documents:
            lines.append(f"| `{doc['file']}` | {doc['date'] or 'undated'} | "
                         f"{doc['net_hawkish_hits']:+d} |")
        lines += [
            "",
            f"Net across the corpus: **{net:+d}**, applied as a drift of "
            f"**{drift:+.3f}** daily standard deviations, scaled by the square "
            f"root of the horizon and capped at "
            f"{text_signal.MAX_DRIFT_SIGMAS} sigma.",
        ]
        skipped = signal.get("skipped_after_cutoff", [])
        if skipped:
            lines += ["", "Excluded as dated after the as-of date:"]
            lines += [f"  - {s}" for s in skipped]

    llm = signal.get("llm")
    if llm:
        lines += ["", f"Reader: **{signal.get('reader', 'llm')}**. Stated "
                      "reasons (bounded tilts only; the sampler never sees "
                      "the text):"]
        lines += [f"  - {r}" for r in llm.get("reasons", [])] or ["  - (none)"]
        per_asset = signal.get("per_asset_drift") or {}
        if per_asset:
            tilts = ", ".join(f"{a}: {v:+.3f}" for a, v in per_asset.items())
            lines += ["", f"Per-asset tilts (sigma units): {tilts}"]

    undated = signal.get("undated_documents", 0)
    if undated:
        lines += ["", f"**{undated} document(s) carry no date** and were read; "
                      "the embargo gate cannot be pre-checked for them here."]

    table = _draws_table(draws)
    if table:
        lines += ["", "## 4. The numbers shipped", ""]
        lines += [f"{n_draws} draws per asset-horizon; the distribution's own "
                  "quantiles, computed from the file being submitted:"]
        lines += table
        section_offset = 1
    else:
        section_offset = 0

    if notes:
        lines += ["", f"## {4 + section_offset}. Degradations and diagnostics", ""]
        lines += [f"- {n}" for n in notes]
        section_offset += 1

    lines += [
        "",
        f"## {4 + section_offset}. Adjustment ledger",
        "",
        "```",
        "anchor        last observed level at or before the as-of date",
        "dispersion    block bootstrap over the realised differences",
        f"drift         {drift:+.3f} sigma  (0.000 when the corpus is unread)",
        "```",
        "",
        f"## {5 + section_offset}. What would change this",
        "",
        "A regime shift the historical differences do not contain. The block "
        "bootstrap can only resample what happened; it cannot invent a move "
        "the sample period never saw, and it will understate the tail of any "
        "event of that kind.",
        "",
    ]
    return "\n".join(lines)
