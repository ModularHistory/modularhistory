#!/bin/bash

PROJECT_DIR=$(dirname "$0")
RED='\033[0;31m'
NC='\033[0m'  # No Color
BOLD=$(tput bold)
MAC_OS="MacOS"
LINUX="Linux"

rerun_required="false"

function _append() {
  grep -qxF "$1" "$2" || {
    echo "Appending the following line to $2:" && echo "  $1"
    echo "$1" >> "$2"
  }
}

function _print_red() {
  # Print a message with red text.
  # shellcheck disable=SC2059
  printf "${RED}$1${NC}\n"
}

function _error() {
  # Print a message with red text and exit the script with an error status (1).
  _print_red "$1" >&2; exit 1
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
  # Exit without error:
  _print_red "
    Unknown operating system: $os_name

    This script must be run from a bash shell on a supported operating system;
    see https://github.com/ModularHistory/modularhistory/wiki/Dev-Environment-Setup.
  " && exit
fi

# Make sure Git is properly installed.
git --help &>/dev/null || {
  _error "Git is not installed."
}

# Make sure this script is being run in the 'main' branch.
# When run in GitHub Actions), the code is in detached HEAD state, 
# but the branch name can be extracted from GITHUB_REF.
branch=$(git branch --show-current || echo "${GITHUB_REF##*/}")
echo "Branch: $branch"
if [[ ! "$branch" = "main" ]]; then
  _error "
    Check out the main branch before running this script.
    You can use the following command to check out the main branch:
      git checkout main
  "
fi

# Make sure the latest updates have been pulled.
if ! git diff --quiet origin/main; then
  _error "
    Pull the latest updates, then try running this script again.
    You can use the following command to pull the latest updates:
      git pull
  "
fi

echo "Detected $os."
zsh_profile="$HOME/.zshrc"

# Enter the project
cd "$PROJECT_DIR" || _error "Could not cd into $PROJECT_DIR"
echo "Working in $(pwd) ..."

# Create shell profiles if they don't already exist.
touch "$bash_profile"
touch "$zsh_profile"

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

function _prompt_to_rerun() {
  read -rp "This might be fixed by rerunning the script. Rerun? [Y/n] " CONT
  if [[ ! "$CONT" = "n" ]]; then
    exec bash "$PROJECT_DIR/setup.sh"
  fi
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
  xcodebuild -version &>/dev/null || {
    xcode-select --install || {
      error "
        XCode is required. Rerun this script after installing XCode: 
          https://apps.apple.com/us/app/xcode/id497799835?mt=12
      "
    }
  }
  softwareupdate -l

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
  brew_install rust
  brew install libjpeg zlib grep gnu-sed jq
  # Modify PATH to use GNU Grep over MacOS Grep.
  # shellcheck disable=SC2016
  _append_to_sh_profile 'export PATH="/usr/local/opt/grep/libexec/gnubin:$PATH"'
elif [[ "$os" == "$LINUX" ]]; then
  sudo apt update -y && sudo apt upgrade -y
  # Basic dev dependencies
  sudo apt install -y bash-completion curl git wget vim
  # PostgreSQL
  wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
  echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" |
  sudo tee /etc/apt/sources.list.d/pgdg.list
  # All other dependencies
  sudo apt update -y
  sudo apt install -y --allow-downgrades \
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

# Note: These are referenced multiple times in this script.
writable_dirs=( "$PROJECT_DIR/.backups" "$PROJECT_DIR/.init" "$PROJECT_DIR/media" "$PROJECT_DIR/.static" "$PROJECT_DIR/frontend/.next" )

for writable_dir in "${writable_dirs[@]}"; do
  mkdir -p "$writable_dir" &>/dev/null
done

if [[ "$os" == "$LINUX" ]]; then
  # Add user to www-data group.
  groups "$USER" | grep -q www-data || {
    echo "Adding $USER to the www-data group ..."
    sudo usermod -a -G www-data "$USER"
    groups "$USER" | grep -q www-data || {
      _error "Failed to add $USER to the www-data group."
    }
    rerun_required="true"
  }
  # shellcheck disable=SC2010
  ls -ld "$PROJECT_DIR" | grep -q "$USER www-data" || {
    echo "Granting the www-data group permission to write in project directories ..."
    sudo chown -R "$USER":www-data "$PROJECT_DIR"
    rerun_required="true"
  }
  for writable_dir in "${writable_dirs[@]}"; do
    # shellcheck disable=SC2010
    echo "Checking write permissions for $writable_dir ..."
    sudo -u www-data test -w "$writable_dir" || {
      echo "Granting the www-data group permission to write in $writable_dir ..."
      sudo chmod g+w -R "$writable_dir"
      rerun_required="true"
    }
  done
  if [[ "$rerun_required" = "true" ]]; then
    _print_red "File permissions have been updated."
    prompt="To finish setup, we must rerun the setup script. Proceed? [Y/n]"
    read -rp "$prompt" CONT
    if [[ ! "$CONT" = "n" ]]; then
      exec bash "$PROJECT_DIR/setup.sh"
    fi
    exit
  fi
fi

# Make sure pyenv is installed.
echo "Checking for pyenv ..."
pyenv_dir="$HOME/.pyenv"
# shellcheck disable=SC2016
_append_to_sh_profile 'export PATH="$HOME/.pyenv/bin:$PATH"'
pyenv --version &>/dev/null || {
  [[ -d "$pyenv_dir" ]] && {
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
      if [[ "$os" == "$MAC_OS" ]]; then
        # Try to fix MacOS environment for installation of Python versions via pyenv.
        # https://stackoverflow.com/questions/50036091/pyenv-zlib-error-on-macos#answer-65556829
        brew install bzip2
        echo "Exporting LDFLAGS and CFLAGS to allow installing new Python versions via pyenv ..."
        echo "https://stackoverflow.com/questions/50036091/pyenv-zlib-error-on-macos#answer-65556829"
        # shellcheck disable=SC2155
        export LDFLAGS="-L $(xcrun --show-sdk-path)/usr/lib -L brew --prefix bzip2/lib"
        # shellcheck disable=SC2155
        export CFLAGS="-L $(xcrun --show-sdk-path)/usr/include -L brew --prefix bzip2/include"
        pyenv install "$pyversion"
        if [[ ! "$(pyenv versions)" =~ "$pyversion" ]]; then
          _error "Failed to install Python $pyversion."
        fi
      else
        _error "Failed to install Python $pyversion."
      fi
    fi
  fi
done < .python-version

# Activate the local Python version.
# shellcheck disable=SC2016
_append_to_sh_profile 'if command -v pyenv 1>/dev/null 2>&1; then eval "$(pyenv init -)"; fi'

# Make sure the correct version of Python is used.
echo "Checking Python version ..."
python --version &>/dev/null || _error "Failed to activate Python"
active_py_version=$(python --version)
if [[ ! "$active_py_version" =~ .*"$pyversion".* ]]; then
  _error "Failed to activate Python $pyversion."
fi
echo "Using $(python --version) ..."

# Make sure Pip is installed.
pip --version &>/dev/null || _error "Pip is not installed; unable to proceed."

# Install Poetry.
# shellcheck disable=SC2016
poetry_init='export PATH="$HOME/.poetry/bin:$PATH"'
poetry --version &>/dev/null || {
  echo "Installing Poetry ..."
  # https://python-poetry.org/docs/#osx-linux-bashonwindows-install-instructions
  curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
  _append_to_sh_profile "$poetry_init"
  poetry --version &>/dev/null || {
    _error "Failed to install Poetry (https://python-poetry.org/docs/#installation)."
  }
  rerun_required="true"
}

# https://python-poetry.org/docs/configuration/
poetry config virtualenvs.create true
poetry config virtualenvs.in-project true
poetry self update &>/dev/null
echo "Using $(poetry --version) ..."

if [[ "$os" == "$MAC_OS" ]]; then
  # https://cryptography.io/en/latest/installation.html#building-cryptography-on-macos
  # shellcheck disable=SC2155
  export LDFLAGS="-L$(brew --prefix openssl@1.1)/lib"
  # shellcheck disable=SC2155
  export CFLAGS="-I$(brew --prefix openssl@1.1)/include" 
fi
# Install dependencies with Poetry.
echo "Installing dependencies ..."
poetry install --no-root || {
  _print_red "Failed to install dependencies with Poetry."
  echo "Attempting workaround ..."
  # Try installing with pip
  set a
  # shellcheck disable=SC1090
  source "$PROJECT_DIR/.venv/bin/activate"; unset a
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
    _prompt_to_rerun
  } || {
    _print_red "Failed to install dependencies with pip."
  }
  rm requirements.txt
  _error "Failed to install dependencies with Poetry."
}

# Add container names to /etc/hosts.
poetry run invoke setup.update-hosts

# Set up Node Version Manager (NVM).
echo "Enabling NVM ..."
nvm --version &>/dev/null || {
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.35.3/install.sh | bash
  export NVM_DIR="$HOME/.nvm"
  # shellcheck disable=SC1090
  [[ -s "$NVM_DIR/nvm.sh" ]] && \. "$NVM_DIR/nvm.sh"  # loads nvm
  # shellcheck disable=SC1090
  [[ -s "$NVM_DIR/bash_completion" ]] && \. "$NVM_DIR/bash_completion"  # loads nvm bash_completion
}
echo "Installing Node modules ..."
npm i -g prettier eslint prettier-eslint
cd frontend && nvm install && nvm use && npm ci --cache .npm && cd ..

# Set up Rclone (https://rclone.org/).
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
mkdir -p "$HOME/.config/rclone"

# Disable THP so it doesn't cause issues for Redis containers.
if test -f /sys/kernel/mm/transparent_hugepage/enabled; then
  echo "Disabling THP ..."
  sudo bash -c "echo madvise > /sys/kernel/mm/transparent_hugepage/enabled"
fi

if [[ "$os" == "$MAC_OS" ]]; then
  # Enable mounting volumes within ~/modularhistory.
  docker_settings_file="$HOME/Library/Group Containers/group.com.docker/settings.json"
  if [[ -f "$docker_settings_file" ]]; then
    sharing_enabled=$(jq ".filesharingDirectories | contains([\"$HOME/modularhistory\"])" < "$docker_settings_file")
    if [[ $sharing_enabled = true ]]; then
      echo "Docker file sharing is enabled for $HOME/modularhistory."
    else
      echo "Enabling file sharing for $PROJECT_DIR ..."
      jq ".filesharingDirectories += [\"$HOME/modularhistory\"]" < "$docker_settings_file" > settings.json.tmp &&
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

if [[ "$rerun_required" = "true" ]]; then
  prompt="To finish setup, we must rerun the setup script. Proceed? [Y/n]"
  read -rp "$prompt" CONT
  if [[ ! "$CONT" = "n" ]]; then
    exec bash "$PROJECT_DIR/setup.sh"
  fi
  exit
fi

prompt="Seed db and env file [Y/n]? "
if [[ -f "$PROJECT_DIR/.env" ]] && [[ -f "$PROJECT_DIR/.init/init.sql" ]]; then
  prompt="init.sql and .env files already exist. Seed new files [Y/n]? "
fi
read -rp "$prompt" CONT
if [[ ! "$CONT" = "n" ]] && [[ ! $TESTING = true ]]; then
  echo "Seeding database and env file ..."
  # shellcheck disable=SC2015
  poetry run invoke seed && echo "Finished seeding db and env file." || {
    _print_red "Failed to seed dev environment."
    _prompt_to_rerun
    _error "
      Failed to seed dev environment. Try running the following in a new shell:

        ${BOLD}cd ~/modularhistory && poetry run invoke seed
    "
  }
fi

read -rp "Sync media [Y/n]? " CONT
if [[ ! "$CONT" = "n" ]] && [[ ! $TESTING = true ]]; then
  # shellcheck disable=SC2015
  poetry run invoke media.sync && echo "Finished syncing media." || {
    _print_red "
      Failed to sync media. Try running the following in a new shell:

        ${BOLD}cd ~/modularhistory && poetry run invoke media.sync

    "
  }
fi

# Remove all dangling (untagged) images
# shellcheck disable=SC2046
docker rmi $(docker images -f "dangling=true" -q) &>/dev/null

echo "Spinning up containers ..."
# shellcheck disable=SC2015
docker-compose up --build -d dev && echo 'Finished.' || {
  _print_red "Failed to start containers."
  [[ ! $TESTING = true ]] && _prompt_to_rerun
  _print_red "
    Could not start containers. 
    Try restarting Docker and/or running the following in a new shell:

      ${BOLD}cd ~/modularhistory && docker-compose up -d dev

  "
}

# Check Docker's memory cap
[[ "$os" == "$MAC_OS" ]] && {
  mem_limit=$(docker stats --format "{{.MemUsage}}" --no-stream | head -1 | gsed -r -e 's/.+ \/ ([0-9]+).*/\1/')
  if [[ "$mem_limit" -lt 2 ]]; then
    _print_red "Consider increasing Docker's memory limit to 3–4 GB."
  fi
}

shasum "$PROJECT_DIR/setup.sh" > "$PROJECT_DIR/.venv/.setup.sha"
