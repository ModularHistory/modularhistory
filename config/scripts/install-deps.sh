#!/bin/bash

RED='\033[0;31m'
NC='\033[0m'  # No Color
MAC_OS="MacOS"

function _print_red() {
  # Print a message with red text.
  # shellcheck disable=SC2059
  printf "${RED}$1${NC}\n"
}

# Detect operating system.
os_name=$(uname -s)
if [[ "$os_name" == Darwin* ]]; then
  os='MacOS'
elif [[ "$os_name" == Linux* ]]; then
  os='Linux'
elif [[ "$os_name" == Windows* ]]; then
  os='Windows'
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
  IN_VENV=$(python -c 'import sys; print ("1" if hasattr(sys, "real_prefix") else "0")')
  [[ "$IN_VENV" = 0 ]] || {
    _error "Failed to create and/or activate virtual environment."
  }
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
