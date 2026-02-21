import pygame
from APP.UI.styles import colors
from APP.UI.styles.fonts import get_fonts
from APP.domain.models.card_model import CardModel

class CardUI:
    def __init__(self, card_model: CardModel, asset_manager, x: int, y: int, w: int = 75, h: int = 105):
        """
        Componente Visual da Carta corrigido para Suportar Zoom e Bloqueio Visual.
        """
        self.card = card_model
        self.asset_manager = asset_manager
        self.rect = pygame.Rect(x, y, w, h)
        self.fontes = get_fonts()
        
        self.is_hovered = False
        self.is_disabled = False # PULO DO GATO: Flag para escurecer a carta
        
        self._img_surface = None
        self._img_tapped = None
        self._last_size = (w, h) # Controle para atualizar o zoom

    def update_position(self, x: int, y: int):
        self.rect.x = x
        self.rect.y = y

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        """Detecta clique apenas se a carta estiver ativa."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.is_hovered and not self.is_disabled
        return False

    def draw(self, screen):
        """Renderiza a carta com suporte a zoom dinâmico e filtro de bloqueio."""
        
        # 1. Checagem de Redimensionamento (Zoom de Grupo)
        # Se o tamanho mudou, precisamos limpar as imagens em cache para re-escalar
        if (self.rect.width, self.rect.height) != self._last_size:
            self._img_surface = None
            self._img_tapped = None
            self._last_size = (self.rect.width, self.rect.height)

        # 2. Carregamento da Imagem
        if self._img_surface is None:
            caminho_direto = self.card.local_image_path
            img_bruta = self.asset_manager.get_card_image(caminho_direto)
            
            if img_bruta:
                self._img_surface = pygame.transform.smoothscale(img_bruta, (self.rect.width, self.rect.height))
                self._img_tapped = pygame.transform.rotate(self._img_surface, -90)
            else:
                # Fallback se a imagem falhar
                self._img_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
                cor = (40, 80, 40) if self.card.is_land else (40, 40, 70)
                pygame.draw.rect(self._img_surface, cor, self._img_surface.get_rect(), border_radius=5)
                txt_nome = self.fontes['status'].render(self.card.name[:12], True, (255, 255, 255))
                self._img_surface.blit(txt_nome, (5, 5))

        # 3. Define a Imagem Final (Normal ou Virada)
        imagem_final = self._img_tapped if self.card.is_tapped and self._img_tapped else self._img_surface.copy()

        # 4. FILTRO DE BLOQUEIO (Regra do Machete)
        # Se a carta não puder ser jogada, desenha uma camada preta por cima
        if self.is_disabled:
            filtro_escuro = pygame.Surface(imagem_final.get_size(), pygame.SRCALPHA)
            filtro_escuro.fill((0, 0, 0, 160)) # Preto semitransparente
            imagem_final.blit(filtro_escuro, (0, 0))

        pos_desenho = imagem_final.get_rect(center=self.rect.center)

        # 5. Sombra (Apenas se não estiver bloqueada)
        if self.is_hovered and not self.is_disabled:
            sombra_rect = pos_desenho.move(4, 4)
            pygame.draw.rect(screen, (0, 0, 0, 80), sombra_rect, border_radius=5)

        # 6. Desenha a Carta
        screen.blit(imagem_final, pos_desenho.topleft)

        # 7. Bordas e Destaques
        borda_cor = colors.TEXT_SEC
        borda_w = 1

        if self.is_hovered and not self.is_disabled:
            borda_cor = colors.ACCENT
            borda_w = 3
        elif self.card.is_land and not self.card.is_tapped and not self.is_disabled:
            borda_cor = (0, 255, 0) # Brilho verde para terrenos prontos

        pygame.draw.rect(screen, borda_cor, pos_desenho, borda_w, border_radius=5)

        # 8. Marcadores
        if self.card.counters:
            self._draw_counters(screen, pos_desenho)

    def _draw_counters(self, screen, draw_rect):
        count_pos = [draw_rect.right - 12, draw_rect.bottom - 12]
        for tipo, qtd in self.card.counters.items():
            pygame.draw.circle(screen, (220, 20, 20), count_pos, 10)
            txt = self.fontes['status'].render(str(qtd), True, (255, 255, 255))
            screen.blit(txt, (count_pos[0] - 5, count_pos[1] - 8))
            count_pos[1] -= 22