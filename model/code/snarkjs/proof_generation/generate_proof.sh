#!/bin/bash

INPUT_DIR=inputs
OUTPUT_DIR=outputs
SNARKJS_DIR=/home/model/snarkjs/proof_generation/

INPUT=${INPUT_DIR}/input.json
CIRCUIT=${INPUT_DIR}/circuit.wasm
PROVING_KEY=${INPUT_DIR}/proving_key.zkey

PROOF=${OUTPUT_DIR}/proof.json
PUBLIC_PARAMETERS=${OUTPUT_DIR}/public_parameters.json

set -e  # Interrompe no primeiro erro
set -x  # Mostra todos os comandos executados

cd ${SNARKJS_DIR}

# ENTRADAS:
#   - input.json (já possui)
#   - circuit.wasm (foi gerado na etapa do trusted setup)
#   - proving_key.zkey (foi gerado na etapa do trusted setup)

# SAIDAS:
#   - proof.json
#   - public_parameters.json


# Gera a prova e os parâmetros públicos
snarkjs groth16 fullprove ${INPUT} ${CIRCUIT} ${PROVING_KEY} ${PROOF} ${PUBLIC_PARAMETERS}
