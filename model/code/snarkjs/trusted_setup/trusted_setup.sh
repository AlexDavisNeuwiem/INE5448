#!/bin/bash

INPUT_DIR=input
OUTPUT_DIR=outputs
SNARKJS_DIR=/home/model/snarkjs/trusted_setup/

CIRCUIT=cosine_similarity

set -e  # Interrompe no primeiro erro
set -x  # Mostra todos os comandos executados

cd ${SNARKJS_DIR}

# ========== CIRCUIT GENERATION ========== #

# 1. Compilando o circuito
circom ${INPUT_DIR}/${CIRCUIT}.circom --r1cs --wasm
mv ${CIRCUIT}_js/${CIRCUIT}.wasm ${OUTPUT_DIR}/${CIRCUIT}.wasm

# ========== TRUSTED SETUP ========== #

# Gera 16 bytes aleatórios em base64 e limita a saída para os primeiros 16 caracteres
ENTROPY=$(openssl rand -base64 16 | head -c 16)

# 2. Início da cerimônia de confiança usando a curva BN128, com potência 16
snarkjs powersoftau new bn128 12 pot_00.ptau -v
snarkjs powersoftau contribute pot_00.ptau pot_01.ptau --name="First contribution" -v -e="$ENTROPY"

# 3. Prepara os parâmetros para a fase 2 (usada em Groth16), salvando em pot_final.ptau
snarkjs powersoftau prepare phase2 pot_01.ptau pot_final.ptau -v

# Gera entropia de novo
ENTROPY=$(openssl rand -base64 16 | head -c 16)

# 4. Cerimônia de setup
snarkjs groth16 setup ${CIRCUIT}.r1cs pot_final.ptau ${CIRCUIT}_00.zkey
snarkjs zkey contribute ${CIRCUIT}_00.zkey ${OUTPUT_DIR}/${CIRCUIT}_final.zkey --name="First contributor" -v -e="$ENTROPY"

# 5. Gera proving key (${CIRCUIT}_final.zkey) e verification key
snarkjs zkey export verificationkey ${OUTPUT_DIR}/${CIRCUIT}_final.zkey ${OUTPUT_DIR}/verification_key.json

# 6. Limpeza de arquivos temporários
rm -rf *.ptau *.r1cs *_00.zkey
