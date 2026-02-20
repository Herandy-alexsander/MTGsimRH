import pygame
import random
import math
import os
from APP.UI.screens.base_screens import BaseScreen
from APP.UI.styles.colors import BG, TEXT_PRIMARY, TEXT_SEC, ACCENT, SUCCESS, DANGER
from APP.UI.styles.fonts import get_fonts
from APP.UI.components.card_ui import CardUI
from APP.UI.components.zone_ui import ZoneUI
from APP.UI.layout.grid import LayoutEngine
from APP.UI.components.button import MenuButton

from APP.UI.components.dice_ui import DiceOverlayUI

class MatchView(BaseScreen):
    def __init__(self, screen, controller, asset_manager): 
        super().__init__(screen, controller)
        self.asset_manager = asset_manager 
        self.largura, self.altura = self.screen.get_size()
        self.fontes = get_fonts()
        self.match = self.controller.match_model
        
        self.card_w = 75
        self.card_h = 105
        
        self.zonas = {}
        self._inicializar_zonas()
        self.mao_ui = []

        self.dice_ui = DiceOverlayUI(self.largura, self.altura, self.fontes)

        # MÁQUINA DE ESTADOS
        self.fase_jogo = "DECIDIR_INICIATIVA" 
        self.res_p1 = 0
        self.res_p2 = 0
        self.vencedor_id = None
        
        # VARIÁVEIS DE MULLIGAN E ANIMAÇÃO
        self.mulligans_restantes = 3
        self.tempo_animacao = 0

        # CARREGA A SUA IMAGEM DO VERSO DA CARTA
        self.img_verso_carta = None
        caminho_verso = "assets/img/fudo_cards.jpg"
        if os.path.exists(caminho_verso):
            try:
                img_temp = pygame.image.load(caminho_verso).convert_alpha()
                # Já deixa ela do tamanho certinho das cartas da mesa
                self.img_verso_carta = pygame.transform.smoothscale(img_temp, (self.card_w, self.card_h))
            except Exception as e:
                print(f"[ERRO] Não consegui carregar fudo_cards.jpg: {e}")

        # Botões de Controle
        cx, cy = self.largura // 2, self.altura // 2
        self.btn_rolar_iniciativa = MenuButton(pygame.Rect(cx - 150, cy - 25, 300, 50), "ROLAR INICIATIVA (D20)", self.fontes['menu'])
        self.btn_comecar_partida = MenuButton(pygame.Rect(cx - 150, cy + 100, 300, 50), "COMPRAR CARTAS E INICIAR", self.fontes['menu'])
        self.btn_dado_lateral = MenuButton(pygame.Rect(10, cy - 25, 60, 50), "D20", self.fontes['menu'])
        
        # Botões do Mulligan
        self.btn_manter_mao = MenuButton(pygame.Rect(cx - 160, cy + 20, 150, 50), "MANTER", self.fontes['menu'])
        self.btn_trocar_mao = MenuButton(pygame.Rect(cx + 10, cy + 20, 150, 50), "MULLIGAN", self.fontes['menu'])

    def _inicializar_zonas(self):
        for p_id in self.match.players.keys():
            id_visual = 1 if p_id == "P1" else 2
            rect_area = self._get_area_jogador(id_visual, 2)
            col_w = rect_area.width * 0.18
            z_cmd = ZoneUI(pygame.Rect(rect_area.x + 10, rect_area.y + 45, col_w, rect_area.height * 0.38), "COMANDANTE", (45, 45, 70), "stack")
            z_mana = ZoneUI(pygame.Rect(rect_area.x + 10, z_cmd.rect.bottom + 10, col_w, rect_area.height * 0.38), "MANA", (30, 50, 30), "overlap")
            z_grave = ZoneUI(pygame.Rect(rect_area.right - col_w - 10, rect_area.y + 45, col_w, rect_area.height * 0.38), "CEMITÉRIO", (40, 30, 30), "stack")
            z_exile = ZoneUI(pygame.Rect(rect_area.right - col_w - 10, z_grave.rect.bottom + 10, col_w, rect_area.height * 0.38), "EXÍLIO", (30, 45, 45), "stack")
            z_battle = ZoneUI(pygame.Rect(z_cmd.rect.right + 15, rect_area.y + 45, rect_area.width - (col_w * 2) - 50, rect_area.height * 0.82), "CAMPO", (40, 45, 40), "grid")
            self.zonas[p_id] = {"COMANDANTE": z_cmd, "MANA": z_mana, "CEMITERIO": z_grave, "EXILIO": z_exile, "CAMPO": z_battle}

    def _get_area_jogador(self, id_visual, qtd):
        if id_visual == 2: return pygame.Rect(0, 0, self.largura, self.altura // 2)      
        return pygame.Rect(0, self.altura // 2, self.largura, self.altura // 2)

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        
        if self.fase_jogo == "DECIDIR_INICIATIVA":
            if self.dice_ui.ativo:
                self.dice_ui.handle_events(events, mouse_pos)
                if not self.dice_ui.ativo: self.fase_jogo = "RESULTADO_INICIATIVA"
                return None
                
            self.btn_rolar_iniciativa.update(mouse_pos)
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.btn_rolar_iniciativa.is_clicked(event):
                        self.res_p1 = random.randint(1, 20)
                        self.res_p2 = random.randint(1, 20)
                        while self.res_p1 == self.res_p2: self.res_p2 = random.randint(1, 20)
                        self.vencedor_id = "P1" if self.res_p1 > self.res_p2 else "P2"
                        self.dice_ui.rolar(self.res_p1)
            return None

        if self.fase_jogo == "RESULTADO_INICIATIVA":
            self.btn_comecar_partida.update(mouse_pos)
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.btn_comecar_partida.is_clicked(event):
                        self.controller.iniciar_partida(self.vencedor_id)
                        self.fase_jogo = "ANIMACAO_EMBARALHAR"
                        self.tempo_animacao = pygame.time.get_ticks()
            return None

        if self.fase_jogo == "ANIMACAO_EMBARALHAR":
            if pygame.time.get_ticks() - self.tempo_animacao > 1500:
                self.fase_jogo = "MULLIGAN"
            return None 
            
        if self.fase_jogo == "MULLIGAN":
            self.btn_manter_mao.update(mouse_pos)
            if self.mulligans_restantes > 0:
                self.btn_trocar_mao.update(mouse_pos)
                
            for event in events:
                if event.type == pygame.QUIT: return "SAIR"
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    
                    if self.btn_manter_mao.is_clicked(event):
                        print("[MESA] O Jogador manteve a mão.")
                        self.fase_jogo = "JOGANDO"
                        
                    elif self.mulligans_restantes > 0 and self.btn_trocar_mao.is_clicked(event):
                        self.mulligans_restantes -= 1
                        self.controller.executar_mulligan("P1")
                        self.fase_jogo = "ANIMACAO_EMBARALHAR"
                        self.tempo_animacao = pygame.time.get_ticks()
            return None

        if self.dice_ui.ativo:
            self.dice_ui.handle_events(events, mouse_pos)
            return None

        self.btn_dado_lateral.update(mouse_pos)
        for card_ui in self.mao_ui: card_ui.update(mouse_pos)

        for event in events:
            if event.type == pygame.QUIT: return "SAIR"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.btn_dado_lateral.is_clicked(event):
                    self.dice_ui.rolar(random.randint(1, 20))
                
                for i, card_ui in enumerate(self.mao_ui):
                    if card_ui.is_clicked(event):
                        self._processar_clique_mao(card_ui.card, i)
                        break
                
                for zona_ui in self.zonas["P1"].values():
                    for card_ui in zona_ui.cards_ui:
                        if card_ui.is_clicked(event):
                            if hasattr(self.controller, 'processar_clique_campo'):
                                self.controller.processar_clique_campo("P1", card_ui.card)
        return None

    def _processar_clique_mao(self, card, index):
        if card.is_land: self.controller.play_land("P1", index)
        elif card.is_creature: self.controller.cast_creature("P1", index)
        else: self.controller.cast_other("P1", index)

    def draw(self):
        self.screen.fill(BG)
        self.controller.sincronizar_view(self.zonas)

        for p_id in self.match.players.keys():
            self._desenhar_mesa_jogador(p_id)

        cx, cy = self.largura // 2, self.altura // 2

        if self.fase_jogo == "DECIDIR_INICIATIVA":
            if self.dice_ui.ativo:
                self.dice_ui.draw(self.screen)
            else:
                overlay = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                self.screen.blit(overlay, (0, 0))
                txt = self.fontes['titulo'].render("DECIDIR INICIATIVA", True, ACCENT)
                self.screen.blit(txt, (cx - txt.get_width()//2, cy - 120))
                self.btn_rolar_iniciativa.draw(self.screen)

        elif self.fase_jogo == "RESULTADO_INICIATIVA":
            overlay = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.screen.blit(overlay, (0, 0))
            cor_p1 = SUCCESS if self.vencedor_id == "P1" else TEXT_SEC
            cor_p2 = SUCCESS if self.vencedor_id == "P2" else TEXT_SEC
            txt_p1 = self.fontes['titulo'].render(f"VOCÊ TIROU: {self.res_p1}", True, cor_p1)
            txt_p2 = self.fontes['titulo'].render(f"OPONENTE TIROU: {self.res_p2}", True, cor_p2)
            msg = "VOCÊ COMEÇA!" if self.vencedor_id == "P1" else "O OPONENTE COMEÇA!"
            txt_msg = self.fontes['titulo'].render(msg, True, ACCENT)
            self.screen.blit(txt_p1, (cx - txt_p1.get_width()//2, cy - 180))
            self.screen.blit(txt_p2, (cx - txt_p2.get_width()//2, cy - 110))
            self.screen.blit(txt_msg, (cx - txt_msg.get_width()//2, cy - 10))
            self.btn_comecar_partida.draw(self.screen)

        elif self.fase_jogo == "ANIMACAO_EMBARALHAR":
            self._desenhar_animacao_embaralhar(cx, cy)

        elif self.fase_jogo == "MULLIGAN":
            caixa_rect = pygame.Rect(cx - 200, cy - 100, 400, 200)
            pygame.draw.rect(self.screen, (30, 30, 35), caixa_rect, border_radius=10)
            pygame.draw.rect(self.screen, ACCENT, caixa_rect, 2, border_radius=10)

            txt = self.fontes['label'].render("COMO ESTÁ SUA MÃO INICIAL?", True, TEXT_PRIMARY)
            self.screen.blit(txt, (cx - txt.get_width()//2, cy - 80))

            if self.mulligans_restantes > 0:
                txt_mul = self.fontes['status'].render(f"Você pode trocar mais {self.mulligans_restantes} vezes.", True, TEXT_SEC)
                self.btn_manter_mao.rect.x = cx - 160
                self.btn_trocar_mao.rect.x = cx + 10
                self.btn_trocar_mao.draw(self.screen)
            else:
                txt_mul = self.fontes['status'].render("Você não tem mais trocas!", True, DANGER)
                self.btn_manter_mao.rect.x = cx - 75 
                
            self.screen.blit(txt_mul, (cx - txt_mul.get_width()//2, cy - 50))
            self.btn_manter_mao.draw(self.screen)

        elif self.fase_jogo == "JOGANDO":
            self.btn_dado_lateral.draw(self.screen)
            if self.dice_ui.ativo:
                self.dice_ui.draw(self.screen)

    # =========================================================
    # EFEITO VISUAL DO EMBARALHAMENTO COM A SUA IMAGEM (fudo_cards.jpg)
    # =========================================================
    def _desenhar_animacao_embaralhar(self, cx, cy):
        overlay = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 230))
        self.screen.blit(overlay, (0, 0))
        
        tempo_passado = pygame.time.get_ticks() - self.tempo_animacao
        deslocamento = abs(math.sin(tempo_passado * 0.01)) * 90 
        
        w_carta, h_carta = self.card_w, self.card_h
        
        def desenhar_carta(rect):
            """Função auxiliar para desenhar o verso da carta."""
            if self.img_verso_carta:
                self.screen.blit(self.img_verso_carta, rect.topleft)
                # Adiciona uma borda dourada pra ficar estiloso
                pygame.draw.rect(self.screen, ACCENT, rect, 1, border_radius=4)
            else:
                # Se não achar a imagem, desenha o marrom antigo pra não travar o jogo
                pygame.draw.rect(self.screen, (43, 37, 33), rect, border_radius=6)
                pygame.draw.rect(self.screen, ACCENT, rect, 2, border_radius=6)

        # 1. Monte Central Fixo
        for i in range(3):
            rect_centro = pygame.Rect(cx - w_carta//2, cy - h_carta//2 - (i*3), w_carta, h_carta)
            desenhar_carta(rect_centro)

        # 2. Metades Voando (Esquerda e Direita)
        for i in range(5):
            rect_esq = pygame.Rect(cx - w_carta//2 - deslocamento - (i*6), cy - h_carta//2 - (i*2), w_carta, h_carta)
            desenhar_carta(rect_esq)
            
            rect_dir = pygame.Rect(cx - w_carta//2 + deslocamento + (i*6), cy - h_carta//2 - (i*2), w_carta, h_carta)
            desenhar_carta(rect_dir)

        # Texto
        pontos = "." * ((tempo_passado // 250) % 4)
        txt = self.fontes['titulo'].render(f"EMBARALHANDO{pontos}", True, ACCENT)
        self.screen.blit(txt, (cx - txt.get_width()//2, cy + h_carta + 20))

    def _desenhar_mesa_jogador(self, p_id):
        player = self.match.players[p_id]
        id_visual = 1 if p_id == "P1" else 2
        rect_area = self._get_area_jogador(id_visual, 2)
        eh_humano = (p_id == "P1")

        cor_fundo = (35, 35, 50) if eh_humano else (25, 25, 35)
        pygame.draw.rect(self.screen, cor_fundo, rect_area)
        pygame.draw.rect(self.screen, (100, 100, 120), rect_area, 2)
        
        status_txt = f"{player.name.upper()} | {player.life} PV"
        surf = self.fontes['label'].render(status_txt, True, TEXT_PRIMARY)
        self.screen.blit(surf, (rect_area.centerx - surf.get_width()//2, rect_area.y + 10))

        for zona_ui in self.zonas[p_id].values():
            zona_ui.draw(self.screen)

        if eh_humano:
            self._renderizar_mao(player.hand, rect_area)
        else:
            txt_mao = self.fontes['label'].render(f"Mão: {len(player.hand)} cartas", True, TEXT_SEC)
            self.screen.blit(txt_mao, (rect_area.centerx - txt_mao.get_width()//2, rect_area.bottom - 35))

    def _renderizar_mao(self, hand_models, rect_area):
        posicoes = LayoutEngine.get_hand_layout(rect_area, len(hand_models), self.card_w, self.card_h)
        self.mao_ui.clear()
        for i, (x, y) in enumerate(posicoes):
            model = hand_models[i]
            card_id = id(model)
            if card_id not in self.controller.ui_manager.ui_cards_cache:
                self.controller.ui_manager.ui_cards_cache[card_id] = CardUI(model, self.asset_manager, x, y, self.card_w, self.card_h)
            
            card_ui = self.controller.ui_manager.ui_cards_cache[card_id]
            card_ui.update_position(x, y)
            self.mao_ui.append(card_ui)
            card_ui.draw(self.screen)