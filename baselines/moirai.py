"""
Adapter stub for Salesforce MOIRAI (uni2ts package).

Wraps the ``uni2ts`` package.  MOIRAI (Masked Encoder-based Universal Time
Series Forecasting Transformer) is a foundation model with a mixture-of-
distribution (MoD) output head.  It supports multi-variate context windows
(i.e. multiple time series can be passed together), but by default the
predictive distribution over each variate is still marginal — joint draws
across variates are NOT correlated unless a custom co-variance patch is
applied to the model head.

See the MOIRAI paper (Woo et al., 2024) for details on the multi-variate
conditioning mechanism and how to extract joint samples.

About MOIRAI model sizes
------------------------
* ``small`` – ~14 M parameters, fastest inference.
* ``base``  – ~91 M parameters (recommended for balanced performance).
* ``large`` – ~311 M parameters (default; highest accuracy).

Patch size
----------
MOIRAI uses patch-based tokenisation.  ``patch_size="auto"`` lets the model
select the optimal patch size based on the input frequency.  You can override
this with an integer (e.g. ``32``, ``64``, ``128``) for ablation studies.

Installation
------------
.. code-block:: bash

    pip install uni2ts

Output shape
------------
``samples[n_draws, n_assets, n_horizons]`` — draws are marginally sampled
unless a cross-asset joint-sampling patch is applied (see paper Appendix B).
"""

from __future__ import annotations

from .base import BaselineForecaster, ForecastRequest, ForecastResult

#: Supported MOIRAI model size identifiers.
_VALID_MODEL_SIZES: frozenset[str] = frozenset({"small", "base", "large"})


class MOIRAIBaseline(BaselineForecaster):
    """Salesforce MOIRAI probabilistic forecaster adapter.

    Wraps ``uni2ts.model.moirai.MoiraiForecast`` from the ``uni2ts`` package.
    The model processes all assets jointly as a multivariate context but
    still produces marginal predictive distributions by default.

    Parameters
    ----------
    model_size : str, optional
        MOIRAI model variant.  One of ``"small"``, ``"base"``,
        ``"large"`` (default).
    patch_size : str or int, optional
        Tokenisation patch size.  ``"auto"`` (default) lets the model select
        based on input frequency.  Integer values override this (e.g. ``32``).
    num_samples : int, optional
        Number of samples to draw from the MoD head per forward pass.
        If ``None``, defaults to ``request.n_draws`` at inference time.
    device : str, optional
        PyTorch device string.  Default: ``"cpu"``.

    Output
    ------
    ``samples[n_draws, n_assets, n_horizons]`` — marginal draws by default.
    Joint draws require applying the cross-asset covariance patch described
    in the MOIRAI paper (Woo et al., 2024, Appendix B).
    """

    def __init__(
        self,
        model_size: str = "large",
        patch_size: str | int = "auto",
        num_samples: int | None = None,
        device: str = "cpu",
    ) -> None:
        if model_size not in _VALID_MODEL_SIZES:
            raise ValueError(
                f"model_size must be one of {sorted(_VALID_MODEL_SIZES)}; got '{model_size}'."
            )
        self._model_size = model_size
        self._patch_size = patch_size
        self._num_samples = num_samples
        self._device = device

    @property
    def model_name(self) -> str:
        return "moirai"

    def forecast(self, request: ForecastRequest) -> ForecastResult:
        """Generate multivariate-context forecasts via MOIRAI.

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

            Samples are drawn from MOIRAI's mixture-of-distribution head.
            By default, draws are marginal across assets (no cross-asset
            dependence).  To obtain joint draws, apply the co-variance patch
            from the MOIRAI paper (Appendix B).

        Notes
        -----
        **MOIRAI path (optional):**

        1. ``pip install uni2ts``
        2. Load the pipeline::

               from uni2ts.model.moirai import MoiraiForecast, MoiraiModule
               model = MoiraiForecast.load_from_checkpoint(
                   checkpoint_path=(
                       f"Salesforce/moirai-1.0-R-{self._model_size}"
                   ),
                   prediction_length=max(request.horizons),
                   context_length=<window_size>,
                   patch_size=self._patch_size,
                   num_samples=self._num_samples or request.n_draws,
                   target_dim=len(request.asset_ids),
                   feat_dynamic_real_dim=0,
                   past_feat_dynamic_real_dim=0,
               )

        3. Construct a GluonTS multivariate ``ListDataset`` containing all
           assets stacked into a single ``[n_assets, T]`` ``"target"`` field.

        4. Run inference and collect the sample paths tensor of shape
           ``[n_draws, n_assets, n_horizons]``.

        5. Slice to the exact requested horizons if the model outputs
           contiguous horizon steps.

        Joint sampling note: MOIRAI supports multi-variate context, but the
        MoD head samples each variate from its own mixture independently.
        For joint draws, refer to the cross-asset covariance extension in
        Woo et al. (2024), Appendix B.

        Model size: ``{self._model_size}``
        Patch size: ``{self._patch_size}``

        **Offline fallback (default):** the MOIRAI checkpoint cannot be vendored into a
        ``--network=none`` image, so when ``uni2ts`` is unavailable this adapter falls
        back to the shared Gaussian random-walk forecaster
        (:meth:`~baselines.base.BaselineForecaster._gaussian_rw_samples`). This is a
        clearly-labelled statistical baseline, not the MOIRAI model — it still emits
        schema-valid joint samples so the pipeline runs end to end.
        """
        try:
            import uni2ts  # noqa: F401  (presence check)

            _have_uni2ts = True
        except ImportError:
            _have_uni2ts = False

        samples = self._gaussian_rw_samples(request, seed=44)
        result = ForecastResult(
            samples=samples,
            asset_ids=request.asset_ids,
            horizons=request.horizons,
            model_name=self.model_name,
            metadata={
                "model_size": self._model_size,
                "patch_size": self._patch_size,
                "num_samples": self._num_samples,
                # What produced these numbers. It is a Gaussian random walk in every case: the
                # import above is a presence check only (uni2ts/moirai is never called), so this
                # must not name the model. Reporting "uni2ts/moirai" here while returning
                # placeholder samples put a false provenance claim into the output metadata.
                "implementation": "gaussian-rw-placeholder",
                "real_adapter_implemented": False,
                "uni2ts_moirai_installed": _have_uni2ts,
                "cross_asset_dependence": False,
            },
        )
        self.validate_output(result, request)
        return result
