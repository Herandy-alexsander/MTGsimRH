import pygame
import sys
import os

# Adiciona o diretório src ao path para garantir que as importações funcionem
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importações dos Módulos Principais
from APP.core.storage import MTGStorageManager
from APP.models.deck_model import DeckModel
from APP.controller.Controller_Deck import DeckController
from APP.view.view_manager import ViewManager

def main():
    # 1. Configuração Inicial do Pygame
    pygame.init()
    
    # Aumentei para 1280x720 para acomodar melhor a Grade 6x2 e o campo de batalha
    WIDTH, HEIGHT = 1280, 720 
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("MTG Commander Simulator - RH")
    
    # 2. Inicializa o Storage (Gerenciador de Arquivos e Downloads)
    # Ele cria automaticamente as pastas 'data/' e 'assets/' se não existirem.
    storage = MTGStorageManager(base_path="data")

    # 3. Inicializa o Modelo de Dados (Onde ficam as cartas do deck carregado)
    deck_model = DeckModel()

    # 4. Inicializa o Controlador Principal (CORREÇÃO DO ERRO)
    # Agora passamos os OBJETOS 'deck_model' e 'storage' diretamente.
    # O erro anterior ocorria porque estávamos passando "profiler_path" (string).
    controller = DeckController(deck_model, storage)

    # 5. Inicializa o Gerenciador de Telas (ViewManager)
    # Ele recebe a tela, o controlador de decks e o storage para coordenar o fluxo
    manager = ViewManager(screen, controller, storage)

    # 6. Loop Principal
    print("Iniciando Gerenciador Commander...")
    try:
        manager.run()
    except KeyboardInterrupt:
        print("Encerrando via teclado...")
    except Exception as e:
        print(f"Erro crítico na execução: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()