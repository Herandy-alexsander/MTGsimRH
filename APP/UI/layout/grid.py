# APP/UI/layout/grid.py
import pygame

class LayoutEngine:
    @staticmethod
    def get_hand_layout(rect_area, card_count, card_w, card_h):
        """
        Calcula as posições das cartas na mão com sobreposição dinâmica.
        Garante que a mão esteja sempre centralizada na área do jogador.
        """
        if card_count == 0:
            return []

        # Define a largura máxima que a mão pode ocupar (85% da área disponível)
        max_hand_w = rect_area.width * 0.85
        
        # Se as cartas couberem lado a lado com um pequeno espaço (10px)
        if (card_count * (card_w + 10)) <= max_hand_w:
            spacing = card_w + 10
            total_w = card_count * spacing - 10
        else:
            # Se não couberem, calcula a sobreposição necessária para caber no limite
            spacing = (max_hand_w - card_w) / (card_count - 1) if card_count > 1 else 0
            total_w = max_hand_w

        # Calcula o ponto inicial para que o bloco de cartas fique centralizado
        start_x = rect_area.x + (rect_area.width - total_w) // 2
        # Posiciona as cartas 15px acima da borda inferior da zona do jogador
        y = rect_area.bottom - card_h - 15
        
        positions = []
        for i in range(card_count):
            x = start_x + (i * spacing)
            positions.append((x, y))
            
        return positions

    @staticmethod
    def get_grid_layout(rect_area, card_count, card_w, card_h, padding=12):
        """
        Calcula posições em grade (linhas e colunas) para o Campo de Batalha.
        Ideal para organizar criaturas e permanentes.
        """
        if card_count == 0:
            return []

        # Calcula quantas colunas cabem na largura da zona, respeitando o padding
        cols = max(1, int((rect_area.width - padding) // (card_w + padding)))
        
        # Define o recuo inicial para não colar nas bordas da zona
        start_x = rect_area.x + padding
        # Deixa 30px de espaço no topo para o título da zona (ex: "CAMPO DE BATALHA")
        start_y = rect_area.y + 35
        
        positions = []
        for i in range(card_count):
            row = i // cols
            col = i % cols
            
            x = start_x + col * (card_w + padding)
            y = start_y + row * (card_h + padding)
            positions.append((x, y))
            
        return positions