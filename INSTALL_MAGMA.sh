

TODO: Apply patch to remove fuzzers installation

mkdir -p workdir/magma_libs


mkdir -p workdir/magma_libs/libpng
TARGET=workdir/magma_libs/libpng
bash workdir/magma/targets/libpng/preinstall.sh
bash workdir/magma/targets/libpng/fetch.sh
bash workdir/magma/targets/libpng/build.sh

mkdir -p workdir/magma_libs/libsndfile
TARGET=workdir/magma_libs/libsndfile
bash workdir/magma/targets/libsndfile/preinstall.sh
bash workdir/magma/targets/libsndfile/fetch.sh
bash workdir/magma/targets/libsndfile/build.sh

mkdir -p workdir/magma_libs/libtiff
TARGET=workdir/magma_libs/libtiff
bash workdir/magma/targets/libtiff/preinstall.sh
bash workdir/magma/targets/libtiff/fetch.sh
bash workdir/magma/targets/libtiff/build.sh

mkdir -p workdir/magma_libs/libxml2
TARGET=workdir/magma_libs/libxml2
bash workdir/magma/targets/libxml2/preinstall.sh
bash workdir/magma/targets/libxml2/fetch.sh
bash workdir/magma/targets/libxml2/build.sh

mkdir -p workdir/magma_libs/lua
TARGET=workdir/magma_libs/lua
bash workdir/magma/targets/lua/preinstall.sh
bash workdir/magma/targets/lua/fetch.sh
bash workdir/magma/targets/lua/build.sh

mkdir -p workdir/magma_libs/openssl
TARGET=workdir/magma_libs/openssl
bash workdir/magma/targets/openssl/preinstall.sh
bash workdir/magma/targets/openssl/fetch.sh
bash workdir/magma/targets/openssl/build.sh

mkdir -p workdir/magma_libs/php
TARGET=workdir/magma_libs/php
bash workdir/magma/targets/php/preinstall.sh
bash workdir/magma/targets/php/fetch.sh
bash workdir/magma/targets/php/build.sh

mkdir -p workdir/magma_libs/poppler
TARGET=workdir/magma_libs/poppler
bash workdir/magma/targets/poppler/preinstall.sh
bash workdir/magma/targets/poppler/fetch.sh
bash workdir/magma/targets/poppler/build.sh

mkdir -p workdir/magma_libs/sqlite3
TARGET=workdir/magma_libs/sqlite3
bash workdir/magma/targets/sqlite3/preinstall.sh
bash workdir/magma/targets/sqlite3/fetch.sh
bash workdir/magma/targets/sqlite3/build.sh
