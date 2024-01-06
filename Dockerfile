FROM python:3.11-slim-buster as builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/source \
    LANG=ru_RU.UTF-8 \
    LANGUAGE=ru_RU.UTF-8 \
    LC_ALL=ru_RU.UTF-8

RUN apt-get update && \
    pip install poetry virtualenv

WORKDIR /source

COPY poetry.lock pyproject.toml ./

RUN poetry export --output requirements.txt --without-hashes --with-credentials --only main
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /source/wheels -r requirements.txt


FROM python:3.11-slim-buster

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/secret_santa \
    LANG=ru_RU.UTF-8 \
    LANGUAGE=ru_RU.UTF-8 \
    LC_ALL=ru_RU.UTF-8

WORKDIR /secret_santa

RUN pip install --upgrade pip
COPY --from=builder /source/wheels /wheels
RUN pip install --no-cache /wheels/*

COPY migrations ./migrations
COPY src ./src
COPY README.md yoyo.ini ./

CMD ["python", "./src/main.py"]
