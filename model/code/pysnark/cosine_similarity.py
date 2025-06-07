import sys
import json
import torch
from pysnark.runtime import snark, PrivVal


def run(entrada):
    with open(entrada, 'r') as arquivo:
        witness = json.load(arquivo)

    embedding1 = witness['embedding1']
    embedding2 = witness['embedding2']
    threshold = witness['threshold']

    calcular_similaridade_cosseno(embedding1, embedding2, threshold)

@snark
def calcular_similaridade_cosseno(embedding1, embedding2, threshold):
        """Calcula similaridade de cosseno entre embeddings"""
        similarity = torch.nn.functional.cosine_similarity(
            embedding1.unsqueeze(0), 
            embedding2.unsqueeze(0)
        ).item()

        return similarity > threshold

if __name__ == "__main__":
    run(sys.argv[1])