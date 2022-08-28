FROM python:3.9-slim AS base
    # Prevents Python from writing .pycr files
ENV PYTHONDONTWRITEBYTECODE=1 \
    # Turns off buffering for easier container logging
    PYTHONUNBUFFERED=1 \
    # Enable randomized Hashs (security related)
    PYTHONHASHSEED=random \
    # Enables Segmentation fault Handler (extensive logs if C failure)
    PYTHONFAULTHANDLER=1

FROM base as builder
    # turn off cache directory logs
ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VERSION=1.1.5 \
    PIP_VERSION=22.1.2

COPY pyproject.toml poetry.lock /

RUN python -m pip install pip==$PIP_VERSION \
    && pip install "poetry==$POETRY_VERSION" \
    && poetry export --without-hashes --no-interaction --no-ansi -f requirements.txt -o requirements.txt \
    && pip install --prefix=/runtime --force-reinstall -r requirements.txt

FROM base as final

COPY --from=builder /runtime /usr/local
WORKDIR /app
COPY main.py /app

RUN useradd -N -M app-user && \
    chown -R app-user /app

USER app-user

ENTRYPOINT ["python3", "main.py"]
CMD ["--help"]
