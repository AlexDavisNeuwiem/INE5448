#!/bin/bash

PREFIX=/home/model/pysnark
PYTHON=/home/model/venv/bin/python3

set -e  # Interrompe no primeiro erro
set -x  # Mostra todos os comandos executados

# Cria um novo arquivo de configuração pot.ptau para a curva BN128, com potência 12 (suporta até ~4096 constraints)
snarkjs powersoftau new bn128 12 ${PREFIX}/pot.ptau -v

# Prepara os parâmetros para a fase 2 (usada em Groth16), salvando em pott.ptau
snarkjs powersoftau prepare phase2 ${PREFIX}/pot.ptau ${PREFIX}/pott.ptau -v

# Executa cosine_similarity.py que cria circuit.r1cs e witness.wtns
PYSNARK_BACKEND=snarkjs $PYTHON ${PREFIX}/cosine_similarity.py

mv /home/model/circuit.r1cs /home/model/pysnark/

mv /home/model/witness.wtns /home/model/pysnark/

# Gera uma zkey (chave de prova) a partir do circuit.r1cs e dos parâmetros da fase 2 (pott.ptau)
snarkjs zkey new ${PREFIX}/circuit.r1cs ${PREFIX}/pott.ptau ${PREFIX}/circuit.zkey

# Extrai a chave de verificação pública verification_key.json
snarkjs zkey export verificationkey ${PREFIX}/circuit.zkey ${PREFIX}/verification_key.json

# Gera a prova proof.json e os parâmetros públicos public_parameters.json
snarkjs groth16 prove ${PREFIX}/circuit.zkey ${PREFIX}/witness.wtns ${PREFIX}/proof.json ${PREFIX}/public_parameters.json

rm -rf ${PREFIX}/pot.ptau ${PREFIX}/pott.ptau ${PREFIX}/circuit.zkey ${PREFIX}/circuit.r1cs ${PREFIX}/witness.wtns
