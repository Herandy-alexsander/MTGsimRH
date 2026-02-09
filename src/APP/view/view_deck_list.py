import pygame
from APP.utils.base import ViewComponent
from APP.utils.ui_components import MenuButton
from APP.utils.style import GameStyle

class DeckListView(ViewComponent):
    def __init__(self, screen, controller, storage):
        super().__init__(screen, controller)
        self.storage = storage
        self.largura, self.altura = self.screen.get_size()
        self.fontes = GameStyle.get_fonts()
        
        # Estado da Lista
        self.decks = []
        self.indice_selecionado = 0
        self.carregar_lista_decks()

        # Botões de Navegação
        cx = self.largura // 2
        self.btn_voltar = MenuButton(pygame.Rect(20, 20, 100, 40), "VOLTAR", self.fontes['label'])
        self.btn_jogar = MenuButton(pygame.Rect(cx - 150, 650, 300, 50), "SELECIONAR DECK", self.fontes['menu'])

    def carregar_lista_decks(self):
        """Busca os decks registrados no profiler.json."""
        perfil = self.storage.carregar_perfil()
        self.decks = perfil.get('decks_info', {}).get('decks', [])

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        self.btn_voltar.update(mouse_pos)
        
        if self.decks:
            self.btn_jogar.update(mouse_pos)

        for event in events:
            if event.type == pygame.QUIT:
                return "QUIT"
            
            if self.btn_voltar.is_clicked(event):
                return "MENU"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.indice_selecionado = (self.indice_selecionado - 1) % len(self.decks)
                if event.key == pygame.K_DOWN:
                    self.indice_selecionado = (self.indice_selecionado + 1) % len(self.decks)

            if self.decks and self.btn_jogar.is_clicked(event):
                # Define o deck ativo no controlador antes de iniciar o jogo
                deck_escolhido = self.decks[self.indice_selecionado]
                self.controller.selecionar_deck(deck_escolhido['id'])
                return "JOGO"
        return None

    def draw(self):
        self.screen.fill(GameStyle.COLOR_BG)
        cx = self.largura // 2

        # Título
        txt_t = self.fontes['titulo'].render("MEUS DECKS", True, GameStyle.COLOR_ACCENT)
        self.screen.blit(txt_t, (cx - txt_t.get_width() // 2, 50))

        # Área da Lista
        rect_lista = pygame.Rect(cx - 300, 150, 600, 450)
        pygame.draw.rect(self.screen, (30, 30, 35), rect_lista, border_radius=10)
        pygame.draw.rect(self.screen, (60, 60, 65), rect_lista, 2, border_radius=10)

        if not self.decks:
            msg = self.fontes['menu'].render("Nenhum deck cadastrado.", True, (150, 150, 150))
            self.screen.blit(msg, (cx - msg.get_width() // 2, 350))
        else:
            for i, deck in enumerate(self.decks):
                # Configuração visual do item da lista
                y_pos = 170 + (i * 50)
                cor_item = GameStyle.COLOR_ACCENT if i == self.indice_selecionado else (200, 200, 200)
                
                # Indicador de Seleção
                if i == self.indice_selecionado:
                    pygame.draw.rect(self.screen, (50, 50, 60), (cx - 280, y_pos - 5, 560, 40), border_radius=5)
                
                txt_deck = self.fontes['menu'].render(f"{deck['name']}", True, cor_item)
                self.screen.blit(txt_deck, (cx - 270, y_pos))

        self.btn_voltar.draw(self.screen)
        if self.decks:
            self.btn_jogar.draw(self.screen)