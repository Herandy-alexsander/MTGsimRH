import pygame
from APP.UI.ui_components import MenuButton, UIComponents
from APP.UI.style import GameStyle

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
        self.total_jogadores = 4 # Padrão Commander é 4
        self.mostrar_aviso = False
        
        # Sincroniza o nome do usuário
        self.atualizar_nickname()
        
        # --- Layout e Posicionamento (Correção de Espaçamento) ---
        cx = self.largura // 2
        
        # 1. Botões de Seleção (Jogadores) - Alinhados horizontalmente
        self.btns_jogadores = {}
        largura_btn_jog = 60
        espacamento_jog = 15
        # Centraliza o grupo de botões
        largura_total_grupo = (largura_btn_jog * 3) + (espacamento_jog * 2)
        inicio_x_jog = cx - (largura_total_grupo // 2)
        
        for i, num in enumerate([2, 3, 4]):
            pos_x = inicio_x_jog + (largura_btn_jog + espacamento_jog) * i
            rect = pygame.Rect(pos_x, 340, largura_btn_jog, 45)
            self.btns_jogadores[num] = MenuButton(rect, str(num), self.fontes['menu'])

        # 2. Botões de Ação Principal - Verticalmente distribuídos
        # Ajustei o Y inicial para 420 e o espaçamento para 70px entre cada botão
        self.btn_abrir_sala = MenuButton(pygame.Rect(cx - 150, 420, 300, 50), "ABRIR SALA", self.fontes['menu'])
        self.btn_meus_decks = MenuButton(pygame.Rect(cx - 150, 490, 300, 50), "MEUS DECKS", self.fontes['menu'])
        self.btn_cadastrar = MenuButton(pygame.Rect(cx - 150, 560, 300, 50), "CADASTRAR", self.fontes['menu'])
        self.btn_sair = MenuButton(pygame.Rect(cx - 150, 660, 300, 50), "SAIR", self.fontes['menu'])

        # Lista para facilitar a iteração no loop de eventos/desenho
        self.btns_acao = [self.btn_abrir_sala, self.btn_meus_decks, self.btn_cadastrar, self.btn_sair]

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
        """Gerencia interações do usuário."""
        mouse_pos = pygame.mouse.get_pos()
        
        # Atualiza hover do botão de fechar se o popup estiver ativo
        if self.mostrar_aviso:
            self.btn_fechar_popup.update(mouse_pos)
        else:
            # Atualiza hover dos botões principais apenas se o popup NÃO estiver ativo
            for btn in self.btns_jogadores.values():
                btn.update(mouse_pos)
            for btn in self.btns_acao:
                btn.update(mouse_pos)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # 1. Lógica do Pop-up (Prioridade Alta)
                if self.mostrar_aviso:
                    if self.btn_fechar_popup.is_clicked(event):
                        self.mostrar_aviso = False
                    return None # Bloqueia outros cliques enquanto o aviso estiver na tela

                # 2. Seleção de Número de Jogadores
                for num, btn in self.btns_jogadores.items():
                    if btn.is_clicked(event):
                        self.total_jogadores = num
                        # Opcional: Tocar som de clique aqui

                # 3. Botões de Ação Principal
                if self.btn_abrir_sala.is_clicked(event):
                    if not has_deck:
                        self.mostrar_aviso = True
                        return None
                    return "ABRIR SALA"

                if self.btn_meus_decks.is_clicked(event):
                    return "MEUS DECKS"

                if self.btn_cadastrar.is_clicked(event):
                    return "CADASTRAR"

                if self.btn_sair.is_clicked(event):
                    return "SAIR"
                    
        return None

    def draw(self, has_deck=False):
        """Renderiza o menu."""
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
        
        # Linha decorativa
        pygame.draw.line(self.screen, (50, 50, 50), (cx - 150, 255), (cx + 150, 255), 1)
        pygame.draw.line(self.screen, GameStyle.COLOR_ACCENT, (cx - 70, 255), (cx + 70, 255), 2)

        # Label Oponentes
        txt_op = self.fontes['label'].render("NÚMERO DE JOGADORES", True, (120, 120, 120))
        self.screen.blit(txt_op, (cx - txt_op.get_width() // 2, 305))

        # Desenho dos Botões de Jogadores
        for num, btn in self.btns_jogadores.items():
            # Destaca visualmente a seleção atual
            eh_selecionado = (self.total_jogadores == num)
            
            # Se selecionado, desenha borda dourada extra
            if eh_selecionado:
                pygame.draw.rect(self.screen, GameStyle.COLOR_ACCENT, btn.rect.inflate(4, 4), 2, border_radius=8)
            
            btn.draw(self.screen)

        # Desenho dos Botões de Ação
        for btn in self.btns_acao:
            # Estilo especial para o botão SAIR (Vermelho suave)
            if btn.text == "SAIR":
                btn.color_border = (180, 60, 60) if btn.is_hovered else (100, 40, 40)
            btn.draw(self.screen)

        # Pop-up de Aviso (Sempre por cima)
        if self.mostrar_aviso:
            self._draw_popup()

    def _draw_popup(self):
        """Desenha o overlay e a caixa de aviso."""
        # Overlay escuro transparente
        overlay = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200)) # Mais escuro para destacar o aviso
        self.screen.blit(overlay, (0, 0))
        
        # Caixa do Pop-up
        pygame.draw.rect(self.screen, (25, 25, 30), self.popup_rect, border_radius=12)
        pygame.draw.rect(self.screen, GameStyle.COLOR_DANGER, self.popup_rect, 2, border_radius=12)
        
        # Textos
        msg = self.fontes['popup'].render("⚠️ NENHUM DECK ENCONTRADO", True, (255, 255, 255))
        sub = self.fontes['label'].render("Cadastre um deck antes de jogar.", True, (180, 180, 180))
        
        self.screen.blit(msg, (self.popup_rect.centerx - msg.get_width() // 2, self.popup_rect.y + 45))
        self.screen.blit(sub, (self.popup_rect.centerx - sub.get_width() // 2, self.popup_rect.y + 90))
        
        self.btn_fechar_popup.draw(self.screen)