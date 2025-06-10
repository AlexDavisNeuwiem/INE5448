#!/bin/bash

SNARKJS_DIR=/home/server/snarkjs/inputs/

set -e  # Interrompe no primeiro erro
set -x  # Mostra todos os comandos executados

cd ${SNARKJS_DIR}

# ENTRADAS:
#   - verification_key.json (foi gerado na etapa do trusted setup)
#   - public_parameters.json (foi gerado na etapa do proof generation)
#   - proof.json (foi gerado na etapa do proof generation)

# Verifica a prova
snarkjs groth16 verify verification_key.json public_parameters.json proof.json
