"""Load the numeric panels, filtered to the as-of date.

The filter is not a courtesy. Gate g2 enforces the cutoff, and a single row
dated after --asof makes the run inadmissible regardless of the forecast. So the
loader drops them itself rather than assuming the unit is already clean.

Layout note, from the track's own status entry: `--panels` names the STAGED
unit's `panels/` directory. `--panels /input/` dies with "no .parquet found";
`/input/panels/` scores the full chain. The exemplar in the public repo keeps
its panel at the unit root instead, so both shapes are accepted here - the
staged tree is what runs, the flat one is what a participant clones.

`load` returns (frame, notes): every silent skip or normalisation that used to
vanish is now a note, because a loader that loses half the panel without a
trace produces a forecast that is confidently wrong about the wrong data.
"""

from __future__ import annotations

import pathlib

import pandas as pd

DATE_COLUMNS = ("date", "Date", "timestamp", "asof", "dt")
#: SUBMISSION_CLI documents the panel columns as [date, asset, value, panel_id],
#: but the shipped exemplar uses `asset_id`. The contract and the data disagree,
#: so accept both rather than pick a side - a loader that insists on the
#: documented spelling melts the frame it should have used as-is and dies with
#: "value_name (value) cannot match an element in the DataFrame columns".
ASSET_COLUMNS = ("asset", "asset_id", "series", "series_id", "ticker", "symbol")
#: Same defence for the value column, which used to be the one hardcoded name
#: among three carefully-aliased ones.
VALUE_COLUMNS = ("value", "val", "level", "close", "px", "price", "rate", "yield")


def _find_parquets(panels_dir: pathlib.Path,
                   unit_dir: pathlib.Path) -> list[pathlib.Path]:
    if panels_dir.is_dir():
        found = sorted(panels_dir.glob("*.parquet"))
        if found:
            return found
    # Fall back to the unit root: the public exemplar ships rates_daily.parquet
    # beside card.toml rather than under panels/.
    return sorted(p for p in unit_dir.glob("*.parquet"))


def _first_present(frame: pd.DataFrame, names: tuple[str, ...]) -> str | None:
    for name in names:
        if name in frame.columns:
            return name
    return None


def _normalise(frame: pd.DataFrame, stem: str,
               cutoff: pd.Timestamp, notes: list[str]) -> pd.DataFrame | None:
    """One file to the canonical long shape: date, asset, value, panel_id.

    Per FILE, not after concat: two files spelling the asset column
    differently used to survive the concat as two half-NaN columns, and the
    rename fixed only the first - the second file's rows then vanished in the
    pivot with no trace.
    """
    column = _first_present(frame, DATE_COLUMNS)
    if column is None:
        notes.append(f"{stem}: no recognised date column "
                     f"({list(frame.columns)[:8]}); file skipped")
        return None
    frame = frame.copy()
    # utc=True accepts naive and tz-aware columns alike (a tz-aware column
    # used to raise on comparison with the naive cutoff); the tz is then
    # dropped so everything downstream is naive.
    frame[column] = pd.to_datetime(frame[column], utc=True).dt.tz_localize(None)
    before = len(frame)
    frame = frame.loc[frame[column] <= cutoff]
    if len(frame) < before:
        notes.append(f"{stem}: {before - len(frame)} row(s) after as-of dropped")
    frame = frame.rename(columns={column: "date"})
    if "panel_id" not in frame.columns:
        frame["panel_id"] = stem

    asset_col = _first_present(frame, ASSET_COLUMNS)
    if asset_col is not None and asset_col != "asset":
        frame = frame.rename(columns={asset_col: "asset"})

    value_col = _first_present(frame, VALUE_COLUMNS)
    if value_col is not None and value_col != "value":
        frame = frame.rename(columns={value_col: "value"})
        notes.append(f"{stem}: value column read from {value_col!r}")

    if "asset" not in frame.columns:
        value_columns = [c for c in frame.columns
                         if c not in {"date", "panel_id"}
                         and pd.api.types.is_numeric_dtype(frame[c])]
        if value_columns == ["value"]:
            # A single-series panel: melting would invent an asset literally
            # named "value". The panel id IS the series identity here.
            frame["asset"] = stem
            notes.append(f"{stem}: single-series panel; asset named after it")
        elif value_columns:
            frame = frame.melt(id_vars=["date", "panel_id"],
                               value_vars=value_columns,
                               var_name="asset", value_name="value")
        else:
            notes.append(f"{stem}: no numeric columns; file skipped")
            return None
    return frame


def load(panels_dir: pathlib.Path, unit_dir: pathlib.Path,
         asof: str) -> tuple[pd.DataFrame, list[str]]:
    """One long frame (date, asset, value, panel_id - never rows after asof),
    plus the notes explaining anything that was skipped or coerced."""
    # End of the as-of DAY, not its midnight: an intraday panel used to lose
    # every observation on the as-of date itself - the most informative ones.
    cutoff = (pd.Timestamp(asof) + pd.Timedelta(days=1)
              - pd.Timedelta(nanoseconds=1))
    notes: list[str] = []
    frames = []
    for path in _find_parquets(panels_dir, unit_dir):
        try:
            raw = pd.read_parquet(path)
        except Exception as error:
            notes.append(f"{path.name}: unreadable ({error}); file skipped")
            continue
        frame = _normalise(raw, path.stem, cutoff, notes)
        if frame is not None:
            frames.append(frame[["date", "asset", "value", "panel_id"]])

    if not frames:
        return pd.DataFrame(columns=["date", "asset", "value", "panel_id"]), notes

    panel = pd.concat(frames, ignore_index=True)
    before = len(panel)
    panel = panel.drop_duplicates(subset=["date", "asset", "panel_id"],
                                  keep="last")
    if len(panel) < before:
        notes.append(f"{before - len(panel)} duplicate (date, asset, panel) "
                     "row(s) dropped, keeping the last")

    return (panel.dropna(subset=["value"]).sort_values(["asset", "date"]),
            notes)


def cumulative_from_returns(panel: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Turn a per-period-return panel into cumulative-return LEVELS.

    16 of 104 public cards declare `target_type = "log_return"`: the panel's
    `value` is already a per-period return and the scored target is the SUM
    over the horizon anchored at 0 - not a level. Forecasting the return
    series as if it were a level (last + bootstrapped diffs of returns) is
    what the kit's own reference CLI gets wrong, and the organizers call it
    "silent and catastrophic". Cumulating first makes every downstream step
    (block bootstrap of diffs, EWMA vol, tail widening) operate on the
    quantity that is graded; the caller subtracts each asset's anchor (the
    cumulative level at the as-of date) so the shipped draws start at 0.
    Returns (cumulative panel, {asset: anchor}).
    """
    if panel.empty:
        return panel, {}
    out = panel.sort_values(["asset", "panel_id", "date"]).copy()
    out["value"] = out.groupby(["asset", "panel_id"])["value"].cumsum()
    anchors = {asset: float(group.sort_values("date")["value"].iloc[-1])
               for asset, group in out.groupby("asset")}
    return out, anchors
