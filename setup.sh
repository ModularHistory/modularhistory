#!/bin/bash

set -a

PYTHON_VERSION="3.9.13"
export PYTHON_VERSION

PROJECT_DIR=$(dirname "$0")
export PROJECT_DIR

unset a

VOLUMES_DIR="$PROJECT_DIR/_volumes"

# Enter the project.
cd "$PROJECT_DIR" || _error "Could not cd into $PROJECT_DIR"
echo "Working in $(pwd) ..."

# Import functions like _print_error.
source "config/scripts/functions.sh"

function _append() {
  grep -qxF "$1" "$2" || {
    echo "Appending the following line to $2:" && echo "  $1"
    echo "$1" >> "$2"
  }
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

while getopts j: flag
do
    case "${flag}" in
        j) just_do_it=true;;
        # Note: flag value can be referenced as ${OPTARG}
        *) _error "An invalid flag was used.";;
    esac
done

# Make sure Git is properly installed.
git --help &>/dev/null || {
  _error "Git is not installed."
}

# Update git hooks.
for filepath in config/hooks/*; do
  filename=$(basename "$filepath")
  cmp --silent ".git/hooks/$filename" "$filepath" || {
    cat "$filepath" > ".git/hooks/$filename"
    sudo chmod +x ".git/hooks/$filename"
    echo "Updated $filename hook."
  }
done

branch=$(git branch --show-current)
# When run in GitHub Actions), the code is in detached HEAD state, 
# but the branch name can be extracted from GITHUB_REF.
[[ $branch = "" ]] && {
  if [[ -z $GITHUB_HEAD_REF ]]; then
    echo "Extracting branch name from GITHUB_REF: $GITHUB_REF ..."
    branch="${GITHUB_REF##*/}"
  else
    echo "Extracting branch name from GITHUB_HEAD_REF: $GITHUB_HEAD_REF ..."
    branch="$GITHUB_HEAD_REF"
  fi
}
echo "On branch '${branch}'."

# Make sure this script is being run in the 'main' branch, if not running in CI.
if [[ -z $GITHUB_REF ]]; then
  if [[ ! "$branch" = "main" ]] && [[ ! "$just_do_it" = true ]]; then
    _print_red "
      Check out the main branch before running this script.
      You can use the following command to check out the main branch:
        git checkout main
    "
    echo "
      Alternatively, if you know what you are doing, you can run 
      this script from a non-main branch with the the -j flag.
    "
    exit 1
  fi
  # Make sure the latest updates have been pulled.
  if ! git diff --quiet origin/main && [[ ! "$just_do_it" = true ]]; then
    _error "
      Your modularhistory code differs from what's in origin/main.
      Pull the latest updates, then try running this script again.
      You can use the following command to pull the latest updates:
        git pull
    "
  fi
fi

echo "Detected $os."
zsh_profile="$HOME/.zshrc"

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
fi

# Update package managers
echo "Checking package manager ..."
# Install/update Homebrew
brew help &>/dev/null || {
  echo "Installing Homebrew ..."
  bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  if [[ "$os" == "$LINUX" ]]; then
    _append_to_sh_profile 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"'
  fi
}
brew update
outdated_formulae=$(brew outdated)

function brew_install {
  if brew ls --versions "$1" >/dev/null; then
    echo "$outdated_formulae" | grep --quiet "$1" && {
      echo "Upgrading $1..."
      brew upgrade "$1"
    }
  else
    echo "Installing $1..."
    HOMEBREW_NO_AUTO_UPDATE=1 brew install "$1"
  fi
}

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
fi

if [[ "$os" == "$MAC_OS" ]]; then
  echo "Updating packages ..."
  # PostgreSQL
  brew tap homebrew/services && brew_install postgresql@14
  # Other packages
  brew_install ctags
  brew_install fdupes
  brew_install graphviz
  brew_install openssl@1.1
  brew_install rust
  brew install libjpeg zlib grep gnu-sed jq
  # https://opam.ocaml.org/doc/Install.html
  brew install gpatch
  brew install opam
  # Modify PATH to use GNU Grep over MacOS Grep.
  # shellcheck disable=SC2016
  _append_to_sh_profile 'export PATH="/usr/local/opt/grep/libexec/gnubin:$PATH"'
