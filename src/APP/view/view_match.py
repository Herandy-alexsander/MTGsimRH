import pygame
from APP.utils.base import ViewComponent
from APP.utils.style import GameStyle

class MatchView(ViewComponent):
    def __init__(self, screen, controller):
        """
        controller: Instância do MatchController que criamos.
        """
        super().__init__(screen, controller)
        self.largura, self.altura = self.screen.get_size()
        self.fontes = GameStyle.get_fonts()
        
        # O Model contém os dados reais (jogadores, mãos, zonas)
        self.model = self.controller.model
        self.jogo_preparado = False

    def _setup_initial_state(self):
        """Prepara os dados uma única vez ao entrar na tela."""
        if not self.jogo_preparado:
            # Pede ao controller para organizar os jogadores baseados no cadastro
            self.controller.setup_game() 
            self.jogo_preparado = True

    def handle_events(self, events):
        self._setup_initial_state()
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "MENU"
                
                # Exemplo: Tecla 'D' para comprar carta (Draw) do jogador atual
                if event.key == pygame.K_d:
                    self.controller.draw_card(self.model.current_turn_player)

            # Lógica de clique para selecionar cartas ou passar turno
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Aqui entrará a lógica de colisão para mover cartas
                pass
        return None

    def draw(self):
        self.screen.fill(GameStyle.COLOR_BG)
        
        # Verifica quantos jogadores existem para definir o layout
        qtd = len(self.model.players)
        
        if qtd <= 2:
            self.desenhar_duelo()
        else:
            self.desenhar_multiplayer()

    def desenhar_duelo(self):
        """Divide a tela horizontalmente para 2 jogadores."""
        # Jogador 2 (Oponente - Topo)
        if 2 in self.model.players:
            rect_oponente = pygame.Rect(10, 10, self.largura - 20, self.altura // 2 - 20)
            self.renderizar_tabuleiro(2, rect_oponente, invertido=True)
            
        # Jogador 1 (Você - Base)
        if 1 in self.model.players:
            rect_voce = pygame.Rect(10, self.altura // 2 + 10, self.largura - 20, self.altura // 2 - 20)
            self.renderizar_tabuleiro(1, rect_voce)

    def renderizar_tabuleiro(self, p_id, rect, invertido=False):
        """Desenha as zonas de um jogador (Terrenos, Combate, Cemitério, Mão)."""
        player = self.model.players[p_id]
        
        # Moldura da área do jogador
        pygame.draw.rect(self.screen, (25, 25, 30), rect, border_radius=10)
        pygame.draw.rect(self.screen, (45, 45, 50), rect, 1, border_radius=10)

        # --- ZONA TÉCNICA (Barra Lateral: Deck, Grave, CMD) ---
        sidebar_x = rect.x + 10
        y_offset = rect.y + 10
        self._desenhar_slot(sidebar_x, y_offset, "DECK", len(player.library), (43, 37, 33))
        self._desenhar_slot(sidebar_x, y_offset + 60, "GRAVE", len(player.graveyard), (25, 20, 20))
        self._desenhar_slot(sidebar_x, y_offset + 120, "CMD", 1, GameStyle.COLOR_ACCENT)

        # --- ZONA DE JOGO (Dividida em Terrenos e Combate) ---
        # Terrenos (Atrás)
        y_terrenos = rect.y + (rect.height * 0.55 if not invertido else 40)
        rect_terrenos = pygame.Rect(rect.x + 110, y_terrenos, rect.width - 150, rect.height * 0.35)
        pygame.draw.rect(self.screen, (20, 25, 20), rect_terrenos, border_radius=5)
        
        # Combate (Frente)
        y_combate = rect.y + (rect.height * 0.15 if not invertido else rect.height * 0.45)
        rect_combate = pygame.Rect(rect.x + 110, y_combate, rect.width - 150, rect.height * 0.35)
        pygame.draw.rect(self.screen, (35, 35, 40), rect_combate, border_radius=5)

        # --- MÃO (Apenas se for o jogador atual ou modo debug) ---
        if not invertido:
            self.renderizar_mao(player.hand, rect)

    def _desenhar_slot(self, x, y, label, count, cor):
        """Desenha as pequenas caixas de status."""
        r = pygame.Rect(x, y, 80, 50)
        pygame.draw.rect(self.screen, cor, r, border_radius=5)
        txt = self.fontes['status'].render(f"{label}: {count}", True, (200, 200, 200))
        self.screen.blit(txt, (x + 5, y + 15))

    def renderizar_mao(self, hand, area_rect):
        """Desenha as cartas na mão na parte inferior da zona do jogador."""
        for i, card in enumerate(hand):
            x = area_rect.x + 120 + (i * 85)
            y = area_rect.bottom - 110
            r_card = pygame.Rect(x, y, 75, 100)
            pygame.draw.rect(self.screen, (50, 50, 60), r_card, border_radius=5)
            pygame.draw.rect(self.screen, (150, 150, 150), r_card, 1, border_radius=5)
            
            # Nome da carta (Apenas texto por enquanto)
            txt = self.fontes['status'].render(card['name'][:8], True, (255, 255, 255))
            self.screen.blit(txt, (x + 5, y + 5))