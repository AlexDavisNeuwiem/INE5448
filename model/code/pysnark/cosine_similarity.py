import sys
import json
import torch
from pysnark.runtime import snark, PrivVal


def run():

    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    with open('/home/model/pysnark/witness.json', 'r') as arquivo:
        witness = json.load(arquivo)

    embedding1 = torch.tensor(witness['embedding1']).unsqueeze(0).to(device)
    embedding2 = torch.tensor(witness['embedding2']).unsqueeze(0).to(device)
    threshold = witness['threshold']

    calcular_similaridade_cosseno(embedding1, embedding2, threshold)

@snark
def calcular_similaridade_cosseno(embedding1, embedding2, threshold):
        """Calcula similaridade de cosseno entre embeddings"""
        similarity = torch.nn.functional.cosine_similarity(embedding1, embedding2).item()

        return similarity > threshold

if __name__ == "__main__":
    run()