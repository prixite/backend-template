FROM python:3-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc

RUN pip install pip==21.1.2

WORKDIR /opt/soccer

COPY prod/requirements.txt prod/requirements.txt

RUN pip install -r prod/requirements.txt

COPY . ./
