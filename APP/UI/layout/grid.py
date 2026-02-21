# APP/UI/layout/grid.py
import pygame

class LayoutEngine:
    @staticmethod
    def get_hand_layout(rect_area, card_count, card_w, card_h, is_group_focused=False):
        """
        Calcula as posições das cartas na mão com suporte a ZOOM DE GRUPO.
        is_group_focused: Se True, as cartas sobem e aumentam de tamanho.
        """
        if card_count == 0:
            return []

        # PULO DO GATO: Se o grupo estiver focado, aumentamos o tamanho base (Zoom 1.3x)
        zoom_factor = 1.3 if is_group_focused else 1.0
        w_zoom = int(card_w * zoom_factor)
        h_zoom = int(card_h * zoom_factor)

        # Define a largura máxima (95% da área para o zoom não cortar as bordas)
        max_hand_w = rect_area.width * 0.95
        
        # Calcula o espaçamento dinâmico entre as cartas
        if (card_count * (w_zoom + 5)) <= max_hand_w:
            spacing = w_zoom + 5
            total_w = card_count * spacing - 5
        else:
            spacing = (max_hand_w - w_zoom) / (card_count - 1) if card_count > 1 else 0
            total_w = max_hand_w

        # Calcula o ponto inicial para centralização
        start_x = rect_area.x + (rect_area.width - total_w) // 2
        
        # POSICIONAMENTO VERTICAL: Se focado, a mão "sobe" (y menor)
        # O offset de 45px garante que o leque se destaque do fundo da tela
        y_base = rect_area.bottom - h_zoom - (45 if is_group_focused else 10)
        
        positions = []
        for i in range(card_count):
            x = start_x + (i * spacing)
            # Retornamos (x, y, zoom) para que a View saiba como desenhar cada carta
            positions.append((x, y_base, zoom_factor))
            
        return positions

    @staticmethod
    def get_grid_layout(rect_area, card_count, card_w, card_h, padding=12):
        """
        Organiza cartas em grade (Campo ou Mana) centralizando as colunas.
        """
        if card_count == 0:
            return []

        cols_possiveis = max(1, int((rect_area.width - padding) // (card_w + padding)))
        cols = min(card_count, cols_possiveis)
        
        largura_grid = (cols * (card_w + padding)) - padding
        start_x = rect_area.x + (rect_area.width - largura_grid) // 2
        start_y = rect_area.y + 30
        
        positions = []
        for i in range(card_count):
            row = i // cols_possiveis
            col = i % cols_possiveis
            x = start_x + col * (card_w + padding)
            y = start_y + row * (card_h + padding)
            positions.append((x, y))
            
        return positions