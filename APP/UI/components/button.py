import pygame
from APP.UI.styles import colors  # Importa sua paleta de cores

class MenuButton:
    def __init__(self, rect, text, font):
        """
        Estrutura base para botões do projeto Machete.
        :param rect: pygame.Rect definindo posição e tamanho.
        :param text: Texto que será exibido.
        :param font: Objeto de fonte vindo do seu fonts.py.
        """
        self.rect = rect
        self.text = text
        self.font = font
        self.is_hovered = False
        # Cores padrão baseadas no seu colors.py
        self.color_text_normal = colors.TEXT_SEC
        self.color_text_hover = colors.TEXT_PRIMARY
        self.color_accent = colors.ACCENT

    def update(self, mouse_pos):
        """Verifica se o mouse está sobre o botão para efeitos visuais."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
        """Desenha o botão com o estilo metálico/MTG que você definiu."""
        # Define a cor da borda baseada no estado do mouse
        cor_borda = self.color_accent if self.is_hovered else (100, 100, 100)
        
        # 1. Sombra (Profundidade)
        pygame.draw.rect(screen, (10, 10, 10), self.rect.move(2, 2), border_radius=8)
        
        # 2. Borda Principal
        pygame.draw.rect(screen, cor_borda, self.rect, border_radius=8)
        
        # 3. Corpo do Botão (Preenchimento Interno)
        corpo_rect = self.rect.inflate(-4, -4)
        pygame.draw.rect(screen, (60, 60, 65), corpo_rect, border_radius=6)
        
        # 4. Renderização do Texto Centralizado
        cor_texto = self.color_text_hover if self.is_hovered else self.color_text_normal
        text_surf = self.font.render(self.text, True, cor_texto)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event):
        """Detecta o clique do botão esquerdo."""
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered