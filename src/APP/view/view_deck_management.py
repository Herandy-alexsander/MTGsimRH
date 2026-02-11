import pygame
import os
from tkinter import filedialog, Tk
from APP.core.base import ViewComponent
from APP.UI.ui_components import MenuButton, UIComponents
from APP.UI.style import GameStyle

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
        self.camin_txt = "" 
        self.deck_carregado = False 
        self.opcoes_comandantes = [] 
        self.indice_commander = 0
        
        # Variáveis de Progresso
        self.progresso_atual = 0
        self.progresso_total = 0
        self.analise_em_andamento = False
        
        self.status_message = "1. Digite o nome e selecione o ficheiro .txt"
        self.input_ativo_nome = False

        cx = self.largura // 2

        # --- REORGANIZAÇÃO DO LAYOUT (Coordenadas Y ajustadas) ---
        
        # 1. Campo de Nome (Mais acima)
        self.rect_input = pygame.Rect(cx - 150, 130, 300, 40)
        
        # 2. Botão Selecionar Arquivo (Logo abaixo do input)
        self.sync_button = MenuButton(
            pygame.Rect(cx - 150, 190, 300, 50), 
            "1. SELECIONAR .TXT", 
            self.fontes['menu']
        )
        
        # (Espaço reservado para a Barra de Progresso em Y = 280)
        
        # 3. Seletor de Comandante (Mais abaixo, para não cobrir a barra)
        self.btn_prev = MenuButton(pygame.Rect(cx - 190, 390, 40, 40), "<", self.fontes['menu'])
        self.btn_next = MenuButton(pygame.Rect(cx + 150, 390, 40, 40), ">", self.fontes['menu'])
        
        # 4. Botão Salvar (No fundo da tela)
        self.save_button = MenuButton(
            pygame.Rect(cx - 150, 480, 300, 60), 
            "INICIAR CADASTRO", 
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
                self.input_ativo_nome = self.rect_input.collidepoint(event.pos)
            
            if event.type == pygame.KEYDOWN and self.input_ativo_nome:
                if event.key == pygame.K_BACKSPACE: self.nome_deck = self.nome_deck[:-1]
                else: self.nome_deck += event.unicode

            if self.sync_button.is_clicked(event):
                self._abrir_seletor_arquivos()

            if self.deck_carregado:
                if self.btn_prev.is_clicked(event): self._navegar_commander(-1)
                if self.btn_next.is_clicked(event): self._navegar_commander(1)
                
                if self.save_button.is_clicked(event):
                    if self._preparar_e_validar():
                        return {
                            "acao": "INICIAR_PROCESSO",
                            "nome": self.nome_deck.strip(),
                            "path": self.camin_txt,
                            "commander": self.commander_selecionado
                        }

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
        return True

    def _abrir_seletor_arquivos(self):
        root = Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        caminho = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        root.destroy()
        if caminho:
            self.camin_txt = caminho
            self._fase1_analise_previa(caminho)

    def _callback_progresso_analise(self, atual, total, nome_carta):
        self.progresso_atual = atual
        self.progresso_total = total
        self.analise_em_andamento = True
        self.status_message = f"Analisando: {nome_carta} ({atual}/{total})"
        self.draw()
        pygame.display.flip()
        pygame.event.pump()

    def _fase1_analise_previa(self, caminho):
        self.status_message = "🔍 Iniciando análise..."
        self.analise_em_andamento = True
        self.draw()
        pygame.display.flip()
        
        try:
            # 1. Validação Básica
            qtd, linhas = self.storage.analisar_txt(caminho)
            
            if qtd == 0:
                self.analise_em_andamento = False
                self.status_message = "❌ Arquivo vazio!"
                return

            # 2. Download dos dados com Callback (Resolve o erro da Image 1)
            cartas_analisadas = self.storage.processar_download_com_progresso(
                linhas, 
                self._callback_progresso_analise
            )
            
            # 3. Filtro de Comandantes
            self.opcoes_comandantes = [
                c for c in cartas_analisadas 
                if 'Legendary' in c.get('type_line', '') and 'Creature' in c.get('type_line', '')
            ]

            self.analise_em_andamento = False # Fim da barra

            if self.opcoes_comandantes:
                self.deck_carregado = True
                self.indice_commander = 0
                self.commander_selecionado = self.opcoes_comandantes[0]['name']
                self.status_message = f"✅ {len(self.opcoes_comandantes)} Lendárias encontradas!"
            else:
                self.deck_carregado = False
                self.status_message = "❌ Nenhuma Criatura Lendária no deck!"
        except Exception as e:
            self.analise_em_andamento = False
            self.status_message = f"❌ Erro: {str(e)}"

    def _navegar_commander(self, direcao):
        if self.opcoes_comandantes:
            self.indice_commander = (self.indice_commander + direcao) % len(self.opcoes_comandantes)
            self.commander_selecionado = self.opcoes_comandantes[self.indice_commander]['name']

    def draw(self):
        self.screen.fill(GameStyle.COLOR_BG)
        cx = self.largura // 2
        
        # Título
        txt_t = self.fontes['titulo'].render("GESTAO DE DECK", True, GameStyle.COLOR_ACCENT)
        self.screen.blit(txt_t, (cx - txt_t.get_width()//2, 40))

        # 1. Input Nome (Y=130)
        self.ui.desenhar_caixa_texto(self.screen, self.rect_input, 
                                     self.nome_deck, self.fontes['menu'], 
                                     self.input_ativo_nome, "Nome do Deck...")

        # 2. Botão Selecionar (Y=190)
        self.sync_button.draw(self.screen)
        
        # Texto do arquivo selecionado (Y=250)
        if self.camin_txt:
            nome_arq = os.path.basename(self.camin_txt)
            txt_path = self.fontes['status'].render(f"Ficheiro: {nome_arq}", True, (150, 255, 150))
            self.screen.blit(txt_path, (cx - txt_path.get_width()//2, 250))

        # 3. BARRA DE PROGRESSO (Y=280) - Área livre
        if self.analise_em_andamento and self.progresso_total > 0:
            largura_barra = 400
            altura_barra = 20
            pos_x = cx - 200
            pos_y = 280 
            
            # Fundo
            pygame.draw.rect(self.screen, (40, 40, 40), (pos_x, pos_y, largura_barra, altura_barra), border_radius=10)
            # Preenchimento
            pct = self.progresso_atual / self.progresso_total
            largura_fill = int(largura_barra * pct)
            pygame.draw.rect(self.screen, GameStyle.COLOR_ACCENT, (pos_x, pos_y, largura_fill, altura_barra), border_radius=10)
            
            # Texto da carta atual (Y=310)
            status_font = self.fontes['status'] # Fonte menor
            txt_status = status_font.render(self.status_message, True, (200, 200, 200))
            # Garante que o texto não saia da tela se for muito grande
            if txt_status.get_width() > 800:
                 txt_status = pygame.transform.scale(txt_status, (800, txt_status.get_height()))
            self.screen.blit(txt_status, (cx - txt_status.get_width()//2, 310))

        # 4. Seletor de Comandante (Y=360+)
        if self.deck_carregado and not self.analise_em_andamento:
            label = self.fontes['label'].render("Escolha o Comandante:", True, (200, 200, 200))
            self.screen.blit(label, (cx - label.get_width()//2, 360))
            
            # Caixa do nome do comandante (Y=390)
            rect_disp = pygame.Rect(cx - 140, 390, 280, 40)
            pygame.draw.rect(self.screen, (30, 30, 35), rect_disp, border_radius=8)
            pygame.draw.rect(self.screen, GameStyle.COLOR_ACCENT, rect_disp, 1, border_radius=8)
            
            nome_c = self.fontes['menu'].render(self.commander_selecionado[:25], True, (255, 255, 255))
            self.screen.blit(nome_c, (rect_disp.centerx - nome_c.get_width()//2, rect_disp.centery - nome_c.get_height()//2))
            
            self.btn_prev.draw(self.screen)
            self.btn_next.draw(self.screen)
            
            # Botão Iniciar (Y=480)
            self.save_button.draw(self.screen) 
        
        # Mensagem de Status (Fica no rodapé se não estiver analisando)
        if not self.analise_em_andamento:
            cor_msg = GameStyle.COLOR_DANGER if "ERRO" in self.status_message or "❌" in self.status_message else (180, 180, 180)
            msg_surf = self.fontes['status'].render(self.status_message, True, cor_msg)
            self.screen.blit(msg_surf, (cx - msg_surf.get_width()//2, 550)) # Bem abaixo

        self.back_button.draw(self.screen)