import pygame
import os
from APP.utils.style import GameStyle
from APP.utils.ui_components import MenuButton

class DeckListView:
    def __init__(self, screen, controller, storage):
        """
        Galeria Visual de Decks (Grade 6x2) com Modo de Seleção.
        """
        self.screen = screen
        self.controller = controller
        self.storage = storage
        self.largura, self.altura = screen.get_size()
        self.fontes = GameStyle.get_fonts()
        
        # --- Estados de Controle ---
        self.modo_selecao = False # Alternado pelo ViewManager
        self.selected_index = None
        
        # --- Configuração da Grade ---
        self.cols = 6
        self.rows = 2
        self.max_decks = self.cols * self.rows # Máximo 12 decks por página
        
        self.card_w = 130
        self.card_h = 182
        self.gap_x = 25
        self.gap_y = 45 # Espaço extra para o nome do deck abaixo da carta
        
        largura_total_grid = (self.cols * self.card_w) + ((self.cols - 1) * self.gap_x)
        self.start_x = (self.largura - largura_total_grid) // 2
        self.start_y = 160 
        
        # --- Dados e Imagens ---
        self.decks = []
        self.imagens_cache = {} # Cache de superfícies Pygame
        self.recarregar_lista()
        
        # --- Botões de Interface ---
        cx = self.largura // 2
        # Botão JOGAR: Só aparece em modo_selecao
        self.btn_jogar = MenuButton(
            pygame.Rect(cx - 100, self.altura - 90, 200, 50), 
            "INICIAR JOGO", 
            self.fontes['menu']
        )
        self.btn_voltar = MenuButton(
            pygame.Rect(20, 20, 100, 40), 
            "VOLTAR", 
            self.fontes['menu']
        )

    def recarregar_lista(self):
        """Sincroniza a galeria com os arquivos em disco."""
        self.decks = self._carregar_dados_decks()
        self.imagens_cache = {}
        self.selected_index = None
        
        # Pré-carrega as capas (Comandantes) para evitar stuttering no draw()
        for i, deck in enumerate(self.decks):
            if i >= self.max_decks: break
            cmd_nome = deck.get('commander', '')
            self.imagens_cache[i] = self._buscar_imagem_commander(cmd_nome)

    def _carregar_dados_decks(self):
        """Lê os metadados do profiler.json."""
        perfil = self.storage.carregar_perfil()
        return perfil.get("decks_info", {}).get("decks", [])

    def _buscar_imagem_commander(self, nome_commander):
        """Localiza e escala a imagem do comandante para a grade."""
        if not nome_commander: return None
        
        nome_arq = nome_commander.replace(" ", "_").lower().replace("/", "") + ".jpg"
        caminhos = [
            os.path.join("assets", "cards", "Criaturas", nome_arq),
            os.path.join("assets", "cards", "Legendary", nome_arq),
            os.path.join("assets", "cards", "Outros", nome_arq)
        ]
        
        for caminho in caminhos:
            if os.path.exists(caminho):
                try:
                    img = pygame.image.load(caminho).convert()
                    return pygame.transform.scale(img, (self.card_w, self.card_h))
                except: pass
        return None

    def handle_events(self, events):
        """Gerencia seleção de deck e confirmação de partida."""
        mouse_pos = pygame.mouse.get_pos()
        self.btn_voltar.update(mouse_pos)
        
        # Trava visual: botão JOGAR só responde se o modo seleção estiver ON
        if self.modo_selecao and self.selected_index is not None:
            self.btn_jogar.update(mouse_pos)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # 1. Clique na Grade de Cartas
                for i in range(len(self.decks)):
                    if i >= self.max_decks: break
                    col, row = i % self.cols, i // self.cols
                    x = self.start_x + col * (self.card_w + self.gap_x)
                    y = self.start_y + row * (self.card_h + self.gap_y)
                    
                    if pygame.Rect(x, y, self.card_w, self.card_h).collidepoint(event.pos):
                        self.selected_index = i
                
                # 2. Botão Voltar
                if self.btn_voltar.is_clicked(event):
                    return "MENU"
                
                # 3. Botão Iniciar Jogo (Confirmação Final)
                if self.modo_selecao and self.selected_index is not None:
                    if self.btn_jogar.is_clicked(event):
                        deck_escolhido = self.decks[self.selected_index]
                        # Dispara o carregamento do JSON completo no DeckController
                        if self.controller.carregar_deck_para_jogo(deck_escolhido['id']):
                            return "JOGO" # Avisa o ViewManager para trocar de tela
        return None

    def draw(self):
        """Renderiza a grade visual e os estados de seleção."""
        self.screen.fill(GameStyle.COLOR_BG)
        cx = self.largura // 2

        # Título Contextual
        titulo_str = "ESCOLHA SEU COMANDANTE" if self.modo_selecao else "GALERIA DE DECKS"
        txt_titulo = self.fontes['titulo'].render(titulo_str, True, GameStyle.COLOR_ACCENT)
        self.screen.blit(txt_titulo, (cx - txt_titulo.get_width() // 2, 60))

        # --- Renderização da Grade ---
        if not self.decks:
            msg = self.fontes['menu'].render("Colecao Vazia. Cadastre um deck primeiro.", True, (80, 80, 80))
            self.screen.blit(msg, (cx - msg.get_width() // 2, 350))
        else:
            for i, deck in enumerate(self.decks):
                if i >= self.max_decks: break
                col, row = i % self.cols, i // self.cols
                x = self.start_x + col * (self.card_w + self.gap_x)
                y = self.start_y + row * (self.card_h + self.gap_y)
                rect = pygame.Rect(x, y, self.card_w, self.card_h)
                
                # Capa do Deck
                img = self.imagens_cache.get(i)
                if img:
                    self.screen.blit(img, (x, y))
                else:
                    # Fallback visual
                    pygame.draw.rect(self.screen, (30, 30, 35), rect, border_radius=6)
                    pygame.draw.rect(self.screen, (50, 50, 55), rect, 1, border_radius=6)
                
                # Destaque Dourado para a Seleção
                if i == self.selected_index:
                    # Borda externa brilhante
                    pygame.draw.rect(self.screen, GameStyle.COLOR_ACCENT, rect.inflate(8, 8), 3, border_radius=8)
                else:
                    # Borda discreta padrão
                    pygame.draw.rect(self.screen, (20, 20, 20), rect, 1, border_radius=6)

                # Rótulo do Nome do Deck
                nome_deck = deck.get('name', 'Sem Nome')
                cor_txt = GameStyle.COLOR_ACCENT if i == self.selected_index else (180, 180, 180)
                txt_n = self.fontes['label'].render(nome_deck[:16], True, cor_txt)
                self.screen.blit(txt_n, (rect.centerx - txt_n.get_width() // 2, rect.bottom + 8))

        # Renderização dos Botões
        self.btn_voltar.draw(self.screen)
        
        # O botão JOGAR só é renderizado se houver algo selecionado E estiver em modo jogo
        if self.modo_selecao and self.selected_index is not None:
            self.btn_jogar.draw(self.screen)