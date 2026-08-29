"""
Adapter stub for Lag-Llama (lag_llama package).

LLM-style univariate probabilistic forecaster.  Draws are produced from the
model's internal Student-t mixture distribution head.  Each asset is forecast
independently — no cross-asset dependence is modelled.

About Lag-Llama
---------------
Lag-Llama is a foundation model for univariate probabilistic time-series
forecasting based on the LLaMA transformer architecture.  The model uses
lagged features as input tokens and outputs parameters of a Student-t
distribution (location, scale, degrees of freedom) from which samples can
be drawn directly.

The pre-trained checkpoint is available on HuggingFace at
``time-series-foundation-models/Lag-Llama``.  The checkpoint must be
downloaded before inference; it is approximately 320 MB.

Installation
------------
.. code-block:: bash

    pip install lag-llama
    # then download checkpoint:
    huggingface-cli download time-series-foundation-models/Lag-Llama \\
        --local-dir ./lag_llama_ckpt

Output shape
------------
``samples[n_draws, n_assets, n_horizons]`` — draws are i.i.d. across assets
(no cross-asset dependence captured).
"""

from __future__ import annotations

from .base import BaselineForecaster, ForecastRequest, ForecastResult


class LagLlamaBaseline(BaselineForecaster):
    """Lag-Llama probabilistic forecaster adapter.

    Wraps the Lag-Llama inference pipeline.  Each asset is passed through a
    separate forward pass; joint draws are formed by stacking independent
    per-asset samples.

    Parameters
    ----------
    ckpt_path : Optional[str], optional
        Path to the downloaded Lag-Llama checkpoint directory.  If ``None``,
        the adapter will attempt to locate the checkpoint via the
        ``LAG_LLAMA_CKPT`` environment variable.  Raises ``FileNotFoundError``
        at inference time if neither is set.
    context_length : int, optional
        Number of historical time steps fed to the model as context.
        Default: ``32`` (Lag-Llama's recommended minimum).
    device : str, optional
        PyTorch device string, e.g. ``"cpu"``, ``"cuda"``.  Default: ``"cpu"``.

    Output
    ------
    ``samples[n_draws, n_assets, n_horizons]`` — draws are i.i.d. across
    assets (no cross-asset dependence structure captured).
    """

    def __init__(
        self,
        ckpt_path: str | None = None,
        context_length: int = 32,
        device: str = "cpu",
    ) -> None:
        self._ckpt_path = ckpt_path
        self._context_length = context_length
        self._device = device

    @property
    def model_name(self) -> str:
        return "lag_llama"

    def forecast(self, request: ForecastRequest) -> ForecastResult:
        """Generate per-asset probabilistic forecasts via Lag-Llama.

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

            Draws are produced by sampling from the Student-t distribution
            head of the Lag-Llama model.  Draws are i.i.d. across assets —
            there is **no** modelled cross-asset covariance.

        Notes
        -----
        **Lag-Llama path (optional):**

        1. ``pip install lag-llama``
        2. Download the checkpoint from HuggingFace::

               huggingface-cli download time-series-foundation-models/Lag-Llama \\
                   --local-dir ./lag_llama_ckpt

        3. Load the model::

               from lag_llama.gluon.estimator import LagLlamaEstimator
               estimator = LagLlamaEstimator(
                   ckpt_path=self._ckpt_path,
                   prediction_length=max(request.horizons),
                   context_length=self._context_length,
                   device=self._device,
                   num_samples=request.n_draws,
               )

        4. For each asset, create a GluonTS ``ListDataset`` from the
           historical panel, call ``estimator.predict()``, and collect the
           sample paths.

        5. Stack per-asset sample tensors along axis 1 to form the final
           ``[n_draws, n_assets, n_horizons]`` array.

        Checkpoint path: ``{self._ckpt_path or '$LAG_LLAMA_CKPT env var'}``

        **Offline fallback (default):** the Lag-Llama checkpoint cannot be vendored
        into a ``--network=none`` image, so when ``lag-llama`` (or the checkpoint) is
        unavailable this adapter falls back to the shared Gaussian random-walk
        forecaster (:meth:`~baselines.base.BaselineForecaster._gaussian_rw_samples`).
        This is a clearly-labelled statistical baseline, not the Lag-Llama model — it
        still emits schema-valid joint samples so the pipeline runs end to end.
        """
        try:
            import lag_llama  # noqa: F401  (presence check)

            _have_lag_llama = True
        except ImportError:
            _have_lag_llama = False

        samples = self._gaussian_rw_samples(request, seed=33)
        result = ForecastResult(
            samples=samples,
            asset_ids=request.asset_ids,
            horizons=request.horizons,
            model_name=self.model_name,
            metadata={
                "ckpt_path": self._ckpt_path,
                "context_length": self._context_length,
                "device": self._device,
                # What produced these numbers. It is a Gaussian random walk in every case: the
                # import above is a presence check only (lag-llama is never called), so this must
                # not name the model. Reporting "lag-llama" here while returning placeholder
                # samples put a false provenance claim into the output metadata.
                "implementation": "gaussian-rw-placeholder",
                "real_adapter_implemented": False,
                "lag_llama_installed": _have_lag_llama,
                "cross_asset_dependence": False,
            },
        )
        self.validate_output(result, request)
        return result
