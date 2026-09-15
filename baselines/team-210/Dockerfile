# Agenthon 2026 Track 2 submission image.
#
# Self-contained: numpy and pandas are the whole runtime. The forecast is a
# block bootstrap over realised differences, so nothing here needs a foundation
# model or its weights - which also means this image is the text-blind floor the
# uplift claim gets measured against.
FROM python:3.13-slim

# Exact pins, not floors: api-category entries are verified by bootstrap-CI
# overlap on an organizer rerun, and a rebuild that silently picks up a new
# numpy can shift the sampler enough to fail its own verification.
RUN pip install --no-cache-dir "numpy==2.2.6" "pandas==2.3.1" "pyarrow==20.0.0"

WORKDIR /agent
COPY agent.py /agent/agent.py
COPY forecast_core/ /agent/forecast_core/

LABEL qfbench2.interface_version="2.0"

ENTRYPOINT ["python", "/agent/agent.py"]
# Runnable as-is: --asof is optional and falls back to the card's own
# data-end date (it used to be required=True, so the image's default CMD
# exited 2 with zero files).
CMD ["forecast", "--panels", "/input/panels/", "--text", "/input/text/", \
     "--out", "/output/forecast.parquet"]
