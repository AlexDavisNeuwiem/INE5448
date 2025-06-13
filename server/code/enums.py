from enum import Enum

class Color(Enum):
    BLUE = '\033[34m[SERVIDOR]\033[0m'

class Address(Enum):
    HOST = '0.0.0.0'
    PORT = 8000

class PostgesData(Enum):
    HOST = 'postgres-container'
    DATABASE = 'biometrics_db'
    USER = 'server'
    PASSWORD = '123456'

class SnarkPath(Enum):
    # === DIRETÓRIOS === #
    SNARKJS_DIR = '/home/server/snarkjs/'
    TRUSTED_SETUP_OUTPUTS = SNARKJS_DIR + 'trusted_setup/outputs/'
    PROOF_VERIFICATION_INPUTS = SNARKJS_DIR + 'proof_verification/inputs/'

    # === TRUSTED SETUP === #
    TRUSTED_SETUP_SCRIPT = '/bin/bash ' + SNARKJS_DIR + 'trusted_setup/trusted_setup.sh'

    VERIFICATION_KEY_OUTPUT = TRUSTED_SETUP_OUTPUTS + 'verification_key.json'
    PROVING_KEY = TRUSTED_SETUP_OUTPUTS + 'cosine_similarity_final.zkey'
    CIRCUIT = TRUSTED_SETUP_OUTPUTS + 'cosine_similarity.wasm'

    # === PROOF VERIFICATION === #
    PROOF = PROOF_VERIFICATION_INPUTS + 'proof.json'
    PUBLIC_PARAMETERS= PROOF_VERIFICATION_INPUTS + 'public_parameters.json'
    VERIFICATION_KEY_INPUT = PROOF_VERIFICATION_INPUTS + 'verification_key.json'

    VERIFY_PROOF_SCRIPT = '/bin/bash ' + SNARKJS_DIR + 'proof_verification/verify_proof.sh'
