import pygame
import os
from APP.utils.base import ViewComponent
from APP.utils.style import GameStyle

class MatchView(ViewComponent):
    def __init__(self, screen, controller, asset_manager): ### NOVO: Recebe asset_manager
        """
        Visualização da Partida com suporte a imagens reais via AssetManager.
        """
        super().__init__(screen, controller)
        self.asset_manager = asset_manager ### NOVO: Guarda a referência
        
        self.largura, self.altura = self.screen.get_size()
        self.fontes = GameStyle.get_fonts()
        self.model = self.controller.model
        
        # Dimensões base para cartas
        self.card_w = 70
        self.card_h = 100
        
        # O cache interno foi removido, pois o AssetManager já faz esse papel globalmente

    def _get_card_category(self, type_line):
        """Helper para mapear o tipo da carta à pasta de assets."""
        tipo = type_line or ""
        if "Creature" in tipo: return "Criaturas"
        if "Land" in tipo: return "Terrenos"
        if "Instant" in tipo: return "Instantes"
        if "Sorcery" in tipo: return "Feiticos"
        if "Enchantment" in tipo: return "Encantamentos"
        if "Artifact" in tipo: return "Artefatos"
        return "Outros"

    def handle_events(self, events):
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
        player = self.model.players.get(1)
        if not player: return

        area_jogador = self._get_area_jogador(1, len(self.model.players))
        
        qtd = len(player.hand)
        if qtd == 0: return
        
        largura_total_mao = qtd * (self.card_w + 5)
        start_x = area_jogador.centerx - (largura_total_mao // 2)
        y = area_jogador.bottom - self.card_h - 10
        
        for i, card in enumerate(player.hand):
            x = start_x + (i * (self.card_w + 5))
            rect_card = pygame.Rect(x, y, self.card_w, self.card_h)
            
            if rect_card.collidepoint(pos):
                if "Land" in card.get("type_line", ""):
                    self.controller.play_land(1, i)

    def draw(self):
        self.screen.fill(GameStyle.COLOR_BG)
        jogadores = list(self.model.players.keys())
        qtd_jogadores = len(jogadores)
        
        for p_id in jogadores:
            rect_area = self._get_area_jogador(p_id, qtd_jogadores)
            self._renderizar_zona_personalizada(p_id, rect_area)

    def _get_area_jogador(self, p_id, qtd):
        w, h = self.largura, self.altura
        if qtd <= 2:
            if p_id == 2: return pygame.Rect(0, 0, w, h // 2)      
            if p_id == 1: return pygame.Rect(0, h // 2, w, h // 2) 
        else:
            half_w, half_h = w // 2, h // 2
            if p_id == 2: return pygame.Rect(0, 0, half_w, half_h)          
            if p_id == 3: return pygame.Rect(half_w, 0, half_w, half_h)    
            if p_id == 1: return pygame.Rect(0, half_h, half_w, half_h)    
            if p_id == 4: return pygame.Rect(half_w, half_h, half_w, half_h)
        return pygame.Rect(0, 0, w, h)

    def _renderizar_zona_personalizada(self, p_id, rect):
        player = self.model.players[p_id]
        eh_humano = (p_id == 1)

        cor_fundo = (30, 30, 45) if eh_humano else (25, 25, 35)
        pygame.draw.rect(self.screen, cor_fundo, rect)
        pygame.draw.rect(self.screen, (100, 100, 120), rect, 2) 

        info_txt = f"{player.name} | {player.life} PV"
        txt = self.fontes['label'].render(info_txt, True, (255, 255, 255))
        self.screen.blit(txt, (rect.centerx - txt.get_width()//2, rect.y + 5))

        w_zona = rect.width * 0.22
        h_top = rect.height * 0.45

        # 1. ZONA DO COMANDANTE
        r_cmd = pygame.Rect(rect.x + 5, rect.y + 35, w_zona - 10, h_top - 40)
        self._desenhar_caixa_zona(r_cmd, "COMANDANTE", (45, 45, 70))
        if self.model.commander:
            cmd_data = {"name": self.model.commander, "type_line": "Legendary Creature"}
            self._desenhar_carta(rect.x + 15, rect.y + 60, cmd_data, w=50, h=70)

        # 2. ZONA DE MANA
        r_mana = pygame.Rect(rect.x + 5, rect.bottom - (rect.height * 0.35), w_zona - 10, (rect.height * 0.35) - 10)
        self._desenhar_caixa_zona(r_mana, "MANA", (30, 50, 30))
        for i, land in enumerate(player.battlefield_lands):
            lx = r_mana.x + 5 + (i * 18)
            ly = r_mana.y + 25
            if lx < r_mana.right - 40:
                self._desenhar_carta(lx, ly, land, w=40, h=56)

        # 3. CEMITÉRIO
        r_grave = pygame.Rect(rect.right - w_zona + 5, rect.y + 35, w_zona - 10, h_top - 40)
        self._desenhar_caixa_zona(r_grave, "CEMITÉRIO", (40, 30, 30))

        # 4. MÃO
        if eh_humano:
            self._renderizar_mao(player.hand, rect)
        else:
            txt_mao = self.fontes['label'].render(f"Cartas: {len(player.hand)}", True, (180, 180, 180))
            self.screen.blit(txt_mao, (rect.centerx - txt_mao.get_width()//2, rect.bottom - 40))

    def _desenhar_caixa_zona(self, rect, titulo, cor_bg):
        pygame.draw.rect(self.screen, cor_bg, rect, border_radius=5)
        pygame.draw.rect(self.screen, (60, 60, 80), rect, 1, border_radius=5)
        txt = self.fontes['status'].render(titulo, True, (160, 160, 160))
        self.screen.blit(txt, (rect.x + 5, rect.y + 2))

    def _desenhar_carta(self, x, y, card_data, w, h):
        """NOVO: Pede a imagem ao AssetManager e aplica redimensionamento suave."""
        nome = card_data.get("name", "Unknown")
        categoria = self._get_card_category(card_data.get("type_line", ""))
        
        # 1. Obtém a imagem original (o AssetManager gerencia o carregamento e cache de disco)
        img_original = self.asset_manager.get_card_image(nome, category=categoria)
        
        if img_original:
            # 2. Redimensiona para o tamanho solicitado na mesa
            img_final = pygame.transform.smoothscale(img_original, (w, h))
            self.screen.blit(img_final, (x, y))
            pygame.draw.rect(self.screen, (0,0,0), (x, y, w, h), 1, border_radius=4)
        else:
            # FALLBACK (Caso o arquivo não exista no HD)
            rect = pygame.Rect(x, y, w, h)
            cor = (200, 200, 180)
            if "Land" in card_data.get("type_line", ""): cor = (150, 200, 150)
            pygame.draw.rect(self.screen, cor, rect, border_radius=4)
            pygame.draw.rect(self.screen, (0,0,0), rect, 1, border_radius=4)
            
            txt_nome = self.fontes['status'].render(nome[:8], True, (0, 0, 0))
            self.screen.blit(txt_nome, (x + 2, y + 2))

    def _renderizar_mao(self, hand, rect_area):
        qtd = len(hand)
        if qtd == 0: return

        espacamento = 5
        largura_total_mao = qtd * (self.card_w + espacamento)
        
        if largura_total_mao > rect_area.width * 0.7:
            espacamento = - (largura_total_mao - rect_area.width * 0.7) // qtd

        start_x = rect_area.centerx - (largura_total_mao // 2)
        y = rect_area.bottom - self.card_h - 15

        for i, card in enumerate(hand):
            x = start_x + (i * (self.card_w + espacamento))
            self._desenhar_carta(x, y, card, self.card_w, self.card_h)
            
            if "Land" in card.get("type_line", ""):
                pygame.draw.rect(self.screen, GameStyle.COLOR_ACCENT, (x, y, self.card_w, self.card_h), 2, border_radius=4)
