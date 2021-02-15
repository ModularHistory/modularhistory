#!/bin/bash

RED='\033[0;31m'
NC='\033[0m' # No Color

MAC_OS="MacOS"
LINUX="Linux"

function error() {
  # shellcheck disable=SC2059
  printf "${RED}$1${NC}" && echo ""
}

function usage() {
  cat - >&2 <<EOF
NAME
    setup.sh - Setup script for ModularHistory development

SYNOPSIS
    setup.sh [-h|--help]
    setup.sh
    setup.sh [--noninteractive] [--no-installation]

OPTIONS
  -h, --help
      Prints this and exits

  --noninteractive
      Option that makes the script run without user input

  --skip-dependencies
      Option that makes the script skip installing dependencies with Poetry/Pip

  --skip-dev-dependencies
      Option that makes the script skip installing dev dependencies with Poetry/Pip

  --
      Specify end of options; useful if the first non option
      argument starts with a hyphen

EOF
}

function fatal() {
  for i; do
    echo -e "${i}" >&2
  done
  exit 1
}

# For long option processing
function next_arg() {
  if [[ $OPTARG == *=* ]]; then
    # for cases like '--opt=arg'
    OPTARG="${OPTARG#*=}"
  else
    # for cases like '--opt arg'
    OPTARG="${args[$OPTIND]}"
    OPTIND=$((OPTIND + 1))
  fi
}

# ':' means preceding option character expects one argument, except
# first ':' which make getopts run in silent mode. We handle errors with
# wildcard case catch. Long options are considered as the '-' character
optspec=":hfb:-:"
args=("" "$@") # dummy first element so $1 and $args[1] are aligned
while getopts "$optspec" optchar; do
  case "$optchar" in
  h)
    usage
    exit 0
    ;;
  -) # long option processing
    case "$OPTARG" in
    help)
      usage
      exit 0
      ;;
    noninteractive)
      noninteractive=true
      ;;
    skip-dependencies)
      skip_dependencies=true
      ;;
    skip-dev-dependencies)
      skip_dev_dependencies=true
      ;;
    -) break ;;
    *) fatal "Unknown option '--${OPTARG}'" "See '${0} --help' for usage" ;;
    esac
    ;;
  *) fatal "Unknown option: '-${OPTARG}'" "See '${0} --help' for usage" ;;
  esac
done

shift $((OPTIND - 1))

if [[ "$noninteractive" == true ]]; then
  interactive=false
else
  interactive=true
fi

# Detect operating system
os_name=$(uname -s)
if [[ "$os_name" == Darwin* ]]; then
  os='MacOS'
elif [[ "$os_name" == Linux* ]]; then
  os='Linux'
elif [[ "$os_name" == Windows* ]]; then
  os='Windows'
else
  error "Detected unknown operating system."
  exit 1
fi
echo "Detected $os."

# Update package managers
echo "Checking package manager..."
if [[ "$os" == "$MAC_OS" ]]; then
  # Install/update Homebrew
  brew help &>/dev/null || {
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
  }
  echo "Updating packages..."
  brew update
  brew tap homebrew/services
elif [[ "$os" == "$LINUX" ]]; then
  sudo apt update -y && 
  sudo apt upgrade -y &&
  sudo apt install -y \
  make \
  build-essential \
  libssl-dev \
  zlib1g-dev \
  libbz2-dev \
  libreadline-dev \
  libsqlite3-dev \
  wget \
  curl \
  llvm \
  libncurses5-dev \
  libncursesw5-dev \
  xz-utils \
  tk-dev \
  libffi-dev \
  liblzma-dev \
  python-openssl \
  git
fi

# Enter the project
cd "$(dirname "$0")" && echo "Running in $(pwd)..." || exit 1

# Create directories for db backups, static files, and media files
mkdir -p .backups static media &>/dev/null

# If running with sudo, source .bashrc explicitly
if [ "$EUID" -e 0 ]; then
  source "$HOME/.bashrc"
fi

# Make sure pyenv is installed
echo "Checking for pyenv..."
pyenv --version &>/dev/null || {
  if [[ "$os" == "$MAC_OS" ]]; then
    brew install pyenv
    echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >>~/.bash_profile
  elif [[ "$os" == "$LINUX" ]]; then
    error "Install and configure pyenv (https://github.com/pyenv/pyenv), then rerun this script."
    exit 1
  fi
}
echo "Using $(pyenv --version)..."
echo "Installing required Python versions..."
while IFS= read -r pyversion; do
  if [[ -n $pyversion ]]; then
    pyenv install "$pyversion"
  fi
done < .python-version

# Make sure correct version of Python is used
echo "Checking Python version..."
python --version &>/dev/null || {
  error "Could not detect Python. Install Python 3.7 and rerun this script."
  exit 1
}
echo "Using $(python --version)..."

# Make sure Pip is installed
pip --version &>/dev/null || {
  error "Pip is not installed; unable to proceed."
  exit 1
}

# Install Poetry
poetry --version &>/dev/null || {
  echo "Installing Poetry..."
  # https://python-poetry.org/docs/#osx-linux-bashonwindows-install-instructions
  curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python &>/dev/null
  # shellcheck source=/dev/null
  source "$HOME/.poetry/env"
  poetry --version &>/dev/null || {
    echo "Unable to use Poetry's custom installer; falling back on pip..."
    # Update Pip
    pip install --upgrade pip &>/dev/null
    # Install Poetry with Pip
    pip install -U poetry
  }
  poetry_version=$(poetry --version)
  if [ -z "$poetry_version" ]; then
    echo "Error: Unable to install Poetry."
    exit 1
  fi
}
poetry self update &>/dev/null
echo "Using $(poetry --version)..."

