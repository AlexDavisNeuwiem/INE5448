from enum import Enum

class Addresses(Enum):
    HOST = '0.0.0.0'
    PORT = 8000

class PostgesData(Enum):
    HOST = 'postgres-container'
    DATABASE = 'biometrics_db'
    USER = 'server'
    PASSWORD = '123456'

class SnarkPath(Enum):
    VERIFICATION_KEY = 'pysnark/verification_key.json'

    PROOF = 'pysnark/proof.json'

    PUBLIC_PARAMETERS= 'pysnark/public_parameters.json'
