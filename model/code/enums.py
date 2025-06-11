from enum import Enum

class Color(Enum):
    RED = '\033[31m[MODELO]\033[0m'

class Address(Enum):
    HOST = '0.0.0.0'
    PORT = 8002

class Adjustments(Enum):
    DIMENSIONS = 512

    THRESHOLD = 0.7

    SCALE = 100_000_000_000_000_000

class SnarkPath(Enum):
    TRUSTED_SETUP_DIR = '/home/model/snarkjs/trusted_setup/'

    PROOF_GENERATION_DIR = '/home/model/snarkjs/proof_generation/'

    SCRIPT = '/bin/bash /home/model/snarkjs/snarkjs.sh'

    WITNESS =  PROOF_GENERATION_DIR + 'inputs/input.json'

    VERIFICATION_KEY = TRUSTED_SETUP_DIR + 'outputs/verification_key.json'

    PROOF = PROOF_GENERATION_DIR + 'outputs/proof.json'

    PUBLIC_PARAMETERS= PROOF_GENERATION_DIR + 'outputs/public_parameters.json'
