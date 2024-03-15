### First stage ###

FROM python:3.11-alpine as base

ENV PYTHONFAULTHANDLER=1 PYTHONUNBUFFERED=1

RUN addgroup -g 1000 appuser \
    && adduser -u 1000 -G appuser -h /home/appuser -D appuser

WORKDIR /application
RUN chown -R appuser:appuser /application


### Second stage ###

FROM base as builder
ENV PIP_NO_CACHE_DIR=1
ENV PATH="/home/appuser/.local/bin:${PATH}"

RUN apk add --update --no-cache pipx && pipx install poetry==1.7.1

COPY ./* /application/app
COPY ../poetry.lock /application/
COPY ../pyproject.toml /application/

# this needs to be moved
COPY ../.env.example /application/
RUN mv .env.example .env

WORKDIR /application/app
RUN poetry config virtualenv.in-project true \
    && poetry install --only=main --no-root --no-interaction --no-ansi \
    && poetry build


### Final stage ###

FROM base as final
COPY --from=builder /application/app/.venv /application/app/.venv
COPY --from=builder /application/app/dist /application/app/dist

RUN chow -R appuser:appuser /application
USER appuser
RUN ./.venv/bin/pip install /application/app/dist/*.whl

ENV PATH="/application/app/.venv/bin:${PATH}"
ENV VIRUTAL_ENV="/application/app/.venv"

CMD ["uvicorn", "app.main:app", "--host"]
