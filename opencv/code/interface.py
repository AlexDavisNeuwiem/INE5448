import os
from fingerprint_recognizer import FingerprintRecognizer

# Interface por terminal (entrada única)
def run():
    print("\n=================================================")
    print("  SISTEMA DE RECONHECIMENTO DE DIGITAL - OPENCV")
    print("=================================================\n")
    
    print("Inicializando sistema...")
    
    try:
        # Criar reconhecedor de digital
        recognizer = FingerprintRecognizer()
        
        def clear_screen():
            """Limpa a tela do terminal"""
            os.system('cls' if os.name == 'nt' else 'clear')
        
        def print_menu():
            """Exibe o menu de opções"""
            clear_screen()
            print("\n===== SISTEMA DE RECONHECIMENTO DE DIGITAL =====")
            print("1. Adicionar pessoa")
            print("2. Verificar se digital pertence a pessoa")
            print("3. Reconhecer pessoa a qual a digital pertence")
            print("4. Listar pessoas cadastradas")
            print("5. Ajustar limiar de similaridade")
            print("0. Sair")
            print("===========================================")
        
        # Menu principal
        while True:
            print_menu()
            
            try:
                opcao = input("Escolha uma opção: ")
                
                if opcao == '0':
                    print("Encerrando programa...")
                    break
                    
                elif opcao == '1':
                    # Adicionar pessoa
                    clear_screen()
                    print("\n--- ADICIONAR PESSOA ---\n")
                    
                    nome = input("Nome da pessoa: ")
                    if not nome:
                        print("Erro: Nome não pode ser vazio")
                        input("\nPressione ENTER para continuar...")
                        continue
                        
                    caminho = input("Caminho para pasta com fotos ou arquivo único: ")
                    if not os.path.exists(caminho):
                        print(f"Erro: Caminho '{caminho}' não existe")
                        input("\nPressione ENTER para continuar...")
                        continue
                    
                    print(f"\nProcessando imagens para '{nome}'...")
                    success = recognizer.add_person(nome, caminho)
                    
                    if success:
                        print(f"Pessoa '{nome}' adicionada com sucesso!")
                    else:
                        print(f"Falha ao adicionar pessoa '{nome}'")
                
                elif opcao == '2':
                    # Verificar se digital pertence a pessoa
                    clear_screen()
                    print("\n--- VERIFICAR DIGITAL ---\n")
                    
                    if not recognizer.database:
                        print("Erro: Nenhuma pessoa cadastrada no sistema")
                        input("\nPressione ENTER para continuar...")
                        continue
                        
                    print("Pessoas cadastradas:")
                    for i, pessoa in enumerate(recognizer.database.keys(), 1):
                        print(f"{i}. {pessoa}")
                    
                    nome = input("\nNome da pessoa a verificar: ")
                    if nome not in recognizer.database:
                        print(f"Erro: Pessoa '{nome}' não está cadastrada")
                        input("\nPressione ENTER para continuar...")
                        continue
                        
                    imagem = input("Caminho para a imagem a ser verificada: ")
                    if not os.path.exists(imagem):
                        print(f"Erro: Arquivo '{imagem}' não existe")
                        input("\nPressione ENTER para continuar...")
                        continue
                    
                    print(f"\nVerificando se a imagem pertence a '{nome}'...")
                    pertence, similaridade = recognizer.verify(imagem, nome)
                    
                    print("\nRESULTADO:")
                    if pertence:
                        print(f"✓ A imagem PERTENCE a {nome} (similaridade: {similaridade:.4f})")
                    else:
                        print(f"✗ A imagem NÃO pertence a {nome} (similaridade: {similaridade:.4f})")
                        print(f"Limiar atual: {recognizer.similarity_threshold}")
                
                elif opcao == '3':
                    # Reconhecer pessoa
                    clear_screen()
                    print("\n--- RECONHECER PESSOA ---\n")
                    
                    if not recognizer.database:
                        print("Erro: Nenhuma pessoa cadastrada no sistema")
                        input("\nPressione ENTER para continuar...")
                        continue
                        
                    imagem = input("Caminho para a imagem a ser reconhecida: ")
                    if not os.path.exists(imagem):
                        print(f"Erro: Arquivo '{imagem}' não existe")
                        input("\nPressione ENTER para continuar...")
                        continue
                    
                    print(f"\nReconhecendo digital...")
                    pessoa_reconhecida, similaridade = recognizer.recognize(imagem)
                    
                    print("\nRESULTADO:")
                    if pessoa_reconhecida:
                        print(f"Pessoa reconhecida: {pessoa_reconhecida} (similaridade: {similaridade:.4f})")
                    else:
                        print(f"Nenhuma pessoa reconhecida (melhor similaridade: {similaridade:.4f})")
                        print(f"Limiar atual: {recognizer.similarity_threshold}")
                
                elif opcao == '4':
                    # Listar pessoas
                    clear_screen()
                    print("\n--- PESSOAS CADASTRADAS ---\n")
                    
                    if not recognizer.database:
                        print("Nenhuma pessoa cadastrada no sistema")
                    else:
                        print(f"Total de pessoas cadastradas: {len(recognizer.database)}")
                        print("-" * 30)
                        for i, pessoa in enumerate(recognizer.database.keys(), 1):
                            print(f"{i}. {pessoa}")
                
                elif opcao == '5':
                    # Ajustar limiar
                    clear_screen()
                    print("\n--- AJUSTAR LIMIAR DE SIMILARIDADE ---\n")
                    
                    print(f"Limiar atual: {recognizer.similarity_threshold}")
                    print("\nRecomendações:")
                    print("- Valores mais altos (ex: 0.8): maior precisão, menos falsos positivos")
                    print("- Valores mais baixos (ex: 0.6): maior sensibilidade, mais detecções")
                    
                    try:
                        novo_limiar = float(input("\nNovo valor do limiar (0.0 a 1.0): "))
                        if 0 <= novo_limiar <= 1:
                            recognizer.similarity_threshold = novo_limiar
                            print(f"Limiar ajustado para: {novo_limiar}")
                        else:
                            print("Erro: O limiar deve estar entre 0.0 e 1.0")
                    except ValueError:
                        print("Erro: Digite um número válido")
                
                else:
                    print("Opção inválida!")
                    
            except Exception as e:
                print(f"Erro: {e}")
                
            input("\nPressione ENTER para continuar...")
    
    except KeyboardInterrupt:
        print("\nPrograma interrompido pelo usuário.")
    except Exception as e:
        print(f"\nErro crítico: {e}")
    finally:
        print("\nEncerrando sistema de reconhecimento de digital...")
        print("Até logo!\n")
