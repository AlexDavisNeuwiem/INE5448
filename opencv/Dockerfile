FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /root

# Instalando pacotes essenciais
RUN apt-get update && \
    apt-get install -y \
    wget unzip curl vim \
    build-essential cmake git python3 python3-full \
    && mkdir /home/opencv/

WORKDIR /home/opencv/
