import pygame
from APP.utils.base import ViewComponent
from APP.utils.style import GameStyle

class MatchView(ViewComponent):
    def __init__(self, screen, controller):
        """
        Visualização da Partida com layout personalizado conforme esboço.
        """
        super().__init__(screen, controller)
        self.largura, self.altura = self.screen.get_size()
        self.fontes = GameStyle.get_fonts()
        
        self.model = self.controller.model
        
        # Dimensões base para cartas
        self.card_w = 70
        self.card_h = 100

    def handle_events(self, events):
        """Gerencia cliques e atalhos."""
        for event in events:
            if event.type == pygame.QUIT:
                return "SAIR"
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "MENU"
                if event.key == pygame.K_d: # Debug: Comprar carta
                    self.controller.draw_card(1)

            if event.type == pygame.MOUSEBUTTONDOWN:
                self._processar_clique_partida(event.pos)
                
        return None

    def _processar_clique_partida(self, pos):
        """Detecta clique para jogar terrenos da mão."""
        player = self.model.players.get(1)
        if not player: return

        # Verifica clique na mão do jogador (Centralizada na base)
        area_jogador = self._get_area_jogador(1, len(self.model.players))
        
        # Recalcula a posição das cartas na mão para ver se clicou
        start_x = area_jogador.centerx - (len(player.hand) * (self.card_w + 5)) // 2
        y = area_jogador.bottom - self.card_h - 10
        
        for i, card in enumerate(player.hand):
            x = start_x + (i * (self.card_w + 5))
            rect_card = pygame.Rect(x, y, self.card_w, self.card_h)
            
            if rect_card.collidepoint(pos):
                print(f"Clicou em: {card['name']}")
                if "Land" in card.get("type_line", ""):
                    self.controller.play_land(1, i)

    def draw(self):
        """Desenha o campo seguindo o layout do esboço."""
        self.screen.fill(GameStyle.COLOR_BG)
        
        qtd_jogadores = len(self.model.players)
        
        # Desenha a área de cada jogador
        for p_id in self.model.players:
            rect_area = self._get_area_jogador(p_id, qtd_jogadores)
            self._renderizar_zona_personalizada(p_id, rect_area)

    def _get_area_jogador(self, p_id, qtd):
        """Calcula o retângulo total de cada jogador na tela."""
        w, h = self.largura, self.altura
        
        if qtd <= 2:
            # Layout Duelo (Tela dividida ao meio)
            if p_id == 2: return pygame.Rect(0, 0, w, h // 2)      # Oponente (Topo)
            if p_id == 1: return pygame.Rect(0, h // 2, w, h // 2) # Você (Base)
        else:
            # Layout 4 Jogadores (Grade)
            half_w, half_h = w // 2, h // 2
            if p_id == 2: return pygame.Rect(0, 0, half_w, half_h)         # Top-Esq
            if p_id == 3: return pygame.Rect(half_w, 0, half_w, half_h)    # Top-Dir
            if p_id == 1: return pygame.Rect(0, half_h, half_w, half_h)    # Bot-Esq (Você)
            if p_id == 4: return pygame.Rect(half_w, half_h, half_w, half_h) # Bot-Dir
            
        return pygame.Rect(0, 0, w, h) # Fallback

    def _renderizar_zona_personalizada(self, p_id, rect):
        """
        Desenha as zonas EXATAMENTE conforme o esboço fornecido.
        """
        player = self.model.players[p_id]
        eh_humano = (p_id == 1)

        # 1. Fundo Azulado (Conforme imagem)
        cor_fundo = (50, 50, 150) if eh_humano else (40, 40, 80)
        pygame.draw.rect(self.screen, cor_fundo, rect)
        pygame.draw.rect(self.screen, (200, 200, 200), rect, 2) # Borda branca

        # HUD: Nome e Vida (No topo da área)
        info_txt = f"{player.name} | Vida: {player.life}"
        txt = self.fontes['label'].render(info_txt, True, (255, 255, 255))
        self.screen.blit(txt, (rect.centerx - txt.get_width()//2, rect.y + 5))

        # --- DEFINIÇÃO DAS ZONAS (Baseado no seu desenho) ---
        
        # Largura e Altura proporcionais para funcionar em qualquer resolução
        w_zona = rect.width * 0.20  # 20% da largura para as zonas laterais
        h_top = rect.height * 0.40  # 40% da altura para zonas de cima
        h_bot = rect.height * 0.40  # 40% da altura para zonas de baixo

        # A. ZONA DE COMANDANTE (Canto Superior Esquerdo)
        r_cmd = pygame.Rect(rect.x, rect.y, w_zona, h_top)
        self._desenhar_caixa_zona(r_cmd, "COMANDANTE", (60, 60, 180))
        # Se tiver comandante, desenha a carta (placeholder)
        if self.controller.model.commander:
             self._desenhar_mini_carta(rect.x + 10, rect.y + 30, (255, 215, 0))

        # B. ZONA DE MANA (Canto Inferior Esquerdo)
        r_mana = pygame.Rect(rect.x, rect.bottom - h_bot, w_zona, h_bot)
        self._desenhar_caixa_zona(r_mana, "MANA", (40, 100, 40))
        # Desenha terrenos empilhados
        for i, land in enumerate(player.battlefield_lands):
            # Empilha visualmente
            lx = r_mana.x + 5 + (i * 15)
            ly = r_mana.y + 25 + (i * 5)
            if lx < r_mana.right - 20: # Limite visual
                self._desenhar_mini_carta(lx, ly, (100, 200, 100))

        # C. ZONA DE CEMITÉRIO (Canto Superior Direito)
        r_grave = pygame.Rect(rect.right - w_zona, rect.y, w_zona, h_top * 0.7) # Um pouco menor
        self._desenhar_caixa_zona(r_grave, "CEMITERIO", (40, 40, 40))
        txt_g = self.fontes['status'].render(str(len(player.graveyard)), True, (255,255,255))
        self.screen.blit(txt_g, (r_grave.centerx-5, r_grave.centery))

        # D. ZONA DE EXÍLIO (Abaixo do Cemitério, Canto Direito)
        r_exile = pygame.Rect(rect.right - w_zona, r_grave.bottom, w_zona, rect.height - r_grave.height)
        self._desenhar_caixa_zona(r_exile, "EXILIO", (60, 40, 60))

        # E. CAMPO DE BATALHA (Centro - O que sobrou)
        # O espaço entre a zona da esquerda e da direita
        x_battle = rect.x + w_zona
        w_battle = rect.width - (2 * w_zona)
        r_battle = pygame.Rect(x_battle, rect.y + 20, w_battle, rect.height - 20)
        # (Opcional) Desenhar linha sutil para marcar o campo
        # pygame.draw.rect(self.screen, (60, 60, 160), r_battle, 1)

        # --- MÃO DO JOGADOR (Sobreposta na parte inferior central) ---
        if eh_humano:
            self._renderizar_mao(player.hand, rect)
        else:
            # Oponente: Mostra apenas quantidade de cartas
            txt_mao = self.fontes['label'].render(f"Mão: {len(player.hand)}", True, (255, 255, 255))
            self.screen.blit(txt_mao, (rect.centerx - 30, rect.bottom - 30))

    def _desenhar_caixa_zona(self, rect, titulo, cor_bg):
        """Desenha o retângulo da zona com título, igual ao esboço."""
        pygame.draw.rect(self.screen, cor_bg, rect)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, 1) # Borda preta fina
        
        txt = self.fontes['status'].render(titulo, True, (200, 200, 200))
        # Centraliza o texto na zona
        self.screen.blit(txt, (rect.x + 5, rect.y + 5))

    def _desenhar_mini_carta(self, x, y, cor):
        """Representação simples de uma carta na mesa."""
        r = pygame.Rect(x, y, 40, 56)
        pygame.draw.rect(self.screen, cor, r)
        pygame.draw.rect(self.screen, (0,0,0), r, 1)

    def _renderizar_mao(self, hand, rect_area):
        """Desenha as cartas na mão (Centralizado no fundo)."""
        qtd = len(hand)
        if qtd == 0: return

        largura_total_mao = qtd * (self.card_w + 5)
        start_x = rect_area.centerx - (largura_total_mao // 2)
        y = rect_area.bottom - self.card_h - 10

        for i, card in enumerate(hand):
            x = start_x + (i * (self.card_w + 5))
            r_card = pygame.Rect(x, y, self.card_w, self.card_h)
            
            # Fundo da Carta
            pygame.draw.rect(self.screen, (200, 200, 180), r_card, border_radius=4)
            pygame.draw.rect(self.screen, (0, 0, 0), r_card, 1, border_radius=4)
            
            # Texto (Nome curto)
            nome = card['name'][:8]
            txt = self.fontes['status'].render(nome, True, (0, 0, 0))
            self.screen.blit(txt, (x + 2, y + 2))
            
            # Indicador se for Terreno (Verde)
            if "Land" in card.get("type_line", ""):
                pygame.draw.circle(self.screen, (50, 200, 50), (x + 10, y + 80), 5)