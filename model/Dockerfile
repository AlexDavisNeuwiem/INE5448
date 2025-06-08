FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /root

# Instalando pacotes essenciais
RUN apt-get update && \
    apt-get install -y \
    wget unzip curl vim \
    build-essential cmake git python3 python3-full \
    && mkdir /home/model/

# Instalando nvm e snarkjs
ENV NVM_DIR=/root/.nvm
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash && \
    . "$NVM_DIR/nvm.sh" && \
    nvm install 22 && \
    nvm use 22 && \
    nvm alias default 22 && \
    npm install -g snarkjs@latest

# Adiciona Node.js ao PATH (para futuros comandos e shells)
ENV NODE_PATH=$NVM_DIR/versions/node/v22.*/lib/node_modules
ENV PATH=$NVM_DIR/versions/node/v22.*/bin:$PATH

WORKDIR /home/model/
