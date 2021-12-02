#!/bin/bash

RED='\033[0;31m'
NC='\033[0m'  # No Color
BOLD=$(tput bold)
MAC_OS="MacOS"
LINUX="Linux"

function _print_red() {
  # Print a message with red text.
  # shellcheck disable=SC2059
  printf "${RED}$1${NC}\n"
}

function _error() {
  # Print a message with red text and exit the script with an error status (1).
  _print_red "$1" >&2; exit 1
}
