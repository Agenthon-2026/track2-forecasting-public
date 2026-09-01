# QFBench 2.0 Track-2 reference submission image.
#
# Follows the shape the other tracks already use on the shared dev box: the verb is an
# executable on PATH, CMD is the verb plus --help so `docker run <img>` is self-describing,
# and the harness overrides argv with the real invocation.
#
#   docker build -t t2-reference:arm .
#   docker run --rm --network=none \
#     -v <unit>:/input:ro -v <out>:/output \
#     t2-reference:arm \
#     forecast --panels /input/panels/ --text /input/text/ --asof 2024-06-28 \
#              --out /output/forecast.parquet
#
# Builds and runs on linux/arm64 (verified on GH200) and linux/amd64.

# Python 3.13. `pyproject.toml` declares `requires-python = ">=3.13"` and CI runs 3.13; a 3.12 base
# here meant the image could not install the package it exists to run, and that contradiction sat
# unnoticed because nothing ever installed the package into the image.
FROM python:3.13-slim-bookworm

LABEL qfbench2.interface_version=2.0
LABEL qfbench2.track=forecasting
LABEL qfbench2.verb=forecast

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Pinned. The scorer's own CI was red for a week because a pinned type checker met an unpinned
# numpy; a submission image that floats its deps has the same failure mode with worse timing.
#
# `qfbench2-common` is required, not optional: `qfbench2_track_forecasting.limits` imports
# `qfbench2_common.contracts`, so an image without it BUILDS CLEANLY and then dies on the first
# `forecast` call. Measured before this line existed: build exit 0, `forecast --help` exit 1 with
# ModuleNotFoundError.
#
# Same repository and tag the README installs, in the TARBALL form rather than `git+https://`.
# That is deliberate: the base image is `python:3.13-slim-bookworm`, which ships no `git`, so the
# `git+` form fails at build time with "Cannot find command 'git'". The tarball needs no VCS
# client and no extra apt layer.
RUN pip install --no-cache-dir \
        "numpy==2.1.3" \
        "pandas==2.2.3" \
        "pyarrow==18.1.0" \
        "jsonschema==4.23.0" \
        "qfbench2-common @ https://github.com/Agenthon-2026/Agenthon2026-public/archive/refs/tags/v2.3.1.tar.gz#subdirectory=common"

WORKDIR /work
COPY qfbench2_track_forecasting /opt/qfbench2_track_forecasting
ENV PYTHONPATH=/opt

# The verb, as an executable on PATH.
RUN printf '#!/bin/sh\nexec python3 -m qfbench2_track_forecasting.cli "$@"\n' \
      > /usr/local/bin/forecast \
 && chmod +x /usr/local/bin/forecast

# Runs as a non-root user: the harness mounts /input read-only and /output writable, and nothing
# in this image needs to write anywhere else.
RUN useradd --create-home --uid 1000 runner
USER runner

CMD ["forecast", "--help"]
