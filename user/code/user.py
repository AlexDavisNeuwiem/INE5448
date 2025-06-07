import time
import json
import base64
import socket
import threading

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

from PIL import Image
from enums import ImagePath, Address


class UserService:
    def __init__(self):
        self.symmetric_key = None

        self.host = Address.HOST.value
        self.port = Address.PORT.value

        self.server_host = Address.SERVER_HOST.value
        self.server_port = Address.SERVER_PORT.value

        self.modelo_host = Address.MODEL_HOST.value
        self.modelo_port = Address.MODEL_PORT.value
        
    def run(self):
        """Inicia o serviço do usuário"""
        print("🟢 Iniciando serviço do usuário...")
        
        # Inicia servidor para receber mensagens
        server_thread = threading.Thread(target=self._start_server)
        server_thread.daemon = True
        server_thread.start()
        
        # Simula processo de registro
        self._processo_registro()
        
        # Mantém o serviço rodando
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🟢 Encerrando serviço do usuário...")
    
    def _start_server(self):
        """Inicia servidor para receber mensagens de outros serviços"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen(5)
            print(f"🟢 Usuario listening on {self.host}:{self.port}")
            
            while True:
                try:
                    conn, addr = s.accept()
                    thread = threading.Thread(target=self._handle_client, args=(conn, addr))
                    thread.start()
                except Exception as e:
                    print(f"🟢 Erro no servidor: {e}")
    
    def _handle_client(self, conn, addr):
        """Processa mensagens recebidas"""
        try:
            with conn:
                data = conn.recv(4096)
                if data:
                    message = json.loads(data.decode())
                    print(f"🟢 Mensagem recebida: {message}")
                    
                    if message['type'] == 'embedding':
                        self._processar_embedding(message['data'])
                    elif message['type'] == 'registration_id':
                        self._processar_id_registro(message['data'])
                    elif message['type'] == 'encrypted_embedding':
                        self._processar_embedding_criptografada(message['data'])
                    elif message['type'] == 'snark_proof':
                        self._processar_prova_snark(message['data'])
                    elif message['type'] == 'authentication_result':
                        self._processar_resultado_autenticacao(message['data'])
                        
        except Exception as e:
            print(f"🟢 Erro ao processar mensagem: {e}")
    
    def gerar_chaves_simetricas(self):
        """Gera chave simétrica AES de 256 bits"""
        self.symmetric_key = get_random_bytes(32)  # 256 bits
        print("🟢 Chave simétrica gerada com sucesso")
        return self.symmetric_key
    
    def criptografar_embedding(self, embedding):
        """Criptografa embedding com AES"""
        if not self.symmetric_key:
            raise ValueError("Chave simétrica não foi gerada")
        
        # Converte embedding para bytes se necessário
        if isinstance(embedding, list):
            embedding_str = json.dumps(embedding)
            embedding_bytes = embedding_str.encode('utf-8')
        else:
            embedding_bytes = embedding
        
        # Criptografia AES
        cipher = AES.new(self.symmetric_key, AES.MODE_CBC)
        encrypted_data = cipher.encrypt(pad(embedding_bytes, AES.block_size))
        
        # Retorna dados criptografados + IV
        encrypted_package = {
            'data': base64.b64encode(encrypted_data).decode('utf-8'),
            'iv': base64.b64encode(cipher.iv).decode('utf-8')
        }
        
        print("🟢 Embedding criptografada com sucesso")
        return encrypted_package
    
    def descriptografar_embedding(self, encrypted_package):
        """Descriptografa embedding"""
        if not self.symmetric_key:
            raise ValueError("Chave simétrica não foi gerada")
        
        # Extrai dados e IV
        encrypted_data = base64.b64decode(encrypted_package['data'])
        iv = base64.b64decode(encrypted_package['iv'])
        
        # Descriptografia AES
        cipher = AES.new(self.symmetric_key, AES.MODE_CBC, iv)
        decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
        
        # Converte de volta para embedding
        embedding = json.loads(decrypted_data.decode('utf-8'))
        print("🟢 Embedding descriptografada com sucesso")
        return embedding
    
    def enviar_mensagem(self, host, port, message):
        """Envia mensagem para outros serviços"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                s.send(json.dumps(message).encode())
                print(f"🟢 Mensagem enviada para {host}:{port}")
                return True
        except Exception as e:
            print(f"🟢 Erro ao enviar mensagem: {e}")
            return False
    
    def _processo_registro(self):
        """Executa o processo completo de registro"""
        print("\n🟢 === INICIANDO PROCESSO DE REGISTRO ===")
        
        # Aguarda um pouco para outros serviços iniciarem
        time.sleep(5)
        
        # 1. Gera chave simétrica
        self.gerar_chaves_simetricas()
        
        # 2. Carrega foto do usuário
        foto_usuario = Image.open(ImagePath.FACE_IMAGE_REG.value).convert('RGB')
        
        # 3. Solicita embedding ao modelo de IA
        print("🟢 Enviando foto para o modelo de IA...")
        mensagem_modelo = {
            'type': 'generate_embedding',
            'data': foto_usuario,
            'return_to': 'user-container:8001'
        }
        
        self.enviar_mensagem(self.modelo_host, self.modelo_port, mensagem_modelo)
    
    def _processar_embedding(self, embedding):
        """Processa embedding recebida do modelo de IA"""
        print("🟢 Embedding recebida do modelo de IA")
        
        # TODO: Tratar quando embedding == None

        # 4. Criptografa embedding
        embedding_criptografada = self.criptografar_embedding(embedding)
        
        # 5. Envia embedding criptografada para servidor
        print("🟢 Enviando embedding criptografada para servidor...")
        mensagem_servidor = {
            'type': 'store_embedding',
            'data': embedding_criptografada,
            'return_to': 'user-container:8001'
        }
        
        self.enviar_mensagem(self.server_host, self.server_port, mensagem_servidor)
    
    def _processar_id_registro(self, registration_id):
        """Processa ID de registro recebido do servidor"""
        print(f"🟢 ✅ REGISTRO CONCLUÍDO! ID: {registration_id}")
        print("🟢 === PROCESSO DE REGISTRO FINALIZADO ===\n")
        
        # Armazena ID para futuras autenticações
        self.user_id = registration_id
        
        # Inicia processo de autenticação após 3 segundos
        threading.Timer(3.0, self._processo_autenticacao).start()
    
    def _processo_autenticacao(self):
        """Executa o processo completo de autenticação"""
        print("\n🟢 === INICIANDO PROCESSO DE AUTENTICAÇÃO ===")
        
        if not hasattr(self, 'user_id'):
            print("🟢 ❌ Erro: ID do usuário não encontrado")
            return
        
        # 1. Solicitar embedding criptografada do servidor
        print(f"🟢 Solicitando embedding para ID: {self.user_id}")
        mensagem_servidor = {
            'type': 'get_embedding',
            'data': self.user_id,
            'return_to': 'user-container:8001'
        }
        
        self.enviar_mensagem(self.server_host, self.server_port, mensagem_servidor)
    
    def _processar_embedding_criptografada(self, embedding_criptografada):
        """Processa embedding criptografada recebida do servidor"""
        print("🟢 Embedding criptografada recebida do servidor")
        
        # 3. Descriptografa embedding
        embedding_antiga = self.descriptografar_embedding(embedding_criptografada)
        print("🟢 Embedding descriptografada com sucesso")
        
        # 4. Carrega nova foto para autenticação
        nova_foto = Image.open(ImagePath.FACE_IMAGE_AUT.value).convert('RGB')
        
        # Solicita prova zk-SNARK ao modelo
        print("🟢 Solicitando prova zk-SNARK ao modelo...")
        mensagem_modelo = {
            'type': 'generate_snark_proof',
            'data': {
                'nova_foto': nova_foto,
                'embedding_antiga': embedding_antiga,
            },
            'return_to': 'user-container:8001'
        }
        
        self.enviar_mensagem(self.modelo_host, self.modelo_port, mensagem_modelo)
    
    def _processar_prova_snark(self, prova_snark):
        """Processa prova zk-SNARK recebida do modelo"""
        print("🟢 Prova zk-SNARK recebida do modelo")
        
        # 7. Envia prova para o servidor verificar
        print("🟢 Enviando prova para servidor verificar...")
        mensagem_servidor = {
            'type': 'verify_snark_proof',
            'data': {
                'user_id': self.user_id,
                'proof': prova_snark
            },
            'return_to': 'user-container:8001'
        }
        
        self.enviar_mensagem(self.server_host, self.server_port, mensagem_servidor)
    
    def _processar_resultado_autenticacao(self, resultado):
        """Processa resultado da autenticação"""
        if resultado['authenticated']:
            print(f"🟢 ✅ AUTENTICAÇÃO BEM-SUCEDIDA!")
            print(f"🟢 Similaridade: {resultado.get('similarity', 'N/A')}")
        else:
            print(f"🟢 ❌ AUTENTICAÇÃO FALHOU!")
            print(f"🟢 Motivo: {resultado.get('reason', 'Desconhecido')}")
        
        print("🟢 === PROCESSO DE AUTENTICAÇÃO FINALIZADO ===\n")
