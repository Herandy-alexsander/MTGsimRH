import pygame
from pathlib import Path
from APP.UI.screens.base_screens import BaseScreen
from APP.UI.styles import colors
from APP.UI.styles.fonts import get_fonts
from APP.UI.components.button import MenuButton
from APP.UI.components.label import Label
from APP.UI.layout.grid import LayoutEngine  # Certifique-se de que o grid.py está na pasta layout

class DeckManagerView(BaseScreen):
    def __init__(self, screen, controller, deck_ctrl):
        super().__init__(screen, controller)
        self.deck_ctrl = deck_ctrl
        self.fontes = get_fonts()
        
        self.cx = self.screen.get_width() // 2
        self.cy = self.screen.get_height() // 2
        
        # --- Configurações da Grade ---
        self.deck_w, self.deck_h = 160, 220  # Tamanho reduzido para caber 12
        self.area_grid = pygame.Rect(100, 130, self.screen.get_width() - 200, self.screen.get_height() - 280)
        
        # --- Elementos Fixos ---
        self.label_titulo = Label("GALERIA DE DECKS", (self.cx, 50), self.fontes['titulo'], colors.ACCENT)
        
        self.btn_cadastrar = MenuButton(
            pygame.Rect(self.screen.get_width() - 220, 30, 180, 45), 
            "NOVO DECK", self.fontes['menu']
        )
        
        self.btn_voltar = MenuButton(
            pygame.Rect(40, self.screen.get_height() - 70, 140, 40), 
            "VOLTAR", self.fontes['menu']
        )
        
        # --- Controles de Paginação (Posicionados nas laterais da grade) ---
        self.btn_prev = MenuButton(pygame.Rect(20, self.cy - 30, 50, 60), "<", self.fontes['menu'])
        self.btn_next = MenuButton(pygame.Rect(self.screen.get_width() - 70, self.cy - 30, 50, 60), ">", self.fontes['menu'])
        
        self.img_cache_local = {}

        if hasattr(self.deck_ctrl, 'reload_data'):
            self.deck_ctrl.reload_data()

    def _get_local_image_small(self, caminho):
        """Lê e redimensiona a imagem para o tamanho da grade."""
        if not caminho: return None
        if caminho in self.img_cache_local: return self.img_cache_local[caminho]
        
        try:
            caminho_fisico = Path(caminho)
            if caminho_fisico.exists():
                surf = pygame.image.load(str(caminho_fisico))
                surf = pygame.transform.smoothscale(surf, (self.deck_w, self.deck_h))
                self.img_cache_local[caminho] = surf
                return surf
        except Exception:
            return None
        return None

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        self.btn_cadastrar.update(mouse_pos)
        self.btn_voltar.update(mouse_pos)
        
        if self.deck_ctrl.total_paginas() > 1:
            self.btn_prev.update(mouse_pos)
            self.btn_next.update(mouse_pos)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.btn_voltar.is_clicked(event): return "MENU"
                if self.btn_cadastrar.is_clicked(event): return "DECK_REGISTER"
                
                # Paginação
                if self.btn_prev.is_clicked(event): self.deck_ctrl.mudar_pagina(-1)
                if self.btn_next.is_clicked(event): self.deck_ctrl.mudar_pagina(1)

                # Clique nos Decks (Detecção de qual deck foi clicado na grade)
                decks_pagina = self.deck_ctrl.obter_decks_pagina_atual()
                posicoes = LayoutEngine.get_grid_layout(self.area_grid, len(decks_pagina), self.deck_w, self.deck_h, padding=25)
                
                for i, pos in enumerate(posicoes):
                    rect_deck = pygame.Rect(pos[0], pos[1], self.deck_w, self.deck_h)
                    if rect_deck.collidepoint(event.pos):
                        # Calcula o índice global do deck e seleciona
                        indice_global = (self.deck_ctrl.pagina_atual * self.deck_ctrl.decks_por_pagina) + i
                        if self.deck_ctrl.selecionar_deck_por_indice_geral(indice_global):
                            return "GAME_START"

        return None

    def draw(self):
        self.screen.fill(colors.BG)
        self.label_titulo.draw(self.screen)
        self.btn_cadastrar.draw(self.screen)
        self.btn_voltar.draw(self.screen)

        # 1. Contador de Decks (Topo)
        total_total = len(self.deck_ctrl.decks_disponiveis)
        Label(f"COLEÇÃO: {total_total} DECKS", (self.cx, 95), self.fontes['label'], colors.TEXT_SEC).draw(self.screen)

        decks_pagina = self.deck_ctrl.obter_decks_pagina_atual()
        
        if not decks_pagina:
            Label("Nenhum deck encontrado.", (self.cx, self.cy), self.fontes['status'], colors.TEXT_SEC).draw(self.screen)
        else:
            # 2. Desenha a Grade
            posicoes = LayoutEngine.get_grid_layout(self.area_grid, len(decks_pagina), self.deck_w, self.deck_h, padding=25)
            
            for i, (x, y) in enumerate(posicoes):
                deck = decks_pagina[i]
                surf = self._get_local_image_small(deck.get('cover_image_path'))
                
                rect_capa = pygame.Rect(x, y, self.deck_w, self.deck_h)
                
                if surf:
                    self.screen.blit(surf, rect_capa)
                else:
                    pygame.draw.rect(self.screen, (40, 40, 45), rect_capa, border_radius=5)
                    pygame.draw.rect(self.screen, colors.INPUT_BORDER, rect_capa, 1, border_radius=5)
                
                # Nome do deck sob a imagem
                txt_nome = self.fontes['status'].render(deck['name'][:18], True, colors.TEXT_PRIMARY)
                self.screen.blit(txt_nome, (x + 5, y + self.deck_h + 5))

            # 3. Contador de Páginas (Rodapé)
            if self.deck_ctrl.total_paginas() > 1:
                pag_txt = f"PÁGINA {self.deck_ctrl.pagina_atual + 1} / {self.deck_ctrl.total_paginas()}"
                Label(pag_txt, (self.cx, self.screen.get_height() - 40), self.fontes['label'], colors.TEXT_SEC).draw(self.screen)
                self.btn_prev.draw(self.screen)
                self.btn_next.draw(self.screen)