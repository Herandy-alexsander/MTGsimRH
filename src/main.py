import pygame
from mtg_commander_app.controller.Controller_Deck import DeckController
from mtg_commander_app.core.storage import MTGStorageManager
from mtg_commander_app.view.view_manager import ViewManager
from mtg_commander_app.utils.setup import inicializar_sistema # Importe o script de ambiente

def main():
    # 1. PASSO ESSENCIAL: Cria as pastas data/decks, data/cards, etc.
    inicializar_sistema() 

    pygame.init()
    screen = pygame.display.set_mode((1024, 768)) 
    pygame.display.set_caption("MTG Commander Simulator - RH")

    # 2. ATUALIZAÇÃO: O storage agora recebe apenas o caminho base (data)
    # O DeckController deve apontar para o profiler.json para verificar decks
    controller = DeckController(json_path="data/profiler.json") 
    storage = MTGStorageManager(base_path="data")

    manager = ViewManager(screen, controller, storage)

    print("Iniciando Gerenciador Commander...")
    manager.run()

    pygame.quit()

if __name__ == '__main__':
    main()