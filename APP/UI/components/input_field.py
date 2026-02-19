import pygame
from APP.UI.styles import colors  # Usa sua paleta de cores

class InputField:
    def __init__(self, rect, font, placeholder="Digite aqui..."):
        self.rect = rect
        self.font = font
        self.placeholder = placeholder
        self.text = ""
        self.active = False
        
        # Cores vindas do seu colors.py
        self.color_bg = colors.INPUT_BG
        self.color_inactive = colors.INPUT_BORDER
        self.color_active = colors.INPUT_ACTIVE
        self.color_text = colors.TEXT_PRIMARY

    def handle_event(self, event):
        """Gerencia cliques e digitação."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Ativa se clicar dentro, desativa se clicar fora
            self.active = self.rect.collidepoint(event.pos)
            
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False # Finaliza a edição ao dar Enter
            else:
                # BLINDAGEM: Limite de caracteres E impede caracteres invisíveis
                if len(self.text) < 20 and event.unicode.isprintable():
                    self.text += event.unicode

    def draw(self, screen):
        """Desenha o campo de input com estilo MTG."""
        # 1. Fundo do campo
        pygame.draw.rect(screen, self.color_bg, self.rect, border_radius=5)
        
        # 2. Borda dinâmica (muda de cor se estiver ativo)
        cor_borda = self.color_active if self.active else self.color_inactive
        pygame.draw.rect(screen, cor_borda, self.rect, 2, border_radius=5)
        
        # 3. Renderização do Texto ou Placeholder
        txt_final = self.text if self.text else self.placeholder
        cor_final = self.color_text if self.text else (120, 120, 120)
        
        img_texto = self.font.render(txt_final, True, cor_final)
        # Centraliza o texto verticalmente dentro do campo
        screen.blit(img_texto, (self.rect.x + 10, self.rect.centery - img_texto.get_height() // 2))

    def get_value(self):
        """Retorna o texto digitado limpo de espaços nas pontas."""
        return self.text.strip()