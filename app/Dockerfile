### Base python stage ###

FROM python:3.11-alpine as base

ENV PYTHONFAULTHANDLER=1 PYTHONUNBUFFERED=1

#RUN addgroup -g 1000 appuser && adduser -u 1000 -G appuser -h /home/appuser -D appuser
RUN adduser -h /home/appuser -D appuser

WORKDIR /.poetry-venv
WORKDIR /application
RUN chown -R appuser:appuser /application


### Development and build stage ###

FROM base as builder
ENV PIP_NO_CACHE_DIR=1
ENV PATH="/home/appuser/.local/bin:${PATH}"

#RUN apk add --update --no-cache pipx && pipx install poetry==1.7.1
RUN python -m venv /.poetry-venv && \
    /.poetry-venv/bin/pip install -U pip setuptools && \
    /.poetry-venv/bin/pip install poetry==1.7.1

# Copy python source code
COPY ./ /python-source/app
RUN mv /python-source/app/poetry.lock /python-source/ \
    && mv /python-source/app/pyproject.toml /python-source/

# Install dependencies, optionally build for production
WORKDIR /python-source
ARG BUILD_PRODUCTION
RUN if [ "$BUILD_PRODUCTION" = "true" ]; then \
/.poetry-venv/bin/poetry config virtualenvs.in-project true \
    && /.poetry-venv/bin/poetry install --only=main --no-root --no-interaction --no-ansi \
    && /.poetry-venv/bin/poetry build; else \
    /.poetry-venv/bin/poetry install --no-root --no-interaction --no-ansi; \
    fi


### Production stage ###

FROM base as production
COPY --from=builder /python-source/.venv /application/.venv
COPY --from=builder /python-source/dist /application/dist

RUN chown -R appuser:appuser /application

USER appuser
ENV PATH="/application/.venv/bin:/application/${USER}:/.local/bin:${PATH}"
ENV VIRTUAL_ENV="/application/.venv"

RUN python -m venv /application/.venv \
    && python -m pip install /application/dist/*.whl \
    && mv /application/.venv/lib/python3.11/site-packages/app /application/
COPY --from=builder /python-source/.env /application/

EXPOSE 8000
CMD ["python", "-m", "app.main"]
