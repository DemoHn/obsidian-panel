## Introduction
## 简介

Wanna hosting a Minecraft Server but no handy management panel?
Come and try it!
Obsidian-Panel is a totally open-source and free Minecraft server panel that written in pure python.  It offers necessary tools for managing a Minecraft Server!

想要开服，却发现没有顺手的管理工具？

试试`黑曜石面板`吧！

`黑曜石面板`是一个完全开源的 Minecraft 服务器管理面板。它完全采用 Python语言编写。  

只要一行，就可以将其安装到你的服务器上！

## Requirement
- Linux Server (Ubuntu or CentOS)
- python >= 3.4
- redis
- pip3

运行此面板需要：
- 一台Linux服务器（Ubuntu或者CentOS为佳）
- Python >= 3.4
- redis
- pip3

## Features 
- **TRUE** real-time server status monitoring
- Built-in FTP server
- Java version management

- **真** 实时服务器状态监控
- 自带FTP服务器
- 自动下载并安装Java

## Installation
## 安装

### One-Line Method
```
curl -s http://static.demohn.com/sh/install-obpanel | bash
```
Paste the above command to your terminal and execute it.

Then just wait, until the install script finishes.

Finally, open your browser and input `[your server domain]:5000` to start!

复制上面的这行代码并将其粘贴到终端，然后执行之。

稍等片刻，直到此安装脚本执行结束。

然后打开浏览器，在URL栏输入`http://<你的服务器IP>:5000` 即可。

### Concrete Method

If you can't install the panel successfully via 'one-line method', this sample script may help you install manually. Notice, it only works in Debian-like servers (including Debian and Ubuntu). For CentOS users, you may use `yum` to install approperate dependencies.  

```
apt-get install python3 python3-pip git redis
pip3 install virtualenv circus
git clone https://github.com/DemoHn/obsidian-panel.git
cd obsidian-panel
virtualenv env
. env/bin/activate
pip3 install -r requirement.txt
ln -s $(realpath ./bin/ob-panel.sh) /usr/local/bin/ob-panel
ob-panel start
```
