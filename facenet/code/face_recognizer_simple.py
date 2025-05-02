import os
from PIL import Image
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
from torch.nn.functional import cosine_similarity

# Define o dispositivo
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Inicializa o detector de rosto e o modelo de embeddings
mtcnn = MTCNN(image_size=160, margin=0, min_face_size=20, device=device)
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

# Função para gerar embedding de uma imagem
def get_embedding(img_path):
    img = Image.open(img_path).convert('RGB')
    face = mtcnn(img)
    if face is not None:
        face = face.unsqueeze(0).to(device)
        embedding = resnet(face)
        return embedding
    return None

# Carrega as faces conhecidas
known_faces_dir = 'faces'
known_embeddings = {}
for filename in os.listdir(known_faces_dir):
    name, ext = os.path.splitext(filename)
    embedding = get_embedding(os.path.join(known_faces_dir, filename))
    if embedding is not None:
        known_embeddings[name] = embedding
        print(f"Carregada face de {name}")
    else:
        print(f"Falha ao detectar rosto em {filename}")

# Reconhecimento: compara imagem de teste com rostos conhecidos
def recognize_face(test_img_path, threshold=0.6):
    test_embedding = get_embedding(test_img_path)
    if test_embedding is None:
        print("Nenhum rosto detectado na imagem de teste.")
        return

    recognized = False
    for name, known_embedding in known_embeddings.items():
        sim = cosine_similarity(test_embedding, known_embedding)
        if sim.item() > threshold:
            print(f"Rosto reconhecido como: {name} (similaridade = {sim.item():.2f})")
            recognized = True
            break
    if not recognized:
        print("Rosto não reconhecido.")

# Exemplo de uso
recognize_face("test.jpeg")
