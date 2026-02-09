import pygame
from APP.utils.ui_components import MenuButton, UIComponents
from APP.utils.style import GameStyle

class MainMenu:
    def __init__(self, screen, storage):
        """
        Menu principal com correções de espaçamento e alinhamento visual.
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
        
        # Sincroniza o nome do usuário
        self.atualizar_nickname()
        
        # --- Layout e Posicionamento (Correção de Espaçamento) ---
        cx = self.largura // 2
        
        # 1. Botões de Seleção (Jogadores) - Alinhados horizontalmente
        self.btns_jogadores = {}
        largura_btn_jog = 60
        espacamento_jog = 15
        inicio_x_jog = cx - ((largura_btn_jog * 3 + espacamento_jog * 2) // 2)
        
        for i, num in enumerate([2, 3, 4]):
            rect = pygame.Rect(inicio_x_jog + (largura_btn_jog + espacamento_jog) * i, 340, largura_btn_jog, 45)
            self.btns_jogadores[num] = MenuButton(rect, str(num), self.fontes['menu'])

        # 2. Botões de Ação Principal - Verticalmente distribuídos sem sobreposição
        # Aumentamos o 'y' inicial e o espaçamento para evitar o erro da imagem
        self.btns_acao = [
            MenuButton(pygame.Rect(cx - 150, 420, 300, 50), "ABRIR SALA", self.fontes['menu']),
            MenuButton(pygame.Rect(cx - 150, 485, 300, 50), "MEUS DECKS", self.fontes['menu']),
            MenuButton(pygame.Rect(cx - 150, 550, 300, 50), "CADASTRAR", self.fontes['menu']),
            MenuButton(pygame.Rect(cx - 150, 650, 300, 50), "SAIR", self.fontes['menu'])
        ]

        # --- Pop-up de Aviso ---
        self.popup_rect = pygame.Rect(cx - 225, self.altura // 2 - 100, 450, 200)
        self.btn_fechar_popup = MenuButton(
            pygame.Rect(cx - 75, self.popup_rect.y + 130, 150, 40), 
            "FECHAR", self.fontes['menu']
        )

    def atualizar_nickname(self):
        """Busca os dados atualizados do profiler.json."""
        perfil = self.storage.carregar_perfil()
        if "player_info" in perfil:
            self.nickname = perfil["player_info"].get("nickname", "Conjurador")

    def handle_event(self, events, has_deck=False):
        mouse_pos = pygame.mouse.get_pos()
        
        if self.mostrar_aviso:
            self.btn_fechar_popup.update(mouse_pos)

        for event in events:
            if self.mostrar_aviso:
                if self.btn_fechar_popup.is_clicked(event):
                    self.mostrar_aviso = False
                continue 

            # Interação com números de jogadores
            for num, btn in self.btns_jogadores.items():
                btn.update(mouse_pos)
                if btn.is_clicked(event):
                    self.total_jogadores = num

            # Interação com botões de ação
            for btn in self.btns_acao:
                btn.update(mouse_pos)
                if btn.is_clicked(event):
                    if btn.text == "ABRIR SALA" and not has_deck:
                        self.mostrar_aviso = True
                        return None
                    return btn.text
        return None

    def draw(self, has_deck=False):
        """Renderiza o menu com as correções de profundidade e alinhamento."""
        self.screen.fill(GameStyle.COLOR_BG)
        cx = self.largura // 2
        
        # Título Principal
        txt_t = self.fontes['titulo'].render("MTG SIMULATOR", True, GameStyle.COLOR_ACCENT)
        self.screen.blit(txt_t, (cx - txt_t.get_width() // 2, 60))

        # Seção do Conjurador
        txt_prefixo = self.fontes['label'].render("CONJURADOR ATIVO", True, (120, 120, 120))
        txt_name = self.fontes['popup'].render(self.nickname.upper(), True, (255, 255, 255))
        self.screen.blit(txt_prefixo, (cx - txt_prefixo.get_width() // 2, 180))
        self.screen.blit(txt_name, (cx - txt_name.get_width() // 2, 215))
        
        # Linha decorativa refinada
        pygame.draw.line(self.screen, (50, 50, 50), (cx - 150, 255), (cx + 150, 255), 1)
        pygame.draw.line(self.screen, GameStyle.COLOR_ACCENT, (cx - 70, 255), (cx + 70, 255), 2)

        # Label Oponentes
        txt_op = self.fontes['label'].render("NÚMERO DE OPONENTES", True, (120, 120, 120))
        self.screen.blit(txt_op, (cx - txt_op.get_width() // 2, 305))

        # Desenho dos Botões (Com realce no selecionado)
        for num, btn in self.btns_jogadores.items():
            # Ativa brilho apenas no número selecionado
            btn.is_hovered = (self.total_jogadores == num) 
            btn.draw(self.screen)

        for btn in self.btns_acao:
            # Botão de SAIR com cor diferenciada
            if btn.text == "SAIR":
                btn.color_border = (100, 50, 50)
            btn.draw(self.screen)

        # Pop-up de Erro (Renderizado por cima de tudo)
        if self.mostrar_aviso:
            self._draw_popup()

    def _draw_popup(self):
        overlay = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        pygame.draw.rect(self.screen, (30, 30, 35), self.popup_rect, border_radius=12)
        pygame.draw.rect(self.screen, GameStyle.COLOR_DANGER, self.popup_rect, 2, border_radius=12)
        
        msg = self.fontes['popup'].render("⚠️ NENHUM DECK ENCONTRADO", True, (255, 255, 255))
        sub = self.fontes['label'].render("Cadastre um deck primeiro.", True, (150, 150, 150))
        
        self.screen.blit(msg, (self.popup_rect.centerx - msg.get_width() // 2, self.popup_rect.y + 45))
        self.screen.blit(sub, (self.popup_rect.centerx - sub.get_width() // 2, self.popup_rect.y + 90))
        self.btn_fechar_popup.draw(self.screen)