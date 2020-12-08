FROM python:3.7-buster

LABEL org.opencontainers.image.source https://github.com/ModularHistory/modularhistory

ENV \
  PYTHONUNBUFFERED=1 \
  PYTHONFAULTHANDLER=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

RUN pip install poetry

# Create necessary directories
RUN mkdir -p -- /modularhistory/static /modularhistory/media

# Set the working directory
WORKDIR /modularhistory

# Install project dependencies
COPY poetry.lock pyproject.toml /modularhistory/
RUN poetry config virtualenvs.create false && \
  poetry install --no-dev --no-interaction --no-ansi

# Add source code
COPY . /modularhistory

# Expose port 8000
EXPOSE 8000

# Grant ownership to www-data
RUN chown -R www-data:www-data /modularhistory

# Change user from root to www-data
USER www-data
