# Protocolo de Autenticação Multimodal com Zero-Knowledge Proofs

Este projeto implementa um protocolo de registro biométrico seguro com três componentes isolados: Usuário, Servidor e Modelo de IA.

## Arquitetura

### Componentes Principais:

🔵 Serviço do Usuário

Gera chaves simétricas AES-256
Criptografa/descriptografa embeddings
Envia mensagens para outros serviços
NÃO tem acesso ao banco de dados

🟢 Serviço do Servidor

Armazena embeddings criptografadas no PostgreSQL
Retorna IDs únicos de registro
NÃO tem acesso ao modelo de IA nem às chaves

🔴 Serviço do Modelo de IA

Gera embeddings biométricas de 512 dimensões
Simula processamento de reconhecimento facial
NÃO tem acesso ao banco nem às chaves

### Fluxo do Protocolo

TODO

### Estrutura de Arquivos

```
.
├── docker-compose.yml
├── postgres/
│   ├── .env
│   └── data/
├── server/
│   ├── Dockerfile
│   └── code/
│       ├── requirements.txt
│       └── server.py
├── model/
│   ├── Dockerfile
│   └── code/
│       ├── requirements.txt
│       └── model.py
└── user/
    ├── Dockerfile
    └── code/
│       ├── requirements.txt
        └── user.py
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
docker-compose logs -f user-service
```

```
docker-compose logs -f server-service
```

```
docker-compose logs -f model-service
```

## Tecnologias

- Python 3: Linguagem principal
- PostgreSQL: Banco de dados
- Docker: Containerização
- PyCryptodome: Criptografia AES
- NumPy: Processamento numérico
- Psycopg2: Driver PostgreSQL