elif [[ "$os" == "$LINUX" ]]; then
  add-apt-repository ppa:avsm/ppa
  sudo apt update -y && sudo apt upgrade -y
  # Basic dev dependencies
  sudo apt install -y bash-completion curl git wget vim ctags fdupes opam
  # PostgreSQL
  wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
  echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" |
  sudo tee /etc/apt/sources.list.d/pgdg.list
  # All other dependencies
  sudo apt update -y
  sudo apt install -y --allow-downgrades \
  build-essential \
  make \
  graphviz graphviz-dev \
  libbz2-dev libffi-dev liblzma-dev libssl-dev \
  libreadline-dev \
  libsqlite3-dev \
  libncurses5-dev libncursesw5-dev \
  llvm \
  postgresql-client-common postgresql-client-14 \
  python-openssl \
  tk-dev \
  xz-utils \
  zlib1g-dev || _error "Unable to install one or more required packages."
fi

# Install watchman.
brew_install watchman

# Note: These are referenced multiple times in this script.
declare -a writable_dirs=(
  "$VOLUMES_DIR/db/backups"
  "$VOLUMES_DIR/db/init"
  "$VOLUMES_DIR/media"
  "$VOLUMES_DIR/static"
  "$VOLUMES_DIR/redirects"
  "$PROJECT_DIR/frontend/.next"
)

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
  }
  # shellcheck disable=SC2010
  ls -ld "$PROJECT_DIR" | grep -q "$USER www-data" || {
    echo "Granting the www-data group permission to write in project directories ..."
    sudo chown -R "$USER":www-data "$PROJECT_DIR"
  }
  for writable_dir in "${writable_dirs[@]}"; do
    # shellcheck disable=SC2010
    echo "Checking write permissions for $writable_dir ..."
    sudo -u www-data test -w "$writable_dir" || {
      ls -ld "$writable_dir" | grep -q "$USER www-data" || {
        echo "Granting ownership of $writable_dir to ${USER}:www-data ..."
        sudo chown -R "$USER":www-data "$writable_dir"
      }
      echo "Granting the www-data group permission to write in $writable_dir ..."
      sudo chmod g+w -R "$writable_dir"
    }
  done
fi

# Install pyenv.
if [[ "$os_name" == Linux* ]]; then
  # Remove conflicting Windows paths from PATH, if necessary.
  # shellcheck disable=SC2016
  mod='export PATH=$(echo "$PATH" | sed -e "s/:\/mnt\/c\/Users\/[^:]+\/\.pyenv\/pyenv-win\/[^:]+$//")'
  _append_to_sh_profile "$mod"
fi
pyenv_dir="$HOME/.pyenv"
# shellcheck disable=SC2016
_append_to_sh_profile 'export PATH="$HOME/.pyenv/bin:$PATH"'
if [[ -d "$pyenv_dir" ]]; then
  pyenv --version &>/dev/null || {
    echo "Removing extant $pyenv_dir ..."
    sudo rm -rf "$pyenv_dir" &>/dev/null
  }
fi
brew_install pyenv
pyenv --help &>/dev/null || _error "Failed to install pyenv."

# Install the required Python version.
# shellcheck disable=SC2076
if [[ ! "$(pyenv versions)" =~ "$PYTHON_VERSION" ]]; then
  pyenv install "$PYTHON_VERSION"
fi

# Install and configure Poetry.
export POETRY_HOME="$HOME/.poetry"
# shellcheck disable=SC2016
poetry_init='export PATH="$HOME/.poetry/bin:$PATH"'
poetry -q || {
  echo "Installing Poetry ..."
  # https://python-poetry.org/docs/#osx-linux-bashonwindows-install-instructions
  curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python3 -
  _append_to_sh_profile "$poetry_init"
  poetry -q || {
    _error "Failed to install Poetry (https://python-poetry.org/docs/#installation)."
  }
}
# https://python-poetry.org/docs/configuration/
poetry config virtualenvs.create true &>/dev/null
poetry config virtualenvs.in-project true &>/dev/null
poetry self update &>/dev/null
echo "Using $(poetry --version) ..."

