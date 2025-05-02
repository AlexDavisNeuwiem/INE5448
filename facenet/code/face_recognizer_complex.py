import os
import torch
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1

class FaceRecognizer:
    def __init__(self, device='cpu'):
        """
        Inicializa o sistema de reconhecimento facial
        
        Args:
            device: dispositivo onde executar a inferência ('cpu' ou 'cuda')
        """
        self.device = torch.device(device)
        
        print("Inicializando sistema de reconhecimento facial...")
        
        # Detector de faces
        print("Carregando detector de faces MTCNN...")
        self.mtcnn = MTCNN(
            image_size=160, 
            margin=20, 
            min_face_size=20,
            thresholds=[0.6, 0.7, 0.7], 
            factor=0.709, 
            keep_all=False,
            device=self.device
        )
        
        # Modelo para embeddings faciais (pré-treinado no VGGFace2)
        print("Carregando modelo de extração de características faciais...")
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        
        # Dicionário para armazenar embeddings das faces conhecidas
        self.known_embeddings = {}
        
        # Limiar de similaridade de cosseno para considerar uma correspondência
        self.similarity_threshold = 0.7
        
        print("Sistema inicializado e pronto para uso!")

    def add_person(self, person_name, images_path):
        """
        Adiciona uma pessoa ao banco de dados de faces conhecidas
        
        Args:
            person_name: nome da pessoa
            images_path: caminho para a pasta com imagens da pessoa
        
        Returns:
            bool: True se a pessoa foi adicionada com sucesso
        """
        embeddings = []
        
        # Verificar se é uma única imagem ou uma pasta
        if os.path.isfile(images_path):
            image_paths = [images_path]
        else:
            # Listar todas as imagens na pasta
            image_paths = [os.path.join(images_path, f) for f in os.listdir(images_path) 
                         if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        if not image_paths:
            print(f"Nenhuma imagem encontrada para {person_name}")
            return False
        
        # Processar cada imagem
        for img_path in image_paths:
            try:
                # Carregar imagem
                img = Image.open(img_path).convert('RGB')
                
                # Detectar face e obter embedding
                face_embedding = self._get_embedding(img)
                
                if face_embedding is not None:
                    embeddings.append(face_embedding)
            except Exception as e:
                print(f"Erro ao processar {img_path}: {e}")
        
        if not embeddings:
            print(f"Nenhuma face detectada para {person_name}")
            return False
        
        # Calcular o embedding médio para a pessoa
        mean_embedding = torch.mean(torch.stack(embeddings), dim=0)
        self.known_embeddings[person_name] = mean_embedding
        
        print(f"Pessoa '{person_name}' adicionada com sucesso ({len(embeddings)} faces)")
        return True

    def recognize(self, image_path):
        """
        Reconhece a pessoa em uma imagem
        
        Args:
            image_path: caminho para a imagem
            
        Returns:
            tuple: (nome da pessoa reconhecida, similaridade) ou (None, 0) se não reconhecida
        """
        if not self.known_embeddings:
            print("Erro: Nenhuma pessoa cadastrada no sistema")
            return None, 0
        
        try:
            # Carregar imagem
            img = Image.open(image_path).convert('RGB')
            
            # Obter embedding da face
            face_embedding = self._get_embedding(img)
            
            if face_embedding is None:
                print("Nenhuma face detectada na imagem")
                return None, 0
            
            # Comparar com faces conhecidas
            best_match = None
            best_similarity = 0
            
            for person_name, known_embedding in self.known_embeddings.items():
                # Calcular similaridade de cosseno
                similarity = self._cosine_similarity(face_embedding, known_embedding)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = person_name
            
            # Verificar se a similaridade está acima do limiar
            if best_similarity >= self.similarity_threshold:
                result = (best_match, best_similarity)
            else:
                result = (None, best_similarity)
            
            return result
            
        except Exception as e:
            print(f"Erro ao processar a imagem: {e}")
            return None, 0
    
    def verify(self, image_path, person_name):
        """
        Verifica se a pessoa na imagem é a pessoa especificada
        
        Args:
            image_path: caminho para a imagem
            person_name: nome da pessoa para verificar
            
        Returns:
            tuple: (True/False, similaridade)
        """
        if person_name not in self.known_embeddings:
            print(f"Erro: Pessoa '{person_name}' não está cadastrada")
            return False, 0
        
        try:
            # Carregar imagem
            img = Image.open(image_path).convert('RGB')
            
            # Obter embedding da face
            face_embedding = self._get_embedding(img)
            
            if face_embedding is None:
                print("Nenhuma face detectada na imagem")
                return False, 0
            
            # Calcular similaridade com a pessoa específica
            known_embedding = self.known_embeddings[person_name]
            similarity = self._cosine_similarity(face_embedding, known_embedding)
            
            # Verificar se está acima do limiar
            result = (similarity >= self.similarity_threshold, similarity)
            
            return result
            
        except Exception as e:
            print(f"Erro ao processar a imagem: {e}")
            return False, 0

    def _get_embedding(self, img):
        """Detecta face e extrai embedding"""
        # Detectar face
        face = self.mtcnn(img)
        
        if face is None:
            return None
        
        # Obter embedding facial (normalizado)
        with torch.no_grad():
            embedding = self.resnet(face.unsqueeze(0).to(self.device))
        
        return embedding.squeeze()
    
    def _cosine_similarity(self, embedding1, embedding2):
        """Calcula similaridade de cosseno entre embeddings"""
        return torch.nn.functional.cosine_similarity(
            embedding1.unsqueeze(0), 
            embedding2.unsqueeze(0)
        ).item()