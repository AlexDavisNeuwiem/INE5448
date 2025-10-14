# Protocolo de Autenticação Biométrica Facial com Provas de Conhecimento Zero

Este projeto implementa um protocolo de autenticação biométrica segura com três componentes isolados: Usuário, Servidor e Modelo de IA.

## Componentes do Sistema

### Modelo de IA

- Gera embeddings biométricas de 512 dimensões por meio de reconhecimento facial
- Gera as provas zk-SNARKs do protocolo Groth16 com base na similaridade das embeddings biométricas

### Usuário

- Gera chaves simétricas AES-256
- Criptografa/descriptografa as embeddings biométricas
- Solicita registro e autenticação

### Servidor

- Armazena as embeddings criptografadas no banco de dados
- Gera IDs únicos de registro
- Valida a autenticação por meio da verificação das provas zk-SNARKs do protocolo Groth16

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

### 3. Insira as imagens com as faces para registro e autenticação na pasta "user/code/faces/":

- Por padrão, a imagem a ser cadastrada na fase de registro deve ser nomeada "1.jpeg", enquanto a imagem com a face para o processo de autenticação deve ter o nome "2.jpeg".

- É possível alterar esses nomes no arquivo "user/code/enum.py".

- **Observação**: O desempenho da biblioteca FaceNet-PyTorch está diretamente relacionado à capacidade de processamento da CPU. Dessa forma, pode ser necessário ajustar a variável "SCALE", localizada em "model/code/enums.py", para assegurar o funcionamento adequado da aplicação para você. (Embora o projeto tenha sido desenvolvido com o objetivo de ser independente de configurações específicas, essas coisas acontecem...)

### 4. Por fim, no terminal de cada serviço, rode o código de execução:
    make
\* Execute o código do Usuário apenas quando os demais serviços já estiverem rodando


## Tecnologias utilizadas

### Bibliotecas Python

- Psycopg2: https://www.psycopg.org/
- PyCryptodome: https://www.pycryptodome.org/
- FaceNet-PyTorch: https://github.com/timesler/facenet-pytorch

### Outras ferramentas

- snarkJS: https://github.com/iden3/snarkjs
- Docker: https://docs.docker.com/get-started/
- PostgreSQL: https://www.postgresql.org/

## TCC de apresentação do protocolo

- Este protocolo é a segunda parte de um TCC sobre provas de conhecimento zero. A primeira parte consiste em um estudo sobre os esquemas zk-SNARKs.

- Para mais informações: https://github.com/AlexDavisNeuwiem/TCC-PCZs
