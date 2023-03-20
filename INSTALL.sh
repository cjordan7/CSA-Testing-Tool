

# Install Makefile, gcc, g++
sudo apt-get install build-essential

# Install cmake
sudo apt-get libssl-dev
sudo apt-get install cmake

# Install git
sudo apt install git-all


# Install ninja
sudo apt-get install ninja-build

# Install z3
sudo apt-get install z3

# Install curl
sudo apt install curl


# File system
# . data
# >. linux-syzbot
# >. csaTable
# >.
# . workdir
# >. codechecker
# >. llvm-project
# >. julietTestSuite
# >. cgc
# >. magma
# >. linux
# . reports
# >. julietTestSuite
# >. cgc
# >. magma
# >. linux

# Special variables



# Change all of this to make it more extensible
declare -a arr=("linux-syzbot" "llvm-project" "codechecker" "julietTestSuite" "cgc"
                "magma" "linux")

temp="class Variables():"
for i in "${arr[@]}"
do
    echo ${i}
    # Create directories
    workDir=workdir/"$i"
    reportsDir=reports/"$i"
    echo ${workDir}
    mkdir -p ${workDir}
    mkdir -p ${reportsDir}

    # Replace instances of `-` with `_`
    replaced="${i/-/_}"

    # Lowercase to capital case
    up=$(echo ${replaced} | tr '[:lower:]' '[:upper:]')

    # Add it to the class Variables
    temp="${temp}"$'\n\t'"DATA_${up}_WORKDIR = \"${workDir}\""
    temp="${temp}"$'\n\t'"DATA_${up}_REPORT_DIR = \"${reportsDir}\""
    echo "$temp"
    # or do whatever with individual element of the array
done

echo "${temp}" > variables.py


# TODO: Create a sub file for each of clone project??

# Clone Magma
git clone -b 'v1.2' --single-branch https://github.com/HexHive/magma.git --depth 1 workdir/magma


# Clone LLVM. We only clone the tags we are interested in.
# We don't need to clone all commits as we only use the last version
git clone -b 'llvmorg-15.0.7' --single-branch https://github.com/llvm/llvm-project.git --depth 1 workdir/llvm-project

# Clone Linux
# We need to clone all of Linux for `git log`
git clone https://github.com/torvalds/linux.git

# TODO: Give parameter to build from source
# Build it
pushd
cd llvm-project
mkdir build
cd build
cmake -G Ninja -DLLVM_TARGETS_TO_BUILD=X86 -DLLVM_ENABLE_PROJECTS="clang;clang-tools-extra" -DCMAKE_BUILD_TYPE=RelWithDebInfo -DLLVM_ENABLE_RUNTIMES="libcxx;libcxxabi;libunwind" -DLLVM_ENABLE_ASSERTIONS=yes -DLLVM_ENABLE_Z3_SOLVER=yes -DBUILD_SHARED_LIBS=yes ../llvm

popd

git clone https://github.com/GrammaTech/cgc-cbs workdir/cgc


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# Git clone CodeChecker
# Install mandatory dependencies for a development and analysis environment.
# NOTE: clang or clang-tidy can be any sufficiently fresh version, and need not
#       come from package manager!
sudo apt-get install clang clang-tidy build-essential curl gcc-multilib \
      git python3-dev python3-venv

# Install nodejs dependency for web. In case of Debian/Ubuntu you can use the
# following commands. For more information see the official docs:
# https://nodejs.org/en/download/package-manager/
curl -sL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs


# TODO: Get a special tags

# Check out CodeChecker source code.
git clone --branch 'v6.21.0' --single-branch https://github.com/Ericsson/CodeChecker.git --depth 1 workdir/codechecker
cd workdir/codechecker

# Create a Python virtualenv and set it as your environment.
# NOTE: if you want to develop CodeChecker, use the `venv_dev` target instead
# of `venv`.
make venv
source $PWD/venv/bin/activate

# [Optional] If you want to use external authentication methods (LDAP / PAM)
# follow the instructions in
# docs/web/authentication.md#external-authentication-methods

# Build and install a CodeChecker package.
make package

# For ease of access, add the build directory to PATH.
export PATH="$PWD/build/CodeChecker/bin:$PATH"
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------