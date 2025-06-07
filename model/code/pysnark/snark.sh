#!/bin/bash

# Primeiro argumento: caminho para o JSON
INPUT_JSON=$1

# Cria um novo arquivo de configuração pot.ptau para a curva BN128, com potência 12 (suporta até ~4096 constraints)
snarkjs powersoftau new bn128 12 pot.ptau -v

# Prepara os parâmetros para a fase 2 (usada em Groth16), salvando em pott.ptau
snarkjs powersoftau prepare phase2 pot.ptau pott.ptau -v
rm -f pot.ptau

# Executa cosine_similarity.py que cria circuit.r1cs e witness.wtns
PYSNARK_BACKEND=snarkjs ../venv/dir/python3 cosine_similarity.py "$INPUT_JSON"

# Gera uma zkey (chave de prova) a partir do circuit.r1cs e dos parâmetros da fase 2 (pott.ptau)
snarkjs zkey new circuit.r1cs pott.ptau circuit.zkey
rm -f pott.ptau

# Extrai a chave de verificação pública verification_key.json
snarkjs zkey export verificationkey circuit.zkey verification_key.json

# Gera a prova proof.json e os parâmetros públicos public_parameters.json
snarkjs groth16 prove circuit.zkey witness.wtns proof.json public_parameters.json
rm -f circuit.zkey
rm -f witness.wtns

snarkjs groth16 verify verification_key.json public_parameters.json proof.json
