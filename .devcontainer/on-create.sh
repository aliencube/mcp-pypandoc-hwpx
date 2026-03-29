#!/bin/bash
set -e

sudo apt-get update && \
    sudo apt upgrade -y && \
    sudo apt-get install -y dos2unix libsecret-1-0 xdg-utils && \
    sudo apt clean -y && \
    sudo rm -rf /var/lib/apt/lists/*

echo "Configure git"
git config --global pull.rebase false
git config --global core.autocrlf input

echo "Install uv"
curl -LsSf https://astral.sh/uv/install.sh | sh

echo "Install Azure Bicep CLI"
az bicep install

echo "Install dependencies"
uv sync

echo "Done!"
