import pygame
from APP.UI.styles import colors  # Importa sua paleta de cores centralizada

class Label:
    def __init__(self, text, pos, font, color=None, align="center"):
        """
        Componente para exibição de textos estáticos no projeto Machete.
        :param text: O conteúdo de texto.
        :param pos: Tupla (x, y) para posicionamento.
        :param font: Objeto de fonte vindo do seu fonts.py.
        :param color: Cor opcional (se None, usa colors.TEXT_PRIMARY).
        :param align: Alinhamento ("center", "left", "right").
        """
        self.text = text
        self.pos = pos
        self.font = font
        self.color = color if color else colors.TEXT_PRIMARY
        self.align = align
        self.update_surface()

    def update_surface(self):
        """Renderiza a superfície de texto e define o retângulo de exibição."""
        self.surface = self.font.render(self.text, True, self.color)
        self.rect = self.surface.get_rect()
        
        # Ajusta o ponto de ancoragem baseado no alinhamento
        if self.align == "center":
            self.rect.center = self.pos
        elif self.align == "left":
            self.rect.topleft = self.pos
        elif self.align == "right":
            self.rect.topright = self.pos

    def set_text(self, new_text):
        """Atualiza o texto dinamicamente (útil para o Nickname)."""
        if new_text != self.text:
            self.text = new_text
            self.update_surface()

    def draw(self, screen):
        """Desenha o rótulo na tela."""
        screen.blit(self.surface, self.rect)