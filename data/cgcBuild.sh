#!/bin/sh
SCRIPTPATH=$(dirname $(readlink -f "$0"))
LIBCGC="$SCRIPTPATH/../workdir/cgc/lib/libcgc"

echo $LIBCGC

if [ ! -d src ]; then
    echo "Multi-process CBs not supported..." >&2
    exit 1
fi

if [ $# -lt 2 ]; then
    echo "Usage: $0 target cc ..." >&2
    exit 1
fi
set -e
TARGET="$1"; shift

DMACRO=""
DMACRO_LIBC_MALLOC="-DLIBC_MALLOC"
case $TARGET in
    NRFIN_00041|CROMU_00018) DMACRO=$DMACRO_LIBC_MALLOC;;
esac

CFLAGS_CONLY="-std=gnu99"
CFLAGS="-fno-builtin -fno-stack-protector"

LIBSTDCPP=""
CC_CFLAGS=""

echo "all:" > Makefile
echo "	rm -fR obj" >> Makefile
echo "	mkdir obj" >> Makefile

#echo "========================"
for src in src/*.c src/*.cc lib/*.c lib/*.cc; do
    [ -f "$src" ] || continue
#    echo "$* -c $src"
    case $src in
        *.cc) CC_CFLAGS="$@ ${CFLAGS}"
              LIBSTDCPP="-lstdc++" ;;
        *.c) CC_CFLAGS="$@ ${CFLAGS_CONLY} ${CFLAGS}" ;;
    esac

echo "	${CC_CFLAGS} ${DMACRO} -Iinclude -Ilib -I$LIBCGC -c -o ""obj/`basename "$src" | sed 's,[.][^.]*$,.o,'`"" $src" >> Makefile
#    ${CC_CFLAGS} ${DMACRO} -Iinclude -Ilib -I$LIBCGC -c "$src"
#${CC_CFLAGS} ${DMACRO} -Iinclude -Ilib -I$LIBCGC -c -o "obj/`basename "$src" | sed 's,[.][^.]*$,.o,'`" "$src"

#echo ""
#echo "=================="
done

echo "	${CC_CFLAGS} ${DMACRO} -c -o obj/libcgc.o $LIBCGC/libcgc.c" >> Makefile
echo "	${CC_CFLAGS} ${DMACRO} -c -o obj/libcgc_lo.o $LIBCGC/libcgc_lo.S" >> Makefile

#${CC_CFLAGS} ${DMACRO} -c -o obj/libcgc.o $LIBCGC/libcgc.c
#${CC_CFLAGS} ${DMACRO} -c -o obj/libcgc_lo.o $LIBCGC/libcgc_lo.S


# NOTE: Padding is no longer needed for ARM CGC tests.
#case "$1" in
#    arm*|*/arm*) cp $LIBCGC/padding.o obj ;;
#    #NOTYET *) ${CC_CFLAGS} -c -o obj/maths.o "$LIBCGC/maths.s" ;;
#esac

echo "	${CC_CFLAGS} -nostartfiles -o "$TARGET" obj/*.o -lm "$LIBSTDCPP >> Makefile
