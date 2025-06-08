from enum import Enum

class Address(Enum):
    HOST = '0.0.0.0'
    PORT = 8002

class SnarkPath(Enum):

    WITNESS =  '/home/model/pysnark/witness.json'

    VERIFICATION_KEY = '/home/model/pysnark/verification_key.json'

    PROOF = '/home/model/pysnark/proof.json'

    PUBLIC_PARAMETERS= '/home/model/pysnark/public_parameters.json'
