import time
import json
import socket
import threading
import subprocess

import psycopg2

from enums import Address, PostgesData, SnarkPath


class Server:
    def __init__(self):
        self.host = Address.HOST.value
        self.port = Address.PORT.value

        self.db_config = {
            'host': PostgesData.HOST.value,
            'database': PostgesData.DATABASE.value,
            'user': PostgesData.USER.value,
            'password': PostgesData.PASSWORD.value
        }
        
    def run(self):
        """Inicia o serviço do servidor"""
        print("🔵 Iniciando serviço do servidor...")
        
        # Inicializa banco de dados
        self._init_database()
        
        # Inicia servidor
        self._start_server()
    
    def _init_database(self):
        """Inicializa tabelas do banco de dados"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Cria tabela para embeddings criptografadas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS encrypted_embeddings (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    encrypted_data TEXT NOT NULL,
                    iv TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            print("🔵 Banco de dados inicializado")
            
        except Exception as e:
            print(f"🔵 Erro ao inicializar banco: {e}")
            # Tenta novamente após um tempo
            time.sleep(5)
            self._init_database()
    
    def _start_server(self):
        """Inicia servidor para receber mensagens"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen(5)
            print(f"🔵 Servidor listening on {self.host}:{self.port}")
            
            while True:
                try:
                    conn, addr = s.accept()
                    thread = threading.Thread(target=self._handle_client, args=(conn, addr))
                    thread.start()
                except Exception as e:
                    print(f"🔵 Erro no servidor: {e}")
                except KeyboardInterrupt:
                    print("\n🔵 Encerrando servidor...")
                    break
    
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
                print(f"🔵 Tamanho da mensagem recebida:", len(data))
                if data:
                    message = json.loads(data.decode())
                    print(f"🔵 Mensagem recebida: {message['type']}")
                    
                    if message['type'] == 'store_embedding':
                        embedding_id = self.armazenar_embedding(message['data'])
                        
                        # Envia ID de volta para o usuário
                        return_address = message['return_to'].split(':')
                        self.enviar_mensagem(
                            return_address[0], 
                            int(return_address[1]),
                            {
                                'type': 'registration_id',
                                'data': embedding_id
                            }
                        )
                    
                    elif message['type'] == 'get_embedding':
                        embedding_criptografada = self.recuperar_embedding(message['data'])
                        
                        if embedding_criptografada:
                            # Envia embedding de volta para o usuário
                            return_address = message['return_to'].split(':')
                            self.enviar_mensagem(
                                return_address[0], 
                                int(return_address[1]),
                                {
                                    'type': 'encrypted_embedding',
                                    'data': embedding_criptografada
                                }
                            )
                        else:
                            # Envia erro se não encontrar embedding
                            return_address = message['return_to'].split(':')
                            self.enviar_mensagem(
                                return_address[0], 
                                int(return_address[1]),
                                {
                                    'type': 'authentication_result',
                                    'data': {
                                        'authenticated': False,
                                        'reason': 'Embedding não encontrada para o ID fornecido'
                                    }
                                }
                            )
                    
                    elif message['type'] == 'verify_snark_proof':
                        resultado = self.verificar_prova_snark(
                            message['data']['prova'], 
                            message['data']['chave'], 
                            message['data']['params']
                        )
                        
                        # Envia resultado de volta para o usuário
                        return_address = message['return_to'].split(':')
                        self.enviar_mensagem(
                            return_address[0], 
                            int(return_address[1]),
                            {
                                'type': 'authentication_result',
                                'data': resultado
                            }
                        )
                        
        except Exception as e:
            print(f"🔵 Erro ao processar mensagem: {e}")
    
    def armazenar_embedding(self, embedding_criptografada):
        """Armazena embedding criptografada no banco e retorna ID"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Insere embedding criptografada
            cursor.execute("""
                INSERT INTO encrypted_embeddings (encrypted_data, iv)
                VALUES (%s, %s)
                RETURNING id
            """, (
                embedding_criptografada['data'],
                embedding_criptografada['iv']
            ))
            
            embedding_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"🔵 Embedding armazenada com ID: {embedding_id}")
            return str(embedding_id)
            
        except Exception as e:
            print(f"🔵 Erro ao armazenar embedding: {e}")
            return None
    
    def recuperar_embedding(self, embedding_id):
        """Recupera embedding criptografada do banco pelo ID"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Busca embedding por ID
            cursor.execute("""
                SELECT encrypted_data, iv FROM encrypted_embeddings
                WHERE id = %s
            """, (embedding_id,))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result:
                embedding_criptografada = {
                    'data': result[0],
                    'iv': result[1]
                }
                print(f"🔵 Embedding recuperada para ID: {embedding_id}")
                return embedding_criptografada
            else:
                print(f"🔵 Embedding não encontrada para ID: {embedding_id}")
                return None
                
        except Exception as e:
            print(f"🔵 Erro ao recuperar embedding: {e}")
            return None
    
    def verificar_prova_snark(self, prova, chave, params):
        """Verifica prova zk-SNARK recebida"""
        try:
            print(f"🔵 Verificando prova zk-SNARK...")
            
            # Verifica se os dados da prova são válidos
            if not all([prova, chave, params]):
                print("🔵 ❌ Dados da prova SNARK inválidos ou incompletos")
                return {
                    'authenticated': False,
                    'reason': 'Dados da prova SNARK inválidos'
                }

            # Converte os dados de bytes para arquivos JSON
            self.escreve_arquivo(SnarkPath.PROOF.value, prova)
            self.escreve_arquivo(SnarkPath.VERIFICATION_KEY.value, chave)
            self.escreve_arquivo(SnarkPath.PUBLIC_PARAMETERS.value, params)

            # Executar o script de verificação SNARK
            resultado = subprocess.run(['/bin/bash', '/home/server/pysnark/verify.sh'], capture_output=True, text=True)
            
            # Verifica se a prova é válida baseado na saída do script
            if resultado.returncode == 0 and 'OK!' in resultado.stdout:
                print("🔵 ✅ Prova zk-SNARK válida - Autenticação aprovada")
                return {
                    'authenticated': True,
                    'timestamp': time.time()
                }
            else:
                print("🔵 ❌ Prova zk-SNARK inválida - Autenticação rejeitada")
                print(f"🔵 Saída do script: {resultado.stdout}")
                print(f"🔵 Erro do script: {resultado.stderr}")
                return {
                    'authenticated': False,
                    'reason': 'Prova inválida'
                }
                
        except Exception as e:
            print(f"🔵 Erro ao verificar prova: {e}")
            return {
                'authenticated': False,
                'reason': f'Erro na verificação: {str(e)}'
            }
    
    def enviar_mensagem(self, host, port, message):
        """Envia mensagem para outros serviços"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                s.send(json.dumps(message).encode())
                print(f"🔵 Mensagem de tamanho {len(json.dumps(message).encode())} enviada para {host}:{port}")
                return True
        except Exception as e:
            print(f"🔵 Erro ao enviar mensagem: {e}")
            return False

    def escreve_arquivo(self, nome, conteudo):
        # Escreve o conteúdo no arquivo JSON
        with open(nome, 'w') as arquivo:
            json.dump(conteudo, arquivo)