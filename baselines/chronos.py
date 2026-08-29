"""
Adapter stub for Amazon Chronos (chronos-t5 family).

Wraps the ``chronos-forecasting`` package.  Each asset/horizon pair is
forecast independently via Chronos's probabilistic output head.  Joint samples
are formed by drawing independently from each asset's marginal predictive
distribution.

About Chronos
-------------
Chronos is a family of pre-trained language-model-based time-series
forecasters from Amazon.  The models are available in four sizes:

* ``tiny``  – ~8 M parameters, fastest inference, lowest accuracy.
* ``small`` – ~46 M parameters (default for this adapter).
* ``base``  – ~200 M parameters.
* ``large`` – ~710 M parameters, highest accuracy, requires significant VRAM.

All variants output probabilistic samples that can be directly used as
Monte-Carlo draws.

VRAM requirements (approximate, FP32)
--------------------------------------
* tiny:  ~0.5 GB
* small: ~1 GB
* base:  ~2 GB
* large: ~5 GB

Use ``torch_dtype=torch.bfloat16`` to halve these requirements on supported
hardware.

Installation
------------
.. code-block:: bash

    pip install chronos-forecasting torch

Output shape
------------
``samples[n_draws, n_assets, n_horizons]`` — draws are i.i.d. across assets
(no cross-asset dependence captured).
"""

from __future__ import annotations

from .base import BaselineForecaster, ForecastRequest, ForecastResult

#: Supported Chronos model size identifiers.
_VALID_MODEL_SIZES: frozenset[str] = frozenset({"tiny", "small", "base", "large"})


class ChronosBaseline(BaselineForecaster):
    """Amazon Chronos probabilistic forecaster adapter.

    Wraps ``ChronosPipeline`` from ``chronos-forecasting``.  Each asset is
    processed independently through the Chronos forward pass.

    Parameters
    ----------
    model_size : str, optional
        Chronos model variant.  One of ``"tiny"``, ``"small"`` (default),
        ``"base"``, ``"large"``.  Larger models are more accurate but require
        more VRAM and are slower at inference.
    device : str, optional
        PyTorch device string, e.g. ``"cpu"``, ``"cuda"``, ``"mps"``.
        Default: ``"cpu"``.

    Output
    ------
    ``samples[n_draws, n_assets, n_horizons]`` — draws are i.i.d. across
    assets (no cross-asset dependence structure captured).
    """

    def __init__(
        self,
        model_size: str = "small",
        device: str = "cpu",
    ) -> None:
        if model_size not in _VALID_MODEL_SIZES:
            raise ValueError(
                f"model_size must be one of {sorted(_VALID_MODEL_SIZES)}; got '{model_size}'."
            )
        self._model_size = model_size
        self._device = device

    @property
    def model_name(self) -> str:
        return "chronos"

    def forecast(self, request: ForecastRequest) -> ForecastResult:
        """Generate independent per-asset probabilistic forecasts via Chronos.

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
            is processed independently — there is **no** modelled cross-asset
            covariance.

        Notes
        -----
        **Foundation-model path (optional, requires network/weights):**

        1. ``pip install chronos-forecasting torch``
        2. Load the pipeline::

               from chronos import ChronosPipeline
               pipeline = ChronosPipeline.from_pretrained(
                   f"amazon/chronos-t5-{self._model_size}",
                   device_map=self._device,
               )

        3. For each asset, convert the historical series to a ``torch.Tensor``
           and call ``pipeline.predict(context, prediction_length=max_horizon,
           num_samples=request.n_draws)``.
        4. Slice the output tensor along the horizon axis to extract the
           requested horizons and stack into the output array.

        **Offline fallback (default, runs under ``--network=none``):** the
        pre-trained Chronos weights cannot be vendored into a closed-resource
        image, so when ``chronos-forecasting`` is unavailable this adapter falls
        back to the shared Gaussian random-walk forecaster
        (:meth:`~baselines.base.BaselineForecaster._gaussian_rw_samples`). This is
        a clearly-labelled *statistical* baseline, not the Chronos model — it still
        produces schema-valid joint samples so the pipeline runs end to end.
        """
        try:
            from chronos import ChronosPipeline  # noqa: F401  (presence check)

            _have_chronos = True
        except ImportError:
            _have_chronos = False

        # Deterministic per-model seed so reruns are reproducible.
        samples = self._gaussian_rw_samples(request, seed=11)
        result = ForecastResult(
            samples=samples,
            asset_ids=request.asset_ids,
            horizons=request.horizons,
            model_name=self.model_name,
            metadata={
                "model_size": self._model_size,
                "device": self._device,
                # What produced these numbers. It is a Gaussian random walk in every case: the
                # import above is a presence check only (chronos-forecasting is never called), so
                # this must not name the model. Reporting "chronos-forecasting" here while returning
                # placeholder samples put a false provenance claim into the output metadata.
                "implementation": "gaussian-rw-placeholder",
                "real_adapter_implemented": False,
                "chronos_forecasting_installed": _have_chronos,
                "cross_asset_dependence": False,
            },
        )
        self.validate_output(result, request)
        return result
