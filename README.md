# Protocolo de Autenticação Multimodal com Zero-Knowledge Proofs

Este projeto implementa um protocolo de registro biométrico seguro com três componentes isolados: Usuário, Servidor e Modelo de IA.

## Arquitetura

### Principais Componentes:

🔴 Modelo de IA

Gera embeddings biométricas de 512 dimensões
Simula processamento de reconhecimento facial

🟢 Usuário

Gera chaves simétricas AES-256
Criptografa/descriptografa embeddings
Solicita registro e autenticação

🔵 Servidor

Armazena embeddings criptografadas no banco de dados
Retorna IDs únicos de registro

### Fluxo do Protocolo

TODO

### Estrutura de Arquivos

```
.
├── docker-compose.yml
├── postgres/
│   ├── data/
│   └── .env
├── server/
│   ├── code/
│   └── Dockerfile
├── model/
│   ├── code/
│   └── Dockerfile
└── user/
    ├── code/
    └── Dockerfile
```

## Execução com Docker

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

## Para acompanhar logs específicos

```
docker-compose logs -f [NOME DO SERVIÇO]
```

## Tecnologias

### Bibliotecas Python

- PySnark: Geração das ZKPs
- Psycopg2: Driver PostgreSQL
- PyCryptodome: Criptografia AES
- FaceNet-PyTorch: Processamento de imagens faciais

## Outras ferramentas utilizadas

- Docker: Containerização
- PostgreSQL: Banco de dados


