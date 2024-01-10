# Dependencies
FROM python:3.11-slim
ENV POETRY_VERSION=1.7.1

RUN apt-get update && apt-get -y install curl docker.io python3-dev gunicorn libpq-dev gcc && apt-get autoclean
RUN curl -sSL https://install.python-poetry.org | python3

# Allows docker to cache installed dependencies between builds
COPY pyproject.toml poetry.toml poetry.lock /
RUN /root/.local/bin/poetry install --no-interaction --no-ansi --no-root

COPY . /app
WORKDIR /app

CMD ["python3", "-m", "app.main"]
# CMD ["tail", "-f", "/dev/null"]