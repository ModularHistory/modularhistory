FROM python:3.7-buster

LABEL org.opencontainers.image.source https://github.com/ModularHistory/modularhistory

RUN apt-get update && apt-get install -y vim dnsutils

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
COPY . /modularhistory/

# Collect static files
RUN python manage.py collectstatic --no-input

# Expose port 8000
EXPOSE 8000

RUN chmod +x /modularhistory/config/wait-for-it.sh

# # Create non-root user
# RUN addgroup --gid $GROUP_ID modularhistory
# RUN adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID modularhistory

# Grant ownership to non-root user
RUN chown -R www-data:www-data /modularhistory

# Switch from root to non-root user
USER www-data
