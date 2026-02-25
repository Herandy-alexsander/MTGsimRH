import pygame
import os
from APP.UI.styles.colors import SUCCESS, TEXT_SEC

class ManaBarUI:
    def __init__(self, fontes):
        self.fontes = fontes
        # Já carrega e fatia a imagem assim que o componente é criado
        self.icones_mana = self._carregar_icones()

    def _carregar_icones(self):
        """Corta a sua imagem manas.png automaticamente ou gera bolinhas coloridas se falhar."""
        icones = {}
        caminho_sprite = "assets/img/manas.png"
        
        if os.path.exists(caminho_sprite):
            try:
                img_full = pygame.image.load(caminho_sprite).convert_alpha()
                bbox = img_full.get_bounding_rect()
                if bbox.width > 0 and bbox.height > 0:
                    img_crop = img_full.subsurface(bbox)
                    
                    # Fatiador: 5 colunas x 2 linhas
                    cw = img_crop.get_width() / 5
                    ch = img_crop.get_height() / 2
                    
                    # Mapeamento do seu arquivo (X, Y)
                    mapa = {
                        'W': (0, 0), 'U': (1, 0), 'B': (2, 0),
                        'R': (3, 0), 'G': (4, 0), 'C': (2, 1) 
                    }
                    
                    for tipo, (col, lin) in mapa.items():
                        rect = pygame.Rect(col * cw, lin * ch, cw, ch)
                        pedaco = img_crop.subsurface(rect)
                        icones[tipo] = pygame.transform.smoothscale(pedaco, (24, 24))
                    
                    print("[UI] Ícones de mana fatiados com sucesso pelo ManaBarUI!")
                    return icones
            except Exception as e:
                print(f"[AVISO] Não foi possível fatiar manas.png: {e}")

        # FALLBACK (Bolinhas coloridas de segurança caso a imagem falhe)
        cores = {'W': (250, 250, 240), 'U': (80, 150, 220), 'B': (40, 40, 40), 
                 'R': (220, 60, 40), 'G': (60, 160, 80), 'C': (140, 140, 140)}
        for tipo, cor in cores.items():
            surf = pygame.Surface((24, 24), pygame.SRCALPHA)
            pygame.draw.circle(surf, cor, (12, 12), 12)
            pygame.draw.circle(surf, (20, 20, 20), (12, 12), 12, 1) # Borda
            
            # Tenta usar a fonte 'status' ou 'label' como reserva
            fonte_letra = self.fontes.get('status', self.fontes.get('label'))
            letra = fonte_letra.render(tipo, True, (0,0,0) if tipo in ['W','C'] else (255,255,255))
            surf.blit(letra, (12 - letra.get_width()//2, 12 - letra.get_height()//2))
            icones[tipo] = surf
        return icones

    def draw(self, screen, player, area):
        """Desenha a barra centralizada abaixo do nome do jogador."""
        # Se o player não tiver mana_pool inicializada, evita erro
        pool = getattr(player, 'mana_pool', {})
        
        y = area.y + 40 # Ajustado para não sobrepor o nome do jogador
        tipos_mana = ['W', 'U', 'B', 'R', 'G', 'C']
        espacamento = 55
        largura_total = len(tipos_mana) * espacamento
        start_x = area.centerx - (largura_total // 2)
        
        for i, m_type in enumerate(tipos_mana):
            qtd = pool.get(m_type, 0)
            x = start_x + (i * espacamento)
            
            # Desenha o ícone
            icone = self.icones_mana.get(m_type)
            if icone:
                screen.blit(icone, (x, y))
            
            # Desenha a quantidade ao lado do ícone
            cor_qtd = SUCCESS if qtd > 0 else TEXT_SEC
            txt_qtd = self.fontes['label'].render(str(qtd), True, cor_qtd)
            # Alinhamento vertical centralizado com o ícone de 24px
            screen.blit(txt_qtd, (x + 28, y + (12 - txt_qtd.get_height() // 2)))
