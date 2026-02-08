import pygame
from mtg_commander_app.utils.style import GameStyle

class MenuButton:
    def __init__(self, rect, text, font):
        self.rect = rect
        self.text = text
        self.font = font
        self.is_hovered = False

    def update(self, mouse_pos):
        """Atualiza o estado de hover do botão."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
        """Desenha o botão com bordas metálicas e profundidade estilo MTG."""
        cor_borda = GameStyle.COLOR_ACCENT if self.is_hovered else (100, 100, 100)
        
        # Sombra e Borda Externa
        pygame.draw.rect(screen, (10, 10, 10), self.rect.move(2, 2), border_radius=8)
        pygame.draw.rect(screen, cor_borda, self.rect, border_radius=8)
        
        # Preenchimento Interno
        corpo_rect = self.rect.inflate(-4, -4)
        pygame.draw.rect(screen, (60, 60, 65), corpo_rect, border_radius=6)
        
        # Texto Centralizado
        cor_texto = (255, 255, 255) if self.is_hovered else (200, 200, 200)
        text_surf = self.font.render(self.text, True, cor_texto)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event):
        """Verifica clique com o botão esquerdo do mouse."""
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered

class UIComponents:
    def __init__(self, largura, altura):
        self.LARGURA, self.ALTURA = largura, altura
        cx = largura // 2
        
        # --- DEFINIÇÃO DE CAMADAS VERTICAIS (Y) ---
        # Removido o y_input_sala para centralizar o Nickname no Menu
        y_botoes_jogadores = 390
        y_botao_abrir = 480
        y_botao_cadastrar = 550

        # --- COMPONENTES DO MENU PRINCIPAL ---
        # O campo_texto_sala foi desativado conforme o novo design
        self.campo_texto_sala = None 
        
        largura_btn_jog = 80
        self.rects_jogadores = {
            2: pygame.Rect(cx - 135, y_botoes_jogadores, largura_btn_jog, 40),
            3: pygame.Rect(cx - 40, y_botoes_jogadores, largura_btn_jog, 40),
            4: pygame.Rect(cx + 55, y_botoes_jogadores, largura_btn_jog, 40)
        }
        
        self.rect_criar = pygame.Rect(cx - 150, y_botao_abrir, 300, 50)
        self.rect_cadastrar = pygame.Rect(cx - 150, y_botao_cadastrar, 300, 50)

        # --- COMPONENTES DE GESTÃO (CADASTRO/UPDATE) ---
        self.btn_voltar = pygame.Rect(20, 20, 100, 40)
        self.rect_input_nome_deck = pygame.Rect(cx - 150, 200, 300, 40)
        self.btn_selecionar_arquivo = pygame.Rect(cx - 150, 300, 300, 50) 
        self.btn_confirmar_cadastro = pygame.Rect(cx - 150, 450, 300, 50)
        
        # --- COMPONENTES DE JOGO (MATCH) ---
        self.btn_manter_mao = pygame.Rect(cx - 210, altura // 2 + 80, 200, 60)
        self.btn_fazer_mulligan = pygame.Rect(cx + 10, altura // 2 + 80, 200, 60)

    @staticmethod
    def desenhar_caixa_texto(surface, rect, texto, fonte, ativo, placeholder=""):
        """Desenha campos de input utilizando as novas constantes do GameStyle."""
        # Utiliza as novas cores de borda ativa definidas no style.py
        cor_borda = getattr(GameStyle, 'COLOR_INPUT_ACTIVE', (100, 100, 255)) if ativo else getattr(GameStyle, 'COLOR_INPUT_BORDER', (80, 80, 80))
        cor_fundo = getattr(GameStyle, 'COLOR_INPUT_BG', (30, 30, 35))
        
        pygame.draw.rect(surface, cor_fundo, rect, border_radius=5)
        pygame.draw.rect(surface, cor_borda, rect, 2, border_radius=5)
        
        txt_final = texto if texto else placeholder
        # RESOLUÇÃO DO ERRO: Usa COLOR_TEXT agora presente no GameStyle
        cor_txt = GameStyle.COLOR_TEXT if texto else (120, 120, 120)
        img_texto = fonte.render(txt_final, True, cor_txt)
        surface.blit(img_texto, (rect.x + 10, rect.centery - img_texto.get_height() // 2))