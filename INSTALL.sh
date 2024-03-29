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

# Special variables
declare -a arr=("linux-syzbot" "llvm-project" "julietTestSuite" "cgc" "magma" "linux")

temp="# Automatically Generated file. DO NOT CHANGE!. \n\n\nclass Variables():"
for i in "${arr[@]}"
do
    # Create directories
    workDir=workdir/"$i"
    reportsDir=reports/"$i"
    mkdir -p ${workDir}
    mkdir -p ${reportsDir}

    # Replace instances of `-` with `_`
    replaced="${i/-/_}"

    # Lowercase to capital case
    up=$(echo ${replaced} | tr '[:lower:]' '[:upper:]')

    # Add it to the class Variables
    temp="${temp}"$'\n    '"DATA_${up}_WORKDIR = \"${workDir}\""
    temp="${temp}"$'\n    '"DATA_${up}_REPORT_DIR = \"${reportsDir}\""
done

temp="${temp}"$'\n    '"DATA_Z3_WORKDIR = \"workdir/z3\""
temp="${temp}"$'\n    '"DATA_CODECHECKER_WORKDIR = \"workdir/codechecker\""
temp="${temp}"$'\n    '"DATA_FOLDER = \"data\""
temp="${temp}"$'\n    '"CGC_PATCH_PATH = \"data/cgc_patch.patch\""
temp="${temp}"$'\n    '"CSA_CHECKERS_PATH = \"data/csaCheckers.txt\""
temp="${temp}"$'\n    '"CGC_BUILD = \"data/cgcBuild.sh\""

echo "${temp}" > variables.py

# Installing z3 from source because it seems the Ubuntu package doesn't install any
# libraries which are need for LLVM
git clone -b 'z3-4.12.1' --single-branch https://github.com/Z3Prover/z3.git --depth 1 workdir/z3

pushd .
cd workdir/z3
python3 scripts/mk_make.py
cd build
make -j$(nproc)
sudo make install
popd

# Clone Magma
git clone -b 'v1.2' --single-branch https://github.com/HexHive/magma.git --depth 1 workdir/magma

debug=$1
if [ "$debug" = "debug" ]; then
  # Clone LLVM. We only clone the tags we are interested in.
  # We don't need to clone all commits as we only use the last version
  git clone -b 'llvmorg-15.0.7' --single-branch https://github.com/llvm/llvm-project.git --depth 1 workdir/llvm-project


  # TODO: Give parameter to build from source
  # Build it
  pushd .
  cd workdir/llvm-project
  mkdir build
  cd build

  # TODO: Test code
  architecture=""
  case $(uname -m) in
      x86_64) architecture="X86" ;;
      arm) architecture="ARM" ;;
  esac

  cmake -G Ninja -DLLVM_TARGETS_TO_BUILD=$architecture -DLLVM_ENABLE_PROJECTS="clang;clang-tools-extra" -DCMAKE_BUILD_TYPE=RelWithDebInfo -DLLVM_ENABLE_RUNTIMES="libcxx;libcxxabi;libunwind" -DLLVM_ENABLE_ASSERTIONS=yes -DLLVM_ENABLE_Z3_SOLVER=yes -DBUILD_SHARED_LIBS=no -DLLVM_USE_LINKER=gold -DLLVM_PARALLEL_LINK_JOBS=1 ../llvm

  ninja

  popd
else
  sudo apt-get install -y clang-15 libclang-common-15-dev libclang-cpp15 libclang1-15 llvm-15 llvm-15-dev llvm-15-linker-tools llvm-15-runtime llvm-15-tools clang-tools-15
fi

sudo pip install pycrypto pyyaml matplotlib defusedxml
sudo apt-get install -y pandoc

pushd .
git clone https://github.com/GrammaTech/cgc-cbs --depth 1 workdir/cgc
cd workdir/cgc
git checkout 797bd722ea544ab8205446dde13dcfdc059c0989
popd


pushd .
# Clone Linux
# We need to clone all of Linux for `git log`
sudo apt-get install build-essential libncurses-dev bison flex libssl-dev libelf-dev
#git clone https://github.com/torvalds/linux.git

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# Git clone CodeChecker
# Install mandatory dependencies for a development and analysis environment.
sudo apt-get install -y build-essential curl gcc-multilib \
      git python3-dev python3-venv

pip install compiledb
echo "export PATH=\"`python3 -m site --user-base`/bin:\$PATH\"" >> ~/.bashrc
source ~/.bashrc

# For intercept-build
pip install scan-build

# Install nodejs dependency for web. In case of Debian/Ubuntu you can use the
# following commands. For more information see the official docs:
# https://nodejs.org/en/download/package-manager/
curl -sL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs

# Check out CodeChecker source code.
git clone --branch 'v6.21.0' --single-branch https://github.com/Ericsson/CodeChecker.git --depth 1 workdir/codechecker
cd workdir/codechecker

# Create a Python virtualenv and set it as your environment.
# NOTE: if you want to develop CodeChecker, use the `venv_dev` target instead
# of `venv`.
make venv
#source $PWD/venv/bin/activate

# Build and install a CodeChecker package.
make package

# For ease of access, add the build directory to PATH.

echo "export PATH=\"$PWD/build/CodeChecker/bin:\$PATH\"" >> ~/.bashrc
source ~/.bashrc


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
 popd
