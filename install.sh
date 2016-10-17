#!/bin/bash
# ref: https://github.com/icy/pacapt/blob/master/pacapt
_SUDO=""
_OSTYPE=""

_URL="https://github.com/DemoHn/obsidian-panel.git"

_check_sudo() {
	if [[ "$EUID" -ne 0 ]]; then
	    echo -e "\n"
	    echo "[HINT] You are not running on root."
	    echo "[HINT] Don't worry. Just input your root password in the following step."
	    echo "[HINT] If 'sudo' command have not been installed yet, or you can't use 'sudo' to"
	    echo "[HINT] elevate your privilege, try using 'su' and run this script again :-)"
	    _SUDO="sudo"
	fi
}

_found_arch() {
  local _ostype="$1"
  shift
  grep -qis "$*" /etc/issue && _OSTYPE="$_ostype"
}

_error() {
  echo >&2 ":: $*"
}

_OSTYPE_detect() {
  _found_arch PACMAN "Arch Linux" && return
  _found_arch DPKG   "Debian GNU/Linux" && return
  _found_arch DPKG   "Ubuntu" && return
  _found_arch YUM    "CentOS" && return
  _found_arch YUM    "Red Hat" && return
  _found_arch YUM    "Fedora" && return
  _found_arch ZYPPER "SUSE" && return

  [[ -z "$_OSTYPE" ]] || return

  # See also https://github.com/icy/pacapt/pull/22
  # Please not that $OSTYPE (which is `linux-gnu` on Linux system)
  # is not our $_OSTYPE. The choice is not very good because
  # a typo can just break the logic of the program.
  if [[ "$OSTYPE" != "darwin"* ]]; then
    _error "Can't detect OS type from /etc/issue. Running fallback method."
  fi
  if [[ -x "/usr/bin/pacman" ]]; then
    # This is to prevent a loop when this script is installed on
    # non-standard system
    grep -q "$FUNCNAME" '/usr/bin/pacman' >/dev/null 2>&1
    [[ $? -ge 1 ]] && _OSTYPE="PACMAN" && return
  fi
  [[ -x "/usr/bin/apt-get" ]]          && _OSTYPE="DPKG" && return
  [[ -x "/usr/bin/yum" ]]              && _OSTYPE="YUM" && return
  [[ -x "/opt/local/bin/port" ]]       && _OSTYPE="MACPORTS" && return
  command -v brew >/dev/null           && _OSTYPE="HOMEBREW" && return
  [[ -x "/usr/bin/emerge" ]]           && _OSTYPE="PORTAGE" && return
  [[ -x "/usr/bin/zypper" ]]           && _OSTYPE="ZYPPER" && return
  if [[ -z "$_OSTYPE" ]]; then
    _error "No supported package manager installed on system"
    _error "(supported: apt, homebrew, pacman, portage, yum)"
    exit 1
  fi
}

_check_sudo
_OSTYPE_detect

echo "Package Manager: $_OSTYPE"
# install necessary packages
# for Ubuntu, Debian
if [ $_OSTYPE = "DPKG" ]; then
    $_SUDO apt-get update
    $_SUDO apt-get install -y python3 python3-pip git

    # install virtualenv,circusd
    $_SUDO pip3 install virtualenv circus
fi

# For CentOS, Red Hat, Fedora
if [ $_OSTYPE = "YUM" ]; then
    $_SUDO yum update
    $_SUDO yum install -y python3.5 pip3.5 git

    $_SUDO pip3.5 install virtualenv circus
fi

# clone code
echo "[HINT] Now clone source code"
echo "[HINT] Obsidian Panel is STILL testing!"
git clone $_URL obsidian-panel
cd obsidian-panel

# shift into virtualenv
virtualenv env
. env/bin/activate

# now, install required packages!
if [ $_OSTYPE = "DPKG" ]; then
    pip3 install -r requirement.txt
fi

# For CentOS, Red Hat, Fedora
if [ $_OSTYPE = "YUM" ]; then
    pip3.5 install -r requirement.txt
fi

echo "[HINT] Finally, run the instance!"
circusd production.ini --daemon

#
# psutil
# redis