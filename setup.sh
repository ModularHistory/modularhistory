#!/bin/bash

# Enable aliases
shopt -s expand_aliases

RED='\033[0;31m'
NC='\033[0m' # No Color

MAC_OS="MacOS"
LINUX="Linux"

VIRTUAL_ENV_PATTERN='*env'
PREFERRED_VENV_NAME='.venv'

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
    setup.sh [--noninteractive]

OPTIONS
  -h, --help
      Prints this and exits

  --noninteractive
      Option that makes the script run without user input

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
    -) break ;;
    *) fatal "Unknown option '--${OPTARG}'" "See '${0} --help' for usage" ;;
    esac
    ;;
  *) fatal "Unknown option: '-${OPTARG}'" "See '${0} --help' for usage" ;;
  esac
done

shift $((OPTIND - 1))

if [[ -n "${USE_PROD_DB}" ]]; then
  error "Cannot run setup script while connected to production database."
  exit 1
fi

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
else
  error "Detected unsupported operating system. (ModularHistory can only be set up on a Linux or MacOS machine.)"
  exit 1
fi
echo "Detected $os."

# Enter the project
cd "$(dirname "$0")" && echo "Running in $(pwd)..." || exit 1

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
  # Update/upgrade apt-get
  apt-get update -y && apt-get upgrade -y
fi

