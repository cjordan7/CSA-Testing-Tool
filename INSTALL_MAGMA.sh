#!/bin/bash

current=$(pwd)
echo "$current"

pushd .
cd workdir/magma/
git apply ../../data/buildMagma.patch
popd

mkdir -p workdir/magma_libs/libsndfile
export TARGET=workdir/magma_libs/libsndfile
sudo bash workdir/magma/targets/libsndfile/preinstall.sh
# Magma line is buggy
sudo apt-get update && \
    apt-get install -y git make autoconf autogen automake build-essential libasound2-dev \
  libflac-dev libogg-dev libtool libvorbis-dev libopus-dev libmp3lame-dev \
  libmpg123-dev pkg-config python-is-python3
sudo ln -s /usr/bin/python3 /usr/bin/python
bash workdir/magma/targets/libsndfile/fetch.sh
bash workdir/magma/targets/libsndfile/build.sh


declare -a arr=("libpng" "libtiff" "libxml2" "lua" "openssl" "php" "poppler" "sqlite3")

for i in "${arr[@]}"
do
    mkdir -p workdir/magma_libs/$i
    export TARGET=$(pwd)/workdir/magma_libs/$i
    sudo bash workdir/magma/targets/$i/preinstall.sh
    bash workdir/magma/targets/$i/fetch.sh
    bash workdir/magma/targets/$i/build.sh
done

#mkdir -p workdir/magma_libs/libpng
#export TARGET=$(pwd)/workdir/magma_libs/libpng
#sudo bash workdir/magma/targets/libpng/preinstall.sh
#bash workdir/magma/targets/libpng/fetch.sh
#bash workdir/magma/targets/libpng/build.sh
#
#mkdir -p workdir/magma_libs/libtiff
#export TARGET=$(pwd)/workdir/magma_libs/libtiff
#sudo bash workdir/magma/targets/libtiff/preinstall.sh
#bash workdir/magma/targets/libtiff/fetch.sh
#bash workdir/magma/targets/libtiff/build.sh
#
#mkdir -p workdir/magma_libs/libxml2
#export TARGET=$(pwd)/workdir/magma_libs/libxml2
#sudo bash workdir/magma/targets/libxml2/preinstall.sh
#bash workdir/magma/targets/libxml2/fetch.sh
#bash workdir/magma/targets/libxml2/build.sh
#
#mkdir -p workdir/magma_libs/lua
#export TARGET=$(pwd)/workdir/magma_libs/lua
#sudo bash workdir/magma/targets/lua/preinstall.sh
#bash workdir/magma/targets/lua/fetch.sh
#bash workdir/magma/targets/lua/build.sh
#
#mkdir -p workdir/magma_libs/openssl
#export TARGET=$(pwd)/workdir/magma_libs/openssl
#sudo bash workdir/magma/targets/openssl/preinstall.sh
#bash workdir/magma/targets/openssl/fetch.sh
#bash workdir/magma/targets/openssl/build.sh
#
#mkdir -p workdir/magma_libs/php
#export TARGET=$(pwd)/workdir/magma_libs/php
#sudo bash workdir/magma/targets/php/preinstall.sh
#bash workdir/magma/targets/php/fetch.sh
#bash workdir/magma/targets/php/build.sh
#
#mkdir -p workdir/magma_libs/poppler
#export TARGET=$(pwd)/workdir/magma_libs/poppler
#sudo bash workdir/magma/targets/poppler/preinstall.sh
#bash workdir/magma/targets/poppler/fetch.sh
#bash workdir/magma/targets/poppler/build.sh
#
#mkdir -p workdir/magma_libs/sqlite3
#export TARGET=$(pwd)/workdir/magma_libs/sqlite3
#sudo bash workdir/magma/targets/sqlite3/preinstall.sh
#bash workdir/magma/targets/sqlite3/fetch.sh
#bash workdir/magma/targets/sqlite3/build.sh
