FROM ubuntu:latest

ENV CCACHE_DIR=/ccache

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y build-essential
RUN apt-get install sudo

RUN apt update ; apt install -yq \
        git \
        ccache

RUN for p in gcc g++ cc c++; do ln -vs /usr/bin/ccache /usr/local/bin/$p;  done

WORKDIR home/CSA-Testing-Tool
ADD INSTALL.sh .
RUN ["chmod", "+x", "INSTALL.sh"]
RUN --mount=type=cache,target=/ccache/ ./INSTALL.sh

ADD data/ data/
ADD INSTALL_MAGMA.sh .
RUN ["chmod", "+x", "INSTALL_MAGMA.sh"]
RUN ./INSTALL_MAGMA.sh

ADD PREINSTALL_JTS.sh .
RUN ["chmod", "+x", "PREINSTALL_JTS.sh"]

RUN ./PREINSTALL_JTS.sh
ADD . .