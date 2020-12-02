FROM python:3.7-buster

ARG ENVIRONMENT=production

RUN apt-get update && apt-get install -y vim nginx

COPY nginx.default /etc/nginx/sites-available/default

RUN ln -sf /dev/stdout /var/log/nginx/access.log && \
  ln -sf /dev/stderr /var/log/nginx/error.log

ENV \
  ENVIRONMENT=${ENVIRONMENT} \
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
  poetry install $(test "$ENVIRONMENT" = production && echo "--no-dev") \
  --no-interaction --no-ansi

# Add source code
COPY . /modularhistory
RUN chown -R www-data:www-data /modularhistory

EXPOSE 8000
STOPSIGNAL SIGTERM
COPY init.sh /usr/local/bin/
RUN chmod u+x /usr/local/bin/init.sh

# Change to non-root user
USER www-data

CMD ["init.sh"]
