from enum import Enum

class Color(Enum):
    RED = '\033[31m[MODELO]\033[0m'

class Address(Enum):
    HOST = '0.0.0.0'
    PORT = 8002

class Adjustments(Enum):
    DIMENSIONS = 512

    THRESHOLD = int(0.7 * 10) # Ajuste necessário, ver server/code/snarkjs/trusted_setup/input/cosine_similarity.circom

    SCALE = 100_000_000_000_000_000_000_000_000

class SnarkPath(Enum):
    # === DIRETÓRIOS === #
    PROOF_GENERATION_DIR = '/home/model/snarkjs/proof_generation/'
    PROOF_GENERATION_INPUTS = PROOF_GENERATION_DIR + 'inputs/'
    PROOF_GENERATION_OUTPUTS = PROOF_GENERATION_DIR + 'outputs/'

    # === ENTRADAS === #
    WITNESS =  PROOF_GENERATION_INPUTS + 'input.json'
    PROVING_KEY = PROOF_GENERATION_INPUTS + 'proving_key.zkey'
    CIRCUIT = PROOF_GENERATION_INPUTS + 'circuit.wasm'

    #  === SCRIPT === #
    GENERATE_PROOF_SCRIPT = '/bin/bash ' + PROOF_GENERATION_DIR + 'generate_proof.sh'

    # === SAIDAS === #
    PROOF = PROOF_GENERATION_OUTPUTS + 'proof.json'
    PUBLIC_PARAMETERS= PROOF_GENERATION_OUTPUTS + 'public_parameters.json'
