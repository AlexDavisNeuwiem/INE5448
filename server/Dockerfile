FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /root

# Instalando pacotes essenciais
RUN apt-get update && \
    apt-get install -y \
    wget unzip curl vim \
    build-essential cmake git python3 python3-full \
    && mkdir /home/server/

# Instalando Rust
ENV CARGO_HOME=/usr/local/cargo
ENV RUSTUP_HOME=/usr/local/rustup
ENV PATH="/usr/local/cargo/bin:$PATH"
RUN curl --proto '=https' --tlsv1.2 https://sh.rustup.rs -sSf | sh -s -- -y && \
    . "$CARGO_HOME/env" && \
    rustup default stable

# Instalando Circom
RUN . "$CARGO_HOME/env" && \
    git clone https://github.com/iden3/circom.git && \
    cd circom && \
    cargo build --release && \
    cargo install --path circom && \
    cd ../

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

# Instalando as bibliotecas circom
RUN mkdir /home/circom-libraries/ && \
    cd /home/circom-libraries/ && \
    git clone https://github.com/iden3/circomlib.git

WORKDIR /home/server/
