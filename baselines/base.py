"""
Track 2 – Reasoning-Augmented Time-Series Forecasting: Baseline Forecaster Protocol
===============================================================================

This module defines the :class:`BaselineForecaster` abstract base class that
all Track 2 baseline and participant adapters must implement.

Shape contract
--------------
Every concrete implementation **must** return a :class:`ForecastResult` whose
``samples`` array satisfies::

    samples.shape == (n_draws, n_assets, n_horizons)

where:

* ``n_draws`` is ``request.n_draws`` (≥ 200 to pass gate g1).
* ``n_assets`` is ``len(request.asset_ids)``.
* ``n_horizons`` is ``len(request.horizons)``.

Axis ordering is strict and must not be transposed.  Draws along axis 0 are
treated as exchangeable Monte-Carlo samples from the joint predictive
distribution.

Note on dependence structure
-----------------------------
Baseline models that forecast each asset independently (e.g.
:class:`~baselines.theta_arima.ThetaARIMABaseline`) assemble the joint draw
matrix by stacking independent per-asset draws.  This means the submitted
samples carry *no* cross-asset dependence structure, which will incur a
penalty on the variogram-based joint score component.  Participants seeking
competitive joint scores should model or learn cross-asset correlations
explicitly.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd
from numpy.typing import NDArray

# ---------------------------------------------------------------------------
# Request / result dataclasses
# ---------------------------------------------------------------------------


# Target types whose panel rows are already per-step returns, so the row IS the step.
# Measured across the shipped kit: every log-return unit is a factors_daily panel whose
# `value` is a daily return. Anything not named here is treated as a level.
_RETURN_TARGETS = frozenset({"log_return", "return", "simple_return", "pct_change"})


@dataclass
class ForecastRequest:
    """Input specification for a forecasting call.

    Attributes
    ----------
    panels : dict[str, pd.DataFrame]
        Mapping from asset ID to its historical price/return panel.
        Each ``DataFrame`` should be indexed by date (``DatetimeIndex``)
        and contain at least a ``"close"`` or ``"return"`` column,
        though adapters may use additional columns.
    asof : str
        ISO-8601 forecast origin date (``YYYY-MM-DD``).  No data after
        this date may be used (leakage guard).
    asset_ids : list[str]
        Ordered list of asset identifiers to forecast.  The output
        ``samples`` axis 1 must correspond to this order.
    horizons : list[int]
        Ordered list of forecast horizon offsets in trading periods
        (e.g. ``[1, 5, 10, 21]`` for 1-day, 1-week, 2-week, 1-month).
        The output ``samples`` axis 2 must correspond to this order.
    n_draws : int, optional
        Number of Monte-Carlo draws to produce.  Must be ≥ 200 to pass
        the leaderboard admissibility gate g1.  Default: ``500``.
    target_type : str, optional
        The unit's ``[targets] target_type``: ``"level"`` (a price, index or
        yield) or ``"log_return"`` (a cumulative return over the horizon).
        It decides what a panel row *means*, and therefore how the per-step
        drift is estimated -- see :meth:`BaselineForecaster._gaussian_rw_samples`.
        Unknown values are treated as ``"level"``.  Default: ``"level"``.
    """

    panels: dict[str, pd.DataFrame]
    asof: str
    asset_ids: list[str]
    horizons: list[int]
    n_draws: int = 500
    target_type: str = "level"


@dataclass
class ForecastResult:
    """Output of a :class:`BaselineForecaster` call.

    Attributes
    ----------
    samples : np.ndarray of shape [n_draws, n_assets, n_horizons]
        Monte-Carlo draw matrix.

        * Axis 0 (``n_draws``): exchangeable draws from the joint
          predictive distribution.
        * Axis 1 (``n_assets``): assets in the same order as
          ``request.asset_ids``.
        * Axis 2 (``n_horizons``): horizons in the same order as
          ``request.horizons``.

    asset_ids : list[str]
        Asset identifiers corresponding to axis 1 of *samples*.
        Must equal ``request.asset_ids``.
    horizons : list[int]
        Horizon offsets corresponding to axis 2 of *samples*.
        Must equal ``request.horizons``.
    model_name : str
        Human-readable identifier of the forecasting model used.
    metadata : dict
        Arbitrary metadata produced by the adapter (e.g. fitted
        parameters, convergence diagnostics, elapsed time).
        Default: empty dict.
    """

    samples: NDArray[np.float64]  # shape: [n_draws, n_assets, n_horizons]
    asset_ids: list[str]
    horizons: list[int]
    model_name: str
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Abstract base class
# ---------------------------------------------------------------------------


class BaselineForecaster(abc.ABC):
    """Abstract base class for all Track 2 forecasting adapters.

    Subclasses must implement :meth:`forecast` and expose a
    :attr:`model_name` property.

    Shape contract
    --------------
    The ``samples`` field of the returned :class:`ForecastResult` **must**
    satisfy::

        result.samples.shape == (request.n_draws,
                                 len(request.asset_ids),
                                 len(request.horizons))

    Violation of this contract causes :meth:`validate_output` to raise a
    ``ValueError`` and will trigger gate g3 failure in the auto-grader.

    Usage example
    -------------
    .. code-block:: python

        class MyForecaster(BaselineForecaster):
            @property
            def model_name(self) -> str:
                return "my_model"

            def forecast(self, request: ForecastRequest) -> ForecastResult:
                ...
                return ForecastResult(
                    samples=samples,  # shape [n_draws, n_assets, n_horizons]
                    asset_ids=request.asset_ids,
                    horizons=request.horizons,
                    model_name=self.model_name,
                )
    """

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------

    @property
    @abc.abstractmethod
    def model_name(self) -> str:
        """Short identifier for this forecasting model.

        Returns
        -------
        str
            Human-readable model name used in leaderboard display and
            :class:`ForecastResult.model_name`.
        """
        ...

    @abc.abstractmethod
    def forecast(self, request: ForecastRequest) -> ForecastResult:
        """Generate probabilistic forecast samples for the given request.

        Parameters
        ----------
        request : ForecastRequest
            Fully populated request object.  Implementations must respect
            ``request.asof`` as a hard cutoff — no data beyond this date
            may be used.

        Returns
        -------
        ForecastResult
            Result with ``samples`` of shape
            ``[n_draws, n_assets, n_horizons]``.

        Notes
        -----
        Callers should invoke :meth:`validate_output` on the returned
        result before passing it downstream to the verifier.
        """
        ...

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Shared statistical fallback
    # ------------------------------------------------------------------

    def _gaussian_rw_samples(
        self,
        request: ForecastRequest,
        seed: int = 0,
        vol_floor: float = 1e-6,
    ) -> NDArray[np.float64]:
        """Produce schema-valid joint samples with a lightweight statistical model.

        This is the **offline fallback** used by every Track-2 baseline adapter when
        the corresponding foundation-model package is not installed (none of the
        pre-trained weights can be vendored into a ``--network=none`` image). It is a
        random-walk-with-drift Gaussian forecaster:

        * For each asset, take the historical level/return series up to ``request.asof``
          (the panel is already truncated to the cutoff by the harness; we additionally
          mask any ``date > asof`` defensively to respect the leakage guard).
        * Estimate a per-step drift ``mu`` and volatility ``sigma``.  For a
          ``level`` target that is the last *differences* of the series; for a
          ``log_return`` target the panel row is already the step, so the series
          is used directly and the walk starts from 0 rather than from ``last``.
        * Propagate the last observed level forward by each horizon ``h`` as
          ``last + mu*h + sigma*sqrt(h)*Z`` with ``Z ~ N(0, 1)``.

        Draws are i.i.d. across assets (no modelled cross-asset dependence), matching
        the documented behaviour of the per-asset baselines. The returned array has
        shape ``[n_draws, n_assets, n_horizons]`` in ``request.asset_ids`` x
        ``request.horizons`` order and is guaranteed finite with positive per-asset
        spread, so it passes gates g1/g3.

        Parameters
        ----------
        request : ForecastRequest
            The originating request.
        seed : int, optional
            RNG seed for reproducibility. Default ``0``.
        vol_floor : float, optional
            Lower bound on the per-asset volatility so degenerate (constant) series
            still yield a non-degenerate predictive distribution. Default ``1e-6``.

        Returns
        -------
        np.ndarray
            Samples of shape ``[n_draws, n_assets, n_horizons]``.
        """
        rng = np.random.default_rng(seed)
        n_assets = len(request.asset_ids)
        n_horizons = len(request.horizons)
        horizons = np.asarray(request.horizons, dtype=np.float64)

        samples = np.empty((request.n_draws, n_assets, n_horizons), dtype=np.float64)

        returns_target = request.target_type.strip().lower() in _RETURN_TARGETS

        for ai, asset in enumerate(request.asset_ids):
            series, dates = self._finite(
                self._extract_series(request, asset), self._extract_dates(request, asset)
            )
            if series.size == 0:
                # No history for this asset: fall back to a unit-scale walk from 0.
                last, mu, sigma = 0.0, 0.0, 1.0
            elif returns_target:
                # The panel already holds the per-step return, so the step IS the row: do not
                # difference it a second time. Differencing returns telescopes the drift away
                # (mean(diff(s)) = (s[-1]-s[0])/(n-1), noise) and inflates the spread by ~sqrt(2),
                # and `last` -- a single day's return -- is not where a cumulative return starts.
                last = 0.0
                mu = float(np.mean(series))
                sigma = float(np.std(series))
                sigma = max(sigma, vol_floor)
            else:
                diffs = self._diffs_without_gaps(series, dates)
                last = float(series[-1])
                mu = float(np.mean(diffs)) if diffs.size else 0.0
                sigma = float(np.std(diffs)) if diffs.size else 0.0
                sigma = max(sigma, abs(last) * 1e-4, vol_floor)

            # [n_draws, n_horizons]
            z = rng.standard_normal((request.n_draws, n_horizons))
            drift = mu * horizons[None, :]
            shock = sigma * np.sqrt(horizons)[None, :] * z
            samples[:, ai, :] = last + drift + shock

        return samples

    @staticmethod
    def _finite(
        series: NDArray[np.float64], dates: NDArray[np.datetime64] | None
    ) -> tuple[NDArray[np.float64], NDArray[np.datetime64] | None]:
        """Drop non-finite observations, and the dates paired with them.

        `np.mean`/`np.std` propagate NaN, so a single hole anywhere in a panel turned the
        whole forecast into NaN and failed g1 -- while the participant CLI (`cli.py`, which
        drops NaN rows and calls `np.nan_to_num` on the correlation) and the organizer's
        frozen baseline (`nanmean`) both survive it. This module was the only one that did not.

        The two arrays are paired POSITIONALLY, so filtering one without the other silently
        misaligns the gap guard. When they cannot be aligned the dates are dropped entirely,
        which the guard already handles, rather than passed on at a mismatched length.
        """
        if series.size == 0:
            return series, dates
        keep = np.isfinite(series)
        if bool(keep.all()):
            return series, dates
        if dates is not None and dates.size == series.size:
            return series[keep], dates[keep]
        return series[keep], None

    @staticmethod
    def _diffs_without_gaps(
        series: NDArray[np.float64],
        dates: NDArray[np.datetime64] | None,
    ) -> NDArray[np.float64]:
        """First differences, dropping any that spans a hole in the history.

        Transfer cards ship their target as an early window plus a single row at the as-of
        date, with the years between withheld on purpose (the card says so, and says not to
        difference across it). Differenced naively that hole reads as one day in which the
        asset moved a decade's worth, and it drives sigma by orders of magnitude. The
        threshold adapts to the panel's own spacing (10x its typical step, floor 5 days), so
        daily and monthly panels are both handled and a gapless panel is untouched.
        """
        diffs = np.diff(series)
        if dates is None or dates.size != series.size or diffs.size == 0:
            return diffs
        step = np.diff(dates).astype("timedelta64[D]").astype(float)
        if not np.isfinite(step).any():
            return diffs
        limit = max(float(np.nanmedian(step)) * 10.0, 5.0)
        # `limit >= median` always, so at least half the steps survive: `kept` cannot be empty.
        # An earlier draft fell back to the unguarded diffs when it was, which would have
        # silently reinstated the very bug this function exists to prevent.
        return diffs[step <= limit]

    @staticmethod
    def _extract_series(request: ForecastRequest, asset: str) -> NDArray[np.float64]:
        """Return the as-of-truncated value series for ``asset`` from the panels.

        Accepts the two panel layouts used across Track-2 fixtures:

        * wide per-asset frames keyed by asset id in ``request.panels`` with a
          ``value``/``close``/``return`` column; or
        * a single long/tidy frame (under any key) with an ``asset`` (or ``asset_id``)
          column and a ``value`` column, from which the rows for ``asset`` are selected.

        Any rows with ``date > request.asof`` are dropped (leakage guard). Returns a
        1-D float array (possibly empty).
        """
        asof = pd.Timestamp(request.asof)

        def _mask_asof(frame: pd.DataFrame) -> pd.DataFrame:
            if "date" in frame.columns:
                return frame[pd.to_datetime(frame["date"]) <= asof]
            if isinstance(frame.index, pd.DatetimeIndex):
                return frame[frame.index <= asof]
            return frame

        # Layout 1: per-asset frame keyed directly by asset id.
        frame = request.panels.get(asset)
        if frame is not None and len(frame) > 0:
            frame = _mask_asof(frame)
            for col in ("value", "close", "return"):
                if col in frame.columns:
                    return np.asarray(frame[col].to_numpy(), dtype=np.float64)

        # Layout 2: a single long/tidy frame with an asset column. Both spellings are
        # accepted: the exemplar unit uses `asset_id`, while the pilot and prospective batches
        # use `asset` (the same split cli.py:53-55 records). Requiring `asset_id` meant this
        # returned empty for all 238 authored panels -- the caller then fell back to a
        # unit-scale walk from 0, i.e. forecasting ~0 for an FX rate of 6.21. The only
        # ForecastRequest ever built from a real panel drives the exemplar, so the `asset`
        # spelling was never exercised and nothing caught it.
        for frame in request.panels.values():
            acol = next((c for c in ("asset", "asset_id") if c in frame.columns), None)
            if acol is not None and "value" in frame.columns:
                sub = _mask_asof(frame)
                sub = sub[sub[acol].astype(str) == asset]
                if len(sub) > 0:
                    if "date" in sub.columns:
                        sub = sub.sort_values("date")
                    return np.asarray(sub["value"].to_numpy(), dtype=np.float64)

        return np.empty(0, dtype=np.float64)

    @staticmethod
    def _extract_dates(request: ForecastRequest, asset: str) -> NDArray[np.datetime64] | None:
        """The date index behind :meth:`_extract_series`, or ``None`` if the panel has none.

        Only used to spot holes in the history; a panel without dates keeps the old behaviour.
        """
        asof = pd.Timestamp(request.asof)

        def _dates_of(frame: pd.DataFrame) -> NDArray[np.datetime64] | None:
            if "date" in frame.columns:
                d = pd.to_datetime(frame["date"])
                return np.asarray(d[d <= asof].sort_values().to_numpy())
            if isinstance(frame.index, pd.DatetimeIndex):
                idx = frame.index[frame.index <= asof]
                return np.asarray(idx.sort_values().to_numpy())
            return None

        frame = request.panels.get(asset)
        if frame is not None and len(frame) > 0:
            for col in ("value", "close", "return"):
                if col in frame.columns:
                    return _dates_of(frame)

        for frame in request.panels.values():
            acol = next((c for c in ("asset", "asset_id") if c in frame.columns), None)
            if acol is not None and "value" in frame.columns:
                # Mask BEFORE the emptiness test, exactly as _extract_series does. Testing the
                # unmasked frame can lock onto a panel that only holds post-as-of rows for this
                # asset; the two functions then return different lengths and the gap guard
                # silently disables itself -- fail-open, which is the wrong direction.
                sub = frame
                if "date" in sub.columns:
                    sub = sub[pd.to_datetime(sub["date"]) <= asof]
                elif isinstance(sub.index, pd.DatetimeIndex):
                    sub = sub[sub.index <= asof]
                sub = sub[sub[acol].astype(str) == asset]
                if len(sub) > 0:
                    return _dates_of(sub)
        return None

    def validate_output(
        self,
        result: ForecastResult,
        request: ForecastRequest,
    ) -> None:
        """Validate that *result* satisfies the shape contract.

        Parameters
        ----------
        result : ForecastResult
            The forecast result to validate.
        request : ForecastRequest
            The originating request (used to derive expected dimensions).

        Raises
        ------
        ValueError
            If any of the following conditions hold:

            * ``result.samples`` is not an ``np.ndarray``.
            * ``result.samples.shape[0] != request.n_draws``.
            * ``result.samples.shape[1] != len(request.asset_ids)``.
            * ``result.samples.shape[2] != len(request.horizons)``.
            * ``result.asset_ids != request.asset_ids``.
            * ``result.horizons != request.horizons``.
        """
        expected_shape = (
            request.n_draws,
            len(request.asset_ids),
            len(request.horizons),
        )

        if not isinstance(result.samples, np.ndarray):
            raise ValueError(
                f"[{self.model_name}] result.samples must be a numpy.ndarray; "
                f"got {type(result.samples).__name__}."
            )

        if result.samples.shape != expected_shape:
            raise ValueError(
                f"[{self.model_name}] result.samples has shape "
                f"{result.samples.shape} but expected {expected_shape} "
                f"(n_draws={request.n_draws}, "
                f"n_assets={len(request.asset_ids)}, "
                f"n_horizons={len(request.horizons)})."
            )

        if result.asset_ids != request.asset_ids:
            raise ValueError(
                f"[{self.model_name}] result.asset_ids {result.asset_ids} "
                f"does not match request.asset_ids {request.asset_ids}."
            )

        if result.horizons != request.horizons:
            raise ValueError(
                f"[{self.model_name}] result.horizons {result.horizons} "
                f"does not match request.horizons {request.horizons}."
            )
