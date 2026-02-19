import pygame
import math
import tkinter as tk
from tkinter import filedialog
import requests
import io
import threading

from APP.UI.screens.base_screens import BaseScreen
from APP.UI.styles import colors, settings
from APP.UI.styles.fonts import get_fonts
from APP.UI.components.button import MenuButton
from APP.UI.components.label import Label
from APP.UI.components.input_field import InputField

class DeckRegisterView(BaseScreen):
    def __init__(self, screen, controller, deck_ctrl):
        super().__init__(screen, controller)
        self.deck_ctrl = deck_ctrl
        self.fontes = get_fonts()
        
        self.img_cache = {}
        self.mensagem_erro_input = ""
        
        self.cx = self.screen.get_width() // 2
        self.cy = self.screen.get_height() // 2
        
        self.label_titulo = Label("REGISTRO DE DECK", (self.cx, 50), self.fontes['titulo'], colors.ACCENT)
        self.input_nome = InputField(pygame.Rect(self.cx - 150, 140, 300, 45), self.fontes['menu'], "Nome do Deck...")
        self.btn_carregar = MenuButton(pygame.Rect(self.cx - 150, 210, 300, 50), "SELECIONAR .TXT", self.fontes['menu'])
        
        self.btn_prev = MenuButton(pygame.Rect(self.cx - 240, self.cy + 50, 60, 60), "<", self.fontes['menu'])
        self.btn_next = MenuButton(pygame.Rect(self.cx + 180, self.cy + 50, 60, 60), ">", self.fontes['menu'])
        self.btn_confirmar = MenuButton(pygame.Rect(self.cx - 150, self.cy + 240, 300, 55), "FINALIZAR CADASTRO", self.fontes['menu'])

        self.btn_cancelar = MenuButton(pygame.Rect(40, self.screen.get_height() - 80, 150, 45), "CANCELAR", self.fontes['menu'])

    # --- LAZY LOADING ASSÍNCRONO DA IMAGEM ---
    def _get_card_image(self, url):
        if not url: return None
        if url in self.img_cache: return self.img_cache[url]
        
        if not hasattr(self, '_fetching_urls'):
            self._fetching_urls = set()
            
        if url not in self._fetching_urls:
            self._fetching_urls.add(url)
            thread = threading.Thread(target=self._baixar_imagem_ram, args=(url,))
            thread.daemon = True 
            thread.start()
            
        return None 

    def _baixar_imagem_ram(self, url):
        try:
            headers = {'User-Agent': 'MTK-Simulador/1.0'}
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                img_data = io.BytesIO(resp.content)
                surf = pygame.image.load(img_data)
                surf = pygame.transform.scale(surf, (280, 390))
                self.img_cache[url] = surf
        except Exception as e:
            print(f"[AVISO] Erro ao baixar arte: {e}")
        finally:
            if hasattr(self, '_fetching_urls') and url in self._fetching_urls:
                self._fetching_urls.remove(url)

    def _abrir_seletor_arquivo(self, nome_deck):
        self.img_cache.clear() 
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        path = filedialog.askopenfilename(filetypes=[("Texto", "*.txt")])
        root.destroy()
        
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    linhas = f.readlines()
                self.deck_ctrl.iniciar_analise(nome_deck, linhas)
            except Exception as e:
                print(f"Erro ao ler arquivo: {e}")

    def handle_events(self, events):
        # O ESCUTADOR DE CONCLUSÃO: Quando a barra chegar em 100%, ele faz a faxina e volta.
        if self.deck_ctrl.estado == "CONCLUIDO":
            self.img_cache.clear()
            self.input_nome.text = ""
            self.mensagem_erro_input = ""
            self.deck_ctrl.limpar_dados()
            return "REGISTER_SUCCESS"

        for event in events:
            if hasattr(self.input_nome, 'handle_event'):
                self.input_nome.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.btn_cancelar.is_clicked(event):
                    self.img_cache.clear()           
                    self.input_nome.text = ""        
                    self.mensagem_erro_input = ""    
                    if hasattr(self.deck_ctrl, 'limpar_dados'):
                        self.deck_ctrl.limpar_dados() 
                    else:
                        self.deck_ctrl.estado = "INICIAL" 
                    return "DECK_MANAGER"
                
                if self.deck_ctrl.estado == "INICIAL":
                    if self.btn_carregar.is_clicked(event):
                        nome_digitado = self.input_nome.get_value()
                        if not nome_digitado or nome_digitado == "Nome do Deck...":
                            self.mensagem_erro_input = "⚠️ Digite o nome do deck primeiro!"
                        else:
                            self.mensagem_erro_input = "" 
                            self.deck_ctrl.mensagem_erro = "" 
                            self._abrir_seletor_arquivo(nome_digitado)
                
                elif self.deck_ctrl.estado == "SELECAO":
                    if self.btn_prev.is_clicked(event): self.deck_ctrl.navegar_lendas(-1)
                    if self.btn_next.is_clicked(event): self.deck_ctrl.navegar_lendas(1)
                    if self.btn_confirmar.is_clicked(event):
                        # Só inicia o salvamento, a troca de tela agora acontece lá em cima no "CONCLUIDO"
                        self.deck_ctrl.finalizar_registro()
        
        mouse_pos = pygame.mouse.get_pos()
        estados_carregamento = ["ANALISANDO", "SALVANDO", "CONCLUIDO"]
        
        if self.deck_ctrl.estado not in estados_carregamento:
            self.btn_cancelar.update(mouse_pos)

        if self.deck_ctrl.estado == "INICIAL":
            self.btn_carregar.update(mouse_pos)
        elif self.deck_ctrl.estado == "SELECAO":
            self.btn_prev.update(mouse_pos)
            self.btn_next.update(mouse_pos)
            self.btn_confirmar.update(mouse_pos)
            
        return None

    def draw(self):
        self.screen.fill(colors.BG)
        self.label_titulo.draw(self.screen)

        estados_carregamento = ["ANALISANDO", "SALVANDO", "CONCLUIDO"]

        if self.deck_ctrl.estado not in estados_carregamento:
            self.btn_cancelar.draw(self.screen)

        if self.deck_ctrl.estado == "INICIAL":
            self.input_nome.draw(self.screen)
            self.btn_carregar.draw(self.screen)
            
            if self.mensagem_erro_input:
                Label(self.mensagem_erro_input, (self.cx, self.cy + 100), 
                      self.fontes['status'], (255, 80, 80)).draw(self.screen)

            if hasattr(self.deck_ctrl, 'mensagem_erro') and self.deck_ctrl.mensagem_erro:
                Label(self.deck_ctrl.mensagem_erro, (self.cx, self.cy + 130), 
                      self.fontes['status'], (255, 80, 80)).draw(self.screen)

        # --- CARREGAMENTO 1: Lendo o TXT na Scryfall (Circular) ---
        elif self.deck_ctrl.estado == "ANALISANDO":
            self._desenhar_progresso_circular(self.cx, self.cy)
            Label(f"Lendo TXT: {self.deck_ctrl.carta_atual_nome}", (self.cx, self.cy + 100), 
                  self.fontes['status'], colors.TEXT_SEC).draw(self.screen)

        # --- CARREGAMENTO 2: Baixando Imagens para o HD (Linear) ---
        elif self.deck_ctrl.estado == "SALVANDO":
            Label("GERANDO BACKUP LOCAL...", (self.cx, self.cy - 60), self.fontes['titulo'], colors.ACCENT).draw(self.screen)
            self._desenhar_barra_backup(self.cx, self.cy)
            Label(f"Baixando: {self.deck_ctrl.carta_atual_nome}", (self.cx, self.cy + 50), 
                  self.fontes['status'], colors.TEXT_SEC).draw(self.screen)

        elif self.deck_ctrl.estado == "SELECAO":
            lenda = self.deck_ctrl.obter_comandante_atual()
            if lenda:
                Label(lenda.get('name'), (self.cx, self.cy - 220), self.fontes['titulo'], colors.ACCENT).draw(self.screen)
                
                surf = self._get_card_image(lenda.get('url_temp'))
                
                if surf:
                    rect = surf.get_rect(center=(self.cx, self.cy + 20))
                    self.screen.blit(surf, rect)
                else:
                    Label("[ Baixando Arte... ]", (self.cx, self.cy), self.fontes['status'], colors.TEXT_SEC).draw(self.screen)
            
            self.btn_prev.draw(self.screen)
            self.btn_next.draw(self.screen)
            self.btn_confirmar.draw(self.screen)

    # =========================================================
    # FUNÇÕES DE DESENHO (BARRAS DE PROGRESSO)
    # =========================================================

    def _desenhar_progresso_circular(self, cx, cy):
        rect = pygame.Rect(cx - 50, cy - 50, 100, 100)
        prog = max(1, self.deck_ctrl.progresso)
        end_angle = (prog / 100) * (2 * math.pi)
        pygame.draw.arc(self.screen, colors.ACCENT, rect, -math.pi/2, end_angle - math.pi/2, 6)

    def _desenhar_barra_backup(self, cx, cy):
        largura_barra = 400
        altura_barra = 30
        x_inicial = cx - (largura_barra // 2)
        y_inicial = cy - (altura_barra // 2)

        # Fundo da barra
        bg_rect = pygame.Rect(x_inicial, y_inicial, largura_barra, altura_barra)
        pygame.draw.rect(self.screen, (50, 50, 50), bg_rect, border_radius=10)

        # Preenchimento da barra
        progresso = max(0, min(100, self.deck_ctrl.progresso)) 
        largura_preenchida = int((progresso / 100) * largura_barra)
        
        if largura_preenchida > 0:
            fill_rect = pygame.Rect(x_inicial, y_inicial, largura_preenchida, altura_barra)
            pygame.draw.rect(self.screen, colors.ACCENT, fill_rect, border_radius=10)
        
        # Texto da porcentagem
        Label(f"{progresso}%", (self.cx, self.cy), self.fontes['label'], (255, 255, 255)).draw(self.screen)