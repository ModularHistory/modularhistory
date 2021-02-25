#!/bin/bash

RED='\033[0;31m'
NC='\033[0m'  # No Color

MAC_OS="MacOS"
LINUX="Linux"

# Print message with red text
function _print_red() {
  # shellcheck disable=SC2059
  printf "${RED}$1${NC}" && echo ""
}

# Print message with red text and exit the script with an error status (1)
function _error() {
  echo "$1" >&2
  _print_red "$1"
  exit 1
}

# Detect operating system.
os_name=$(uname -s)
if [[ "$os_name" == Darwin* ]]; then
  os='MacOS'
  bash_profile="$HOME/.bash_profile"
elif [[ "$os_name" == Linux* ]]; then
  os='Linux'
  bash_profile="$HOME/.bashrc"
elif [[ "$os_name" == Windows* ]]; then
  os='Windows'
  # Exit without error:
  _print_red "
    This setup script must be run in a bash shell in Windows Subsystem for Linux (WSL):
    https://github.com/ModularHistory/modularhistory/wiki/Dev-Environment-Setup#windows-prereqs
  " && exit
else
  _error "Unknown operating system."
fi
echo "Detected $os."

zsh_profile="$HOME/.zshrc"

# Create shell profiles if they don't already exist
touch "$bash_profile"
touch "$zsh_profile"

function _append() {
  grep -qxF "$1" "$2" || {
    echo "Appending the following line to $2:" && echo "  $1"
    echo "$1" >> "$2"
  }
}

function _append_to_sh_profile() {
  # Append to bash profile
  _append "$1" "$bash_profile"
  # Append to zsh profile
  _append "$1" "$zsh_profile"
  # Explicitly execute the statement, regardless of whether it was already present
  # in the bash profile, since non-interactive shells on Ubuntu do not execute all 
  # the statements in .bashrc.
  eval "$1"
}

if [[ "$os" == "$MAC_OS" ]]; then
  # Use GNU Grep
  # shellcheck disable=SC2016
  _append_to_sh_profile 'export PATH="/usr/local/opt/grep/libexec/gnubin:$PATH"'
elif [[ "$os_name" == Linux* ]]; then
  # Remove conflicting Windows paths from PATH, if necessary.
  # shellcheck disable=SC2016
  mod='export PATH=$(echo "$PATH" | sed -e "s/:\/mnt\/c\/Users\/[^:]+\/\.pyenv\/pyenv-win\/[^:]+$//")'
  _append_to_sh_profile "$mod"
fi

# Update package managers
echo "Checking package manager ..."
if [[ "$os" == "$MAC_OS" ]]; then
  # Update software dependencies through XCode
  echo "Updating software ..."
  xcode-select --install &>/dev/null || softwareupdate -l

  function brew_install {
    if brew ls --versions "$1" >/dev/null; then
      HOMEBREW_NO_AUTO_UPDATE=1 brew upgrade "$1"
    else
      HOMEBREW_NO_AUTO_UPDATE=1 brew install "$1"
    fi
  }

  # Install/update Homebrew and Homebrew-managed packages
  brew help &>/dev/null || {
    echo "Installing Homebrew ..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
  }
  echo "Updating Homebrew packages ..."
  brew update
  # PostgreSQL
  brew tap homebrew/services && brew_install postgresql
  # Other packages
  brew_install openssl@1.1
  brew install rust libjpeg zlib grep jq
  # Modify PATH to use GNU Grep over MacOS Grep.
  echo "Modifying PATH (in $bash_profile) to use GNU Grep over BSD Grep ..."
  # shellcheck disable=SC2016
  _append_to_sh_profile 'export PATH="/usr/local/opt/grep/libexec/gnubin:$PATH"'
  # Fix environment for installation of Python versions via pyenv.
  # https://stackoverflow.com/questions/50036091/pyenv-zlib-error-on-macos#answer-65556829
  brew install bzip2
  echo "Exporting LDFLAGS and CFLAGS to allow installing new Python versions via pyenv ..."
  echo "https://stackoverflow.com/questions/50036091/pyenv-zlib-error-on-macos#answer-65556829"
  export LDFLAGS="-L $(xcrun --show-sdk-path)/usr/lib -L brew --prefix bzip2/lib"
  export CFLAGS="-L $(xcrun --show-sdk-path)/usr/include -L brew --prefix bzip2/include"