# Install the project's Python dependencies.
bash config/scripts/install-deps.sh

# Set up Node Version Manager (NVM).
echo "Enabling NVM ..."
nvm --version &>/dev/null || {
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.35.3/install.sh | bash
  export NVM_DIR="$HOME/.nvm"
  # shellcheck disable=SC1091
  [[ -s "$NVM_DIR/nvm.sh" ]] && \. "$NVM_DIR/nvm.sh"  # loads nvm
  # shellcheck disable=SC1091
  [[ -s "$NVM_DIR/bash_completion" ]] && \. "$NVM_DIR/bash_completion"  # loads nvm bash_completion
}

echo "Updating npm to latest supported version"
nvm install-latest-npm

echo "Installing Node modules ..."
cd frontend && nvm install && nvm use && npm ci --cache .npm && cd ..
npm i -g prettier eslint cypress

# Update ctags
ctags -R -f .vscode/.tags --exclude=".venv/**" --exclude=".backups/**" --exclude="**/node_modules/**" &>/dev/null

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
mkdir -p "$HOME/config/rclone"

# Install dotenv linter.
curl -sSfL https://raw.githubusercontent.com/dotenv-linter/dotenv-linter/master/install.sh | sudo sh -s -- -b /usr/local/bin

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
        docker compose down
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

[[ "$TESTING" = true ]] && {
  echo "
    Finished testing the setup script. Omitted the docker-dependent steps
    of building images & starting containers, syncing media, etc.
  "
  exit 0
}

# Install configuration file for PyInvoke.
cp .config/invoke.yaml "$HOME/.invoke.yaml"

# Add container names to /etc/hosts.
poetry run invoke setup.update-hosts

# Seed a .env file.
poetry run invoke seed --no-db

# Check Docker's memory cap
[[ "$os" == "$MAC_OS" ]] && {
  mem_limit=$(docker stats --format "{{.MemUsage}}" --no-stream | head -1 | gsed -r -e 's/.+ \/ ([0-9]+).*/\1/')
  if [[ "$mem_limit" -lt 2 ]]; then
    _print_red "
      The configured memory limit for Docker is ${mem_limit}. Please increase the memory limit to 3–4 GB.
    "
    echo "
      To do so, open the Docker Desktop application, go to settings, and click Resources.
      Then adjust the memory allocation, and click the Apply & Restart button.
    "
    read -rp "Hit enter to continue. " _
  fi
}

# Build Docker images.
# Note: This requires a .env file.
image_names=( "django" "next" )
for image_name in "${image_names[@]}"; do
  docker compose build "$image_name" || _error "Failed to build $image_name image."
done

# Seed init.sql file.
prompt="Seed db [Y/n]? "
if [[ -f "$VOLUMES_DIR/db/init/init.sql" ]]; then
  prompt="Seed new init.sql file [Y/n]? "
fi
read -rp "$prompt" CONT
if [[ ! "$CONT" = "n" ]] && [[ ! $TESTING = true ]]; then
  # shellcheck disable=SC2015
  poetry run invoke db.seed --remote --migrate || {
    _print_red "Failed to seed database."
    _prompt_to_rerun
    _error "
      Failed to seed database. Try running the following in a new shell:

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
docker compose up -d django next && echo 'Finished.' || {
  _print_red "Failed to start containers."
  [[ ! $TESTING = true ]] && _prompt_to_rerun
  _print_red "
    Could not start containers. 
    Try restarting Docker and/or running the following in a new shell:

      ${BOLD}cd ~/modularhistory && docker compose up -d django next

  "
}

shasum "$PROJECT_DIR/setup.sh" > "$PROJECT_DIR/.venv/.setup.sha"
