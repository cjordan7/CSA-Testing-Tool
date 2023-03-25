#!/bin/bash

sudo apt-get update -y

# Install Makefile, gcc, g++
sudo apt-get install -y build-essential

# Install cmake
sudo apt-get -y libssl-dev
sudo apt-get -y install cmake

# Install git
sudo apt install -y git

sudo apt-get install -y lld
sudo apt-get install -y ccache

# Update symlinks
sudo /usr/sbin/update-ccache-symlinks

# Prepend ccache into the PATH
echo 'export PATH="/usr/lib/ccache:$PATH"' | tee -a ~/.bashrc

# Source bashrc to test the new PATH
source ~/.bashrc && echo $PATH


# Install ninja
sudo apt-get install -y ninja-build

# Install python
sudo apt install -y python3-pip

# Install curl
sudo apt install -y curl

pip install argparse
