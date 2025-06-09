import json
import socket
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

        print("\n" + "=" * 60)
        print("🔴 INICIALIZANDO MODELO DE IA")
        print("=" * 60)

        # Configurações de rede
        self.host = Address.HOST.value
        self.port = Address.PORT.value

        # Configuração do dispositivo (GPU ou CPU)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Detector de faces MTCNN
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
        
        # Modelo InceptionResnetV1 pré-treinado no VGGFace2
        print("🔴 Carregando modelo de extração de características faciais...")
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        
        # Limiar de similaridade para correspondência facial
        self.limiar_similaridade = 0.7

    def executar(self):
        """Método principal que inicia o serviço do modelo"""
        
        # Inicia servidor para receber mensagens
        self.iniciar_servidor()
    
    def iniciar_servidor(self):
        """Inicia servidor TCP para receber mensagens de outros serviços"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((self.host, self.port))
                s.listen(5)

                print(f"🔴 Servidor escutando em {self.host}:{self.port}")

                print("=" * 60)
                print("🔴 MODELO DE IA INICIALIZADO COM SUCESSO")
                print("=" * 60 + "\n")
                
                while True:
                    try:
                        conn, addr = s.accept()
                        # Cria thread para cada conexão
                        thread = threading.Thread(target=self.processar_cliente, args=(conn, addr))
                        thread.start()
                    except Exception as e:
                        print(f"🔴 ❌ Erro no servidor: {e}")
        except KeyboardInterrupt:
            print("\n🔴 Encerrando serviço do modelo...")
        except Exception as e:
            print(f"🔴 ❌ Erro crítico no servidor: {e}")
    
    def processar_cliente(self, conn, addr):
        """Processa mensagens recebidas de outros serviços"""
        try:
            with conn:
                # Recebe dados em chunks para mensagens grandes
                dados_completos = b''
                while True:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    dados_completos += chunk
                
                if dados_completos:
                    print(f"🔴 Mensagem recebida de {addr} - Tamanho: {len(dados_completos)} bytes")
                    
                    # Converte dados recebidos para JSON
                    mensagem = json.loads(dados_completos.decode())
                    tipo_mensagem = mensagem.get('type', 'desconhecido')
                    print(f"🔴 Tipo da mensagem: {tipo_mensagem}")
                    
                    # Processa mensagem baseada no tipo
                    self.processar_mensagem(mensagem)
                        
        except json.JSONDecodeError as e:
            print(f"🔴 ❌ Erro ao decodificar JSON: {e}")
        except Exception as e:
            print(f"🔴 ❌ Erro ao processar cliente: {e}")
    
    def processar_mensagem(self, mensagem):
        """Roteia mensagens baseado no tipo"""
        tipo_mensagem = mensagem.get('type')
        dados = mensagem.get('data')
        endereco_retorno = mensagem.get('return_to')
        
        if tipo_mensagem == 'generate_embedding':
            self.processar_solicitacao_embedding(dados, endereco_retorno)
        elif tipo_mensagem == 'generate_snark_proof':
            self.processar_solicitacao_prova_snark(dados, endereco_retorno)
        else:
            print(f"🔴 ⚠️ Tipo de mensagem desconhecido: {tipo_mensagem}")
    
    def processar_solicitacao_embedding(self, foto_base64, endereco_retorno):
        """Processa solicitação de geração de embedding (fase de registro)"""
        print("\n" + "=" * 60)
        print("🔴 INICIANDO FASE DE REGISTRO")
        print("=" * 60)
        print("🔴 Gerando embedding facial...")
        
        # Gera embedding da foto
        embedding = self.gerar_embedding(foto_base64)
        
        if embedding is not None:
            print("=" * 60)
            print("🔴 FASE DE REGISTRO CONCLUÍDA")
            print("=" * 60 + "\n")
            
            # Envia embedding de volta para o usuário
            self.enviar_resposta(endereco_retorno, {
                'type': 'embedding',
                'data': embedding
            })
        else:
            print("🔴 ❌ Falha ao gerar embedding")
            print("=" * 60)
            print("🔴 FASE DE REGISTRO FALHOU")
            print("=" * 60)
            
            # Envia erro de volta para o usuário
            self.enviar_resposta(endereco_retorno, {
                'type': 'embedding_error',
                'data': None
            })
    
    def processar_solicitacao_prova_snark(self, dados, endereco_retorno):
        """Processa solicitação de geração de prova zk-SNARK (fase de autenticação)"""
        print("\n" + "=" * 60)
        print("🔴 INICIANDO FASE DE AUTENTICAÇÃO")
        print("=" * 60)
        print("🔴 Gerando prova zk-SNARK...")
        
        # Gera prova zk-SNARK
        dados_prova = self.gerar_prova_snark(dados)
        
        if dados_prova is not None:
            print("=" * 60)
            print("🔴 FASE DE AUTENTICAÇÃO CONCLUÍDA")
            print("=" * 60 + "\n")
            
            # Envia prova de volta para o usuário
            self.enviar_resposta(endereco_retorno, {
                'type': 'snark_proof',
                'data': {
                    'prova': dados_prova[0],
                    'chave': dados_prova[1],
                    'params': dados_prova[2]
                }
            })
        else:
            print("🔴 ❌ Falha ao gerar prova zk-SNARK")
            print("=" * 60)
            print("🔴 FASE DE AUTENTICAÇÃO FALHOU")
            print("=" * 60)
            
            # Envia erro de volta para o usuário
            self.enviar_resposta(endereco_retorno, {
                'type': 'snark_proof_error',
                'data': {
                    'error': 'Falha ao gerar prova zk-SNARK'
                }
            })
    
    def gerar_embedding(self, foto_base64):
        """Gera embedding biométrica a partir da foto em base64"""
        try:
            print("🔴 Decodificando imagem base64...")
            
            # Decodifica imagem base64
            dados_imagem = base64.b64decode(foto_base64)
            imagem = Image.open(BytesIO(dados_imagem))
            
            print("🔴 Detectando face na imagem...")
            
            # Detecta e extrai face da imagem
            face = self.mtcnn(imagem)
            
            if face is None:
                print("🔴 ❌ Nenhuma face detectada na imagem")
                return None

            print("🔴 Extraindo características faciais...")
            
            # Gera embedding facial usando o modelo InceptionResnetV1
            with torch.no_grad():
                embedding = self.resnet(face.unsqueeze(0).to(self.device))
            
            # Converte tensor para lista para serialização JSON
            embedding_list = embedding.squeeze().cpu().numpy().tolist()
            
            print(f"🔴 Embedding gerada - Dimensões: {len(embedding_list)}")
            return embedding_list
            
        except Exception as e:
            print(f"🔴 ❌ Erro ao gerar embedding: {e}")
            return None
    
    def gerar_prova_snark(self, dados_mensagem):
        """Gera prova zk-SNARK para verificação de similaridade facial"""
        try:
            foto_nova_base64 = dados_mensagem['foto_nova']
            embedding_antiga = dados_mensagem['embedding_antiga']
            
            print("🔴 Gerando embedding da nova foto...")
            
            # Gera nova embedding da foto atual
            embedding_nova = self.gerar_embedding(foto_nova_base64)
            
            if embedding_nova is None:
                print("🔴 ❌ Não foi possível extrair embedding da nova foto")
                return None

            print("🔴 Preparando dados para geração da prova zk-SNARK...")
            
            # Salva dados temporariamente para o script zk-SNARK
            dados_witness = {
                'embedding1': embedding_antiga,
                'embedding2': embedding_nova,
                'threshold': self.limiar_similaridade
            }
            
            with open(SnarkPath.WITNESS.value, 'w') as arquivo:
                json.dump(dados_witness, arquivo)
            
            print("🔴 Executando script zk-SNARK...")

            # Executa o script de geração da prova zk-SNARK
            resultado = subprocess.run(
                '/bin/bash /home/model/pysnark/snark.sh', 
                capture_output=True, 
                text=True, 
                shell=True
            )
            
            if resultado.returncode != 0:
                print(f"🔴 ❌ Erro ao executar script SNARK: {resultado.stderr}")
                return None

            print("🔴 Carregando arquivos da prova zk-SNARK...")
            
            # Carrega os arquivos gerados pelo script zk-SNARK
            prova = self.carregar_arquivo_json(SnarkPath.PROOF.value)
            chave_verificacao = self.carregar_arquivo_json(SnarkPath.VERIFICATION_KEY.value)
            parametros_publicos = self.carregar_arquivo_json(SnarkPath.PUBLIC_PARAMETERS.value)

            if not all([prova, chave_verificacao, parametros_publicos]):
                print("🔴 ❌ Falha ao carregar arquivos da prova zk-SNARK")
                return None

            print("🔴 ✅ Prova zk-SNARK gerada com sucesso")
            return (prova, chave_verificacao, parametros_publicos)
            
        except Exception as e:
            print(f"🔴 ❌ Erro ao gerar prova zk-SNARK: {e}")
            return None
    
    def carregar_arquivo_json(self, caminho_arquivo):
        """Carrega e retorna conteúdo de arquivo JSON"""
        try:
            with open(caminho_arquivo, 'r') as arquivo:
                conteudo = json.load(arquivo)
            return conteudo
        except Exception as e:
            print(f"🔴 ❌ Erro ao carregar arquivo {caminho_arquivo}: {e}")
            return None
    
    def enviar_resposta(self, endereco_retorno, mensagem):
        """Envia resposta de volta para o serviço solicitante"""
        try:
            # Divide endereço de retorno em host e porta
            host, porta = endereco_retorno.split(':')
            porta = int(porta)
            
            # Envia mensagem
            sucesso = self.enviar_mensagem(host, porta, mensagem)
            
            if sucesso:
                print(f"🔴 Resposta enviada para {endereco_retorno}")
            else:
                print(f"🔴 ❌ Falha ao enviar resposta para {endereco_retorno}")
                
            return sucesso
            
        except Exception as e:
            print(f"🔴 ❌ Erro ao processar endereço de retorno: {e}")
            return False
    
    def enviar_mensagem(self, host, porta, mensagem):
        """Envia mensagem JSON para outros serviços via TCP"""
        try:
            mensagem_json = json.dumps(mensagem)
            tamanho_mensagem = len(mensagem_json.encode())
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, porta))
                s.send(mensagem_json.encode())
                
            print(f"🔴 Mensagem enviada para {host}:{porta} - Tamanho: {tamanho_mensagem} bytes")
            return True
            
        except ConnectionRefusedError:
            print(f"🔴 ❌ Conexão recusada para {host}:{porta}")
            return False
        except Exception as e:
            print(f"🔴 ❌ Erro ao enviar mensagem: {e}")
            return False
