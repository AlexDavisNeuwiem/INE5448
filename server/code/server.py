import time
import json
import socket
import threading
import subprocess
import base64

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

        # Compila o circuito e gera as chaves de prova e de verificação
        self.executar_trusted_setup()
        
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
            
            # Cria tabela para armazenar arquivos do trusted setup
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trusted_setup_files (
                    id SERIAL PRIMARY KEY,
                    file_type VARCHAR(50) NOT NULL UNIQUE,
                    file_content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

    def executar_trusted_setup(self):
        """Executa o script que realiza o trusted setup"""
        print(Color.BLUE.value + " Executando trusted setup...")
        
        resultado = subprocess.run(
            SnarkPath.TRUSTED_SETUP_SCRIPT.value, 
            capture_output=True, 
            text=True,
            shell=True
        )

        print(Color.BLUE.value + f" Trusted Setup realizado - Código de retorno: {resultado.returncode}")
            
        # Analisa resultado da verificação
        if resultado.returncode == 0:
            print(Color.BLUE.value + " ✅ Trusted Setup realizado com sucesso")
            
            # Armazena os arquivos gerados no banco de dados
            self.armazenar_arquivos_trusted_setup()
            
        else:
            print(Color.BLUE.value + "❌ Trusted Setup falhou")
            if resultado.stdout:
                print("\n" + Color.BLUE.value + f" Saída do script: {resultado.stdout}")
            if resultado.stderr:
                print(Color.BLUE.value + f" Erro do script: {resultado.stderr}")
                
            raise Exception("Falha no trusted setup - não é possível continuar")

    def armazenar_arquivos_trusted_setup(self):
        """Armazena os arquivos do trusted setup no banco de dados"""
        try:
            print(Color.BLUE.value + " Armazenando arquivos do trusted setup no banco de dados...")
            
            conn = psycopg2.connect(**self.config_banco)
            cursor = conn.cursor()
            
            # Lista de arquivos para armazenar
            arquivos = [
                ('verification_key', SnarkPath.VERIFICATION_KEY_OUTPUT.value),
                ('proving_key', SnarkPath.PROVING_KEY.value),
                ('circuit', SnarkPath.CIRCUIT.value)
            ]
            
            for tipo_arquivo, caminho_arquivo in arquivos:
                print(Color.BLUE.value + f" Lendo arquivo: {caminho_arquivo}")
                
                try:
                    # Lê o conteúdo do arquivo
                    if caminho_arquivo.endswith('.wasm') or caminho_arquivo.endswith('.zkey'):
                        # Para arquivos binários (.wasm), codifica em base64
                        with open(caminho_arquivo, 'rb') as arquivo:
                            conteudo_binario = arquivo.read()
                            conteudo = base64.b64encode(conteudo_binario).decode('utf-8')
                    else:
                        # Para arquivos JSON, lê como texto
                        with open(caminho_arquivo, 'r') as arquivo:
                            conteudo = arquivo.read()
                    
                    # Insere ou atualiza o arquivo no banco
                    cursor.execute("""
                        INSERT INTO trusted_setup_files (file_type, file_content)
                        VALUES (%s, %s)
                        ON CONFLICT (file_type) 
                        DO UPDATE SET 
                            file_content = EXCLUDED.file_content,
                            updated_at = CURRENT_TIMESTAMP
                    """, (tipo_arquivo, conteudo))
                    
                    print(Color.BLUE.value + f" ✅ Arquivo {tipo_arquivo} armazenado com sucesso")
                    
                except FileNotFoundError:
                    print(Color.BLUE.value + f"❌ Arquivo não encontrado: {caminho_arquivo}")
                    raise
                except Exception as e:
                    print(Color.BLUE.value + f"❌ Erro ao processar arquivo {caminho_arquivo}: {e}")
                    raise
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(Color.BLUE.value + " ✅ Todos os arquivos do trusted setup foram armazenados")
            
        except Exception as e:
            print(Color.BLUE.value + f"❌ Erro ao armazenar arquivos do trusted setup: {e}")
            raise

    def recuperar_arquivo_trusted_setup(self, tipo_arquivo):
        """Recupera um arquivo do trusted setup do banco de dados"""
        try:
            conn = psycopg2.connect(**self.config_banco)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT file_content FROM trusted_setup_files
                WHERE file_type = %s
            """, (tipo_arquivo,))
            
            resultado = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if resultado:
                return resultado[0]
            else:
                print(Color.BLUE.value + f"❌ Arquivo {tipo_arquivo} não encontrado no banco")
                return None
                
        except Exception as e:
            print(Color.BLUE.value + f"❌ Erro ao recuperar arquivo {tipo_arquivo}: {e}")
            return None

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
            
            # Recupera arquivos do trusted setup
            print(Color.BLUE.value + " Recuperando arquivos do trusted setup...")
            proving_key = self.recuperar_arquivo_trusted_setup('proving_key')
            circuit = self.recuperar_arquivo_trusted_setup('circuit')
            
            if proving_key and circuit:
                print(Color.BLUE.value + " Arquivos do trusted setup recuperados com sucesso")
                print("=" * 60)
                print(Color.BLUE.value + " FASE DE RECUPERAÇÃO CONCLUÍDA")
                print("=" * 60 + "\n")
                
                # Envia embedding criptografada junto com os arquivos do trusted setup
                self.enviar_resposta(endereco_retorno, {
                    'type': 'snark_ingredients',
                    'data': {
                        'embedding': embedding_criptografada,
                        'proving_key': proving_key,
                        'circuit': circuit
                    }
                })
            else:
                print(Color.BLUE.value + "❌ Falha ao recuperar arquivos do trusted setup")
                print("=" * 60)
                print(Color.BLUE.value + " FASE DE RECUPERAÇÃO FALHOU")
                print("=" * 60)
                
                # Envia erro de volta para o usuário
                self.enviar_resposta(endereco_retorno, {
                    'type': 'authentication_result',
                    'data': {
                        'authenticated': False,
                        'reason': 'Falha ao recuperar arquivos do trusted setup'
                    }
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
    
    def verificar_prova_snark(self, prova, parametros_publicos):
        """Verifica a validade da prova zk-SNARK recebida"""
        try:
            print(Color.BLUE.value + " Iniciando processo de verificação da prova zk-SNARK...")

            print(Color.BLUE.value + " Salvando arquivos da prova zk-SNARK...")
            
            # Salva os dados da prova em arquivos JSON para verificação
            self.escrever_arquivo_json(SnarkPath.PROOF.value, prova)
            self.escrever_arquivo_json(SnarkPath.PUBLIC_PARAMETERS.value, parametros_publicos)
            
            # Recupera e salva a chave de verificação do banco
            verification_key = self.recuperar_arquivo_trusted_setup('verification_key')
            if verification_key:
                with open(SnarkPath.VERIFICATION_KEY_INPUT.value, 'w') as f:
                    f.write(verification_key)
                print(Color.BLUE.value + " Chave de verificação restaurada do banco")
            else:
                raise Exception("Chave de verificação não encontrada no banco")

            print(Color.BLUE.value + " Executando script de verificação zk-SNARK...")
            
            # Executa o script de verificação SNARK
            resultado = subprocess.run(
                SnarkPath.VERIFY_PROOF_SCRIPT.value, 
                capture_output=True, 
                text=True,
                shell=True
            )
            
            print(Color.BLUE.value + f" Prova verificada - Código de retorno: {resultado.returncode}")
            
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
