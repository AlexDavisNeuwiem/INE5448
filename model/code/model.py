import json
import socket
import threading
import subprocess

import base64
from PIL import Image
from io import BytesIO

import torch
from enums import Address, Adjustments, Color, SnarkPath
from facenet_pytorch import MTCNN, InceptionResnetV1


class Model:
    def __init__(self):

        print("\n" + "=" * 60)
        print(Color.RED.value + " INICIALIZANDO MODELO DE IA")
        print("=" * 60)

        # Configurações de rede
        self.host = Address.HOST.value
        self.port = Address.PORT.value

        # Configuração do dispositivo (GPU ou CPU)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Detector de faces MTCNN
        print(Color.RED.value + " Carregando detector de faces MTCNN...")
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
        print(Color.RED.value + " Carregando modelo de extração de características faciais...")
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        
        # Limiar de similaridade para correspondência facial
        self.limiar_similaridade = int(Adjustments.THRESHOLD.value * Adjustments.SCALE.value)

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

                print(Color.RED.value + f" Servidor escutando em {self.host}:{self.port}")

                print("=" * 60)
                print(Color.RED.value + " MODELO DE IA INICIALIZADO COM SUCESSO")
                print("=" * 60 + "\n")
                
                while True:
                    try:
                        conn, addr = s.accept()
                        # Cria thread para cada conexão
                        thread = threading.Thread(target=self.processar_cliente, args=(conn, addr))
                        thread.start()
                    except Exception as e:
                        print(Color.RED.value + f"❌ Erro no servidor: {e}")
        except KeyboardInterrupt:
            print("\n" + Color.RED.value + " Encerrando serviço do modelo...")
        except Exception as e:
            print(Color.RED.value + f"❌ Erro crítico no servidor: {e}")
    
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
                    print(Color.RED.value + f" Mensagem recebida de {addr} - Tamanho: {len(dados_completos)} bytes")
                    
                    # Converte dados recebidos para JSON
                    mensagem = json.loads(dados_completos.decode())
                    tipo_mensagem = mensagem.get('type', 'desconhecido')
                    print(Color.RED.value + f" Tipo da mensagem: {tipo_mensagem}")
                    
                    # Processa mensagem baseada no tipo
                    self.processar_mensagem(mensagem)
                        
        except json.JSONDecodeError as e:
            print(Color.RED.value + f"❌ Erro ao decodificar JSON: {e}")
        except Exception as e:
            print(Color.RED.value + f"❌ Erro ao processar cliente: {e}")
    
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
            print(Color.RED.value + f"⚠️ Tipo de mensagem desconhecido: {tipo_mensagem}")
    
    def processar_solicitacao_embedding(self, foto_base64, endereco_retorno):
        """Processa solicitação de geração de embedding (fase de registro)"""
        print("\n" + "=" * 60)
        print(Color.RED.value + " INICIANDO FASE DE REGISTRO")
        print("=" * 60)
        print(Color.RED.value + " Gerando embedding facial...")
        
        # Gera embedding da foto
        embedding = self.gerar_embedding(foto_base64)
        
        if embedding is not None:
            print("=" * 60)
            print(Color.RED.value + " FASE DE REGISTRO CONCLUÍDA")
            print("=" * 60 + "\n")
            
            # Envia embedding de volta para o usuário
            self.enviar_resposta(endereco_retorno, {
                'type': 'embedding',
                'data': embedding
            })
        else:
            print(Color.RED.value + "❌ Falha ao gerar embedding")
            print("=" * 60)
            print(Color.RED.value + " FASE DE REGISTRO FALHOU")
            print("=" * 60)
            
            # Envia erro de volta para o usuário
            self.enviar_resposta(endereco_retorno, {
                'type': 'embedding_error',
                'data': {
                    'error': 'Falha ao gerar embedding'
                }
            })
    
    def processar_solicitacao_prova_snark(self, dados, endereco_retorno):
        """Processa solicitação de geração de prova zk-SNARK (fase de autenticação)"""
        print("\n" + "=" * 60)
        print(Color.RED.value + " INICIANDO FASE DE AUTENTICAÇÃO")
        print("=" * 60)
        print(Color.RED.value + " Gerando prova zk-SNARK...")
        
        # Gera prova zk-SNARK
        dados_prova = self.gerar_prova_snark(dados)
        
        if dados_prova is not None:
            print("=" * 60)
            print(Color.RED.value + " FASE DE AUTENTICAÇÃO CONCLUÍDA")
            print("=" * 60 + "\n")
            
            # Envia prova de volta para o usuário
            self.enviar_resposta(endereco_retorno, {
                'type': 'snark_proof',
                'data': {
                    'prova': dados_prova[0],
                    'params': dados_prova[1]
                }
            })
        else:
            print(Color.RED.value + "❌ Falha ao gerar prova zk-SNARK")
            print("=" * 60)
            print(Color.RED.value + " FASE DE AUTENTICAÇÃO FALHOU")
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
            print(Color.RED.value + " Decodificando imagem base64...")
            
            # Decodifica imagem base64
            dados_imagem = base64.b64decode(foto_base64)
            imagem = Image.open(BytesIO(dados_imagem))
            
            print(Color.RED.value + " Detectando face na imagem...")
            
            # Detecta e extrai face da imagem
            face = self.mtcnn(imagem)
            
            if face is None:
                print(Color.RED.value + "❌ Nenhuma face detectada na imagem")
                return None

            print(Color.RED.value + " Extraindo características faciais...")
            
            # Gera embedding facial usando o modelo InceptionResnetV1
            with torch.no_grad():
                embedding = self.resnet(face.unsqueeze(0).to(self.device))
            
            # Converte tensor para lista para serialização JSON
            embedding_list = embedding.squeeze().cpu().numpy().tolist()

            # Ajusta o vetor para ser aceito pelo circom
            for i in range(Adjustments.DIMENSIONS.value):
                embedding_list[i] = int(embedding_list[i] * Adjustments.SCALE.value)
            
            print(Color.RED.value + f" Embedding gerada - Dimensões: {len(embedding_list)}")
            return embedding_list
            
        except Exception as e:
            print(Color.RED.value + f"❌ Erro ao gerar embedding: {e}")
            return None
    
    def gerar_prova_snark(self, dados_mensagem):
        """Gera prova zk-SNARK para verificação de similaridade facial"""
        try:
            foto_nova_base64 = dados_mensagem['new_image']
            embedding_antiga = dados_mensagem['old_embedding']
            proving_key_b64 = dados_mensagem['proving_key']
            circuit_wasm_b64 = dados_mensagem['circuit']
            
            print(Color.RED.value + " Salvando arquivos do trusted setup recebidos...")
            
            # Salva a chave de prova (proving_key.zkey)
            proving_key_data = base64.b64decode(proving_key_b64)
            with open(SnarkPath.PROVING_KEY.value, 'wb') as f:
                f.write(proving_key_data)
            print(Color.RED.value + f" Chave de prova salva em: {SnarkPath.PROVING_KEY.value}")
            
            # Salva o circuit.wasm (decodifica de base64)
            circuit_wasm_data = base64.b64decode(circuit_wasm_b64)
            with open(SnarkPath.CIRCUIT.value, 'wb') as f:
                f.write(circuit_wasm_data)
            print(Color.RED.value + f" Circuit WASM salvo em: {SnarkPath.CIRCUIT.value}")
            
            print(Color.RED.value + " Gerando embedding da nova foto...")
            
            # Gera nova embedding da foto atual
            embedding_nova = self.gerar_embedding(foto_nova_base64)
            
            if embedding_nova is None:
                print(Color.RED.value + "❌ Não foi possível extrair embedding da nova foto")
                return None

            print(Color.RED.value + " Preparando dados para geração da prova zk-SNARK...")

            # Salva dados temporariamente para o script zk-SNARK
            dados_witness = {
                'embedding1': embedding_antiga,
                'embedding2': embedding_nova,
                'threshold': self.limiar_similaridade
            }
            
            with open(SnarkPath.WITNESS.value, 'w') as arquivo:
                json.dump(dados_witness, arquivo)
            
            print(Color.RED.value + " Executando script zk-SNARK...")

            # Executa o script de geração da prova zk-SNARK
            resultado = subprocess.run(
                SnarkPath.GENERATE_PROOF_SCRIPT.value,
                capture_output=True,
                text=True,
                shell=True
            )
            
            if resultado.returncode != 0:
                print(Color.RED.value + f"❌ Erro ao executar script SNARK: {resultado.stderr}")
                return None

            print(Color.RED.value + " Carregando arquivos da prova zk-SNARK...")
            
            # Carrega os arquivos gerados pelo script zk-SNARK
            prova = self.carregar_arquivo_json(SnarkPath.PROOF.value)
            parametros_publicos = self.carregar_arquivo_json(SnarkPath.PUBLIC_PARAMETERS.value)

            print(Color.RED.value + " ✅ Prova zk-SNARK gerada com sucesso")
            return (prova, parametros_publicos)
            
        except Exception as e:
            print(Color.RED.value + f"❌ Erro ao gerar prova zk-SNARK: {e}")
            return None
    
    def carregar_arquivo_json(self, caminho_arquivo):
        """Carrega e retorna conteúdo de arquivo JSON"""
        try:
            with open(caminho_arquivo, 'r') as arquivo:
                conteudo = json.load(arquivo)
            return conteudo
        except Exception as e:
            print(Color.RED.value + f"❌ Erro ao carregar arquivo {caminho_arquivo}: {e}")
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
                print(Color.RED.value + f" Resposta enviada para {endereco_retorno}")
            else:
                print(Color.RED.value + f"❌ Falha ao enviar resposta para {endereco_retorno}")
                
            return sucesso
            
        except Exception as e:
            print(Color.RED.value + f"❌ Erro ao processar endereço de retorno: {e}")
            return False
    
    def enviar_mensagem(self, host, porta, mensagem):
        """Envia mensagem JSON para outros serviços via TCP"""
        try:
            mensagem_json = json.dumps(mensagem)
            tamanho_mensagem = len(mensagem_json.encode())
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, porta))
                s.send(mensagem_json.encode())
                
            print(Color.RED.value + f" Mensagem enviada para {host}:{porta} - Tamanho: {tamanho_mensagem} bytes")
            return True
            
        except ConnectionRefusedError:
            print(Color.RED.value + f"❌ Conexão recusada para {host}:{porta}")
            return False
        except Exception as e:
            print(Color.RED.value + f"❌ Erro ao enviar mensagem: {e}")
            return False
