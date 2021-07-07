FROM python:3

ENV LANG C.UTF-8
ENV TZ Asia/Tokyo

RUN set -ex \
  && pip install poetry \
  && poetry config virtualenvs.in-project true


WORKDIR /app

ENV PYTHONPATH /app/src

COPY pyproject.toml poetry.lock ./

RUN set -ex \
  && poetry install
