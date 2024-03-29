### First stage ###

FROM python:3.11-alpine as python-base

ENV PYTHONFAULTHANDLER=1 PYTHONUNBUFFERED=1

#RUN addgroup -g 1000 appuser && adduser -u 1000 -G appuser -h /home/appuser -D appuser
RUN adduser -h /home/appuser -D appuser

WORKDIR /.poetry-venv
WORKDIR /application
RUN chown -R appuser:appuser /application


### Second stage ###

FROM python-base as python-builder
ENV PIP_NO_CACHE_DIR=1
ENV PATH="/home/appuser/.local/bin:${PATH}"

#RUN apk add --update --no-cache pipx && pipx install poetry==1.7.1
RUN python -m venv /.poetry-venv && \
    /.poetry-venv/bin/pip install -U pip setuptools && \
    /.poetry-venv/bin/pip install poetry==1.7.1

# Copy python source code
COPY app/ /python-source/app
COPY poetry.lock /python-source/
COPY pyproject.toml /python-source/
COPY README.md /python-source

# This needs to be moved
COPY .env.example /python-source/
RUN mv /python-source/.env.example /python-source/.env

# Build python package
WORKDIR /python-source
RUN /.poetry-venv/bin/poetry config virtualenvs.in-project true \
    && /.poetry-venv/bin/poetry install --only=main --no-root --no-interaction --no-ansi \
    && /.poetry-venv/bin/poetry build


### Final stage ###

FROM python-base as python-final
COPY --from=python-builder /python-source/.venv /application/.venv
COPY --from=python-builder /python-source/dist /application/dist

RUN chown -R appuser:appuser /application

USER appuser
RUN python -m venv /application/.venv && \
    /application/.venv/bin/pip install /application/dist/*.whl

ENV PATH="/application/.venv/bin:${PATH}"
ENV VIRUTAL_ENV="/application/.venv"

# CMD ["uvicorn", "app.main:app", "--host"]