elif [[ "$os" == "$LINUX" ]]; then
  sudo apt update -y && sudo apt upgrade -y
  # Basic dev dependencies
  sudo apt install -y bash-completion curl git wget vim
  # PostgreSQL
  wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
  echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" | sudo tee /etc/apt/sources.list.d/pgdg.list
  # All other dependencies
  sudo apt update -y
  sudo apt install -y \
  make \
  build-essential \
  libssl-dev \
  zlib1g-dev \
  libbz2-dev \
  libreadline-dev \
  libsqlite3-dev \
  llvm \
  libncurses5-dev \
  libncursesw5-dev \
  xz-utils \
  tk-dev \
  libffi-dev \
  liblzma-dev \
  python-openssl \
  postgresql-client-common \
  postgresql-client-13 || _error "Unable to install one or more required packages."
fi

# Enter the project
project_dir=$(dirname "$0")
cd "$project_dir" || _error "Could not cd into $project_dir"
echo "Working in $(pwd) ..."

# Create directories for db backups, static files, and media files
mkdir -p .backups static media &>/dev/null

# Add container names to /etc/hosts
echo "Updating /etc/hosts ..."
sudo grep -qxF "127.0.0.1 postgres" /etc/hosts || { 
  sudo echo "127.0.0.1 postgres" | sudo tee -a /etc/hosts 
}
sudo grep -qxF "127.0.0.1 redis" /etc/hosts || { 
  sudo echo "127.0.0.1 redis" | sudo tee -a /etc/hosts 
}

# Make sure pyenv is installed
echo "Checking for pyenv ..."
pyenv_dir="$HOME/.pyenv"
# shellcheck disable=SC2016
_append_to_sh_profile 'export PATH="$HOME/.pyenv/bin:$PATH"'
pyenv --version &>/dev/null || {
  [ -d "$pyenv_dir" ] && {
    echo "Removing extant $pyenv_dir ..."
    sudo rm -rf "$pyenv_dir" &>/dev/null
  }
  if [[ "$os" == "$MAC_OS" ]]; then
    brew install pyenv
  elif [[ "$os" == "$LINUX" ]]; then
    echo "Installing pyenv ..."
    # https://github.com/pyenv/pyenv-installer
    curl https://pyenv.run | bash
  fi
}
echo "Ensuring pyenv is in PATH ..."
pyenv --version &>/dev/null || _error 'ERROR: pyenv is not in PATH.'
echo "Ensuring pyenv automatic activation is enabled ..."
echo "Using $(pyenv --version) ..."
echo "Installing required Python versions ..."
installed_py_versions="$(pyenv versions)"
while IFS= read -r pyversion; do
  # shellcheck disable=SC2076
  if [[ -n $pyversion ]] && [[ ! "$installed_py_versions" =~ "$pyversion" ]]; then
    pyenv install "$pyversion"
    # shellcheck disable=SC2076
    if [[ ! "$(pyenv versions)" =~ "$pyversion" ]]; then
      _error "Failed to install Python $pyversion."
    fi
  fi
done < .python-version

# Activate the local Python version by re-entering the directory.
# shellcheck disable=SC2016
_append_to_sh_profile 'if command -v pyenv 1>/dev/null 2>&1; then eval "$(pyenv init -)"; fi'
# # shellcheck disable=SC2015
# cd .. && cd modularhistory || _error "Cannot cd into modularhistory directory."

# Make sure correct version of Python is used
echo "Checking Python version ..."
python --version &>/dev/null || _error "Failed to activate Python"
active_py_version=$(python --version)
if [[ ! "$active_py_version" =~ .*"$pyversion".* ]]; then
  _error "Failed to activate Python $pyversion."
fi
echo "Using $(python --version) ..."

# Make sure Pip is installed
pip --version &>/dev/null || _error "Pip is not installed; unable to proceed."

