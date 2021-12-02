#!/bin/bash

echo ""
echo "Sourcing functions from $(dirname "$0")/functions.sh ..."
source "$(dirname $0)/functions.sh"

cd "$PROJECT_DIR" || _error "Could not cd into $PROJECT_DIR"

# Detect operating system.
os_name=$(uname -s)
if [[ "$os_name" == Darwin* ]]; then
  os="$MAC_OS"
elif [[ "$os_name" == Linux* ]]; then
  os="$LINUX"
elif [[ "$os_name" == Windows* ]]; then
  os="$WINDOWS"
  # Exit without error:
  _print_red "
    This setup script must be run in a bash shell in Windows Subsystem for Linux (WSL):
    https://github.com/ModularHistory/modularhistory/wiki/Dev-Environment-Setup#windows-prereqs
  " && exit
else
  # Exit without error:
  _print_red "
    Unknown operating system: $os_name

    This script must be run from a bash shell on a supported operating system;
    see https://github.com/ModularHistory/modularhistory/wiki/Dev-Environment-Setup.
  " && exit
fi

poetry config virtualenvs.create true &>/dev/null
poetry config virtualenvs.in-project true &>/dev/null

# Initialize .venv with the correct Python version.
if [[ -d .venv ]]; then
  echo "Verifying the active Python version is $PYTHON_VERSION..."
  if [[ ! "$(.venv/bin/python --version)" =~ .*"$PYTHON_VERSION".* ]]; then
    echo "Destroying the existing .venv ..."
    rm -r .venv
  fi
else
  echo "Virtual environment does not yet exist at $(pwd)/.venv."
fi
[[ -d .venv ]] || {
  python -m venv .venv
  poetry env use "$HOME/.pyenv/versions/$PYTHON_VERSION/bin/python" &>/dev/null
}
[[ -d .venv ]] || {
  _error "Could not create .venv in $(pwd)."
}

# Activate the virtual environment.
echo ""
echo "Activating virtual environment ..."
set -a
# shellcheck disable=SC1091
source .venv/bin/activate
.venv/bin/activate
unset a
IN_VENV=$(python -c 'import sys; print ("1" if hasattr(sys, "real_prefix") else "0")')
if [[ "$IN_VENV" = 0 ]]; then
  _error "
    Failed to create and/or activate virtual environment.

    Python version: $(python --version) (expected: $PYTHON_VERSION)

    IN_VENV: $IN_VENV
    VIRTUAL_ENV: $VIRTUAL_ENV

    $(pwd)

    $(ls -a .venv)
  "
else
  echo "$VIRTUAL_ENV" | grep -q "$(pwd)" || {
    _error "
      Failed to activate virtual environment in $(pwd); instead, the active 
      virtual environment is $VIRTUAL_ENV.
    "
  }
fi
if [[ ! "$(python --version)" =~ .*"$PYTHON_VERSION".* ]]; then
  _error "Failed to activate Python $PYTHON_VERSION."
fi
echo "Virtual environment activated."

# Install project dependencies.
echo "Installing dependencies ..."
pip install --upgrade pip
if [[ "$os" == "$MAC_OS" ]]; then
  # https://cryptography.io/en/latest/installation.html#building-cryptography-on-macos
  # shellcheck disable=SC2155
  export LDFLAGS="-L$(brew --prefix openssl@1.1)/lib"
  # shellcheck disable=SC2155
  export CFLAGS="-I$(brew --prefix openssl@1.1)/include" 
fi
poetry install --no-root || {
  echo ""
  _print_red "Failed to install dependencies with Poetry."
  echo "Attempting workaround ..."
  # https://python-poetry.org/docs/cli/#export
  poetry export -f requirements.txt --without-hashes --dev -o requirements.txt
  pip install --upgrade pip
  # shellcheck disable=SC2015
  pip install -r requirements.txt && {
    rm requirements.txt
    echo "Installed dependencies with pip after failing to install with Poetry."
  } || {
    rm requirements.txt
    _print_red "Failed to install dependencies with pip."
  }
}
