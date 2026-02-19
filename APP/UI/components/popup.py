import pygame
from APP.UI.styles import colors, settings
from APP.UI.components.button import MenuButton
from APP.UI.components.label import Label

class Popup:
    def __init__(self, title_text, sub_text, font_dict):
        """
        Componente de Pop-up para avisos e mensagens do sistema Machete.
        """
        self.largura = settings.SCREEN_WIDTH
        self.altura = settings.SCREEN_HEIGHT
        
        # Dimensões da Caixa
        self.rect = pygame.Rect(0, 0, 450, 220)
        self.rect.center = (self.largura // 2, self.altura // 2)
        
        # Cores e Estilo
        self.color_bg = (25, 25, 30)
        self.color_border = colors.DANGER  # Usa o vermelho de alerta
        
        # Componentes Internos
        self.label_titulo = Label(
            title_text, 
            (self.rect.centerx, self.rect.y + 45), 
            font_dict['popup'], 
            colors.TEXT_PRIMARY
        )
        
        self.label_sub = Label(
            sub_text, 
            (self.rect.centerx, self.rect.y + 90), 
            font_dict['label'], 
            (180, 180, 180)
        )
        
        # Botão de Fechar reaproveitando sua lógica de MenuButton
        btn_rect = pygame.Rect(0, 0, 150, 45)
        btn_rect.center = (self.rect.centerx, self.rect.y + 160)
        self.btn_fechar = MenuButton(btn_rect, "FECHAR", font_dict['menu'])

    def handle_event(self, event):
        """Retorna True se o botão de fechar for clicado."""
        if self.btn_fechar.is_clicked(event):
            return True
        return False

    def update(self, mouse_pos):
        """Atualiza o estado de hover do botão interno."""
        self.btn_fechar.update(mouse_pos)

    def draw(self, screen):
        """Desenha o overlay e a caixa de popup."""
        # 1. Overlay semi-transparente (Escurece o fundo)
        overlay = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)) 
        screen.blit(overlay, (0, 0))
        
        # 2. Caixa do Pop-up
        pygame.draw.rect(screen, self.color_bg, self.rect, border_radius=12)
        pygame.draw.rect(screen, self.color_border, self.rect, 2, border_radius=12)
        
        # 3. Desenha os componentes
        self.label_titulo.draw(screen)
        self.label_sub.draw(screen)
        self.btn_fechar.draw(screen)