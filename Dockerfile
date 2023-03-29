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

#ADD PREINSTALL_JTS.sh .
#RUN ["chmod", "+x", "PREINSTALL_JTS.sh"]

#RUN ./PREINSTALL_JTS.sh

#RUN pip intall BeautifulSoup4
#RUN ln -s /usr/bin/clang-15 /usr/bin/clang
#RUN ln -s /usr/bin/clang++-15 /usr/bin/clang++
#RUN ln -s /usr/bin/clang-cpp-15 /usr/bin/clang-cpp

#RUN rm /bin/sh && ln -s /bin/bash /bin/sh
#RUN pip3 install codechecker
#RUN echo "export PATH=\"$PWD/build/CodeChecker/bin:\$PATH\"" >> ~/.bashrc
#RUN source ~/.bashrc
#ADD . .
#RUN ["chmod", "+x", "createDocker.sh"]
#RUN ./createDocker.sh