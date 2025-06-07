from enum import Enum

class Address(Enum):
    HOST = '0.0.0.0'
    PORT = 8002

class SnarkPath(Enum):
    VERIFICATION_KEY = 'pysnark/verification_key.json'

    PROOF = 'pysnark/proof.json'

    PUBLIC_PARAMETERS= 'pysnark/public_parameters.json'
