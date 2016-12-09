**WRANING: This website currently only has Chinese version. For English version, please wait for a while :-) **

## Introduction
Wanna hosting a Minecraft Server but no handy management panel?
Come and try it!
Obsidian-Panel is a totally open-source and free Minecraft server panel that written in pure python.  It offers necessary tools for managing a Minecraft Server!
Only input one line to install it!

## Requirement
- Linux Server (Ubuntu or CentOS)
- python >= 3.4

## Features
- **TRUE** real-time server status monitoring
- Built-in FTP server
- Java version management

## Installation

### One-Line Method
```
curl -s http://static.demohn.com/sh/install-obpanel | bash
```

Then open your browser and input `[your server domain]:5000` to start!

### Concrete Method

Ubuntu & Debian:

```
apt-get install python3 python3-pip git
pip3 install virtualenv circus
git clone https://github.com/DemoHn/obsidian-panel.git
cd obsidian-panel
virtualenv env
. env/bin/activate
pip3 install -r requirement.txt
circusd production.ini --daemon
```

CentOS & Red Hat:

```
yum update
yum install python3.5 pip3.5 git
pip3.5 install virtualenv circus
git clone https://github.com/DemoHn/obsidian-panel.git
cd obsidian-panel
virtualenv env
. env/bin/activate
pip3.5 install -r requirement.txt
circusd production.ini --daemon
```

Then open your browser and input `[your server domain]:5000` to start!
