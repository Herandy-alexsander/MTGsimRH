import pygame
from APP.UI.styles import colors
from APP.UI.styles.fonts import get_fonts
from APP.UI.layout.grid import LayoutEngine

class ZoneUI:
    def __init__(self, rect: pygame.Rect, title: str, bg_color: tuple, layout_style: str = "overlap"):
        """
        Componente modular para as zonas do campo de batalha.
        Aplica um recuo (padding) de 10% para que as cartas não toquem as bordas.
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
        """Renderiza a zona com margens internas (padding) de 10%."""
        # 1. Desenha o Fundo da Zona
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, (80, 80, 100), self.rect, 2, border_radius=8)
        
        # 2. Título da Zona
        txt = self.fontes['status'].render(self.title, True, (200, 200, 200))
        screen.blit(txt, (self.rect.x + 10, self.rect.y + 5))

        if not self.cards_ui:
            return

        # 3. CÁLCULO DA ÁREA ÚTIL (O PULO DO GATO: 10% de preenchimento)
        # Criamos um retângulo menor dentro da zona para o LayoutEngine trabalhar
        padding_x = self.rect.width * 0.10
        padding_y = self.rect.height * 0.15 # Um pouco mais no topo por causa do título
        area_util = self.rect.inflate(-padding_x, -padding_y)
        area_util.top += 10 # Desce um pouco mais para não bater no título

        # 4. APLICAÇÃO DO LAYOUT DINÂMICO
        card_w = self.cards_ui[0].rect.width
        card_h = self.cards_ui[0].rect.height
        
        if self.layout_style == "grid":
            posicoes = LayoutEngine.get_grid_layout(area_util, len(self.cards_ui), card_w, card_h)
        
        elif self.layout_style == "overlap":
            posicoes = LayoutEngine.get_hand_layout(area_util, len(self.cards_ui), card_w, card_h)
            
        elif self.layout_style == "stack":
            # Centraliza no meio da área útil
            cx = area_util.centerx - (card_w // 2)
            cy = area_util.centery - (card_h // 2)
            
            # Efeito 3D: Desloca cada carta 1 pixel para parecer um monte físico
            posicoes = []
            for i in range(len(self.cards_ui)):
                posicoes.append((cx + (i * 0.5), cy - (i * 0.5)))
        
        else:
            posicoes = []

        # 5. DESENHA AS CARTAS
        for i, card_ui in enumerate(self.cards_ui):
            if i < len(posicoes):
                x, y = posicoes[i]
                card_ui.update_position(x, y)
                
                # Performance no stack: Desenha apenas as 3 do topo para dar volume
                if self.layout_style == "stack" and i < len(self.cards_ui) - 3:
                    continue
                    
                card_ui.draw(screen)