import pygame
from APP.view.view_menu import MainMenu
from APP.view.view_register_progress import RegisterProgressView 
from APP.view.view_deck_management import RegisterDeckView # Ajustado para bater com seu arquivo atual
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
        self.controller = controller  # DeckController principal
        self.storage = storage        # MTGStorageManager
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Inicializa o controlador de partida com seu modelo de dados
        match_model = MatchModel()
        self.match_controller = MatchController(match_model)
        
        # --- Mapeamento Inicial das Views ---
        self.views = {
            "WELCOME": WelcomeView(self.screen, self.controller, self.storage),
            "MENU": MainMenu(self.screen, self.storage),
            # Usando o nome da classe conforme seu último arquivo editado
            "CADASTRAR": RegisterDeckView(self.screen, self.controller, self.storage), 
            "JOGO": MatchView(self.screen, self.match_controller) 
        }
        
        # --- LÓGICA DE INICIALIZAÇÃO DE PERFIL ---
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
                
                # Atalho ESC: Voltar ao menu (bloqueado na Welcome e Progresso)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.state not in ["WELCOME", "PROGRESSO"]:
                        self.state = "MENU"

            current_view = self.views.get(self.state)
            if not current_view: continue

            # --- LÓGICA ESPECÍFICA DO MENU ---
            if self.state == "MENU":
                action = current_view.handle_event(events, has_deck=self.controller.has_deck())
                
                if action == "ABRIR SALA":
                    self.match_controller.total_players = current_view.total_jogadores
                    self.state = "JOGO"
                elif action == "CADASTRAR":
                    self.state = "CADASTRAR"
                elif action == "SAIR":
                    self.running = False
            
            # --- LÓGICA DE TRANSIÇÃO E CADASTRO ---
            else:
                res = current_view.handle_events(events)

                # Verifica se a RegisterDeckView enviou os dados para o download
                if isinstance(res, dict) and res.get("acao") == "INICIAR_PROCESSO":
                    # Passamos também o comandante selecionado para a próxima etapa
                    self.iniciar_cadastro_com_progresso(res)
                
                elif isinstance(res, str):
                    self.state = res
                    # Sincroniza dados ao retornar ao menu
                    if res == "MENU":
                        self.controller.reload_data()
                        if hasattr(self.views["MENU"], "atualizar_nickname"):
                            self.views["MENU"].atualizar_nickname()

            self.draw()
            self.clock.tick(60)

    def iniciar_cadastro_com_progresso(self, dados_deck):
        """
        Instancia a tela de progresso e inicia o download real (Fase 2).
        """
        # Extraímos os dados vindos do formulário
        nome = dados_deck["nome"]
        path = dados_deck["path"]
        commander = dados_deck.get("commander", "")

        # Criamos a view de progresso passando os dados
        progress_view = RegisterProgressView(self.screen, self.storage, nome, path)
        self.state = "PROGRESSO"
        self.views["PROGRESSO"] = progress_view
        
        # Antes de iniciar, definimos o comandante no modelo
        self.controller.model.commander = commander
        
        # Dispara o download real com a barra de progresso visível
        progress_view.iniciar_fluxo(self.controller.model)

    def draw(self):
        """Renderiza a interface gráfica da tela ativa."""
        self.screen.fill((15, 15, 18)) # Fundo ultra-dark premium

        if self.state == "MENU":
            self.views["MENU"].draw(has_deck=self.controller.has_deck())
        elif self.state in self.views:
            self.views[self.state].draw()

        pygame.display.flip()