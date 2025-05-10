# INE5448
Implementação de um Sistema de Autenticação Multimodal com Zero-Knowledge Proofs

## Docker

### Criando os contêineres
    docker-compose up --build

### Removendo os contêineres
    docker-compose down

### Executando um serviço específico
    docker exec -it [NOME DO CONTÊINER] /bin/bash

### Saindo do ambiente do serviço
    exit

## Make

### Instalando as dependências
    make install

### Executando um programa (INPUT é opcional)
    make run INPUT=[ENTRADA]

### Limpando os binários
    make clean
