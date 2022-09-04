#!/bin/bash

set -a

RED='\033[0;31m'
NC='\033[0m'  # Reset
BOLD='\033[1m'
MAC_OS="MacOS"
LINUX="Linux"

PYTHON_VERSION="3.9.13"
export PYTHON_VERSION

unset a

function _print_red() {
  # Print a message with red text.
  # shellcheck disable=SC2059
  printf "${RED}$1${NC}\n"
}

function _error() {
  # Print a message with red text and exit the script with an error status (1).
  _print_red "$1" >&2; exit 1
}
