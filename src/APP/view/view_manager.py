import pygame
from mtg_commander_app.view.view_menu import MainMenu
from mtg_commander_app.view.view_register import RegisterDeckView 
from mtg_commander_app.view.view_match import MatchView
from mtg_commander_app.view.view_welcome import WelcomeView
from mtg_commander_app.controller.match_controller import MatchController
from mtg_commander_app.models.match_model import MatchModel

class ViewManager:
    def __init__(self, screen, controller, storage):
        """
        Gerencia a transição entre telas e o ciclo de vida do simulador.
        """
        self.screen = screen
        self.controller = controller  # DeckController principal
        self.storage = storage        # MTGStorageManager
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Inicializa o controlador de partida com seu modelo de dados
        match_model = MatchModel()
        self.match_controller = MatchController(match_model)
        
        # Mapeamento de todas as Views do projeto
        self.views = {
            "WELCOME": WelcomeView(self.screen, self.controller, self.storage),
            "MENU": MainMenu(self.screen, self.storage),
            "CADASTRAR": RegisterDeckView(self.screen, self.controller, self.storage),
            "JOGO": MatchView(self.screen, self.match_controller) 
        }
        
        # --- LÓGICA DE INICIALIZAÇÃO ---
        # Verifica se o profiler.json já contém um nickname registrado
        if not self.storage.verificar_perfil_existente():
            self.state = "WELCOME"
        else:
            self.state = "MENU"

    def run(self):
        """Loop principal de gestão de eventos e renderização."""
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                
                # Atalho ESC: Voltar ao menu (bloqueado na tela Welcome)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.state != "WELCOME":
                        self.state = "MENU"

            current_view = self.views.get(self.state)
            
            if self.state == "MENU":
                # O Menu retorna ações baseadas nos cliques dos botões
                action = current_view.handle_event(events, has_deck=self.controller.has_deck())
                
                if action == "ABRIR SALA":
                    # Configura a partida com o número de jogadores selecionado
                    self.match_controller.total_players = current_view.total_jogadores
                    self.state = "JOGO"
                elif action == "CADASTRAR":
                    self.state = "CADASTRAR"
                elif action == "SAIR":
                    self.running = False
                    
            elif current_view:
                # Processa lógica específica de cada tela (Welcome, Cadastro ou Jogo)
                res = current_view.handle_events(events)
                if res:
                    self.state = res
                    # Se houve transição para o Menu, atualiza dados do controlador
                    if res == "MENU":
                        self.controller.reload_data()
                        # Garante que o nickname no menu esteja atualizado
                        if hasattr(self.views["MENU"], "atualizar_nickname"):
                            self.views["MENU"].atualizar_nickname()

            self.draw()
            self.clock.tick(60)

    def draw(self):
        """Renderiza a interface gráfica da tela ativa."""
        self.screen.fill((20, 20, 25)) # Fundo base escuro

        if self.state == "MENU":
            # O Menu recebe o status de existência de deck para avisos
            self.views["MENU"].draw(has_deck=self.controller.has_deck())
        elif self.state in self.views:
            self.views[self.state].draw()

        pygame.display.flip()