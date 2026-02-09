import pygame
import sys
import os

# 1. Ajuste de Path para garantir que a pasta APP seja encontrada
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 2. Importações corrigidas: Importamos o ViewManager em vez de uma View individual
from APP.utils.setup import inicializar_sistema
from APP.core.storage import MTGStorageManager
from APP.controller.Controller_Deck import DeckController
from APP.view.view_manager import ViewManager

def main():
    # PASSO ESSENCIAL: Cria a estrutura de pastas na raiz (data/, assets/cards/, etc.)
    inicializar_sistema() 

    # Inicialização do Pygame
    pygame.init()
    
    # Definindo dimensões da janela conforme o padrão do projeto
    screen = pygame.display.set_mode((1024, 768)) 
    pygame.display.set_caption("MTG Commander Simulator - RH")

    # 3. Inicialização dos componentes de dados
    # O storage gerencia arquivos físicos e o perfil do usuário
    storage = MTGStorageManager(base_path="data")
    
    # O DeckController gerencia a lógica das cartas carregadas
    controller = DeckController(profiler_path="data/profiler.json") 

    # 4. Gerenciador de Interface (ViewManager)
    # Ele recebe os 3 argumentos corretamente e inicia o estado WELCOME ou MENU
    manager = ViewManager(screen, controller, storage)

    print("Iniciando Gerenciador Commander...")
    
    try:
        # Inicia o loop principal coordenado pelo ViewManager
        manager.run() 
    except Exception as e:
        print(f"Erro crítico na execução: {e}")
        import traceback
        traceback.print_exc() 
    finally:
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    main()