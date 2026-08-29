"""
Adapter stub for Theta model and AutoARIMA.

Wraps ``statsforecast`` (if installed).  Each asset is forecast independently
using either the Theta method or AutoARIMA; joint draws are formed by
independent sampling across assets (no cross-asset dependence structure is
modelled).

This is the **classical-statistical baseline** for T2-F1 and provides a
reference for univariate probabilistic accuracy.

Dependence note
---------------
Because each asset is forecast independently, the joint draw matrix is formed
by concatenating independent per-asset sample vectors.  The variogram-based
joint score component will therefore reflect the null hypothesis of zero
cross-asset correlation.  Participants requiring a competitive joint score
should replace or augment this adapter with a multivariate model.

Installation
------------
.. code-block:: bash

    pip install statsforecast

Output shape
------------
``samples[n_draws, n_assets, n_horizons]`` — draws are i.i.d. across assets
(no dependence structure captured).
"""

from __future__ import annotations

from .base import BaselineForecaster, ForecastRequest, ForecastResult


class ThetaARIMABaseline(BaselineForecaster):
    """Theta / AutoARIMA probabilistic forecaster adapter.

    Each asset is modelled independently with either the Theta exponential
    smoothing method or AutoARIMA, as implemented in ``statsforecast``.

    Prediction intervals from the fitted model are used to construct
    Monte-Carlo samples.  Specifically, for each asset the quantile function
    is approximated by drawing from the model's predictive distribution using
    simulation or analytic Gaussian intervals (depending on the
    ``statsforecast`` version).

    Output
    ------
    ``samples[n_draws, n_assets, n_horizons]`` — draws are i.i.d. across
    assets (no cross-asset dependence structure captured).

    Parameters
    ----------
    model : str, optional
        Which model family to use.  Options: ``"theta"`` (default),
        ``"autoarima"``.
    season_length : int, optional
        Seasonal period passed to the underlying model.  Default: ``5``
        (weekly cycle for daily financial data).
    """

    def __init__(
        self,
        model: str = "theta",
        season_length: int = 5,
    ) -> None:
        self._model = model
        self._season_length = season_length

    @property
    def model_name(self) -> str:
        return "theta_arima"

    def forecast(self, request: ForecastRequest) -> ForecastResult:
        """Generate independent per-asset probabilistic forecasts.

        Parameters
        ----------
        request : ForecastRequest
            Forecast request.  ``request.asof`` is respected as a hard
            data cutoff (no leakage).

        Returns
        -------
        ForecastResult
            Result with ``samples`` of shape
            ``[n_draws, n_assets, n_horizons]``.

            Draws along axis 0 are i.i.d. across assets because each asset
            is fitted and sampled independently — there is **no** modelled
            cross-asset covariance.

        Notes
        -----
        **statsforecast path (optional):**

        1. ``pip install statsforecast``
        2. Import ``from statsforecast import StatsForecast`` and
           ``from statsforecast.models import AutoTheta, AutoARIMA``.
        3. For each asset in ``request.asset_ids``:

           a. Slice the panel up to ``request.asof``.
           b. Fit the chosen model.
           c. Call ``.predict_intervals()`` or simulate draws from the
              predictive distribution.
           d. Stack into axis 1 of the output ``samples`` array.

        **Offline fallback (default):** when ``statsforecast`` is not installed this
        adapter uses the shared Gaussian random-walk-with-drift forecaster
        (:meth:`~baselines.base.BaselineForecaster._gaussian_rw_samples`). It is the
        same idea as a degenerate Theta/ARIMA(0,1,0)-with-drift model: it estimates a
        per-asset drift and innovation volatility from the as-of-truncated series and
        propagates them forward. Joint draws are constructed by stacking independent
        per-asset samples, so cross-asset correlation in the draw matrix is ~zero.
        """
        try:
            import statsforecast  # noqa: F401  (presence check)

            _have_sf = True
        except ImportError:
            _have_sf = False

        samples = self._gaussian_rw_samples(request, seed=1)
        result = ForecastResult(
            samples=samples,
            asset_ids=request.asset_ids,
            horizons=request.horizons,
            model_name=self.model_name,
            metadata={
                "model": self._model,
                "season_length": self._season_length,
                # What produced these numbers. It is a Gaussian random walk in every case: the
                # import above is a presence check only (statsforecast is never called), so this
                # must not name the model. Reporting "statsforecast" here while returning
                # placeholder samples put a false provenance claim into the output metadata.
                "implementation": "gaussian-rw-placeholder",
                "real_adapter_implemented": False,
                "statsforecast_installed": _have_sf,
                "cross_asset_dependence": False,
            },
        )
        self.validate_output(result, request)
        return result
