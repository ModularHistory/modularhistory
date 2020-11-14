FROM python:3.7-buster

ARG ENVIRONMENT

ENV \
  ENVIRONMENT=${ENVIRONMENT} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

RUN pip install poetry
RUN apt-get update
RUN apt-get install memcached libmemcached-tools -y
#RUN systemctl start memcached && systemctl enable memcached

EXPOSE 11211/tcp 11211/udp

RUN mkdir -p /src
WORKDIR /src
COPY poetry.lock pyproject.toml /src/

RUN poetry config virtualenvs.create false
RUN poetry install $(test "$ENVIRONMENT" == production && echo "--no-dev") --no-interaction --no-ansi

COPY . /src

EXPOSE 8000

COPY init.sh /usr/local/bin/
RUN chmod u+x /usr/local/bin/init.sh
ENTRYPOINT ["init.sh"]
