import pygame
from APP.UI.styles import colors
from APP.UI.styles.fonts import get_fonts
from APP.UI.layout.grid import LayoutEngine

class ZoneUI:
    def __init__(self, rect: pygame.Rect, title: str, bg_color: tuple, layout_style: str = "overlap"):
        """
        Componente modular para as zonas do campo de batalha.
        Ajustado para suportar o novo retorno do LayoutEngine (X, Y, Zoom).
        """
        self.rect = rect
        self.title = title
        self.bg_color = bg_color
        self.layout_style = layout_style # 'overlap', 'grid', 'stack'
        self.fontes = get_fonts()
        
        self.cards_ui = [] # Lista de componentes CardUI

    def clear_cards(self):
        self.cards_ui.clear()

    def add_card_ui(self, card_ui):
        self.cards_ui.append(card_ui)

    def draw(self, screen):
        """Renderiza a zona e organiza as cartas internamente."""
        # 1. Desenha o Fundo da Zona
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, (80, 80, 100), self.rect, 2, border_radius=8)
        
        # 2. Título da Zona
        txt = self.fontes['status'].render(self.title, True, (200, 200, 200))
        screen.blit(txt, (self.rect.x + 10, self.rect.y + 5))

        if not self.cards_ui:
            return

        # 3. CÁLCULO DA ÁREA ÚTIL
        padding_x = self.rect.width * 0.10
        padding_y = self.rect.height * 0.15
        area_util = self.rect.inflate(-padding_x, -padding_y)
        area_util.top += 10

        card_w = self.cards_ui[0].rect.width
        card_h = self.cards_ui[0].rect.height
        
        # 4. APLICAÇÃO DO LAYOUT DINÂMICO
        if self.layout_style == "grid":
            posicoes = LayoutEngine.get_grid_layout(area_util, len(self.cards_ui), card_w, card_h)
        
        elif self.layout_style == "overlap":
            # PULO DO GATO: Zonas de campo (Mana/Battlefield) não usam zoom de grupo
            # Passamos is_group_focused=False para evitar que cartas no campo subam
            posicoes = LayoutEngine.get_hand_layout(area_util, len(self.cards_ui), card_w, card_h, False)
            
        elif self.layout_style == "stack":
            cx = area_util.centerx - (card_w // 2)
            cy = area_util.centery - (card_h // 2)
            posicoes = []
            for i in range(len(self.cards_ui)):
                # No stack, simulamos o X, Y e um zoom padrão de 1.0
                posicoes.append((cx + (i * 0.5), cy - (i * 0.5), 1.0))
        else:
            posicoes = []

        # 5. DESENHA AS CARTAS (Tratando o retorno de 2 ou 3 valores)
        for i, card_ui in enumerate(self.cards_ui):
            if i < len(posicoes):
                dados_pos = posicoes[i]
                
                # Desempacota com segurança: aceita (x, y) ou (x, y, zoom)
                x = dados_pos[0]
                y = dados_pos[1]
                
                card_ui.update_position(x, y)
                
                # Performance no stack: Desenha apenas as 3 do topo para dar volume
                if self.layout_style == "stack" and i < len(self.cards_ui) - 3:
                    continue
                    
                card_ui.draw(screen)