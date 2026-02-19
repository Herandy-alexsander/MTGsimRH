# APP/core/engine.py
import pygame
import sys
from APP.core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GAME_TITLE

class Engine:
    def __init__(self):
        """Inicializa a janela do sistema operacional e o relógio."""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self, screen_manager, transition_handler):
        """
        O Loop Principal do Jogo.
        :param screen_manager: Sabe qual tela desenhar.
        :param transition_handler: Função do AppController que decide para onde ir se a tela pedir.
        """
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            # 1. Pega os cliques e manda para a tela atual
            action = screen_manager.handle_events(events)
            
            # 2. Se a tela retornou um comando (ex: "MENU", "GAME_START", "SAIR")
            if action:
                if action in ["QUIT", "SAIR"]:
                    self.running = False
                else:
                    # Avisa o Maestro (AppController) para fazer a mágica dele
                    transition_handler(action)

            # 3. Manda a tela atual desenhar os gráficos
            screen_manager.draw()
            
            # 4. Atualiza o monitor
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()