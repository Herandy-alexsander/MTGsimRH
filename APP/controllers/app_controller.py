from APP.core.engine import Engine
from APP.core.screen_manager import ScreenManager

# --- Controladores e Infraestrutura ---
from APP.controllers.profile_controller import ProfileController
from APP.controllers.deck_controller import DeckController
from APP.controllers.deck_register_controller import DeckRegisterController 
from APP.controllers.match_controller import MatchController
from APP.controllers.game_ui_manager import GameUIManager 

from APP.infrastructure.storage.deck_repository import DeckRepository
from APP.infrastructure.services.scryfall_service import ScryfallService
from APP.infrastructure.services.image_downloader import ImageDownloader
from APP.infrastructure.services.asset_manager import AssetManager
from APP.domain.models.deck_model import DeckModel

# --- Importação das Telas (Views) ---
from APP.UI.screens.welcome_ui import WelcomeView
from APP.UI.screens.main_menu_ui import MainMenu
from APP.UI.screens.deck_manager_ui import DeckManagerView
from APP.UI.screens.deck_register_ui import DeckRegisterView
from APP.UI.screens.match_ui import MatchView

class AppController:
    def __init__(self, profile_repo):
        """
        Maestro Central: Gerencia a conexão entre os dados, controladores e a tela.
        """
        self.profile_repo = profile_repo
        
        # 1. LIGA O MOTOR (Core)
        self.engine = Engine()
        self.screen_manager = ScreenManager()

        # 2. Injeção de dependências (Serviços e Repositórios)
        self.deck_repo = DeckRepository()
        self.scryfall = ScryfallService()
        self.downloader = ImageDownloader()
        self.asset_manager = AssetManager()
        self.deck_model = DeckModel()

        # 3. Inicialização dos Sub-Controladores
        self.profile_ctrl = ProfileController(self.profile_repo)
        
        self.deck_ctrl = DeckController(
            self.deck_model, self.deck_repo, self.profile_repo, 
            self.scryfall, self.downloader
        )
        
        self.deck_register_ctrl = DeckRegisterController(
            self.scryfall, self.deck_repo, self.profile_repo, self.downloader
        )
        
        # O controlador de partida começa vazio e é criado apenas no GAME_START
        self.match_ctrl = None

        # 4. Define a tela de entrada
        self._definir_tela_inicial()

    def _definir_tela_inicial(self):
        """Verifica se é o primeiro acesso para mostrar a WelcomeView ou o Menu."""
        if not self.profile_ctrl.verificar_primeiro_acesso():
            tela = WelcomeView(self.engine.screen, self, self.profile_ctrl)
        else:
            # CORREÇÃO: Enviando o deck_ctrl para o MainMenu saber qual deck está ativo
            tela = MainMenu(self.engine.screen, self.profile_ctrl, self.deck_ctrl)
        self.screen_manager.set_screen(tela)

    def run(self):
        """Inicia o loop principal do jogo."""
        self.engine.run(self.screen_manager, self._handle_transitions)

    def _handle_transitions(self, action):
        """
        O Câmbio do jogo: Gerencia a troca de telas baseada nas ações do usuário.
        """
        # 1. MENU PRINCIPAL
        if action == "MENU":
            # Limpa cache de partida ao voltar ao menu para liberar RAM
            if self.match_ctrl:
                self.asset_manager.limpar_cache()
            
            # CORREÇÃO: Enviando o deck_ctrl aqui também na transição de volta
            self.screen_manager.set_screen(MainMenu(self.engine.screen, self.profile_ctrl, self.deck_ctrl))
        
        # 2. GALERIA DE DECKS (Gerenciador)
        elif action in ["DECK_MANAGER", "REGISTER_SUCCESS"]:
            self.deck_ctrl.reload_data()
            self.screen_manager.set_screen(DeckManagerView(self.engine.screen, self, self.deck_ctrl))

        # 3. CADASTRO DE NOVOS DECKS
        elif action == "DECK_REGISTER":
            self.deck_register_ctrl.limpar_dados()
            self.screen_manager.set_screen(DeckRegisterView(self.engine.screen, self, self.deck_register_ctrl))

        # 4. INÍCIO DA PARTIDA (Onde a mágica acontece)
        elif action == "GAME_START":
            deck_info = self.deck_ctrl.get_deck_atual()
            
            if deck_info:
                # Carrega os dados reais do JSON salvos no HD
                dados_deck = self.deck_repo.carregar_deck_completo(deck_info['name'])
                
                if dados_deck:
                    nickname = self.profile_ctrl.obter_nickname()
                    
                    # --- MONTAGEM DA PARTIDA ---
                    # 1. Cria o GameUIManager (Diretor de Cena) para gerenciar as ZoneUI e CardUI
                    ui_manager = GameUIManager(self.asset_manager)
                    
                    # 2. Injeta o ui_manager no MatchController (Árbitro)
                    self.match_ctrl = MatchController(ui_manager)
                    
                    # 3. Prepara os dados (Grimório, Mão, Vida)
                    self.match_ctrl.setup_game(dados_deck, nickname)
                    
                    # 4. Transição para a tela de Partida (MatchView)
                    print(f"[APP] Partida iniciada com sucesso: {deck_info['name']}")
                    self.screen_manager.set_screen(MatchView(self.engine.screen, self.match_ctrl, self.asset_manager))
                else:
                    print(f"[ERRO] Falha crítica: O arquivo do deck '{deck_info['name']}' não foi achado.")
            else:
                # CORREÇÃO: Força o bloqueio de segurança voltando pra galeria
                print("[AVISO] Seleção de deck obrigatória!")
                self._handle_transitions("DECK_MANAGER")

        # 5. FINALIZAR APLICAÇÃO
        elif action in ["QUIT", "SAIR"]:
            self.engine.running = False