# https://python-poetry.org/docs/configuration/
poetry config virtualenvs.create true
poetry config virtualenvs.in-project true

if [[ ! "$skip_dependencies" == true ]]; then
  # Install dependencies with Poetry
  echo "Installing dependencies..."
  if [[ "$skip_dev_dependencies" == true ]]; then
    poetry install --no-dev --no-root || {
      error "Failed to install dependencies with Poetry."
      exit 1
    }
  else
    poetry install --no-root
  fi
fi

rclone version &>/dev/null || {
  curl https://rclone.org/install.sh | sudo bash
}
mkdir -p $HOME/.config/rclone
cp config/rclone/rclone.conf $HOME/.config/rclone/rclone.conf

# read -r -d '' INITIAL_ENV_CONTENTS << EOM
# This is line 1.
# This is line 2.
# Line 3.
# EOM
# $INITIAL_ENV_CONTENTS >> .env

# TODO
if [[ false ]]; then
  echo "Initializing db..."
  # # Grant the db user access to create databases (so that tests can be run, etc.)
  # db_user=$(python -c 'from modularhistory.settings import DATABASES; print(DATABASES["default"]["USER"])')
  # echo "Granting $db_user permission to create databases..."
  # psql postgres -c "ALTER USER $db_user CREATEDB" &>/dev/null

  # if [[ "$interactive" == true ]]; then
  #   # Check if default db exists
  #   db_name=$(python -c 'from modularhistory.settings import DATABASES; print(DATABASES["default"]["NAME"])')
  #   echo "Checking if db named $db_name (specified in project settings) exists..."
  #   # Check if db already exists
  #   if psql "$db_name" -c '\q' 2>&1; then
  #     echo "Database named $db_name already exists."
  #     while [ "$create_database" != "y" ] && [ "$create_database" != "n" ]; do
  #       echo "Recreate database? (WARNING: All local changes will be obliterated.) [y/n] "
  #       read -r create_database
  #     done
  #     if [[ "$create_database" == "y" ]]; then
  #       echo "Dropping $db_name..."
  #       lsof -t -i tcp:8000 | xargs kill -9 &>/dev/null
  #       dropdb "$db_name" || {
  #         error "Failed to drop database '$db_name'"
  #         error "Hint: Try stopping the development server and rerunning this script."
  #         exit 1
  #       }
  #     fi
  #   else
  #     create_database="y"
  #   fi

  #   # Create db (if it does not already exist)
  #   if [[ "$create_database" == "y" ]]; then
  #     echo "Creating $db_name..."
  #     createdb "$db_name" || error "Failed to create database."

  #     while [ "$use_sql_file" != "y" ] && [ "$use_sql_file" != "n" ]; do
  #       read -r -p "Build db from a SQL backup file? [y/n] " use_sql_file
  #     done

  #     if [[ "$use_sql_file" == "y" ]]; then
  #       while [[ ! -f "$sql_file" ]]; do
  #         read -r -e -p "Enter path to SQL file (to build db): " sql_file
  #         sql_file="${sql_file/\~/$HOME}"
  #         if [[ ! -f "$sql_file" ]]; then
  #           echo "$sql_file does not exist."
  #         fi
  #       done
  #       echo "Importing $sql_file..."
  #       psql "$db_name" <"$sql_file" &>/dev/null || error "Failed to import $sql_file."

  #       # Set db permissions correctly
  #       psql "$db_name" -c "alter database $db_name owner to $db_user" &>/dev/null
  #       psql "$db_name" -c "alter schema public owner to $db_user" &>/dev/null
  #       # Set permissions for db tables
  #       tables=$(psql "$db_name" -qAt -c "select tablename from pg_tables where schemaname = 'public';")
  #       for table in $tables; do
  #         psql "$db_name" -c "alter table \"$table\" owner to $db_user" &>/dev/null
  #       done
  #       # Set permissions for db sequences
  #       seqs=$(psql "$db_name" -qAt -c "select sequence_name from information_schema.sequences where sequence_schema = 'public';")
  #       for seq in $seqs; do
  #         psql "$db_name" -c "alter table \"$seq\" owner to $db_user" &>/dev/null
  #       done
  #       # Set permissions for db views
  #       views=$(psql "$db_name" -qAt -c "select table_name from information_schema.views where table_schema = 'public';")
  #       for view in $views; do
  #         psql "$db_name" -c "alter table \"$view\" owner to $db_user" &>/dev/null
  #       done
  #     fi
  #   fi
  # fi

  # # Run database migrations
  # if [[ "${USE_PROD_DB}" != 'True' ]]; then
  #   if [[ "$interactive" == true ]]; then
  #     while [ "$run_migrations" != "y" ] && [ "$run_migrations" != "n" ]; do
  #       echo "Run db migrations? [y/n] "
  #       read -r run_migrations
  #     done
  #   else
  #     run_migrations="y"
  #   fi
  #   if [[ "$run_migrations" == "y" ]]; then
  #     echo "Running database migrations..."
  #     python manage.py migrate || exit 1
  #     echo ""
  #   fi
  # fi
fi
