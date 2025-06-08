import os
import json
import socket
import tempfile
import threading
import subprocess

import base64
from PIL import Image
from io import BytesIO

import torch
from enums import Address, SnarkPath
from facenet_pytorch import MTCNN, InceptionResnetV1


class Model:
    def __init__(self):
        self.host = Address.HOST.value
        self.port = Address.PORT.value

        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        print("🔴 Inicializando sistema de reconhecimento facial...")
        
        # Detector de faces
        print("🔴 Carregando detector de faces MTCNN...")
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
        print("🔴 Carregando modelo de extração de características faciais...")
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        print("🔴 Modelo Carregado!")

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
                data = b''
                while True:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                print(f"🔴 Tamanho da mensagem recebida:", len(data))
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
                        
                        if dados_verificacao is not None:
                            # Envia prova de volta para o usuário
                            return_address = message['return_to'].split(':')
                            self.enviar_mensagem(
                                return_address[0], 
                                int(return_address[1]),
                                {
                                    'type': 'snark_proof',
                                    'data': {
                                        'prova': dados_verificacao[0],
                                        'chave': dados_verificacao[1],
                                        'params': dados_verificacao[2]
                                    }
                                }
                            )
                        else:
                            # Envia erro de volta para o usuário
                            return_address = message['return_to'].split(':')
                            self.enviar_mensagem(
                                return_address[0], 
                                int(return_address[1]),
                                {
                                    'type': 'snark_proof_error',
                                    'data': {
                                        'error': 'Falha ao gerar prova zk-SNARK'
                                    }
                                }
                            )
                        
        except Exception as e:
            print(f"🔴 Erro ao processar mensagem: {e}")
    
    def gerar_embedding(self, foto_base64):
        """Gera embedding biométrica a partir da foto"""
        print("🔴 Gerando embedding da foto...")

        try:

            dados = base64.b64decode(foto_base64)
            foto_usuario = Image.open(BytesIO(dados))

            # Detecta face
            face = self.mtcnn(foto_usuario)
            
            if face is None:
                print("🔴 ❌ Nenhuma face detectada na imagem")
                return None

            # Gera embedding facial (normalizado)
            with torch.no_grad():
                embedding = self.resnet(face.unsqueeze(0).to(self.device))
            
            # Converte tensor para lista para serialização JSON
            embedding_list = embedding.squeeze().cpu().numpy().tolist()
            
            print(f"🔴 Embedding gerada com sucesso!")
            return embedding_list
            
        except Exception as e:
            print(f"🔴 Erro ao gerar embedding: {e}")
            return None

    
    def gerar_prova_snark(self, dados):
        """Gera prova zk-SNARK para similaridade de embeddings"""
        print("🔴 Gerando prova zk-SNARK...")
        
        try:
            foto_base64 = dados['foto_nova']
            embedding_antiga = dados['embedding_antiga']

            dados = base64.b64decode(foto_base64)
            foto_nova = Image.open(BytesIO(dados))
            
            # 5. Gera nova embedding da foto atual
            embedding_nova = self.gerar_embedding(foto_nova)
            
            if embedding_nova is None:
                print("🔴 ❌ Não foi possível extrair embedding da nova foto")
                return None
            
            # Salvar os dados temporariamente em JSON
            with tempfile.NamedTemporaryFile(delete=False, mode='w', prefix='witness_', suffix='.json', dir='pysnark/') as temp:
                json.dump({
                    'embedding1': embedding_antiga,
                    'embedding2': embedding_nova,
                    'threshold': self.similarity_threshold
                }, temp)
                caminho_temp = temp.name

            # Executar o script .sh, passando o caminho do arquivo como argumento
            resultado = subprocess.run(['bash', 'pysnark/snark.sh', caminho_temp], 
                                     capture_output=True, text=True)
            
            if resultado.returncode != 0:
                print(f"🔴 ❌ Erro ao executar script SNARK: {resultado.stderr}")
                return None

            # Limpeza opcional do arquivo temporário
            os.remove(caminho_temp)

            prova = self.converte_arquivo_para_bytes(SnarkPath.PROOF.value)
            chave = self.converte_arquivo_para_bytes(SnarkPath.VERIFICATION_KEY.value)
            params = self.converte_arquivo_para_bytes(SnarkPath.PUBLIC_PARAMETERS.value)

            print(f"🔴 Prova zk-SNARK gerada com sucesso")

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
                print(f"🔴 Mensagem de tamanho {len(json.dumps(message).encode())} enviada para {host}:{port}")
                return True
        except Exception as e:
            print(f"🔴 Erro ao enviar mensagem: {e}")
            return False

    def converte_arquivo_para_bytes(self, caminho):
        """Converte arquivo JSON para bytes"""
        try:
            # 1. Abre e carrega o conteúdo do arquivo .json
            with open(caminho, 'r') as arquivo_json:
                conteudo = json.load(arquivo_json)

            # 2. Converte o conteúdo para string JSON e depois para bytes
            return json.dumps(conteudo).encode()
        except Exception as e:
            print(f"🔴 Erro ao converter arquivo {caminho} para bytes: {e}")
            return None