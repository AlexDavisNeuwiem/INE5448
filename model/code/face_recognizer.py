import torch
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1


class SimpleFaceRecognizer:
    def __init__(self, similarity_threshold=0.7):
        """
        Inicializa o sistema de reconhecimento facial simplificado
        
        Args:
            similarity_threshold: limiar para considerar duas faces como da mesma pessoa
        """
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.similarity_threshold = similarity_threshold
        
        # Detector de faces
        self.mtcnn = MTCNN(
            image_size=160, 
            margin=20, 
            min_face_size=20,
            keep_all=False,
            device=self.device
        )
        
        # Modelo para extrair embeddings (pré-treinado no VGGFace2)
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        
        print("Sistema de reconhecimento facial inicializado!")

    def get_embedding(self, image_path):
        """
        Extrai o embedding facial de uma imagem
        
        Args:
            image_path: caminho para a imagem ou objeto PIL Image
            
        Returns:
            torch.Tensor: embedding da face ou None se nenhuma face for detectada
        """
        try:
            # Carregar imagem se for um caminho string
            if isinstance(image_path, str):
                img = Image.open(image_path).convert('RGB')
            else:
                img = image_path.convert('RGB')
            
            # Detectar e extrair face
            face = self.mtcnn(img)
            
            if face is None:
                print("Nenhuma face detectada na imagem")
                return None
            
            # Extrair embedding facial
            with torch.no_grad():
                embedding = self.resnet(face.unsqueeze(0).to(self.device))
            
            return embedding.squeeze()
            
        except Exception as e:
            print(f"Erro ao processar a imagem: {e}")
            return None

    def compare_embeddings(self, embedding1, embedding2):
        """
        Compara dois embeddings e determina se são da mesma pessoa
        
        Args:
            embedding1: primeiro embedding (torch.Tensor)
            embedding2: segundo embedding (torch.Tensor)
            
        Returns:
            tuple: (is_same_person: bool, similarity_score: float)
        """
        if embedding1 is None or embedding2 is None:
            return False, 0.0
        
        try:
            # Calcular similaridade de cosseno
            similarity = torch.nn.functional.cosine_similarity(
                embedding1.unsqueeze(0), 
                embedding2.unsqueeze(0)
            ).item()
            
            # Determinar se são da mesma pessoa baseado no limiar
            is_same_person = similarity >= self.similarity_threshold
            
            return is_same_person, similarity
            
        except Exception as e:
            print(f"Erro ao comparar embeddings: {e}")
            return False, 0.0

    def compare_faces(self, image_path1, image_path2):
        """
        Método auxiliar que compara duas imagens diretamente
        
        Args:
            image_path1: caminho para a primeira imagem
            image_path2: caminho para a segunda imagem
            
        Returns:
            tuple: (is_same_person: bool, similarity_score: float)
        """
        embedding1 = self.get_embedding(image_path1)
        embedding2 = self.get_embedding(image_path2)
        
        return self.compare_embeddings(embedding1, embedding2)


# Exemplo de uso
if __name__ == "__main__":
    # Inicializar o reconhecedor
    recognizer = SimpleFaceRecognizer()
    
    # Exemplo 1: Extrair embeddings de duas imagens
    # embedding1 = recognizer.get_embedding("pessoa1.jpg")
    # embedding2 = recognizer.get_embedding("pessoa2.jpg")
    
    # Exemplo 2: Comparar os embeddings
    # is_same, similarity = recognizer.compare_embeddings(embedding1, embedding2)
    # print(f"Mesma pessoa: {is_same}, Similaridade: {similarity:.3f}")
    
    # Exemplo 3: Comparar imagens diretamente
    # is_same, similarity = recognizer.compare_faces("image1.jpg", "image2.jpg")
    # print(f"Mesma pessoa: {is_same}, Similaridade: {similarity:.3f}")
    
    print("Exemplo de uso disponível no código!")