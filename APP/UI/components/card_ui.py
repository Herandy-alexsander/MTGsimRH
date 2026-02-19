import pygame
from APP.UI.styles import colors
from APP.UI.styles.fonts import get_fonts
from APP.domain.models.card_model import CardModel

class CardUI:
    def __init__(self, card_model: CardModel, asset_manager, x: int, y: int, w: int = 75, h: int = 105):
        """
        Componente Visual da Carta. 
        Agora corrigido para usar caminhos diretos e evitar TypeError.
        """
        self.card = card_model
        self.asset_manager = asset_manager
        self.rect = pygame.Rect(x, y, w, h)
        self.fontes = get_fonts()
        
        self.is_hovered = False
        self._img_surface = None
        self._img_tapped = None 

    def update_position(self, x: int, y: int):
        self.rect.x = x
        self.rect.y = y

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.is_hovered
        return False

    def draw(self, screen):
        """Renderiza a carta com suporte a imagens reais e fallback visual."""
        
        # 1. Tenta carregar a imagem real se o cache estiver vazio
        if self._img_surface is None:
            # PULO DO GATO: Pegamos o caminho direto que o seu JSON já tem
            caminho_direto = self.card.local_image_path
            
            # CHAMADA CORRIGIDA: Removemos o 'category=categoria' 
            # para bater com a nova assinatura do AssetManager.get_card_image(self, local_path)
            img_bruta = self.asset_manager.get_card_image(caminho_direto)
            
            if img_bruta:
                # Otimização: Escala para a memória RAM uma única vez
                self._img_surface = pygame.transform.smoothscale(img_bruta, (self.rect.width, self.rect.height))
                self._img_tapped = pygame.transform.rotate(self._img_surface, -90)
            else:
                # FALLBACK: Se a imagem física não existir, desenha o card colorido
                self._img_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
                cor = (40, 80, 40) if self.card.is_land else (40, 40, 70)
                pygame.draw.rect(self._img_surface, cor, self._img_surface.get_rect(), border_radius=5)
                
                # Escreve o nome da carta para você saber quem ela é
                txt_nome = self.fontes['status'].render(self.card.name[:12], True, (255, 255, 255))
                self._img_surface.blit(txt_nome, (5, 5))

        # 2. Define o frame de desenho baseado no estado (Virada ou Não)
        imagem_final = self._img_tapped if self.card.is_tapped and self._img_tapped else self._img_surface
        pos_desenho = imagem_final.get_rect(center=self.rect.center)

        # 3. Sombra de Elevação no Hover
        if self.is_hovered:
            sombra_rect = pos_desenho.move(4, 4)
            pygame.draw.rect(screen, (0, 0, 0, 80), sombra_rect, border_radius=5)

        # 4. Desenha a Imagem Principal
        screen.blit(imagem_final, pos_desenho.topleft)

        # 5. Bordas e Destaques Dinâmicos
        borda_cor = colors.TEXT_SEC
        borda_w = 1

        if self.is_hovered:
            borda_cor = colors.ACCENT
            borda_w = 3
        elif self.card.is_land and not self.card.is_tapped:
            borda_cor = (0, 255, 0) # Brilho verde para terrenos prontos

        pygame.draw.rect(screen, borda_cor, pos_desenho, borda_w, border_radius=5)

        # 6. Renderiza os Marcadores
        if self.card.counters:
            self._draw_counters(screen, pos_desenho)

    def _draw_counters(self, screen, draw_rect):
        """Desenha bolinhas de marcadores no canto inferior."""
        count_pos = [draw_rect.right - 12, draw_rect.bottom - 12]
        for tipo, qtd in self.card.counters.items():
            pygame.draw.circle(screen, (220, 20, 20), count_pos, 10)
            txt = self.fontes['status'].render(str(qtd), True, (255, 255, 255))
            screen.blit(txt, (count_pos[0] - 5, count_pos[1] - 8))
            count_pos[1] -= 22