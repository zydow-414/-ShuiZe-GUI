#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

apt install python3 -y
apt install python3-pip --fix-missing -y
apt install python3-setuptools -y
apt install tmux -y
python3 -m pip install --upgrade pip
python3 -m pip install openpyxl==2.6.4
python3 -m pip install Cython
python3 -m pip install -r "${REPO_ROOT}/requirements.txt"
chmod 777 "${REPO_ROOT}/Plugins/infoGather/subdomain/ksubdomain/ksubdomain_linux"