if [[ "$interactive" == true ]]; then
  # Make sure pyenv is installed
  echo "Checking for pyenv..."
  pyenv --version &>/dev/null || {
    if [[ "$os" == "$MAC_OS" ]]; then
      brew install pyenv
      echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >>~/.bash_profile
    elif [[ "$os" == "$LINUX" ]]; then
      error "Please install and configure pyenv (https://github.com/pyenv/pyenv), then rerun this script."
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
fi

# Install gettext (for envsubst)
if [[ "$os" == "$MAC_OS" ]]; then
  brew install gettext
  brew link --force gettext
elif [[ "$os" == "$LINUX" ]]; then
  apt-get install envsubst
fi

# Make sure correct version of Python is used
echo "Checking Python version..."
python --version &>/dev/null || {
  error "Could not detect Python. Install Python 3.7 and rerun this script."
  exit 1
}
if [[ "$os" == "$MAC_OS" ]]; then
  python3 --version && alias python=python3
fi
echo "Using $(python --version)..."

# Make sure Pip is installed
pip --version &>/dev/null || {
  pip3 --version &>/dev/null && alias pip=pip3
} || {
  error "Pip is not installed; unable to proceed."
  exit 1
}

if [[ "$interactive" == true ]]; then
  # Make sure that Postgres is installed
  psql -V &>/dev/null || {
    echo "Installing PostgreSQL..."
    if [[ "$os" == "$MAC_OS" ]]; then
      brew install postgres &&
        initdb /usr/local/var/postgres
      brew services start postgresql &&
        brew services list
    elif [[ "$os" == "$LINUX" ]]; then
      sudo apt-get install wget ca-certificates
      wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
      sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'
      sudo apt-get update
      sudo apt-get install postgresql postgresql-contrib
    fi
  }
  {
    psql_version=$(psql -V) && echo "Using $psql_version..."
  } || {
    error "Could not detect PostgreSQL installation. Install PostgreSQL (>=12.3) and rerun this script."
    exit 1
  }

  # Make sure Memcached is installed
  {
    memcached_version=$(memcached -V) && echo "Using $memcached_version..."
  } || {
    if [[ "$os" == "$MAC_OS" ]]; then
      brew install memcached && brew services start memcached
    elif [[ "$os" == "$LINUX" ]]; then
      apt-get install memcached libmemcached-tools -y
      systemctl start memcached && systemctl enable memcached
    fi
  }

  # Ensure that virtualenv is installed
  {
    venv_version=$(virtualenv --version) && echo "Using $venv_version..."
  } || {
    echo "Installing virtualenv..."
    pip install -U virtualenv
  } || {
    error "Could not install virtualenv."
    exit 1
  }

  # Activate virtual Python environment
  echo "Activating virtual Python environment..."
  in_venv=0
  num=$(find . -name "$VIRTUAL_ENV_PATTERN" -type d -maxdepth 1 -exec echo x \; | wc -l | tr -d '[:space:]')
  if [[ "$num" -gt 0 ]]; then
    # Attempt to activate existing virtual environment
    find . -name "$VIRTUAL_ENV_PATTERN" -type d -maxdepth 1 -print0 |
      while IFS= read -r -d '' path; do
        echo "Inspecting $path"
        ls "$path/bin/activate" &>/dev/null && virtual_env_dir="$path" && source "$virtual_env_dir"/bin/activate
      done
    if [[ $(python -c 'import sys; print(sys.prefix)') == *"$(pwd)"* ]]; then
      in_venv=1
    fi
  fi
  if [ "$num" = 0 ] || [ "$in_venv" = 0 ]; then
    # Attempt to create the virtual environment
    echo "Creating virtual environment..."
    rm -r "$PREFERRED_VENV_NAME" &>/dev/null
    virtualenv "$PREFERRED_VENV_NAME" && source "$PREFERRED_VENV_NAME/bin/activate"
    if [[ $(python -c 'import sys; print(sys.prefix)') == *"$(pwd)"* ]]; then
      in_venv=1
    fi
  fi
  if [[ "$in_venv" == 0 ]]; then
    error "Unable to activate virtual Python environment."
    echo "Create a virtual environment named $PREFERRED_VENV_NAME in your project root, then rerun this script."
    exit 1
  fi
  echo "Activated virtual environment at $VIRTUAL_ENV"
fi

# Update Pip
pip install --upgrade pip &>/dev/null

# Install Poetry
poetry --version &>/dev/null || {
  echo "Installing Poetry..."
  curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python &>/dev/null
  # shellcheck source=/dev/null
  source "$HOME/.poetry/env"
  poetry --version &>/dev/null || {
    echo "Unable to use Poetry's custom installer; falling back on pip..."
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

# Prevent Poetry from creating virtual environments;
# this is essential to avoid errors in GitHub builds.
poetry config virtualenvs.create false
# poetry config --list

# Create requirements.txt in case of manual deploys; TODO: move this to a test
echo "Exporting requirements.txt..."
if [[ -f "requirements.txt" ]]; then
  rm requirements.txt
fi
poetry export -f requirements.txt > requirements.txt
# Remove hashes from requirements.txt so Google Cloud can read the file correctly
sed -e '/--hash/d' -e 's/ \\//g' ./requirements.txt > requirements.tmp && mv requirements.tmp requirements.txt

# Install dependencies
echo "Installing dependencies..."
poetry install || {
  error "Failed to install dependencies with Poetry."
  echo "Falling back on pip..."
  pip install -r requirements.txt
}

# Grant the db user access to create databases (so that tests can be run, etc.)
db_user=$(python -c 'from modularhistory.settings import DATABASES; print(DATABASES["default"]["USER"])')
echo "Granting $db_user permission to create databases..."
psql postgres -c "ALTER USER $db_user CREATEDB" &>/dev/null

if [[ "$interactive" == true ]]; then
  # Check if default db exists
  db_name=$(python -c 'from modularhistory.settings import DATABASES; print(DATABASES["default"]["NAME"])')
  echo "Checking if db named $db_name (specified in project settings) exists..."
  # Check if db already exists
  if psql "$db_name" -c '\q' 2>&1; then
    echo "Database named $db_name already exists."
    while [ "$create_database" != "y" ] && [ "$create_database" != "n" ]; do
      echo "Recreate database? (WARNING: All local changes will be obliterated.) [y/n] "
      read -r create_database
    done
    if [[ "$create_database" == "y" ]]; then
      echo "Dropping $db_name..."
      lsof -t -i tcp:8000 | xargs kill -9 &>/dev/null
      dropdb "$db_name" || {
        error "Failed to drop database '$db_name'"
        error "Hint: Try stopping the development server and rerunning this script."
        exit 1
      }
    fi
  else
    create_database="y"
  fi

  # Create db (if it does not already exist)
  if [[ "$create_database" == "y" ]]; then
    echo "Creating $db_name..."
    createdb "$db_name" || error "Failed to create database."

    while [ "$use_sql_file" != "y" ] && [ "$use_sql_file" != "n" ]; do
      read -r -p "Build db from a SQL backup file? [y/n] " use_sql_file
    done

    if [[ "$use_sql_file" == "y" ]]; then
      while [[ ! -f "$sql_file" ]]; do
        read -r -e -p "Enter path to SQL file (to build db): " sql_file
        sql_file="${sql_file/\~/$HOME}"
        if [[ ! -f "$sql_file" ]]; then
          echo "$sql_file does not exist."
        fi
      done
      echo "Importing $sql_file..."
      psql "$db_name" <"$sql_file" &>/dev/null || error "Failed to import $sql_file."

      # Set db permissions correctly
      psql "$db_name" -c "alter database $db_name owner to $db_user" &>/dev/null
      psql "$db_name" -c "alter schema public owner to $db_user" &>/dev/null
      # Set permissions for db tables
      tables=$(psql "$db_name" -qAt -c "select tablename from pg_tables where schemaname = 'public';")
      for table in $tables; do
        psql "$db_name" -c "alter table \"$table\" owner to $db_user" &>/dev/null
      done
      # Set permissions for db sequences
      seqs=$(psql "$db_name" -qAt -c "select sequence_name from information_schema.sequences where sequence_schema = 'public';")
      for seq in $seqs; do
        psql "$db_name" -c "alter table \"$seq\" owner to $db_user" &>/dev/null
      done
      # Set permissions for db views
      views=$(psql "$db_name" -qAt -c "select table_name from information_schema.views where table_schema = 'public';")
      for view in $views; do
        psql "$db_name" -c "alter table \"$view\" owner to $db_user" &>/dev/null
      done
    fi
  fi
fi

# Run database migrations
if [[ -z "${USE_PROD_DB}" ]]; then
  echo "Running database migrations..."
  python manage.py migrate
  echo ""
fi
