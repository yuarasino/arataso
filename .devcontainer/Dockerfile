FROM python:3.9

ENV LANG C.UTF-8
ENV TZ Asia/Tokyo
ENV PYTHONDONTWRITEBYTECODE 1


RUN set -ex \
  && pip install poetry \
  && poetry config virtualenvs.in-project true


WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN set -ex \
  && poetry install
