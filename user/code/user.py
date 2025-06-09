import time
import json
import base64
import socket
import threading
from io import BytesIO

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

from PIL import Image
from enums import Addresses, ImagePath


class User:
    def __init__(self):

        print("\n" + "=" * 60)
        print("🟢 INICIALIZANDO USUÁRIO")
        print("=" * 60)

        # Chave simétrica para criptografia
        self.chave_simetrica = None
        self.user_id = None
        
        # Configurações de rede - endereços locais
        self.host = Addresses.HOST.value
        self.port = Addresses.PORT.value
        
        # Configurações de rede - serviços externos
        self.servidor_host = Addresses.SERVER_HOST.value
        self.servidor_port = Addresses.SERVER_PORT.value
        self.modelo_host = Addresses.MODEL_HOST.value  
        self.modelo_port = Addresses.MODEL_PORT.value
    
    def executar(self):
        """Método principal que inicia o serviço do usuário"""
        
        # Inicia servidor para receber mensagens dos outros serviços
        servidor_thread = threading.Thread(target=self.iniciar_servidor)
        servidor_thread.daemon = True
        servidor_thread.start()
        print("🟢 Servidor de escuta iniciado em thread separada")
        
        # Aguarda um momento para outros serviços iniciarem
        print("🟢 Aguardando outros serviços iniciarem...")
        time.sleep(5)
        
        # Inicia processo de registro
        self.processo_registro()
        
        # Mantém o serviço rodando
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🟢 Encerrando serviço do usuário...")
    
    def iniciar_servidor(self):
        """Inicia servidor TCP para receber mensagens de outros serviços"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((self.host, self.port))
                s.listen(5)

                print(f"🟢 Servidor escutando em {self.host}:{self.port}")

                print("=" * 60)
                print("🟢 USUÁRIO INICIALIZADO COM SUCESSO")
                print("=" * 60)
                
                while True:
                    try:
                        conn, addr = s.accept()
                        # Cria thread para cada conexão
                        thread = threading.Thread(target=self.processar_cliente, args=(conn, addr))
                        thread.start()
                    except Exception as e:
                        print(f"🟢 ❌ Erro no servidor: {e}")
        except Exception as e:
            print(f"🟢 ❌ Erro crítico no servidor: {e}")
    
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
                    print(f"🟢 Mensagem recebida de {addr} - Tamanho: {len(dados_completos)} bytes")
                    
                    # Converte dados recebidos para JSON
                    mensagem = json.loads(dados_completos.decode())
                    print(f"🟢 Tipo da mensagem: {mensagem.get('type', 'desconhecido')}")
                    
                    # Processa mensagem baseada no tipo
                    self.processar_mensagem(mensagem)
                        
        except json.JSONDecodeError as e:
            print(f"🟢 ❌ Erro ao decodificar JSON: {e}")
        except Exception as e:
            print(f"🟢 ❌ Erro ao processar cliente: {e}")
    
    def processar_mensagem(self, mensagem):
        """Roteia mensagens baseado no tipo"""
        tipo_mensagem = mensagem.get('type')
        dados = mensagem.get('data')
        
        if tipo_mensagem == 'embedding':
            self.processar_embedding_recebida(dados)
        elif tipo_mensagem == 'registration_id':
            self.processar_id_registro(dados)
        elif tipo_mensagem == 'encrypted_embedding':
            self.processar_embedding_criptografada(dados)
        elif tipo_mensagem == 'snark_proof':
            self.processar_prova_snark(dados)
        elif tipo_mensagem == 'authentication_result':
            self.processar_resultado_autenticacao(dados)
        else:
            print(f"🟢 ⚠️ Tipo de mensagem desconhecido: {tipo_mensagem}")
    
    def gerar_chave_simetrica(self):
        """Gera chave simétrica AES de 256 bits para criptografia"""
        print("🟢 Gerando chave simétrica AES-256...")
        self.chave_simetrica = get_random_bytes(32)  # 256 bits = 32 bytes
        print("🟢 Chave simétrica gerada com sucesso")
        return self.chave_simetrica
    
    def criptografar_embedding(self, embedding):
        """Criptografa embedding usando AES-256 no modo CBC"""
        if not self.chave_simetrica:
            raise ValueError("❌ Chave simétrica não foi gerada")
        
        print("🟢 Criptografando embedding...")
        
        # Converte embedding para formato serializável
        if isinstance(embedding, list):
            embedding_str = json.dumps(embedding)
            embedding_bytes = embedding_str.encode('utf-8')
        else:
            embedding_bytes = str(embedding).encode('utf-8')
        
        # Inicializa cipher AES no modo CBC
        cipher = AES.new(self.chave_simetrica, AES.MODE_CBC)
        
        # Aplica padding e criptografa
        dados_padded = pad(embedding_bytes, AES.block_size)
        dados_criptografados = cipher.encrypt(dados_padded)
        
        # Empacota dados criptografados com IV
        pacote_criptografado = {
            'data': base64.b64encode(dados_criptografados).decode('utf-8'),
            'iv': base64.b64encode(cipher.iv).decode('utf-8')
        }
        
        print("🟢 Embedding criptografada com sucesso")
        return pacote_criptografado
    
    def descriptografar_embedding(self, pacote_criptografado):
        """Descriptografa embedding usando AES-256"""
        if not self.chave_simetrica:
            raise ValueError("❌ Chave simétrica não foi gerada")
        
        print("🟢 Descriptografando embedding...")
        
        # Extrai dados criptografados e IV do pacote
        dados_criptografados = base64.b64decode(pacote_criptografado['data'])
        iv = base64.b64decode(pacote_criptografado['iv'])
        
        # Inicializa cipher com IV original
        cipher = AES.new(self.chave_simetrica, AES.MODE_CBC, iv)
        
        # Descriptografa e remove padding
        dados_descriptografados = cipher.decrypt(dados_criptografados)
        dados_sem_padding = unpad(dados_descriptografados, AES.block_size)
        
        # Converte de volta para embedding
        embedding = json.loads(dados_sem_padding.decode('utf-8'))
        print("🟢 Embedding descriptografada com sucesso")
        return embedding
    
    def enviar_mensagem(self, host, port, mensagem):
        """Envia mensagem JSON para outros serviços via TCP"""
        try:
            mensagem_json = json.dumps(mensagem)
            tamanho_mensagem = len(mensagem_json.encode())
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                s.send(mensagem_json.encode())
                
            print(f"🟢 Mensagem enviada para {host}:{port} - Tamanho: {tamanho_mensagem} bytes")
            return True
            
        except ConnectionRefusedError:
            print(f"🟢 ❌ Conexão recusada para {host}:{port}")
            return False
        except Exception as e:
            print(f"🟢 ❌ Erro ao enviar mensagem: {e}")
            return False
    
    def carregar_imagem_como_base64(self, caminho_imagem):
        """Carrega imagem e converte para base64"""
        try:
            print(f"🟢 Carregando imagem: {caminho_imagem}")
            imagem = Image.open(caminho_imagem)
            
            # Converte para base64
            buffer = BytesIO()
            imagem.save(buffer, format='JPEG')
            imagem_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            print(f"🟢 Imagem carregada - Tamanho: {len(imagem_base64)} caracteres")
            return imagem_base64
            
        except Exception as e:
            print(f"🟢 ❌ Erro ao carregar imagem: {e}")
            return None
    
    # === PROCESSO DE REGISTRO ===
    
    def processo_registro(self):
        """Executa o processo completo de registro do usuário"""
        print("\n" + "=" * 60)
        print("🟢 INICIANDO FASE DE REGISTRO")
        print("=" * 60)
        
        # Etapa 1: Gerar chave simétrica
        print("🟢 Etapa 1/4: Gerando chave de criptografia")
        self.gerar_chave_simetrica()
        
        # Etapa 2: Carregar foto do usuário
        print("\n🟢 Etapa 2/4: Carregando foto do usuário")
        foto_base64 = self.carregar_imagem_como_base64(ImagePath.FACE_IMAGE_REG.value)
        
        if not foto_base64:
            print("🟢 ❌ Falha no registro: Não foi possível carregar a foto")
            return
        
        # Etapa 3: Solicitar embedding ao modelo de IA
        print("\n🟢 Etapa 3/4: Enviando foto para o modelo de IA")
        mensagem_modelo = {
            'type': 'generate_embedding',
            'data': foto_base64,
            'return_to': Addresses.RETURN.value
        }
        
        sucesso = self.enviar_mensagem(self.modelo_host, self.modelo_port, mensagem_modelo)
        if not sucesso:
            print("🟢 ❌ Falha no registro: Não foi possível enviar foto para o modelo")
            return
        
        print("🟢 Aguardando resposta do modelo de IA...")
    
    def processar_embedding_recebida(self, embedding):
        """Processa embedding recebida do modelo de IA durante o registro"""
        print("\n🟢 Etapa 4/4: Processando embedding recebida")
        
        # Verifica se embedding é válida
        if embedding is None:
            print("🟢 ❌ Falha no registro: Embedding inválida recebida do modelo")
            return
        
        print(f"🟢 Embedding recebida - Dimensões: {len(embedding) if isinstance(embedding, list) else 'formato desconhecido'}")
        
        # Criptografa embedding
        try:
            embedding_criptografada = self.criptografar_embedding(embedding)
        except Exception as e:
            print(f"🟢 ❌ Falha no registro: Erro na criptografia - {e}")
            return
        
        # Envia embedding criptografada para servidor
        print("🟢 Enviando embedding criptografada para servidor...")
        mensagem_servidor = {
            'type': 'store_embedding',
            'data': embedding_criptografada,
            'return_to': Addresses.RETURN.value
        }
        
        sucesso = self.enviar_mensagem(self.servidor_host, self.servidor_port, mensagem_servidor)
        if not sucesso:
            print("🟢 ❌ Falha no registro: Não foi possível enviar para o servidor")
    
    def processar_id_registro(self, registration_id):
        """Processa ID de registro recebido do servidor"""
        print(f"🟢 ID do usuário: {registration_id}")
        print("=" * 60)
        print("🟢 FASE DE REGISTRO FINALIZADA")
        print("=" * 60)
        
        # Armazena ID para futuras autenticações
        self.user_id = registration_id
        
        # Agenda processo de autenticação
        print("\n" + "🟢 Autenticação será iniciada em 3 segundos...")
        threading.Timer(3.0, self.processo_autenticacao).start()
    
    # === PROCESSO DE AUTENTICAÇÃO ===
    
    def processo_autenticacao(self):
        """Executa o processo completo de autenticação do usuário"""
        print("\n" + "=" * 60)
        print("🟢 INICIANDO FASE DE AUTENTICAÇÃO")
        print("=" * 60)
        
        if not self.user_id:
            print("🟢 ❌ Falha na autenticação: ID do usuário não encontrado")
            print("🟢 É necessário fazer o registro primeiro")
            return
        
        # Etapa 1: Solicitar embedding armazenada do servidor
        print(f"🟢 Etapa 1/4: Solicitando embedding para ID {self.user_id}")
        mensagem_servidor = {
            'type': 'get_embedding',
            'data': self.user_id,
            'return_to': Addresses.RETURN.value
        }
        
        sucesso = self.enviar_mensagem(self.servidor_host, self.servidor_port, mensagem_servidor)
        if not sucesso:
            print("🟢 ❌ Falha na autenticação: Não foi possível contatar o servidor")
            return
        
        print("🟢 Aguardando embedding do servidor...")
    
    def processar_embedding_criptografada(self, embedding_criptografada):
        """Processa embedding criptografada recebida do servidor"""
        print("\n🟢 Etapa 2/4: Processando embedding do servidor")
        
        # Descriptografa embedding armazenada
        try:
            embedding_antiga = self.descriptografar_embedding(embedding_criptografada)
            print(f"🟢 Embedding descriptografada - Dimensões: {len(embedding_antiga) if isinstance(embedding_antiga, list) else 'formato desconhecido'}")
        except Exception as e:
            print(f"🟢 ❌ Falha na autenticação: Erro na descriptografia - {e}")
            return
        
        # Carrega nova foto para autenticação
        print("\n🟢 Etapa 3/4: Carregando foto para autenticação")
        foto_nova_base64 = self.carregar_imagem_como_base64(ImagePath.FACE_IMAGE_AUT.value)
        
        if not foto_nova_base64:
            print("🟢 ❌ Falha na autenticação: Não foi possível carregar foto de autenticação")
            return
        
        # Solicita prova zk-SNARK ao modelo
        print("🟢 Enviando dados para geração de prova zk-SNARK...")
        mensagem_modelo = {
            'type': 'generate_snark_proof',
            'data': {
                'foto_nova': foto_nova_base64,
                'embedding_antiga': embedding_antiga,
            },
            'return_to': Addresses.RETURN.value
        }
        
        sucesso = self.enviar_mensagem(self.modelo_host, self.modelo_port, mensagem_modelo)
        if not sucesso:
            print("🟢 ❌ Falha na autenticação: Não foi possível enviar dados para o modelo")
    
    def processar_prova_snark(self, dados_prova):
        """Processa prova zk-SNARK recebida do modelo"""
        print("\n🟢 Etapa 4/4: Processando prova zk-SNARK")
        print("🟢 Prova zk-SNARK recebida do modelo")
        
        # Verifica se prova contém dados necessários
        if not all(key in dados_prova for key in ['prova', 'chave', 'params']):
            print("🟢 ❌ Falha na autenticação: Prova zk-SNARK incompleta")
            return
        
        # Envia prova para o servidor verificar
        print("🟢 Enviando prova para verificação no servidor...")
        mensagem_servidor = {
            'type': 'verify_snark_proof',
            'data': {
                'user_id': self.user_id,
                'prova': dados_prova['prova'],
                'chave': dados_prova['chave'],
                'params': dados_prova['params']
            },
            'return_to': Addresses.RETURN.value
        }
        
        sucesso = self.enviar_mensagem(self.servidor_host, self.servidor_port, mensagem_servidor)
        if not sucesso:
            print("🟢 ❌ Falha na autenticação: Não foi possível enviar prova para o servidor")
    
    def processar_resultado_autenticacao(self, resultado):
        """Processa resultado final da autenticação"""
        print(f"\n🟢 RESULTADO DA AUTENTICAÇÃO:")
        
        if resultado.get('authenticated', False):
            print("🟢 ✅ AUTENTICAÇÃO BEM-SUCEDIDA!")
            print(f"🟢 Usuário autenticado com sucesso")
            if 'timestamp' in resultado:
                print(f"🟢 Timestamp: {resultado['timestamp']}")
        else:
            print("🟢 ❌ AUTENTICAÇÃO FALHOU!")
            motivo = resultado.get('reason', 'Motivo não especificado')
            print(f"🟢 Motivo da falha: {motivo}")
        
        print("=" * 60)
        print("🟢 FASE DE AUTENTICAÇÃO FINALIZADA")
        print("=" * 60 + "\n")
