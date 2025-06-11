import time
import json
import socket
import threading
import subprocess

import psycopg2

from enums import Address, Color, PostgesData, SnarkPath


class Server:
    def __init__(self):

        print("\n" + "=" * 60)
        print(Color.BLUE.value + " INICIALIZANDO SERVIDOR")
        print("=" * 60)

        # Configurações de rede
        self.host = Address.HOST.value
        self.port = Address.PORT.value

        # Configurações do banco de dados PostgreSQL
        self.config_banco = {
            'host': PostgesData.HOST.value,
            'database': PostgesData.DATABASE.value,
            'user': PostgesData.USER.value,
            'password': PostgesData.PASSWORD.value
        }
    
    def executar(self):
        """Método principal que inicia o serviço do servidor"""
        
        # Inicializa banco de dados
        self.inicializar_banco_dados()
        
        # Inicia servidor para receber mensagens
        self.iniciar_servidor()
    
    def inicializar_banco_dados(self):
        """Inicializa tabelas do banco de dados PostgreSQL"""
        try:
            print(Color.BLUE.value + " Conectando ao banco de dados PostgreSQL...")
            
            conn = psycopg2.connect(**self.config_banco)
            cursor = conn.cursor()
            
            print(Color.BLUE.value + " Criando tabelas se não existirem...")
            
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
            
            print(Color.BLUE.value + " Banco de dados inicializado com sucesso")
            
        except Exception as e:
            print(Color.BLUE.value + f"❌ Erro ao inicializar banco de dados: {e}")
            print(Color.BLUE.value + " Tentando novamente em 5 segundos...")
            time.sleep(5)
            self.inicializar_banco_dados()
    
    def iniciar_servidor(self):
        """Inicia servidor TCP para receber mensagens de outros serviços"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((self.host, self.port))
                s.listen(5)

                print(Color.BLUE.value + f" Servidor escutando em {self.host}:{self.port}")

                print("=" * 60)
                print(Color.BLUE.value + " SERVIDOR INICIALIZADO COM SUCESSO")
                print("=" * 60 + "\n")
                
                while True:
                    try:
                        conn, addr = s.accept()
                        # Cria thread para cada conexão
                        thread = threading.Thread(target=self.processar_cliente, args=(conn, addr))
                        thread.start()
                    except Exception as e:
                        print(Color.BLUE.value + f"❌ Erro no servidor: {e}")
                        
        except KeyboardInterrupt:
            print("\n" + Color.BLUE.value + "Encerrando serviço do servidor...")
        except Exception as e:
            print(Color.BLUE.value + f"❌ Erro crítico no servidor: {e}")
    
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
                    print(Color.BLUE.value + f" Mensagem recebida de {addr} - Tamanho: {len(dados_completos)} bytes")
                    
                    # Converte dados recebidos para JSON
                    mensagem = json.loads(dados_completos.decode())
                    tipo_mensagem = mensagem.get('type', 'desconhecido')
                    print(Color.BLUE.value + f" Tipo da mensagem: {tipo_mensagem}")
                    
                    # Processa mensagem baseada no tipo
                    self.processar_mensagem(mensagem)
                        
        except json.JSONDecodeError as e:
            print(Color.BLUE.value + f"❌ Erro ao decodificar JSON: {e}")
        except Exception as e:
            print(Color.BLUE.value + f"❌ Erro ao processar cliente: {e}")
    
    def processar_mensagem(self, mensagem):
        """Roteia mensagens baseado no tipo"""
        tipo_mensagem = mensagem.get('type')
        dados = mensagem.get('data')
        endereco_retorno = mensagem.get('return_to')
        
        if tipo_mensagem == 'store_embedding':
            self.processar_armazenamento_embedding(dados, endereco_retorno)
        elif tipo_mensagem == 'get_embedding':
            self.processar_recuperacao_embedding(dados, endereco_retorno)
        elif tipo_mensagem == 'verify_snark_proof':
            self.processar_verificacao_prova_snark(dados, endereco_retorno)
        else:
            print(Color.BLUE.value + f"⚠️ Tipo de mensagem desconhecido: {tipo_mensagem}")
    
    def processar_armazenamento_embedding(self, embedding_criptografada, endereco_retorno):
        """Processa solicitação de armazenamento de embedding (fase de registro)"""
        print("\n" + "=" * 60)
        print(Color.BLUE.value + " PROCESSANDO FASE DE REGISTRO")
        print("=" * 60)
        print(Color.BLUE.value + " Armazenando embedding criptografada...")
        
        # Armazena embedding no banco de dados
        embedding_id = self.armazenar_embedding(embedding_criptografada)
        
        if embedding_id:
            print(Color.BLUE.value + " Embedding armazenada com sucesso")
            print(Color.BLUE.value + f" ID gerado: {embedding_id}")
            print("=" * 60)
            print(Color.BLUE.value + " FASE DE REGISTRO CONCLUÍDA")
            print("=" * 60 + "\n")
            
            # Envia ID de registro de volta para o usuário
            self.enviar_resposta(endereco_retorno, {
                'type': 'registration_id',
                'data': embedding_id
            })
        else:
            print(Color.BLUE.value + "❌ Falha ao armazenar embedding")
            print("=" * 60)
            print(Color.BLUE.value + " FASE DE REGISTRO FALHOU")
            print("=" * 60)
            
            # Envia erro de volta para o usuário
            self.enviar_resposta(endereco_retorno, {
                'type': 'registration_error',
                'data': {
                    'error': 'Falha ao armazenar embedding no banco de dados'
                }
            })
    
    def processar_recuperacao_embedding(self, user_id, endereco_retorno):
        """Processa solicitação de recuperação de embedding (fase de autenticação)"""
        print("\n" + "=" * 60)
        print(Color.BLUE.value + " PROCESSANDO FASE DE AUTENTICAÇÃO - RECUPERAÇÃO")
        print("=" * 60)
        print(Color.BLUE.value + f" Recuperando embedding para ID: {user_id}")
        
        # Recupera embedding do banco de dados
        embedding_criptografada = self.recuperar_embedding(user_id)
        
        if embedding_criptografada:
            print(Color.BLUE.value + " Embedding recuperada com sucesso")
            print("=" * 60)
            print(Color.BLUE.value + " FASE DE RECUPERAÇÃO CONCLUÍDA")
            print("=" * 60 + "\n")
            
            # Envia embedding criptografada de volta para o usuário
            self.enviar_resposta(endereco_retorno, {
                'type': 'encrypted_embedding',
                'data': embedding_criptografada
            })
        else:
            print(Color.BLUE.value + "❌ Embedding não encontrada")
            print("=" * 60)
            print(Color.BLUE.value + " FASE DE RECUPERAÇÃO FALHOU")
            print("=" * 60)
            
            # Envia erro de volta para o usuário
            self.enviar_resposta(endereco_retorno, {
                'type': 'authentication_result',
                'data': {
                    'authenticated': False,
                    'reason': 'Embedding não encontrada para o ID fornecido'
                }
            })
    
    def processar_verificacao_prova_snark(self, dados_prova, endereco_retorno):
        """Processa solicitação de verificação de prova zk-SNARK (fase de autenticação)"""
        print("\n" + "=" * 60)
        print(Color.BLUE.value + " PROCESSANDO FASE DE AUTENTICAÇÃO - VERIFICAÇÃO")
        print("=" * 60)
        print(Color.BLUE.value + f" Verificando prova zk-SNARK para usuário: {dados_prova.get('user_id')}")
        
        # Verifica prova zk-SNARK
        resultado = self.verificar_prova_snark(
            dados_prova['prova'], 
            dados_prova['chave'], 
            dados_prova['params']
        )
        
        if resultado.get('authenticated', False):
            print("=" * 60)
            print(Color.BLUE.value + " FASE DE AUTENTICAÇÃO CONCLUÍDA COM SUCESSO")
            print("=" * 60)
        else:
            print(Color.BLUE.value + f" Motivo: {resultado.get('reason', 'Não especificado')}")
            print("=" * 60)
            print(Color.BLUE.value + " AUTENTICAÇÃO FALHOU")
            print("=" * 60 + "\n")
        
        # Envia resultado de volta para o usuário
        self.enviar_resposta(endereco_retorno, {
            'type': 'authentication_result',
            'data': resultado
        })
    
    def armazenar_embedding(self, embedding_criptografada):
        """Armazena embedding criptografada no banco de dados e retorna ID único"""
        try:
            print(Color.BLUE.value + " Conectando ao banco de dados para armazenamento...")
            
            conn = psycopg2.connect(**self.config_banco)
            cursor = conn.cursor()
            
            # Insere embedding criptografada na tabela
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
            
            print(Color.BLUE.value + f" Embedding armazenada no banco com ID: {embedding_id}")
            return str(embedding_id)
            
        except Exception as e:
            print(Color.BLUE.value + f"❌ Erro ao armazenar embedding no banco: {e}")
            return None
    
    def recuperar_embedding(self, embedding_id):
        """Recupera embedding criptografada do banco de dados pelo ID"""
        try:
            print(Color.BLUE.value + f" Conectando ao banco de dados para recuperação do ID: {embedding_id}")
            
            conn = psycopg2.connect(**self.config_banco)
            cursor = conn.cursor()
            
            # Busca embedding por ID na tabela
            cursor.execute("""
                SELECT encrypted_data, iv FROM encrypted_embeddings
                WHERE id = %s
            """, (embedding_id,))
            
            resultado = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if resultado:
                embedding_criptografada = {
                    'data': resultado[0],
                    'iv': resultado[1]
                }
                print(Color.BLUE.value + f" Embedding recuperada do banco para ID: {embedding_id}")
                return embedding_criptografada
            else:
                print(Color.BLUE.value + f"❌ Nenhuma embedding encontrada para ID: {embedding_id}")
                return None
                
        except Exception as e:
            print(Color.BLUE.value + f"❌ Erro ao recuperar embedding do banco: {e}")
            return None
    
    def verificar_prova_snark(self, prova, chave_verificacao, parametros_publicos):
        """Verifica a validade da prova zk-SNARK recebida"""
        try:
            print(Color.BLUE.value + " Iniciando processo de verificação da prova zk-SNARK...")
            
            # Verifica se todos os dados necessários estão presentes
            if not all([prova, chave_verificacao, parametros_publicos]):
                print(Color.BLUE.value + "❌ Dados da prova SNARK inválidos ou incompletos")
                return {
                    'authenticated': False,
                    'reason': 'Dados da prova SNARK inválidos ou incompletos'
                }

            print(Color.BLUE.value + " Salvando arquivos da prova zk-SNARK...")
            
            # Salva os dados da prova em arquivos JSON para verificação
            self.escrever_arquivo_json(SnarkPath.PROOF.value, prova)
            self.escrever_arquivo_json(SnarkPath.VERIFICATION_KEY.value, chave_verificacao)
            self.escrever_arquivo_json(SnarkPath.PUBLIC_PARAMETERS.value, parametros_publicos)

            print(Color.BLUE.value + " Executando script de verificação zk-SNARK...")
            
            # Executa o script de verificação SNARK
            resultado = subprocess.run(
                SnarkPath.SCRIPT.value, 
                capture_output=True, 
                text=True,
                shell=True
            )
            
            print(Color.BLUE.value + f" Script executado - Código de retorno: {resultado.returncode}")
            
            # Analisa resultado da verificação
            if resultado.returncode == 0 and 'OK!' in resultado.stdout:
                print(Color.BLUE.value + " ✅ Prova zk-SNARK válida - Autenticação aprovada")
                return {
                    'authenticated': True,
                    'timestamp': time.time(),
                    'verification_method': 'zk-SNARK'
                }
            else:
                print(Color.BLUE.value + "❌ Prova zk-SNARK inválida - Autenticação rejeitada")
                if resultado.stdout:
                    print("\n" + Color.BLUE.value + f" Saída do script: {resultado.stdout}")
                if resultado.stderr:
                    print(Color.BLUE.value + f" Erro do script: {resultado.stderr}")
                    
                return {
                    'authenticated': False,
                    'reason': 'Prova zk-SNARK inválida',
                    'details': resultado.stderr or 'Verificação falhou'
                }
                
        except Exception as e:
            print(Color.BLUE.value + f"❌ Erro durante verificação da prova zk-SNARK: {e}")
            return {
                'authenticated': False,
                'reason': f'Erro na verificação: {str(e)}'
            }
    
    def escrever_arquivo_json(self, caminho_arquivo, conteudo):
        """Escreve conteúdo em arquivo JSON"""
        try:
            with open(caminho_arquivo, 'w') as arquivo:
                json.dump(conteudo, arquivo, indent=2)
            print(Color.BLUE.value + f" Arquivo salvo: {caminho_arquivo}")
        except Exception as e:
            print(Color.BLUE.value + f"❌ Erro ao escrever arquivo {caminho_arquivo}: {e}")
            raise e
    
    def enviar_resposta(self, endereco_retorno, mensagem):
        """Envia resposta de volta para o serviço solicitante"""
        try:
            # Divide endereço de retorno em host e porta
            host, porta = endereco_retorno.split(':')
            porta = int(porta)
            
            # Envia mensagem
            sucesso = self.enviar_mensagem(host, porta, mensagem)
            
            if sucesso:
                print(Color.BLUE.value + f" Resposta enviada para {endereco_retorno}")
            else:
                print(Color.BLUE.value + f"❌ Falha ao enviar resposta para {endereco_retorno}")
                
            return sucesso
            
        except Exception as e:
            print(Color.BLUE.value + f"❌ Erro ao processar endereço de retorno: {e}")
            return False
    
    def enviar_mensagem(self, host, porta, mensagem):
        """Envia mensagem JSON para outros serviços via TCP"""
        try:
            mensagem_json = json.dumps(mensagem)
            tamanho_mensagem = len(mensagem_json.encode())
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, porta))
                s.send(mensagem_json.encode())
                
            print(Color.BLUE.value + f" Mensagem enviada para {host}:{porta} - Tamanho: {tamanho_mensagem} bytes")
            return True
            
        except ConnectionRefusedError:
            print(Color.BLUE.value + f"❌ Conexão recusada para {host}:{porta}")
            return False
        except Exception as e:
            print(Color.BLUE.value + f"❌ Erro ao enviar mensagem: {e}")
            return False
