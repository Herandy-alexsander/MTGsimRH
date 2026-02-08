import pygame
import os
from tkinter import filedialog, Tk
from mtg_commander_app.utils.base import ViewComponent
from mtg_commander_app.utils.ui_components import MenuButton, UIComponents
from mtg_commander_app.utils.style import GameStyle

class RegisterDeckView(ViewComponent):
    def __init__(self, screen, controller, storage_manager):
        super().__init__(screen, controller)
        self.storage = storage_manager
        self.largura, self.altura = self.screen.get_size()
        self.fontes = GameStyle.get_fonts()
        self.ui = UIComponents(self.largura, self.altura)
        
        # --- Estados de Dados ---
        self.nome_deck = ""
        self.commander_selecionado = ""
        self.caminho_txt = "" 
        self.deck_carregado = False 
        self.opcoes_comandantes = [] 
        self.indice_commander = 0
        
        self.status_message = "1. Digite o nome e selecione o ficheiro .txt"
        self.input_ativo_nome = False

        # --- Inicialização dos Botões ---
        cx = self.largura // 2
        # Botão de Rastreio
        self.sync_button = MenuButton(self.ui.btn_selecionar_arquivo, "1. SELECIONAR .TXT", self.fontes['menu'])
        
        # Setas do Seletor de Comandante
        self.btn_prev = MenuButton(pygame.Rect(cx - 190, 380, 40, 40), "<", self.fontes['menu'])
        self.btn_next = MenuButton(pygame.Rect(cx + 150, 380, 40, 40), ">", self.fontes['menu'])
        
        # BOTÃO ÚNICO DE CADASTRO/SALVAMENTO
        self.save_button = MenuButton(
            pygame.Rect(cx - 150, 480, 300, 60), 
            "SALVAR DECK", 
            self.fontes['menu']
        )
        
        self.back_button = MenuButton(self.ui.btn_voltar, "VOLTAR", self.fontes['menu'])

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        self.sync_button.update(mouse_pos)
        self.back_button.update(mouse_pos)
        
        if self.deck_carregado:
            self.save_button.update(mouse_pos)
            self.btn_prev.update(mouse_pos)
            self.btn_next.update(mouse_pos)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.input_ativo_nome = self.ui.rect_input_nome_deck.collidepoint(event.pos)
            
            if event.type == pygame.KEYDOWN and self.input_ativo_nome:
                if event.key == pygame.K_BACKSPACE: self.nome_deck = self.nome_deck[:-1]
                else: self.nome_deck += event.unicode

            if self.sync_button.is_clicked(event):
                self._abrir_seletor_arquivos()

            if self.deck_carregado:
                if self.btn_prev.is_clicked(event): self._navegar_commander(-1)
                if self.btn_next.is_clicked(event): self._navegar_commander(1)
                
                # Lógica unificada de salvamento
                if self.save_button.is_clicked(event):
                    if self._preparar_e_validar():
                        # O storage agora decide se registra novo ou atualiza
                        self.storage.salvar_deck_inteligente(self.controller.model)
                        return "MENU"

            if self.back_button.is_clicked(event):
                return "MENU"
        return None

    def _preparar_e_validar(self):
        nome_limpo = self.nome_deck.strip()
        if not nome_limpo or nome_limpo == "Nome do Deck...":
            self.status_message = "⚠️ ERRO: O Nome do Deck nao pode estar vazio!"
            return False
            
        if not self.commander_selecionado:
            self.status_message = "⚠️ ERRO: Selecione um Comandante valido!"
            return False

        self.controller.model.name = nome_limpo
        self.controller.model.commander = self.commander_selecionado
        self.controller.model.deck_id = nome_limpo.replace(" ", "_").lower()
        return True

    def _abrir_seletor_arquivos(self):
        root = Tk()
        root.withdraw()
        caminho = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        root.destroy()
        if caminho:
            self.caminho_txt = caminho
            self._processar_rastreio(caminho)

    def _processar_rastreio(self, caminho):
        self.status_message = "🔍 Analisando cartas..."
        self.draw()
        pygame.display.flip()
        try:
            cartas = self.storage.download_deck_from_txt(caminho)
            self.opcoes_comandantes = [
                c for c in cartas 
                if 'Legendary' in c.get('type_line', '') and 'Creature' in c.get('type_line', '')
            ]
            
            if self.opcoes_comandantes:
                self.deck_carregado = True
                self.indice_commander = 0
                self.commander_selecionado = self.opcoes_comandantes[0]['name']
                self.status_message = f"✅ {len(self.opcoes_comandantes)} Lendárias encontradas!"
            else:
                self.deck_carregado = False
                self.status_message = "❌ Erro: Nenhuma Criatura Lendária detectada!"
        except Exception as e:
            self.status_message = f"❌ Falha: {str(e)}"

    def _navegar_commander(self, direcao):
        if self.opcoes_comandantes:
            self.indice_commander = (self.indice_commander + direcao) % len(self.opcoes_comandantes)
            self.commander_selecionado = self.opcoes_comandantes[self.indice_commander]['name']

    def draw(self):
        self.screen.fill(GameStyle.COLOR_BG)
        cx = self.largura // 2
        
        txt_t = self.fontes['titulo'].render("GESTAO DE DECK", True, GameStyle.COLOR_ACCENT)
        self.screen.blit(txt_t, (cx - txt_t.get_width()//2, 40))

        self.ui.desenhar_caixa_texto(self.screen, self.ui.rect_input_nome_deck, 
                                     self.nome_deck, self.fontes['menu'], 
                                     self.input_ativo_nome, "Nome do Deck...")

        self.sync_button.draw(self.screen)
        
        if self.caminho_txt:
            nome_arq = os.path.basename(self.caminho_txt)
            txt_path = self.fontes['status'].render(f"Ficheiro: {nome_arq}", True, (150, 255, 150))
            self.screen.blit(txt_path, (cx - txt_path.get_width()//2, 280))

        if self.deck_carregado:
            label = self.fontes['label'].render("Escolha o Comandante Lendário:", True, (200, 200, 200))
            self.screen.blit(label, (cx - label.get_width()//2, 350))
            
            rect_disp = pygame.Rect(cx - 140, 380, 280, 40)
            pygame.draw.rect(self.screen, (35, 35, 40), rect_disp, border_radius=5)
            pygame.draw.rect(self.screen, GameStyle.COLOR_ACCENT, rect_disp, 1, border_radius=5)
            
            nome_c = self.fontes['menu'].render(self.commander_selecionado, True, (255, 255, 255))
            self.screen.blit(nome_c, (rect_disp.centerx - nome_c.get_width()//2, rect_disp.centery - nome_c.get_height()//2))
            
            self.btn_prev.draw(self.screen)
            self.btn_next.draw(self.screen)
            self.save_button.draw(self.screen) # Botão Unificado
        
        self.back_button.draw(self.screen)
        cor_msg = GameStyle.COLOR_DANGER if "ERRO" in self.status_message or "❌" in self.status_message else (200, 200, 200)
        msg_surf = self.fontes['status'].render(self.status_message, True, cor_msg)
        self.screen.blit(msg_surf, (cx - msg_surf.get_width()//2, 445))