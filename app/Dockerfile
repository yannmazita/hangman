### Base stage ###

FROM python:3.11-alpine as base

ARG WORKDIR
ARG BUILD_PRODUCTION
ENV PYTHONFAULTHANDLER=1 PYTHONUNBUFFERED=1

RUN adduser -h /home/appuser -D appuser
USER appuser
ENV PATH="/home/appuser/.local/bin:${PATH}"
WORKDIR ${WORKDIR}/.venv
WORKDIR ${WORKDIR}/code


### Builder stage for development ###

FROM base as builder-dev
ENV PIP_NO_CACHE_DIR=1
# Install pip, poetry and dev dependencies
RUN python -m venv ${WORKDIR}/.venv && \
    ${WORKDIR}/.venv/bin/pip install -U pip setuptools && \
    ${WORKDIR}/.venv/bin/pip install poetry==1.7.1
COPY --chown=appuser:appuser pyproject.toml poetry.lock ${WORKDIR}/code
RUN if [[ "${BUILD_PRODUCTION}" != "true" ]]; then \
    ${WORKDIR}/.venv/bin/poetry install --no-root --no-interaction --no-ansi; \
    fi


### Builder stage for production ###

FROM builder-dev as builder-prod

# Copy python source code
COPY --chown=appuser:appuser app ${WORKDIR}/code/app
COPY --chown=appuser:appuser README.md .env ${WORKDIR}/code
# Install prod dependencies and build
WORKDIR ${WORKDIR}/code
RUN ${WORKDIR}/.venv/bin/poetry install --only=main --no-root --no-interaction --no-ansi && \
    ${WORKDIR}/.venv/bin/poetry build


### Production stage ###

FROM base as production
# Copy application
COPY --chown=appuser:appuser --from=builder-prod ${WORKDIR}/code/dist ${WORKDIR}/dist
COPY --chown=appuser:appuser --from=builder-prod ${WORKDIR}/code/app ${WORKDIR}/code/app

RUN python -m venv ${WORKDIR}/.venv && \
    ${WORKDIR}/.venv/bin/pip install ${WORKDIR}/dist/*.whl
