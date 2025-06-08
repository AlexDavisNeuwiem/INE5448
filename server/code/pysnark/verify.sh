#!/bin/bash

PREFIX=/home/server/pysnark

snarkjs groth16 verify ${PREFIX}/verification_key.json ${PREFIX}/public_parameters.json ${PREFIX}/proof.json
