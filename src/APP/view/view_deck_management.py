import pygame
import os
from tkinter import filedialog, Tk
from APP.utils.base import ViewComponent
from APP.utils.ui_components import MenuButton, UIComponents
from APP.utils.style import GameStyle

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
        self.sync_button = MenuButton(self.ui.btn_selecionar_arquivo, "1. SELECIONAR .TXT", self.fontes['menu'])
        
        # Setas do Seletor de Comandante
        self.btn_prev = MenuButton(pygame.Rect(cx - 190, 380, 40, 40), "<", self.fontes['menu'])
        self.btn_next = MenuButton(pygame.Rect(cx + 150, 380, 40, 40), ">", self.fontes['menu'])
        
        # BOTÃO ÚNICO DE CADASTRO
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
                self.input_ativo_nome = self.ui.rect_input_nome_deck.collidepoint(event.pos)
            
            if event.type == pygame.KEYDOWN and self.input_ativo_nome:
                if event.key == pygame.K_BACKSPACE: self.nome_deck = self.nome_deck[:-1]
                else: self.nome_deck += event.unicode

            if self.sync_button.is_clicked(event):
                self._abrir_seletor_arquivos()

            if self.deck_carregado:
                if self.btn_prev.is_clicked(event): self._navegar_commander(-1)
                if self.btn_next.is_clicked(event): self._navegar_commander(1)
                
                # FASE 1: Validação e Envio para a Tela de Progresso
                if self.save_button.is_clicked(event):
                    if self._preparar_e_validar():
                        # Retorna dicionário para o ViewManager disparar a RegisterProgressView
                        return {
                            "acao": "INICIAR_PROCESSO",
                            "nome": self.nome_deck.strip(),
                            "path": self.caminho_txt,
                            "commander": self.commander_selecionado
                        }

            if self.back_button.is_clicked(event):
                return "MENU"
        return None

    def _preparar_e_validar(self):
        nome_limpo = self.nome_deck.strip()
        if not nome_limpo or nome_limpo == "Nome do Deck...":
            self.status_message = "⚠️ ERRO: O Nome do Deck não pode estar vazio!"
            return False
        if not self.commander_selecionado:
            self.status_message = "⚠️ ERRO: Selecione um Comandante válido!"
            return False
        return True

    def _abrir_seletor_arquivos(self):
        root = Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        caminho = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        root.destroy()
        if caminho:
            self.caminho_txt = caminho
            self._fase1_analise_previa(caminho)

    def _fase1_analise_previa(self, caminho):
        """ETAPA 1: Analisa o TXT para buscar comandantes sem baixar imagens ainda."""
        self.status_message = "🔍 Analisando arquivo..."
        self.draw()
        pygame.display.flip()
        
        try:
            # Apenas lê o arquivo, não baixa nada da API pesada ainda
            qtd, linhas = self.storage.analisar_txt(caminho)
            
            # Filtra potenciais comandantes (Busca simples por texto nas linhas ou análise básica)
            # Para uma análise real de tipos, ainda precisamos de uma consulta leve ou cache
            self.opcoes_comandantes = []
            for linha in linhas:
                # Se a linha contiver algo que pareça um comandante (lógica simplificada para a fase 1)
                # O ideal é que o storage tenha um cache de nomes lendários
                name = linha.split(' ', 1)[1] if linha[0].isdigit() else linha
                self.opcoes_comandantes.append({"name": name})

            if self.opcoes_comandantes:
                self.deck_carregado = True
                self.indice_commander = 0
                self.commander_selecionado = self.opcoes_comandantes[0]['name']
                self.status_message = f"✅ {qtd} cartas detectadas. Escolha o Comandante:"
            else:
                self.status_message = "❌ Erro: Nenhuma carta encontrada no arquivo!"
        except Exception as e:
            self.status_message = f"❌ Falha: {str(e)}"

    def _navegar_commander(self, direcao):
        if self.opcoes_comandantes:
            self.indice_commander = (self.indice_commander + direcao) % len(self.opcoes_comandantes)
            self.commander_selecionado = self.opcoes_comandantes[self.indice_commander]['name']

    def draw(self):
        self.screen.fill(GameStyle.COLOR_BG)
        cx = self.largura // 2
        
        # Título decorado
        txt_t = self.fontes['titulo'].render("GESTAO DE DECK", True, GameStyle.COLOR_ACCENT)
        self.screen.blit(txt_t, (cx - txt_t.get_width()//2, 40))

        # Campo de Texto
        self.ui.desenhar_caixa_texto(self.screen, self.ui.rect_input_nome_deck, 
                                     self.nome_deck, self.fontes['menu'], 
                                     self.input_ativo_nome, "Nome do Deck...")

        self.sync_button.draw(self.screen)
        
        if self.caminho_txt:
            nome_arq = os.path.basename(self.caminho_txt)
            txt_path = self.fontes['status'].render(f"Ficheiro: {nome_arq}", True, (150, 255, 150))
            self.screen.blit(txt_path, (cx - txt_path.get_width()//2, 280))

        if self.deck_carregado:
            label = self.fontes['label'].render("Definir Comandante do Deck:", True, (200, 200, 200))
            self.screen.blit(label, (cx - label.get_width()//2, 350))
            
            rect_disp = pygame.Rect(cx - 140, 380, 280, 40)
            pygame.draw.rect(self.screen, (30, 30, 35), rect_disp, border_radius=8)
            pygame.draw.rect(self.screen, GameStyle.COLOR_ACCENT, rect_disp, 1, border_radius=8)
            
            nome_c = self.fontes['menu'].render(self.commander_selecionado[:25], True, (255, 255, 255))
            self.screen.blit(nome_c, (rect_disp.centerx - nome_c.get_width()//2, rect_disp.centery - nome_c.get_height()//2))
            
            self.btn_prev.draw(self.screen)
            self.btn_next.draw(self.screen)
            self.save_button.draw(self.screen) 
        
        self.back_button.draw(self.screen)
        
        # Mensagem de Status
        cor_msg = GameStyle.COLOR_DANGER if "ERRO" in self.status_message or "❌" in self.status_message else (180, 180, 180)
        msg_surf = self.fontes['status'].render(self.status_message, True, cor_msg)
        self.screen.blit(msg_surf, (cx - msg_surf.get_width()//2, 445))