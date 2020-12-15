FROM python:3.9.1-buster

LABEL org.opencontainers.image.source https://github.com/ModularHistory/modularhistory

# Add PostgreSQL repo
RUN wget --quiet https://www.postgresql.org/media/keys/ACCC4CF8.asc && \
  apt-key add ACCC4CF8.asc && \
  sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ buster-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'

# Install packages
RUN apt-get update && apt-get install -y --no-install-recommends \
  dnsutils gnupg2 libenchant-dev postgresql-client-common postgresql-client-13 vim && \
  apt-get clean && rm -rf /var/lib/apt/lists/*

# Set environment vars
ENV \
  PYTHONUNBUFFERED=1 \
  PYTHONFAULTHANDLER=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

RUN pip install "poetry>=1.0.5"

# Create required directories
RUN mkdir -p -- /modularhistory/static /modularhistory/media /modularhistory/.backups

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

# Grant necessary permissions to non-root user
RUN chown -R www-data:www-data /modularhistory && \
  chmod g+w -R /modularhistory/media && \
  chmod g+w -R /modularhistory/.backups && \
  chmod +x /modularhistory/config/wait-for-it.sh

# Expose port 8000
EXPOSE 8000

# Switch from root to non-root user
USER www-data
