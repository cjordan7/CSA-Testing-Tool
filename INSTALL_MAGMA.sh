#!/bin/bash

current=$(pwd)
echo "$current"

pushd .
cd workdir/magma/
git apply ../../data/buildMagma.patch
popd

mkdir -p workdir/magma_libs/libpng
export TARGET=workdir/magma_libs/libpng
bash workdir/magma/targets/libpng/preinstall.sh
bash workdir/magma/targets/libpng/fetch.sh
MAGMA_PATCH="$current/data/MagmaLibPatches/libpngPatchesModified.patch"
cd "$TARGET/repo"
git apply $MAGMA_PATCH
cd "$current"
bash workdir/magma/targets/libpng/build.sh


#mkdir -p workdir/magma_libs/libsndfile
#export TARGET=workdir/magma_libs/libsndfile
#bash workdir/magma/targets/libsndfile/preinstall.sh
## Magma line is buggy
#apt-get update && \
#    apt-get install -y git make autoconf autogen automake build-essential libasound2-dev \
#  libflac-dev libogg-dev libtool libvorbis-dev libopus-dev libmp3lame-dev \
#  libmpg123-dev pkg-config python-is-python3
#sudo ln -s /usr/bin/python3 /usr/bin/python
#bash workdir/magma/targets/libsndfile/fetch.sh
#MAGMA_PATCH="$current/data/MagmaLibPatches/libsndfilePatches.patch"
#cd "$TARGET/repo"
#git apply $MAGMA_PATCH
#cd "$current"
#bash workdir/magma/targets/libsndfile/build.sh

#mkdir -p workdir/magma_libs/libtiff
#export TARGET=/home/CSA-Testing-Tool/workdir/magma_libs/libtiff
#bash workdir/magma/targets/libtiff/preinstall.sh
#bash workdir/magma/targets/libtiff/fetch.sh
#MAGMA_PATCH="$current/data/MagmaLibPatches/libtiffPatches.patch"
#cd "$TARGET/repo"
#git apply $MAGMA_PATCH
#cd "$current"
#bash workdir/magma/targets/libtiff/build.sh

#mkdir -p workdir/magma_libs/libxml2
#export TARGET=workdir/magma_libs/libxml2
#bash workdir/magma/targets/libxml2/preinstall.sh
#bash workdir/magma/targets/libxml2/fetch.sh
#MAGMA_PATCH="$current/data/MagmaLibPatches/libxml2Patches.patch"
#cd "$TARGET/repo"
#git apply $MAGMA_PATCH
#cd "$current"
#bash workdir/magma/targets/libxml2/build.sh

#mkdir -p workdir/magma_libs/lua
#export TARGET=workdir/magma_libs/lua
#bash workdir/magma/targets/lua/preinstall.sh
#bash workdir/magma/targets/lua/fetch.sh
#MAGMA_PATCH="$current/data/MagmaLibPatches/luaPatches.patch"
#cd "$TARGET/repo"
#git apply $MAGMA_PATCH
#cd "$current"
#bash workdir/magma/targets/lua/build.sh

#mkdir -p workdir/magma_libs/openssl
#export TARGET=workdir/magma_libs/openssl
#bash workdir/magma/targets/openssl/preinstall.sh
#bash workdir/magma/targets/openssl/fetch.sh
#MAGMA_PATCH="$current/data/MagmaLibPatches/openssl.patch"
#cd "$TARGET/repo"
#git apply $MAGMA_PATCH
#cd "$current"
#bash workdir/magma/targets/openssl/build.sh

#mkdir -p workdir/magma_libs/php
#export TARGET=workdir/magma_libs/php
#bash workdir/magma/targets/php/preinstall.sh
#bash workdir/magma/targets/php/fetch.sh
#MAGMA_PATCH="$current/data/MagmaLibPatches/php.patch"
#cd "$TARGET/repo"
#git apply $MAGMA_PATCH
#cd "$current"
#bash workdir/magma/targets/php/build.sh

mkdir -p workdir/magma_libs/poppler
export TARGET=/home/CSA-Testing-Tool/workdir/magma_libs/poppler
bash workdir/magma/targets/poppler/preinstall.sh
bash workdir/magma/targets/poppler/fetch.sh
MAGMA_PATCH="$current/data/MagmaLibPatches/popplerPatches.patch"
cd "$TARGET/repo"
git apply $MAGMA_PATCH
cd "$current"

#bash workdir/magma/targets/poppler/build.sh

#mkdir -p workdir/magma_libs/sqlite3
#export TARGET=/home/CSA-Testing-Tool/workdir/magma_libs/sqlite3
#bash workdir/magma/targets/sqlite3/preinstall.sh
#bash workdir/magma/targets/sqlite3/fetch.sh
#MAGMA_PATCH="$current/data/MagmaLibPatches/sqlitePatches.patch"
#cd "$TARGET/repo"
#git apply $MAGMA_PATCH
#cd "$current"

#bash workdir/magma/targets/sqlite3/build.sh
