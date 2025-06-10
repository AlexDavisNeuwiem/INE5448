from enum import Enum

class Address(Enum):
    HOST = '0.0.0.0'
    PORT = 8000

class PostgesData(Enum):
    HOST = 'postgres-container'
    DATABASE = 'biometrics_db'
    USER = 'server'
    PASSWORD = '123456'

class SnarkPath(Enum):
    SNARKJS_DIR = '/home/server/snarkjs/'

    SCRIPT = '/bin/bash ' + SNARKJS_DIR + 'verify_proof.sh'

    VERIFICATION_KEY = SNARKJS_DIR + 'inputs/verification_key.json'

    PROOF = SNARKJS_DIR + 'inputs/proof.json'

    PUBLIC_PARAMETERS= SNARKJS_DIR + 'inputs/public_parameters.json'
