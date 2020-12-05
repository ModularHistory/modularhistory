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

EXPOSE 8000
STOPSIGNAL SIGTERM
RUN chmod u+x /modularhistory/init.sh && chown -R modularhistory:modularhistory /modularhistory

# Change to non-root user
USER modularhistory

CMD ["/modularhistory/init.sh"]
