import pygame
from pathlib import Path
from APP.UI.styles import colors, settings
from APP.UI.styles.fonts import get_fonts
from APP.UI.components.button import MenuButton
from APP.UI.components.label import Label
from APP.UI.components.popup import Popup

class MainMenu:
    def __init__(self, screen, profile_controller, deck_controller):
        """Interface principal do simulador."""
        self.screen = screen
        self.controller = profile_controller
        self.deck_ctrl = deck_controller
        self.largura, self.altura = settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT
        
        self.fontes = get_fonts()
        self.mostrar_aviso = False
        
        nickname_inicial = self.controller.obter_nickname()
        cx = self.largura // 2
        
        # Títulos e Identificação
        self.label_titulo = Label("MTG SIMULATOR", (cx, 80), self.fontes['titulo'], colors.ACCENT)
        self.label_prefixo = Label("CONJURADOR:", (cx, 160), self.fontes['label'], (150, 150, 150))
        self.label_nickname = Label(nickname_inicial.upper(), (cx, 195), self.fontes['menu'], colors.ACCENT)

        # Botões de Seleção de Jogadores (Mantendo o 2 como Padrão)
        self.total_jogadores = 2 
        self.btns_jogadores = {}
        for i, num in enumerate([2, 3, 4]):
            rect = pygame.Rect(cx - 110 + (i * 75), 320, 60, 45)
            self.btns_jogadores[num] = MenuButton(rect, str(num), self.fontes['menu'])

        # Botões de Ação Principal
        self.btn_abrir_sala = MenuButton(pygame.Rect(cx - 150, 410, 300, 50), "ABRIR SALA", self.fontes['menu'])
        self.btn_meus_decks = MenuButton(pygame.Rect(cx - 150, 480, 300, 50), "MEUS DECKS", self.fontes['menu'])
        self.btn_sair = MenuButton(pygame.Rect(cx - 150, 600, 300, 50), "SAIR", self.fontes['menu'])
        
        self.popup_deck = None

        # --- SISTEMA DE CAPA DO DECK NO MENU ---
        self.capa_surface = None
        self._carregar_capa_selecionada()

    def _carregar_capa_selecionada(self):
        """Carrega a imagem em miniatura do deck selecionado para exibir no canto."""
        deck_info = self.deck_ctrl.get_deck_atual()
        if deck_info and deck_info.get('cover_image_path'):
            try:
                caminho = Path(deck_info['cover_image_path'])
                if caminho.exists():
                    surf = pygame.image.load(str(caminho)).convert_alpha()
                    # Redimensiona para o formato de carta no canto (120x168)
                    self.capa_surface = pygame.transform.smoothscale(surf, (120, 168)) 
            except Exception as e:
                print(f"[ERRO CAPA MENU] {e}")

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        
        for event in events:
            if self.mostrar_aviso and self.popup_deck:
                if self.popup_deck.handle_event(event):
                    self.mostrar_aviso = False
                continue
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Seleção de jogadores
                for num, btn in self.btns_jogadores.items():
                    if btn.is_clicked(event):
                        self.total_jogadores = num
                
                # ABRIR SALA: Com trava de segurança
                if self.btn_abrir_sala.is_clicked(event):
                    if not self.deck_ctrl.get_deck_atual():
                        # Bloqueio de segurança aciona o Popup
                        self.popup_deck = Popup("⚠️ ATENÇÃO", "Selecione um deck na Galeria primeiro.", self.fontes)
                        self.mostrar_aviso = True
                    else:
                        # Aqui sim, com o deck no canto da tela, ele inicia o jogo!
                        return "GAME_START"

                if self.btn_meus_decks.is_clicked(event):
                    return "DECK_MANAGER"

                if self.btn_sair.is_clicked(event):
                    return "QUIT"
        
        self._update_hovers(mouse_pos)
        return None

    def _update_hovers(self, mouse_pos):
        self.btn_abrir_sala.update(mouse_pos)
        self.btn_meus_decks.update(mouse_pos)
        self.btn_sair.update(mouse_pos)
        for btn in self.btns_jogadores.values():
            btn.update(mouse_pos)
        if self.mostrar_aviso:
            self.popup_deck.update(mouse_pos)

    def draw(self):
        self.screen.fill(colors.BG)
        
        self.label_titulo.draw(self.screen)
        self.label_prefixo.draw(self.screen)
        self.label_nickname.draw(self.screen)
        
        # -------------------------------------------------------------
        # DESENHA A CAPA E O NOME DO DECK NO CANTO SUPERIOR DIREITO
        # -------------------------------------------------------------
        deck_info = self.deck_ctrl.get_deck_atual()
        
        # Posições no canto direito da tela
        canto_x = self.largura - 170
        canto_y = 40
        rect_capa = pygame.Rect(canto_x, canto_y, 120, 168)

        if deck_info:
            # 1. Título acima da carta (DECK PRONTO)
            txt_status = self.fontes['label'].render("DECK PRONTO", True, colors.SUCCESS)
            self.screen.blit(txt_status, (canto_x + 60 - txt_status.get_width()//2, canto_y - 25))
            
            # 2. Imagem da Carta
            if self.capa_surface:
                self.screen.blit(self.capa_surface, rect_capa)
            else:
                pygame.draw.rect(self.screen, (40, 40, 45), rect_capa, border_radius=5)
            
            # 3. Borda Verde indicando confirmação
            pygame.draw.rect(self.screen, colors.SUCCESS, rect_capa, 2, border_radius=5)
            
            # 4. Nome do Deck logo abaixo da imagem
            nome_display = deck_info['name'][:14] + "..." if len(deck_info['name']) > 14 else deck_info['name']
            txt_nome = self.fontes['status'].render(nome_display.upper(), True, colors.TEXT_PRIMARY)
            self.screen.blit(txt_nome, (canto_x + 60 - txt_nome.get_width()//2, canto_y + 175))
            
        else:
            # Se não tiver deck selecionado, desenha um slot vazio em vermelho
            txt_status = self.fontes['label'].render("SEM DECK", True, colors.DANGER)
            self.screen.blit(txt_status, (canto_x + 60 - txt_status.get_width()//2, canto_y - 25))
            
            pygame.draw.rect(self.screen, (30, 30, 35), rect_capa, border_radius=5)
            pygame.draw.rect(self.screen, colors.DANGER, rect_capa, 2, border_radius=5)
            
            txt_aviso = self.fontes['status'].render("Vá em Meus Decks", True, colors.TEXT_SEC)
            self.screen.blit(txt_aviso, (canto_x + 60 - txt_aviso.get_width()//2, canto_y + 70))
        # -------------------------------------------------------------

        # Desenha Botões de Jogadores
        Label("JOGADORES:", (self.largura // 2, 290), self.fontes['status'], colors.TEXT_SEC).draw(self.screen)
        for num, btn in self.btns_jogadores.items():
            if self.total_jogadores == num:
                pygame.draw.rect(self.screen, colors.ACCENT, btn.rect.inflate(6, 6), 2, border_radius=8)
            btn.draw(self.screen)
            
        # Botões de Ação
        self.btn_abrir_sala.draw(self.screen)
        self.btn_meus_decks.draw(self.screen)
        self.btn_sair.draw(self.screen)
        
        # Popup por cima de tudo
        if self.mostrar_aviso and self.popup_deck:
            self.popup_deck.draw(self.screen)