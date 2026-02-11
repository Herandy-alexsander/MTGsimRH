import pygame
import threading
from APP.UI.style import GameStyle

class RegisterProgressView:
    def __init__(self, screen, storage, deck_name, file_path):
        """
        Interface de progresso com suporte a processamento em segundo plano (Threading).
        """
        self.screen = screen
        self.storage = storage
        self.deck_name = deck_name
        self.file_path = file_path
        self.fontes = GameStyle.get_fonts()
        
        # --- Variáveis de Estado de Download ---
        self.progresso_atual = 0
        self.progresso_total = 0
        self.carta_atual = "Inicializando conexao com Scryfall..."
        self.concluido = False
        self.erro = None
        
        # Controle de Thread para evitar múltiplas execuções
        self.thread_iniciada = False

    def iniciar_fluxo(self, deck_model):
        """
        Dispara a tarefa de download em uma thread separada para manter o Pygame responsivo.
        """
        if not self.thread_iniciada:
            deck_model.name = self.deck_name
            # Inicia o processo pesado em background
            t = threading.Thread(target=self._tarefa_download, args=(deck_model,))
            t.daemon = True # Fecha a thread se o programa principal encerrar
            t.start()
            self.thread_iniciada = True

    def _tarefa_download(self, deck_model):
        """
        Executa a analise, download e validacao final dos dados.
        """
        try:
            # 1. Fase de Analise de Arquivo
            qtd, linhas = self.storage.analisar_txt(self.file_path)
            self.progresso_total = qtd
            
            # 2. Fase de Download (Imagens e Dados Técnicos)
            # O callback permite que esta thread atualize a interface grafica principal
            cards = self.storage.processar_download_com_progresso(
                linhas, 
                self._atualizar_progresso
            )
            
            # 3. Fase de Persistencia
            deck_model.cards = cards
            self.storage.salvar_deck_inteligente(deck_model)
            
            # 4. Fase de Auditoria (Verificação de Integridade JSON)
            self.carta_atual = "Verificando consistencia do arquivo JSON..."
            ok, msg = self.storage.validar_deck_recem_criado(deck_model.name)
            
            if not ok:
                raise Exception(f"Falha na integridade: {msg}")
            
            # Finalização com Sucesso
            self.concluido = True
            self.carta_atual = "Cadastro Finalizado com Sucesso!"
            
        except Exception as e:
            self.erro = str(e)
            self.carta_atual = "Falha no processamento."

    def _atualizar_progresso(self, atual, total, nome):
        """Metodo de callback usado pelo Storage para reportar progresso."""
        self.progresso_atual = atual
        self.progresso_total = total
        self.carta_atual = nome

    def handle_events(self, events):
        """
        Captura a interacao de retorno apos a conclusao ou erro.
        """
        if self.concluido or self.erro:
            for event in events:
                if event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
                    # Retorna para a galeria visual para ver o novo deck cadastrado
                    return "LISTA_DECKS"
        return None

    def draw(self):
        """Renderiza a barra de progresso e status em tempo real."""
        self.screen.fill(GameStyle.COLOR_BG)
        cx, cy = self.screen.get_rect().center
        
        # Definicao dinamica de cores e textos de titulo
        titulo_str = "BAIXANDO ACERVO..." if not self.concluido else "CONCLUIDO COM SUCESSO!"
        cor_titulo = GameStyle.COLOR_ACCENT if not self.erro else GameStyle.COLOR_DANGER
        
        if self.erro: titulo_str = "ERRO NO CADASTRO"

        txt_t = self.fontes['titulo'].render(titulo_str, True, cor_titulo)
        self.screen.blit(txt_t, (cx - txt_t.get_width()//2, cy - 120))

        # Exibicao de Erro Critico
        if self.erro:
            msg = self.fontes['status'].render(f"Detalhes: {self.erro}", True, (255, 100, 100))
            self.screen.blit(msg, (cx - msg.get_width()//2, cy))
            info = self.fontes['label'].render("Clique em qualquer lugar para voltar", True, (150, 150, 150))
            self.screen.blit(info, (cx - info.get_width()//2, cy + 60))
            return

        # --- Renderizacao da Barra de Progresso Visual ---
        largura_barra = 600
        altura_barra = 25
        pos_x_barra = cx - largura_barra // 2
        
        # Desenho do Fundo da Barra (Container)
        pygame.draw.rect(self.screen, (35, 35, 40), (pos_x_barra, cy, largura_barra, altura_barra), border_radius=12)
        
        # Desenho do Preenchimento (Dinamico)
        if self.progresso_total > 0:
            porcentagem = self.progresso_atual / self.progresso_total
            largura_preenchida = int(largura_barra * porcentagem)
            # Cor dourada para indicar progresso
            pygame.draw.rect(self.screen, GameStyle.COLOR_ACCENT, (pos_x_barra, cy, largura_preenchida, altura_barra), border_radius=12)

        # Texto de Status da Carta (Centralizado abaixo da barra)
        status_texto = f"Baixando: {self.carta_atual}" if not self.concluido else self.carta_atual
        txt_status = self.fontes['status'].render(status_texto, True, (180, 180, 180))
        
        # Protecao para nomes de cartas excessivamente longos
        if txt_status.get_width() > 750:
            txt_status = pygame.transform.scale(txt_status, (750, txt_status.get_height()))
            
        self.screen.blit(txt_status, (cx - txt_status.get_width()//2, cy + 45))
        
        # Instrucao final para o usuario
        if self.concluido:
            instrucao = self.fontes['label'].render("Pressione qualquer tecla para ver sua colecao", True, (120, 255, 120))
            self.screen.blit(instrucao, (cx - instrucao.get_width()//2, cy + 90))