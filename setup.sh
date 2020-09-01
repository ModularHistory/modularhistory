#!/bin/bash

cd "$(dirname "$0")" || exit 1

# If not running in Google Cloud App Engine
if [ -z "${GAE_APPLICATION}" ]; then
  # Try activating virtual Python environment
  {
    echo "Activating virtual Python environment..."
    find . -name '*env' -maxdepth 1 -type d -exec bash -c 'source "$1"/bin/activate' sh {} \;
  } || {
    echo "Unable to activate virtual Python environment."
    echo "Create a virtual Python environment (named .venv, .env, venv, or env) in your project root, "
    echo "then rerun this script."
    exit 1
  }
  echo ""

  # Install Poetry
  poetry_version=$(poetry --version) &>/dev/null
  if [ -n "$poetry_version" ]; then
    poetry self update &>/dev/null || pip install -U poetry
  else
    {
      echo "Installing Poetry..."
      curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
      echo "Sourcing Poetry environment..."
      # shellcheck source=/dev/null
      source "$HOME/.poetry/env"
      echo ""
    } || {
      echo "Unable to use Poetry's custom installer; falling back on pip..."
      pip install -U poetry
      echo ""
    }
    echo "Unable to use Poetry's custom installer; falling back on pip..."
    pip install -U poetry
    echo ""
    poetry_version=$(poetry --version)
    if [ -z "$poetry_version" ]; then
      echo "Error: Unable to install Poetry."
      exit 1
    fi
  fi
  echo "Using $poetry_version"

  # Prevent Poetry from creating virtual environments;
  # this is essential to avoid errors in GitHub builds.
  poetry config virtualenvs.create false
  poetry config --list
  echo ""

  # Create requirements.txt in case of manual deploys
  echo "Exporting requirements.txt..."
  if [ -f "requirements.txt" ]; then
    rm requirements.txt
  fi
  poetry export -f requirements.txt > requirements.txt
  # Remove hashes from requirements.txt so Google Cloud can read the file correctly
  sed -e '/--hash/d' -e 's/ \\//g' ./requirements.txt > requirements.tmp && mv requirements.tmp requirements.txt
  echo ""

  # Install dependencies
  echo "Installing dependencies..."
  poetry install || pip install -r requirements.txt
  echo ""

  # Run database migrations
  if [ -z "${USE_PROD_DB}" ]; then
    echo "Running database migrations..."
    python manage.py migrate
    echo ""
  fi
fi
