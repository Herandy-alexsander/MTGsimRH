import pygame
from pathlib import Path
from APP.UI.screens.base_screens import BaseScreen
from APP.UI.styles import colors
from APP.UI.styles.fonts import get_fonts
from APP.UI.components.button import MenuButton
from APP.UI.components.label import Label
from APP.UI.layout.grid import LayoutEngine 

class DeckManagerView(BaseScreen):
    def __init__(self, screen, controller, deck_ctrl):
        super().__init__(screen, controller)
        self.deck_ctrl = deck_ctrl
        self.fontes = get_fonts()
        
        self.cx = self.screen.get_width() // 2
        self.cy = self.screen.get_height() // 2
        
        # --- Configurações da Grade ---
        self.deck_w, self.deck_h = 160, 220  
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

        # --- MUDANÇA: BOTÃO CONFIRMAR SELEÇÃO ---
        self.btn_confirmar = MenuButton(
            pygame.Rect(self.cx - 150, self.screen.get_height() - 75, 300, 50), 
            "CONFIRMAR SELEÇÃO", self.fontes['menu']
        )
        
        # --- Controles de Paginação ---
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
                surf = pygame.image.load(str(caminho_fisico)).convert_alpha()
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
        self.btn_confirmar.update(mouse_pos) # Atualiza o botão de confirmar
        
        if self.deck_ctrl.total_paginas() > 1:
            self.btn_prev.update(mouse_pos)
            self.btn_next.update(mouse_pos)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.btn_voltar.is_clicked(event): return "MENU"
                if self.btn_cadastrar.is_clicked(event): return "DECK_REGISTER"
                
                # --- MUDANÇA: RETORNA PARA O MENU COM O DECK SELECIONADO ---
                if self.btn_confirmar.is_clicked(event) and self.deck_ctrl.get_deck_atual(): 
                    return "MENU"
                
                # Paginação
                if self.btn_prev.is_clicked(event): self.deck_ctrl.mudar_pagina(-1)
                if self.btn_next.is_clicked(event): self.deck_ctrl.mudar_pagina(1)

                # CLIQUE NOS DECKS (Apenas Seleção Visual na memória)
                decks_pagina = self.deck_ctrl.obter_decks_pagina_atual()
                posicoes = LayoutEngine.get_grid_layout(self.area_grid, len(decks_pagina), self.deck_w, self.deck_h, padding=25)
                
                for i, pos in enumerate(posicoes):
                    rect_deck = pygame.Rect(pos[0], pos[1], self.deck_w, self.deck_h)
                    if rect_deck.collidepoint(event.pos):
                        indice_global = (self.deck_ctrl.pagina_atual * self.deck_ctrl.decks_por_pagina) + i
                        self.deck_ctrl.selecionar_deck_por_indice_geral(indice_global)

        return None

    def draw(self):
        self.screen.fill(colors.BG)
        self.label_titulo.draw(self.screen)
        self.btn_cadastrar.draw(self.screen)
        self.btn_voltar.draw(self.screen)
        
        # Só desenha o botão CONFIRMAR se um deck estiver selecionado
        if self.deck_ctrl.get_deck_atual():
            self.btn_confirmar.draw(self.screen)

        total_total = len(self.deck_ctrl.decks_disponiveis)
        Label(f"COLEÇÃO: {total_total} DECKS", (self.cx, 95), self.fontes['label'], colors.TEXT_SEC).draw(self.screen)

        decks_pagina = self.deck_ctrl.obter_decks_pagina_atual()
        
        if not decks_pagina:
            Label("Nenhum deck encontrado.", (self.cx, self.cy), self.fontes['status'], colors.TEXT_SEC).draw(self.screen)
        else:
            posicoes = LayoutEngine.get_grid_layout(self.area_grid, len(decks_pagina), self.deck_w, self.deck_h, padding=25)
            
            for i, (x, y) in enumerate(posicoes):
                deck = decks_pagina[i]
                surf = self._get_local_image_small(deck.get('cover_image_path'))
                rect_capa = pygame.Rect(x, y, self.deck_w, self.deck_h)
                
                # --- EFEITO DE BORDA VERDE NO DECK SELECIONADO ---
                indice_global = (self.deck_ctrl.pagina_atual * self.deck_ctrl.decks_por_pagina) + i
                if self.deck_ctrl.index_deck_atual == indice_global:
                    pygame.draw.rect(self.screen, colors.SUCCESS, rect_capa.inflate(12, 12), border_radius=8)
                
                if surf:
                    self.screen.blit(surf, rect_capa)
                else:
                    pygame.draw.rect(self.screen, (40, 40, 45), rect_capa, border_radius=5)
                    
                pygame.draw.rect(self.screen, colors.INPUT_BORDER, rect_capa, 2, border_radius=5)
                
                txt_nome = self.fontes['status'].render(deck['name'][:18], True, colors.TEXT_PRIMARY)
                self.screen.blit(txt_nome, (x + 5, y + self.deck_h + 8))

            if self.deck_ctrl.total_paginas() > 1:
                pag_txt = f"PÁGINA {self.deck_ctrl.pagina_atual + 1} / {self.deck_ctrl.total_paginas()}"
                Label(pag_txt, (self.cx, self.screen.get_height() - 25), self.fontes['label'], colors.TEXT_SEC).draw(self.screen)
                self.btn_prev.draw(self.screen)
                self.btn_next.draw(self.screen)