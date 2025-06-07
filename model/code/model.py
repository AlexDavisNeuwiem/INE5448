import os
import json
import socket
import tempfile
import threading
import subprocess

import torch
from enums import SnarkPath, Address
from facenet_pytorch import MTCNN, InceptionResnetV1


class ModeloService:
    def __init__(self):
        self.host = Address.HOST.value
        self.port = Address.PORT.value

        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
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
        
        # Limiar de similaridade de cosseno para considerar uma correspondência
        self.similarity_threshold = 0.7

    def run(self):
        """Inicia o serviço do modelo de IA"""
        print("🔴 Iniciando serviço do modelo de IA...")
        self._start_server()
    
    def _start_server(self):
        """Inicia servidor para receber mensagens"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen(5)
            print(f"🔴 Modelo listening on {self.host}:{self.port}")
            
            while True:
                try:
                    conn, addr = s.accept()
                    thread = threading.Thread(target=self._handle_client, args=(conn, addr))
                    thread.start()
                except Exception as e:
                    print(f"🔴 Erro no servidor: {e}")
    
    def _handle_client(self, conn, addr):
        """Processa mensagens recebidas"""
        try:
            with conn:
                data = conn.recv(4096)
                if data:
                    message = json.loads(data.decode())
                    print(f"🔴 Mensagem recebida: {message['type']}")
                    
                    if message['type'] == 'generate_embedding':
                        embedding = self.gerar_embedding(message['data'])
                        
                        # Envia embedding de volta para o usuário
                        return_address = message['return_to'].split(':')
                        self.enviar_mensagem(
                            return_address[0], 
                            int(return_address[1]),
                            {
                                'type': 'embedding',
                                'data': embedding
                            }
                        )
                    
                    elif message['type'] == 'generate_snark_proof':
                        dados_verificacao = self.gerar_prova_snark(message['data'])
                        
                        # Envia prova de volta para o usuário
                        return_address = message['return_to'].split(':')
                        self.enviar_mensagem(
                            return_address[0], 
                            int(return_address[1]),
                            {
                                'type': 'snark_proof',
                                'prova': dados_verificacao[0],
                                'chave': dados_verificacao[1],
                                'params': dados_verificacao[2]
                            }
                        )
                        
        except Exception as e:
            print(f"🔴 Erro ao processar mensagem: {e}")
    
    def gerar_embedding(self, foto):
        """Gera embedding biométrica a partir da foto"""
        print("🔴 Gerando embedding da foto...")

        # Detecta face
        face = self.mtcnn(foto)
        
        if face is None:
            return None

        # Gera embedding facial (normalizado)
        with torch.no_grad():
            embedding = self.resnet(face.unsqueeze(0).to(self.device))
        
        
        print(f"🔴 Embedding gerada!")
        return embedding.squeeze()

    
    def gerar_prova_snark(self, dados):
        """Gera prova zk-SNARK para similaridade de embeddings"""
        print("🔴 Gerando prova zk-SNARK...")
        
        try:
            nova_foto = dados['nova_foto']
            embedding_antiga = dados['embedding_antiga']
            
            # 5. Gera nova embedding da foto atual
            embedding_nova = self.gerar_embedding(nova_foto)
            
            # Calcula similaridade cosseno

            # Salvar os dados temporariamente em JSON
            with tempfile.NamedTemporaryFile(delete=False, mode='w', prefix='witness_', suffix='.json', dir='pysnark/') as temp:
                json.dump({
                    'embedding1': embedding_antiga,
                    'embedding2': embedding_nova,
                    'threshold': self.similarity_threshold
                }, temp)
                caminho_temp = temp.name

            # Executar o script .sh, passando o caminho do arquivo como argumento
            subprocess.run(['bash', 'pysnark/snark.sh', caminho_temp])

            # Limpeza opcional do arquivo temporário
            os.remove(caminho_temp)

            prova = self.converte_arquivo_para_bytes(SnarkPath.PROOF.value)
            chave = self.converte_arquivo_para_bytes(SnarkPath.VERIFICATION_KEY.value)
            params = self.converte_arquivo_para_bytes(SnarkPath.PUBLIC_PARAMETERS.value)

            print(f"🔴 Prova zk-SNARK gerada")

            return (prova, chave, params)

            
        except Exception as e:
            print(f"🔴 Erro ao gerar prova zk-SNARK: {e}")
            return None

    
    def enviar_mensagem(self, host, port, message):
        """Envia mensagem para outros serviços"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                s.send(json.dumps(message).encode())
                print(f"🔴 Mensagem enviada para {host}:{port}")
                return True
        except Exception as e:
            print(f"🔴 Erro ao enviar mensagem: {e}")
            return False

    def converte_arquivo_para_bytes(self, caminho):
        # 1. Abre e carrega o conteúdo do arquivo .json
        with open(caminho, 'r') as arquivo_json:
            conteudo = json.load(arquivo_json)

        # 2. Converte o conteúdo para string JSON e depois para bytes
        return json.dumps(conteudo).encode()