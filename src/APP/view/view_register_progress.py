import pygame
from APP.utils.style import GameStyle
from APP.utils.ui_components import MenuButton

class RegisterProgressView:
    def __init__(self, screen, storage, deck_name, file_path):
        """
        Gerencia o fluxo de cadastro com barra de progresso e validação em duas etapas.
        """
        self.screen = screen
        self.storage = storage
        self.deck_name = deck_name
        self.file_path = file_path
        self.fontes = GameStyle.get_fonts()
        
        # --- Estados do Processo ---
        self.etapa = "ANALISANDO" # ANALISANDO -> BAIXANDO -> CONCLUIDO
        self.progresso = 0
        self.total = 1
        self.card_atual = "Aguardando..."
        self.mostrar_sucesso = False
        
        # --- UI do Pop-up de Sucesso ---
        cx, cy = self.screen.get_width() // 2, self.screen.get_height() // 2
        self.popup_rect = pygame.Rect(cx - 200, cy - 100, 400, 220)
        self.btn_voltar = MenuButton(
            pygame.Rect(cx - 100, cy + 50, 200, 45), 
            "VOLTAR AO MENU", 
            self.fontes['menu']
        )

    def callback_progresso(self, atual, total, nome_card):
        """Atualiza os dados da barra enquanto o storage faz o download."""
        self.progresso = atual
        self.total = total
        self.card_atual = nome_card
        # Força o redesenho para o usuário ver a animação
        self.draw()
        pygame.display.flip()

    def iniciar_fluxo(self, deck_model):
        """Executa a análise prévia e o download real dos dados e imagens."""
        # 1. ETAPA DE ANÁLISE (Pré-carga)
        qtd, linhas = self.storage.analisar_txt(self.file_path)
        
        if qtd > 0:
            self.etapa = "BAIXANDO ASSETS"
            # 2. ETAPA DE DOWNLOAD (Processamento)
            cards = self.storage.processar_download_com_progresso(linhas, self.callback_progresso)
            
            # 3. CONFIGURAÇÃO E SALVAMENTO
            deck_model.name = self.deck_name
            deck_model.deck_id = self.deck_name.lower().replace(" ", "_")
            deck_model.limpar_deck()
            
            for c in cards:
                deck_model.adicionar_carta(c)
            
            # Salva JSONs e Imagens em assets/cards/Categoria/
            self.storage.salvar_deck_inteligente(deck_model)
            
            self.etapa = "CONCLUIDO"
            self.mostrar_sucesso = True
        else:
            print("[ERRO] Arquivo vazio ou inválido.")

    def handle_event(self, events):
        """Gerencia o clique no botão de finalização."""
        mouse_pos = pygame.mouse.get_pos()
        if self.mostrar_sucesso:
            self.btn_voltar.update(mouse_pos)
            for event in events:
                if self.btn_voltar.is_clicked(event):
                    return "MENU" # Sinaliza ao ViewManager para voltar
        return None

    def draw(self):
        """Renderiza a interface de carregamento e o pop-up final."""
        self.screen.fill(GameStyle.COLOR_BG)
        cx, cy = self.screen.get_width() // 2, self.screen.get_height() // 2

        # Título da Etapa
        txt_etapa = self.fontes['menu'].render(self.etapa, True, GameStyle.COLOR_ACCENT)
        self.screen.blit(txt_etapa, (cx - txt_etapa.get_width() // 2, cy - 100))

        # Barra de Progresso
        largura_barra = 400
        pygame.draw.rect(self.screen, (40, 40, 45), (cx - 200, cy - 20, largura_barra, 30), border_radius=15)
        
        preenchimento = int((self.progresso / self.total) * largura_barra)
        if preenchimento > 5:
            pygame.draw.rect(self.screen, GameStyle.COLOR_ACCENT, (cx - 200, cy - 20, preenchimento, 30), border_radius=15)

        # Informações do Card Atual
        txt_card = self.fontes['label'].render(f"Processando: {self.card_atual}", True, (180, 180, 180))
        self.screen.blit(txt_card, (cx - txt_card.get_width() // 2, cy + 30))

        # Pop-up de Sucesso
        if self.mostrar_sucesso:
            self._draw_modal_sucesso(cx, cy)

    def _draw_modal_sucesso(self, cx, cy):
        # Overlay escuro
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 210))
        self.screen.blit(overlay, (0, 0))

        # Moldura do Pop-up
        pygame.draw.rect(self.screen, (30, 35, 30), self.popup_rect, border_radius=15)
        pygame.draw.rect(self.screen, (0, 200, 80), self.popup_rect, 2, border_radius=15)

        msg = self.fontes['popup'].render("DECK PRONTO!", True, (255, 255, 255))
        sub = self.fontes['label'].render("Dados e imagens salvos com sucesso.", True, (180, 180, 180))
        
        self.screen.blit(msg, (cx - msg.get_width() // 2, cy - 60))
        self.screen.blit(sub, (cx - sub.get_width() // 2, cy - 20))
        self.btn_voltar.draw(self.screen)