# Protocolo de Autenticação Biométrica com Provas de Conhecimento Zero

Este projeto implementa um protocolo de autenticação biométrica segura com três componentes isolados: Usuário, Servidor e Modelo de IA.

## Componentes do Sistema

### Modelo de IA

- Gera embeddings biométricas de 512 dimensões por meio de reconhecimento facial
- Gera as provas zk-SNARKs com base na similaridade das embeddings biométricas

### Usuário

- Gera chaves simétricas AES-256
- Criptografa/descriptografa as embeddings biométricas
- Solicita registro e autenticação

### Servidor

- Armazena as embeddings criptografadas no banco de dados
- Gera IDs únicos de registro
- Valida a autenticação por meio da verificação das provas zk-SNARKs

## Comandos Docker

### Criar os contêineres
    docker-compose up --build

### Acompanhar logs específicos
    docker-compose logs -f [NOME DO SERVIÇO]

### Remover os contêineres
    docker-compose down

### Executar um contêiner específico
    docker exec -it [NOME DO CONTÊINER] /bin/bash

### Sair do ambiente do serviço
    exit


## Comandos Make

### Instalar as dependências
    make install

### Executar o programa (INPUT é opcional)
    make run INPUT=[ENTRADA]

### Instalar as dependências e executar o programa em seguida
    make

### Limpando os binários
    make clean


## Execução do projeto

### 1. Na raiz do projeto, execute o comando de criação dos contêineres:
    docker-compose up --build

### 2. Em seguida, acesse cada contêiner separadamente:
```
docker exec -it model-container /bin/bash
```
```
docker exec -it user-container /bin/bash
```
```
docker exec -it server-container /bin/bash
```

### 3. Por fim, no terminal de cada serviço, rode o código de execução:
    make
\* Execute o código do Usuário apenas quando os demais serviços já estiverem rodando


## Tecnologias utilizadas

### Bibliotecas Python

- snarkJS: Geração das ZKPs
- Psycopg2: Driver PostgreSQL
- PyCryptodome: Criptografia AES
- FaceNet-PyTorch: Processamento de imagens faciais

### Outras ferramentas

- Docker: Containerização
- PostgreSQL: Banco de dados


