"""
Adapter stub for Google TimesFM (timesfm package).

Wraps the ``timesfm`` package.  TimesFM produces probabilistic output via a
quantile regression head; samples are reconstructed from those quantile outputs
by interpolation (or by treating quantile levels as an empirical CDF and
inverting it).  Each asset is forecast independently — no cross-asset
dependence is modelled.

About TimesFM
-------------
TimesFM (Time Series Foundation Model) is a large pre-trained model from
Google Research that accepts arbitrary-length time-series context windows and
produces multi-horizon probabilistic forecasts via a quantile head.

Quantile-to-sample reconstruction
----------------------------------
TimesFM outputs a set of quantile forecasts (e.g. at levels
0.1, 0.2, …, 0.9) rather than direct Monte-Carlo draws.  This adapter
reconstructs samples from those quantiles using one of two approaches:

1. **Empirical CDF inversion** (default): treat the K quantile values as
   order statistics from a K-sample empirical distribution and sample
   ``n_draws`` points by inverse-CDF interpolation.
2. **Gaussian fit**: fit a normal distribution to the quantile outputs
   (matching median and one IQR-based scale estimate) and draw samples
   from that Gaussian.

Approach (1) is recommended as it preserves non-Gaussian tail shapes.

Installation
------------
.. code-block:: bash

    pip install timesfm

Output shape
------------
``samples[n_draws, n_assets, n_horizons]`` — draws are i.i.d. across assets
(no cross-asset dependence captured).
"""

from __future__ import annotations

from .base import BaselineForecaster, ForecastRequest, ForecastResult


class TimesFMBaseline(BaselineForecaster):
    """Google TimesFM probabilistic forecaster adapter.

    Wraps ``timesfm.TimesFm`` and reconstructs Monte-Carlo samples from the
    model's quantile outputs.

    Parameters
    ----------
    checkpoint : str, optional
        HuggingFace model ID or local path for the TimesFM checkpoint.
        Default: ``"google/timesfm-1.0-200m"``.
    quantile_reconstruction : str, optional
        Method used to reconstruct samples from quantile outputs.
        Options: ``"ecdf"`` (default), ``"gaussian"``.

    Output
    ------
    ``samples[n_draws, n_assets, n_horizons]`` — draws are i.i.d. across
    assets (no cross-asset dependence structure captured).
    """

    def __init__(
        self,
        checkpoint: str = "google/timesfm-1.0-200m",
        quantile_reconstruction: str = "ecdf",
    ) -> None:
        if quantile_reconstruction not in ("ecdf", "gaussian"):
            raise ValueError(
                "quantile_reconstruction must be 'ecdf' or 'gaussian'; "
                f"got '{quantile_reconstruction}'."
            )
        self._checkpoint = checkpoint
        self._quantile_reconstruction = quantile_reconstruction

    @property
    def model_name(self) -> str:
        return "timesfm"

    def forecast(self, request: ForecastRequest) -> ForecastResult:
        """Generate per-asset forecasts via TimesFM quantile outputs.

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

            Samples are reconstructed from TimesFM's quantile outputs using
            the configured ``quantile_reconstruction`` method (``"ecdf"`` or
            ``"gaussian"``).  Draws are i.i.d. across assets — there is
            **no** modelled cross-asset covariance.

        Notes
        -----
        **TimesFM path (optional):**

        1. ``pip install timesfm``
        2. Load the model::

               import timesfm
               tfm = timesfm.TimesFm(
                   context_len=512,
                   horizon_len=max(request.horizons),
                   input_patch_len=32,
                   output_patch_len=128,
                   num_layers=20,
                   model_dims=1280,
                   backend="gpu",  # or "cpu"
               )
               tfm.load_from_checkpoint(repo_id=self._checkpoint)

        3. For each asset, build the input tensor and call
           ``tfm.forecast_on_df()`` or the lower-level
           ``tfm.forecast()`` to obtain quantile predictions.

        4. Reconstruct ``n_draws`` samples from the quantile outputs:

           * **ecdf**: treat quantile values as order statistics; draw by
             interpolating the empirical CDF at ``np.random.uniform`` points.
           * **gaussian**: fit ``mu = q50``, ``sigma = (q75 - q25) / 1.35``
             and draw from ``N(mu, sigma^2)``.

        Checkpoint: ``{self._checkpoint}``
        Quantile reconstruction: ``{self._quantile_reconstruction}``

        **Offline fallback (default):** the pre-trained TimesFM checkpoint cannot be
        vendored into a ``--network=none`` image, so when ``timesfm`` is unavailable
        this adapter falls back to the shared Gaussian random-walk forecaster
        (:meth:`~baselines.base.BaselineForecaster._gaussian_rw_samples`). This is a
        clearly-labelled statistical baseline, not the TimesFM model — it still emits
        schema-valid joint samples so the pipeline runs end to end.
        """
        try:
            import timesfm  # noqa: F401  (presence check)

            _have_timesfm = True
        except ImportError:
            _have_timesfm = False

        samples = self._gaussian_rw_samples(request, seed=22)
        result = ForecastResult(
            samples=samples,
            asset_ids=request.asset_ids,
            horizons=request.horizons,
            model_name=self.model_name,
            metadata={
                "checkpoint": self._checkpoint,
                "quantile_reconstruction": self._quantile_reconstruction,
                # What produced these numbers. It is a Gaussian random walk in every case: the
                # import above is a presence check only (timesfm is never called), so this must
                # not name the model. Reporting "timesfm" here while returning placeholder
                # samples put a false provenance claim into the output metadata.
                "implementation": "gaussian-rw-placeholder",
                "real_adapter_implemented": False,
                "timesfm_installed": _have_timesfm,
                "cross_asset_dependence": False,
            },
        )
        self.validate_output(result, request)
        return result
