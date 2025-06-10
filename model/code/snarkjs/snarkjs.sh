#!/bin/bash

SNARKJS_DIR=/home/model/snarkjs

OUTPUT_DIR=/home/model/snarkjs/trusted_setup/outputs
INPUT_DIR=/home/model/snarkjs/proof_generation/inputs

# Executa o trusted setup
/bin/bash ${SNARKJS_DIR}/trusted_setup/trusted_setup.sh

# Renomeia as saidas do trusted setup e move-as para as entradas do proof generator
mv ${OUTPUT_DIR}/cosine_similarity.wasm ${INPUT_DIR}/circuit.wasm
mv ${OUTPUT_DIR}/cosine_similarity_final.zkey ${INPUT_DIR}/proving_key.zkey

# Gera a prova
/bin/bash ${SNARKJS_DIR}/proof_generation/generate_proof.sh
