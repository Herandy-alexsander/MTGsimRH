import pygame
from mtg_commander_app.utils.ui_components import MenuButton, UIComponents
from mtg_commander_app.utils.style import GameStyle

class MainMenu:
    def __init__(self, screen, storage):
        """
        Inicializa o menu principal com o novo botão de navegação para a lista de decks.
        """
        self.screen = screen
        self.storage = storage  
        self.largura, self.altura = self.screen.get_size()
        
        # Inicializa Estilos e Componentes de UI
        self.fontes = GameStyle.get_fonts()
        self.ui = UIComponents(self.largura, self.altura)
        
        # --- Estado Interno ---
        self.nickname = "Conjurador"
        self.total_jogadores = 2
        self.mostrar_aviso = False
        
        # Carrega o nome definido na WelcomeView
        self.atualizar_nickname()
        
        # --- Configuração do Pop-up de Aviso ---
        cx, cy = self.largura // 2, self.altura // 2
        self.popup_rect = pygame.Rect(cx - 225, cy - 100, 450, 200)
        self.btn_fechar_popup = MenuButton(
            pygame.Rect(cx - 75, cy + 30, 150, 45), 
            "FECHAR", 
            self.fontes['menu']
        )
        
        # --- Inicialização dos Botões de Seleção (Jogadores) ---
        self.btns_jogadores = {}
        for num, rect in self.ui.rects_jogadores.items():
            self.btns_jogadores[num] = MenuButton(rect, str(num), self.fontes['menu'])

        # --- NOVA LISTA DE BOTÕES DE AÇÃO ---
        # Adicionado o botão "MEUS DECKS" entre Abrir Sala e Cadastrar
        self.btns_acao = [
            MenuButton(self.ui.rect_criar, "ABRIR SALA", self.fontes['menu']),
            
            # Botão de navegação para ViewDeckList
            MenuButton(pygame.Rect(cx - 150, 510, 300, 50), "MEUS DECKS", self.fontes['menu']),
            
            MenuButton(self.ui.rect_cadastrar, "CADASTRAR", self.fontes['menu']),
            MenuButton(pygame.Rect(cx - 150, 650, 300, 50), "SAIR", self.fontes['menu'])
        ]

    def atualizar_nickname(self):
        """Busca os dados atualizados do profiler.json."""
        perfil = self.storage.carregar_perfil()
        if "player_info" in perfil:
            self.nickname = perfil["player_info"].get("nickname", "Conjurador")

    def handle_event(self, events, has_deck=False):
        """Gerencia interações e retorna a ação selecionada."""
        mouse_pos = pygame.mouse.get_pos()
        
        if self.mostrar_aviso:
            self.btn_fechar_popup.update(mouse_pos)

        for event in events:
            if self.mostrar_aviso:
                if self.btn_fechar_popup.is_clicked(event):
                    self.mostrar_aviso = False
                continue 

            # Botões de quantidade de jogadores
            for num, btn in self.btns_jogadores.items():
                btn.update(mouse_pos)
                if btn.is_clicked(event):
                    self.total_jogadores = num

            # Botões de ação principal
            for btn in self.btns_acao:
                btn.update(mouse_pos)
                if btn.is_clicked(event):
                    # Validação de segurança para abrir sala
                    if btn.text == "ABRIR SALA" and not has_deck:
                        self.mostrar_aviso = True
                        return None
                    return btn.text
        return None

    def draw(self, has_deck=False):
        """Renderiza o menu com o Nickname centralizado e a nova lista de botões."""
        self.screen.fill(GameStyle.COLOR_BG)
        cx = self.largura // 2
        
        # Título Principal
        txt_t = self.fontes['titulo'].render("MTG SIMULATOR", True, GameStyle.COLOR_ACCENT)
        self.screen.blit(txt_t, (cx - txt_t.get_width() // 2, 40))

        # Nickname Centralizado (Design conforme imagem anterior)
        txt_prefixo = self.fontes['label'].render("Conjurador Ativo:", True, (150, 150, 150))
        txt_name = self.fontes['popup'].render(self.nickname.upper(), True, GameStyle.COLOR_ACCENT)
        
        self.screen.blit(txt_prefixo, (cx - txt_prefixo.get_width() // 2, 180))
        self.screen.blit(txt_name, (cx - txt_name.get_width() // 2, 210))
        pygame.draw.line(self.screen, GameStyle.COLOR_ACCENT, (cx - 100, 245), (cx + 100, 245), 2)

        # Desenho dos botões
        for num, btn in self.btns_jogadores.items():
            btn.is_hovered = (self.total_jogadores == num) 
            btn.draw(self.screen)

        for btn in self.btns_acao:
            btn.draw(self.screen)

        # Pop-up de aviso (Deck ausente)
        if self.mostrar_aviso:
            overlay = pygame.Surface((self.largura, self.altura))
            overlay.set_alpha(190)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            pygame.draw.rect(self.screen, (35, 35, 40), self.popup_rect, border_radius=15)
            pygame.draw.rect(self.screen, GameStyle.COLOR_DANGER, self.popup_rect, 3, border_radius=15)
            s1 = self.fontes['popup'].render("⚠️ NENHUM DECK ENCONTRADO!", True, (255, 255, 255))
            self.screen.blit(s1, (self.popup_rect.centerx - s1.get_width() // 2, self.popup_rect.y + 40))
            self.btn_fechar_popup.draw(self.screen)