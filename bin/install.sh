#!/bin/bash
# detect OS type
# ref: https://github.com/icy/pacapt/blob/master/pacapt
_SUDO=""
_OSTYPE=""

_URL="https://github.com/DemoHn/obsidian-panel.git"

_check_sudo() {
	if [[ "$EUID" -ne 0 ]]; then
	    echo -e "\n"
	    echo "[INFO] You are not running on root."
	    echo "[INFO] Don't worry. Just input your root password in the following step."
	    echo "[INFO] If 'sudo' command have not been installed yet, or you can't use 'sudo' to"
	    echo "[INFO] elevate your privilege, try using 'su' and run this script again :-)"
	    _SUDO="sudo"
	fi
}

_realpath () {
    [[ $1 = /* ]] && echo "$1" || echo "$PWD/${1#./}"
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

_get_centOS_version(){
    _centOS_version=$($_SUDO rpm -q --queryformat '%{VERSION}' centos-release)
}

_detect_dpendency(){
    if command -v $1 >/dev/null 2>&1; then
        return 1
    else
        return 0
    fi
}

_make_install_git(){
    # install Git
    cd /var/tmp
    wget https://github.com/git/git/archive/v2.4.0.tar.gz -O /var/tmp/git-2.4.0.tar.gz
    tar xzf git-2.4.0.tar.gz
    cd git-2.4.0
    autoconf
    ./configure
    make
    make install
}

_make_install_python3(){
    # install python 3.5.2 by compiling it
    cd /var/tmp
    wget http://www.python.org/ftp/python/3.5.2/Python-3.5.2.tar.xz -O /var/tmp/Python-3.5.2.tar.xz

    # for centos 5, this does a small trick
    # see https://www.centos.org/forums/viewtopic.php?t=5059
    # this is the most conservative way to uncompress tar.xz
    $_SUDO yum install -y xz
    cd /var/tmp
    unxz Python-3.5.2.tar.xz
    tar xf Python-3.5.2.tar
    tar xf /var/tmp/Python-3.5.2.tar.xz

    cd /var/tmp/Python-3.5.2
    ./configure --enable-loadable-sqlite-extensions
    make
    make install
}

_make_install_pip3(){
    echo "[INFO] install python3-pip"
    wget --no-check-certificate https://pypi.python.org/packages/source/s/setuptools/setuptools-1.4.2.tar.gz -O /var/tmp/setuptools-1.4.2.tar.gz
    cd /var/tmp
    tar xf /var/tmp/setuptools-1.4.2.tar.gz
    cd setuptools-1.4.2
    python3 setup.py install
    wget --no-check-certificate https://bootstrap.pypa.io/get-pip.py -O /var/tmp/get-pip.py
    python3 /var/tmp/get-pip.py install
    # upgrade pip
    pip3 install --upgrade pip
}

_check_sudo
_OSTYPE_detect

echo "Package Manager: $_OSTYPE"
# install necessary packages
# for Ubuntu, Debian
if [ $_OSTYPE = "DPKG" ]; then
    $_SUDO apt-get update -y
    $_SUDO apt-get install -y python3 python3-pip git libzmq-dev
    # install virtualenv,circusd
    $_SUDO pip3 install virtualenv circus
fi

# For CentOS, Red Hat, Fedora
if [ $_OSTYPE = "YUM" ]; then
    $_SUDO yum update -y

    $_SUDO yum groupinstall -y "Development Tools"
    $_SUDO yum install -y zlib zlib-devel openssl-devel curl-devel sqlite-devel

    # install dependcies
    _detect_dpendency git && _make_install_git
    _detect_dpendency python3 && _make_install_python3
    _detect_dpendency pip3 && _make_install_pip3

    $_SUDO pip3 install virtualenv circus
fi

#TODO other OS support
# clone code
echo "[INFO] Now let's clone the source code"
CLONE_DIR="/opt/obsidian-panel"
ENV_DIR="/opt/obsidian-panel/env"
if [ ! -d "$CLONE_DIR" ]; then
    $_SUDO git clone $_URL /opt/obsidian-panel
    $_SUDO cd $CLONE_DIR
    virtualenv /opt/obsidian-panel/env
else
    $_SUDO cd $CLONE_DIR
    if [ ! -d "$ENV_DIR" ]; then
        virtualenv /opt/obsidian-panel/env
    fi
fi
# run virtualenv
. env/bin/activate

# now, install required packages!
pip3 install -r requirement.txt

# install `ob-panel` command to /usr/local/bin
echo "[INFO] Copying op-panel command"

# make sure the old file has been removed
$_SUDO rm /usr/local/bin/ob-panel 2>/dev/null
$_SUDO ln -s $(_realpath ./bin/ob-panel.sh) /usr/local/bin/ob-panel

$_SUDO rm /etc/init.d/ob-panel 2>/dev/null
$_SUDO ln -s $(_realpath ./bin/ob-panel.sh) /etc/init.d/ob-panel

# copy config.sample
CONFIG_SAMPLE_FILE=$(_realpath ./config.yaml.sample)
CONFIG_FILE=$(_realpath ./config.yaml)
if [ ! -f "$CONFIG_FILE" ]; then
    cp $CONFIG_SAMPLE_FILE $CONFIG_FILE
fi
# configure autostart
if [ $_OSTYPE = "DPKG" ]; then
    update-rc.d ob-panel defaults
    update-rc.d ob-panel enable
fi

if [ $_OSTYPE = "YUM" ]; then
    chkconfig --add ob-panel
    chkconfig ob-panel on
fi
echo "[INFO] Finally, let's start!"
ob-panel restart
