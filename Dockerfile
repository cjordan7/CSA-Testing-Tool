FROM ubuntu:latest
MAINTAINER "Cosme Jordan" "email"

ENV CCACHE_DIR=/ccache

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y build-essential
RUN apt-get install sudo

RUN apt update ; apt install -yq \
        git \
        ccache

RUN for p in gcc g++ cc c++; do ln -vs /usr/bin/ccache /usr/local/bin/$p;  done

RUN mkdir -p home/CSA-Testing-Tool
ADD ./INSTALL.sh home/CSA-Testing-Tool/
RUN ["chmod", "+x", "home/CSA-Testing-Tool/INSTALL.sh"]
RUN --mount=type=cache,target=/ccache/ home/CSA-Testing-Tool/INSTALL.sh debug
RUN --mount=type=cache,target=/ccache/ ccache -s