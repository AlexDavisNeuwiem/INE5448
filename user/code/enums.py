from enum import Enum

class Addresses(Enum):
    HOST = '0.0.0.0'
    PORT = 8001

    RETURN = 'user-container:8001'

    SERVER_HOST = 'server-container'
    SERVER_PORT = 8000

    MODEL_HOST = 'model-container'
    MODEL_PORT = 8002

class ImagePath(Enum):
    FACE_IMAGE_REG = './faces/1.jpeg'
    FACE_IMAGE_AUT = './faces/2.jpeg'
    FINGERPRINT_REG = './fingerprints/1.jpg'
    FINGERPRINT_AUT = './fingerprints/2.jpg'
