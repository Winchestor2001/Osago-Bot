FROM python:3.10.12

ENV PYTHONUNBUFFERED 1

WORKDIR /bot

COPY req.txt /bot/req.txt

RUN pip install --no-cache-dir -r req.txt

COPY . .
