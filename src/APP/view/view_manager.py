import pygame
from APP.view.view_menu import MainMenu
from APP.view.view_register_progress import RegisterProgressView 
from APP.view.view_deck_management import RegisterDeckView
from APP.view.view_deck_list import DeckListView 
from APP.view.view_match import MatchView
from APP.view.view_welcome import WelcomeView
from APP.controller.match_controller import MatchController
from APP.models.match_model import MatchModel

class ViewManager:
    def __init__(self, screen, controller, storage):
        """
        Gerencia a transição entre telas e o ciclo de vida do simulador.
        """
        self.screen = screen
        self.controller = controller  # DeckController (Gerencia coleção)
        self.storage = storage        # MTGStorageManager (Gerencia arquivos)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Inicializa o controlador de partida com seu modelo de dados
        match_model = MatchModel()
        self.match_controller = MatchController(match_model)
        
        # --- Mapeamento Inicial das Views ---
        self.views = {
            "WELCOME": WelcomeView(self.screen, self.controller, self.storage),
            "MENU": MainMenu(self.screen, self.storage),
            "CADASTRAR": RegisterDeckView(self.screen, self.controller, self.storage),
            "LISTA_DECKS": DeckListView(self.screen, self.controller, self.storage), 
            "JOGO": MatchView(self.screen, self.match_controller) 
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
                
                # Atalho ESC: Voltar ao menu (bloqueado em telas críticas)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.state not in ["WELCOME", "PROGRESSO", "JOGO"]:
                        self.state = "MENU"

            current_view = self.views.get(self.state)
            if not current_view: continue

            # --- LÓGICA ESPECÍFICA DO MENU ---
            if self.state == "MENU":
                action = current_view.handle_event(events, has_deck=self.controller.has_deck())
                
                if action == "ABRIR SALA":
                    # 1. Configura número de jogadores selecionado no Menu
                    self.match_controller.total_players = current_view.total_jogadores
                    # 2. Ativa o modo de seleção na galeria para liberar o botão JOGAR
                    self.views["LISTA_DECKS"].modo_selecao = True
                    self._ir_para_lista_decks()
                
                elif action == "MEUS DECKS":
                    # 1. Desativa modo seleção: apenas observação segura
                    self.views["LISTA_DECKS"].modo_selecao = False
                    self._ir_para_lista_decks()

                elif action == "CADASTRAR":
                    self.state = "CADASTRAR"
                
                elif action == "SAIR":
                    self.running = False
            
            # --- LÓGICA DE TRANSIÇÃO GENÉRICA ---
            else:
                res = current_view.handle_events(events)

                # Tratamento para início da partida configurada
                if self.state == "LISTA_DECKS" and res == "JOGO":
                    self._iniciar_partida_configurada()

                # Tratamento para Cadastro de Deck
                elif isinstance(res, dict) and res.get("acao") == "INICIAR_PROCESSO":
                    self.iniciar_cadastro_com_progresso(res)
                
                # Tratamento para Navegação Simples (Strings)
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
        """
        Coleta dados finais e injeta no MatchController para iniciar o jogo.
        """
        # 1. Pega as cartas do deck que o DeckController carregou da galeria
        deck_cartas = self.controller.model.cards
        
        # 2. Pega o NOME DO COMANDANTE que foi carregado no DeckController
        # Isso corrige o erro AttributeError na MatchView
        commander_name = self.controller.model.commander 
        
        # 3. Pega o apelido do jogador para o HUD
        nickname = self.storage.carregar_perfil()["player_info"].get("nickname", "Conjurador")
        
        # 4. Inicializa o controlador da partida PASSANDO O COMANDANTE
        self.match_controller.setup_game(deck_cartas, commander_name, nickname)
        
        # 5. Muda para a tela de partida real
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