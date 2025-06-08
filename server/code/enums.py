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
    VERIFICATION_KEY = '/home/server/pysnark/verification_key.json'

    PROOF = '/home/server/pysnark/proof.json'

    PUBLIC_PARAMETERS= '/home/server/pysnark/public_parameters.json'
