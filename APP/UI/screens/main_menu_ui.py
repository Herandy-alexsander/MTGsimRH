import pygame
from APP.UI.styles import colors, settings
from APP.UI.styles.fonts import get_fonts
from APP.UI.components.button import MenuButton
from APP.UI.components.label import Label
from APP.UI.components.popup import Popup

class MainMenu:
    def __init__(self, screen, profile_controller):
        """
        Interface principal do simulador.
        :param profile_controller: Instância de ProfileController para gerenciar o Conjurador.
        """
        self.screen = screen
        self.controller = profile_controller
        self.largura, self.altura = settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT
        
        # 1. Recursos e Estilo
        self.fontes = get_fonts()
        self.mostrar_aviso = False
        
        # 2. Estado do Jogador
        nickname_inicial = self.controller.obter_nickname()
        
        # 3. Componentes de UI
        cx = self.largura // 2
        
        # Títulos e Identificação
        self.label_titulo = Label("MTG SIMULATOR", (cx, 80), self.fontes['titulo'], colors.ACCENT)
        self.label_prefixo = Label("CONJURADOR:", (cx, 180), self.fontes['label'], (150, 150, 150))
        
        # Exibição fixa do Nickname (Upper para estilo)
        self.label_nickname = Label(nickname_inicial.upper(), (cx, 220), self.fontes['menu'], colors.ACCENT)
        
        # Botões de Seleção de Jogadores
        self.total_jogadores = 4
        self.btns_jogadores = {}
        for i, num in enumerate([2, 3, 4]):
            rect = pygame.Rect(cx - 110 + (i * 75), 340, 60, 45)
            self.btns_jogadores[num] = MenuButton(rect, str(num), self.fontes['menu'])

        # Botões de Ação Principal
        self.btn_abrir_sala = MenuButton(pygame.Rect(cx - 150, 430, 300, 50), "ABRIR SALA", self.fontes['menu'])
        self.btn_meus_decks = MenuButton(pygame.Rect(cx - 150, 500, 300, 50), "MEUS DECKS", self.fontes['menu'])
        self.btn_sair = MenuButton(pygame.Rect(cx - 150, 620, 300, 50), "SAIR", self.fontes['menu'])
        
        self.popup_deck = None

    def handle_events(self, events):
        """Processa eventos e transições do menu principal."""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in events:
            # Se o popup estiver ativo, ele consome os eventos
            if self.mostrar_aviso and self.popup_deck:
                if self.popup_deck.handle_event(event):
                    self.mostrar_aviso = False
                continue
            
            # Cliques nos Botões
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Seleção de Jogadores
                for num, btn in self.btns_jogadores.items():
                    if btn.is_clicked(event):
                        self.total_jogadores = num
                
                # Ações Principais
                if self.btn_abrir_sala.is_clicked(event):
                    # Verifica se o conjurador tem decks cadastrados
                    estatisticas = self.controller.obter_estatisticas()
                    if estatisticas['total_decks'] == 0:
                        self.popup_deck = Popup("⚠️ SEM DECK", "Cadastre um deck primeiro.", self.fontes)
                        self.mostrar_aviso = True
                    else:
                        return "MATCH"

                if self.btn_meus_decks.is_clicked(event):
                    return "DECK_MANAGER"

                if self.btn_sair.is_clicked(event):
                    return "QUIT"
        
        # Atualiza hover dos botões
        self._update_hovers(mouse_pos)
        return None

    def _update_hovers(self, mouse_pos):
        self.btn_abrir_sala.update(mouse_pos)
        self.btn_meus_decks.update(mouse_pos)
        self.btn_sair.update(mouse_pos)
        for btn in self.btns_jogadores.values():
            btn.update(mouse_pos)
        if self.mostrar_aviso:
            self.popup_deck.update(mouse_pos)

    def draw(self):
        """Desenha a interface do Menu Principal."""
        self.screen.fill(colors.BG)
        
        # Desenha as Labels (Textos fixos)
        self.label_titulo.draw(self.screen)
        self.label_prefixo.draw(self.screen)
        self.label_nickname.draw(self.screen)
        
        # Destaque visual da quantidade de jogadores selecionada
        for num, btn in self.btns_jogadores.items():
            if self.total_jogadores == num:
                pygame.draw.rect(self.screen, colors.ACCENT, btn.rect.inflate(6, 6), 2, border_radius=8)
            btn.draw(self.screen)
            
        # Botões de Ação
        self.btn_abrir_sala.draw(self.screen)
        self.btn_meus_decks.draw(self.screen)
        self.btn_sair.draw(self.screen)
        
        # Popup por cima de tudo
        if self.mostrar_aviso and self.popup_deck:
            self.popup_deck.draw(self.screen)