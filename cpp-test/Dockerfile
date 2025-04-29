FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /root

RUN apt-get update && \
    apt-get install -y \
    wget unzip curl vim \
    build-essential cmake git libgmp3-dev libprocps-dev python3-markdown libboost-program-options-dev libssl-dev python3 pkg-config

RUN git clone https://github.com/scipr-lab/libsnark/ \
    && cd libsnark \
    && git submodule init && git submodule update \
    && mkdir build && cd build && cmake .. \
    && make \
    && make install \
    NO_PROCPS=1 NO_GTEST=1 NO_DOCS=1 CURVE=EDWARDS FEATUREFLAGS="-DBINARY_OUTPUT=1 -DMONTGOMERY_OUTPUT=1 -DNO_PT_COMPRESSION=1"

ENV LD_LIBRARY_PATH $LD_LIBRARY_PATH:/usr/local/lib

WORKDIR /home

RUN mkdir zk-test/

CMD ["tail", "-f", "/dev/null"]
