FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /root

# Instalando pacotes essenciais
RUN apt-get update && \
    apt-get install -y \
    wget unzip curl vim \
    build-essential cmake git python3 python3-full \
    && mkdir /home/model/

# Instalando snarkjs
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash \
    && \. "$HOME/.nvm/nvm.sh" \
    && nvm install 22 \
    && npm install -g snarkjs@latest

WORKDIR /home/model/
