import pygame
from APP.view.view_menu import MainMenu
from APP.view.view_register_progress import RegisterProgressView 
from APP.view.view_deck_management import RegisterDeckView
from APP.view.view_deck_list import DeckListView 
from APP.view.view_match import MatchView
from APP.view.view_welcome import WelcomeView
from APP.controller.match_controller import MatchController
from APP.models.match_model import MatchModel

# --- 1. IMPORTAÇÃO DO NOVO GERENCIADOR ---
from APP.utils.asset_manager import AssetManager

class ViewManager:
    def __init__(self, screen, controller, storage):
        """
        Gerencia a transição entre telas e o ciclo de vida do simulador.
        """
        self.screen = screen
        self.controller = controller  # DeckController
        self.storage = storage        # MTGStorageManager
        self.clock = pygame.time.Clock()
        self.running = True
        
        # --- 2. INICIALIZAÇÃO ÚNICA DO ASSET MANAGER ---
        # Todas as telas usarão este mesmo objeto para compartilhar o cache de RAM
        self.asset_manager = AssetManager(self.storage)
        
        # Inicializa o controlador de partida com seu modelo de dados
        match_model = MatchModel()
        self.match_controller = MatchController(match_model)
        
        # --- 3. MAPEAMENTO DAS VIEWS (COM INJEÇÃO DO ASSET MANAGER) ---
        self.views = {
            "WELCOME": WelcomeView(self.screen, self.controller, self.storage),
            "MENU": MainMenu(self.screen, self.storage),
            "CADASTRAR": RegisterDeckView(self.screen, self.controller, self.storage),
            
            # Passamos para a lista de decks para que ela mostre as miniaturas/previsões
            "LISTA_DECKS": DeckListView(self.screen, self.controller, self.storage, self.asset_manager), 
            
            # Passamos para a partida para renderizar o tabuleiro
            "JOGO": MatchView(self.screen, self.match_controller, self.asset_manager) 
        }
        
        # Verifica se já existe perfil para decidir a tela inicial
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
                
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.state not in ["WELCOME", "PROGRESSO", "JOGO"]:
                        self.state = "MENU"

            current_view = self.views.get(self.state)
            if not current_view: continue

            if self.state == "MENU":
                action = current_view.handle_event(events, has_deck=self.controller.has_deck())
                
                if action == "ABRIR SALA":
                    self.match_controller.total_players = current_view.total_jogadores
                    self.views["LISTA_DECKS"].modo_selecao = True
                    self._ir_para_lista_decks()
                
                elif action == "MEUS DECKS":
                    self.views["LISTA_DECKS"].modo_selecao = False
                    self._ir_para_lista_decks()

                elif action == "CADASTRAR":
                    self.state = "CADASTRAR"
                
                elif action == "SAIR":
                    self.running = False
            
            else:
                res = current_view.handle_events(events)

                if self.state == "LISTA_DECKS" and res == "JOGO":
                    self._iniciar_partida_configurada()

                elif isinstance(res, dict) and res.get("acao") == "INICIAR_PROCESSO":
                    self.iniciar_cadastro_com_progresso(res)
                
                elif isinstance(res, str):
                    self.state = res
                    
                    if res == "LISTA_DECKS":
                        self._ir_para_lista_decks()
                    
                    elif res == "MENU":
                        self.controller.reload_data()
                        if hasattr(self.views["MENU"], "atualizar_nickname"):
                            self.views["MENU"].atualizar_nickname()

            self.draw()
            self.clock.tick(60)

    def _ir_para_lista_decks(self):
        """Recarrega a lista do disco e muda de tela."""
        if hasattr(self.views["LISTA_DECKS"], 'recarregar_lista'):
            self.views["LISTA_DECKS"].recarregar_lista()
        self.state = "LISTA_DECKS"

    def _iniciar_partida_configurada(self):
        """Coleta dados finais e injeta no MatchController."""
        deck_cartas = self.controller.model.cards
        commander_name = self.controller.model.commander 
        nickname = self.storage.carregar_perfil()["player_info"].get("nickname", "Conjurador")
        
        # Limpa o cache de imagens ao iniciar um novo jogo para liberar RAM de decks antigos
        self.asset_manager.clear_unused_cache()
        
        self.match_controller.setup_game(deck_cartas, commander_name, nickname)
        self.state = "JOGO"

    def iniciar_cadastro_com_progresso(self, dados_deck):
        """Instancia a tela de progresso e inicia o download."""
        nome = dados_deck["nome"]
        path = dados_deck["path"]
        commander = dados_deck.get("commander", "")

        progress_view = RegisterProgressView(self.screen, self.storage, nome, path)
        self.state = "PROGRESSO"
        self.views["PROGRESSO"] = progress_view
        
        self.controller.model.commander = commander
        progress_view.iniciar_fluxo(self.controller.model)

    def draw(self):
        """Renderiza a interface gráfica da tela ativa."""
        self.screen.fill((15, 15, 18))

        if self.state == "MENU":
            self.views["MENU"].draw(has_deck=self.controller.has_deck())
        elif self.state in self.views:
            self.views[self.state].draw()

        pygame.display.flip()
