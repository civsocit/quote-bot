FROM python:3.8-buster

COPY . /app

WORKDIR /app

RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry install --no-dev --no-root

CMD ["poetry", "run", "bot"]