# Install Poetry
poetry --version &>/dev/null || {
  echo "Installing Poetry ..."
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
    _error "Unable to install Poetry."
  fi
}

# https://python-poetry.org/docs/configuration/
poetry config virtualenvs.create true
poetry config virtualenvs.in-project true
poetry self update &>/dev/null
echo "Using $(poetry --version) ..."

if [[ "$os" == "$MAC_OS" ]]; then
  # https://cryptography.io/en/latest/installation.html#building-cryptography-on-macos
  export LDFLAGS="-L$(brew --prefix openssl@1.1)/lib"
  export CFLAGS="-I$(brew --prefix openssl@1.1)/include" 
fi
# Install dependencies with Poetry
echo "Installing dependencies ..."
poetry install --no-root || _error "Failed to install dependencies with Poetry."

# Node Version Manager (NVM)
echo "Enabling NVM ..."
nvm --version &>/dev/null || {
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.35.3/install.sh | bash
  export NVM_DIR="$HOME/.nvm"
  # shellcheck disable=SC1090
  [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
  # shellcheck disable=SC1090
  [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
}
echo "Installing Node modules ..."
cd frontend && nvm install && nvm use && npm ci --cache .npm && cd ..

# Rclone: https://rclone.org/
rclone version &>/dev/null || {
  echo "Creating .tmp dir ..."
  # shellcheck disable=SC2164
  mkdir -p .tmp && cd .tmp
  echo "Downloading rclone setup script ..."
  curl https://rclone.org/install.sh --output install-rclone.sh
  cd ..
  echo "Installing rclone ..."
  sudo bash .tmp/install-rclone.sh
  echo "Cleaning up ..."
  rm -r .tmp
}
echo "Overwriting rclone.conf ..."
mkdir -p "$HOME/.config/rclone"
cp config/rclone/rclone.conf "$HOME/.config/rclone/rclone.conf"

# Disable THP so it doesn't cause issues for Redis containers
if test -f /sys/kernel/mm/transparent_hugepage/enabled; then
  echo "Disabling THP ..."
  sudo bash -c "echo madvise > /sys/kernel/mm/transparent_hugepage/enabled"
fi

if [[ "$os" == "$MAC_OS" ]]; then
  # Enable mounting volumes within ~/modularhistory
  docker_settings_file="$HOME/Library/Group Containers/group.com.docker/settings.json"
  if [[ -f "$docker_settings_file" ]]; then 
    # shellcheck disable=SC2002
    if [[ $(cat "$docker_settings_file" | jq ".filesharingDirectories | contains([\"$HOME/modularhistory\"])") = true ]]; then
      echo "Docker file sharing is enabled for $HOME/modularhistory."
    else
      echo "Enabling file sharing for $HOME/modularhistory ..."
      cat "$HOME/Library/Group Containers/group.com.docker/settings.json" | jq ".filesharingDirectories += [\"$HOME/modularhistory\"]" > settings.json.tmp &&
      mv settings.json.tmp "$docker_settings_file"
      test "$(docker ps -q)" && {
        echo "Stopping containers ..."
        docker-compose down
      }
      test -z "$(docker ps -q)" && {
        echo "Quitting Docker ..."
        osascript -e 'quit app "Docker"'
        sleep 9
        echo "Starting Docker ..."
        open --background -a Docker
        while ! docker system info > /dev/null 2>&1; do sleep 2; done
      }
    fi
  else
    echo "Could not find Docker settings file; skipping enabling Docker file sharing ... "
  fi
fi

if [[ "$os" == "$LINUX" ]]; then
  # Add user to www-data group
  echo "Granting file permissions to $USER ..."
  sudo usermod -a -G www-data "$USER"
  sudo chown -R "$USER:www-data" .
  sudo chmod g+w -R .
fi

read -rp "Seed db, env file, and media [Y/n]? " CONT
if [ ! "$CONT" = "n" ]; then
  echo "Seeding database, env file, and media files (NOTE: This could take a long time!) ..."
  poetry run invoke seed && echo "Finished seeding dev environment."
fi

echo "Finished setup."

echo "Spinning up containers ..."
docker-compose up -d dev
