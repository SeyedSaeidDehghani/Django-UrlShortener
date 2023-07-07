FROM python:3.10-slim-buster
LABEL authors="saeid"

WORKDIR /app

COPY ./requirements.txt /app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY ./core /app