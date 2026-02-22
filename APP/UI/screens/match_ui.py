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
from APP.UI.components.mana_bar_ui import ManaBarUI
from APP.UI.components.phase_bar_ui import PhaseBarUI

# 🚨 PULO DO GATO: A importação do RuleEngine foi DELETADA. A UI não pensa mais, só obedece!

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
        self.mao_ui = []

        self.dice_ui = DiceOverlayUI(self.largura, self.altura, self.fontes)
        self.mana_bar_ui = ManaBarUI(self.fontes)
        self.phase_bar_ui = PhaseBarUI(self.largura, self.altura, self.fontes)

        self.fase_jogo = "DECIDIR_INICIATIVA" 
        self.res_p1 = 0
        self.res_p2 = 0
        self.vencedor_id = None
        self.quem_esta_rolando = "VOCÊ" 

        self.mulligans_restantes = 3
        self.tempo_animacao = 0

        self.img_verso_carta = None
        caminho_verso = "assets/img/fudo_cards.jpg"
        if os.path.exists(caminho_verso):
            try:
                img_temp = pygame.image.load(caminho_verso).convert_alpha()
                self.img_verso_carta = pygame.transform.smoothscale(img_temp, (self.card_w, self.card_h))
            except Exception: pass

        self._inicializar_zonas()

        cx, cy = self.largura // 2, self.altura // 2
        self.btn_rolar_iniciativa = MenuButton(pygame.Rect(cx - 150, cy - 25, 300, 50), "ROLAR INICIATIVA (D20)", self.fontes['menu'])
        self.btn_comecar_partida = MenuButton(pygame.Rect(cx - 150, cy + 100, 300, 50), "COMPRAR CARTAS E INICIAR", self.fontes['menu'])
        self.btn_manter_mao = MenuButton(pygame.Rect(cx - 160, cy + 20, 150, 50), "MANTER", self.fontes['menu'])
        self.btn_trocar_mao = MenuButton(pygame.Rect(cx + 10, cy + 20, 150, 50), "MULLIGAN", self.fontes['menu'])
        
        y_barra_inf = self.altura - 55
        self.btn_dado_lateral = MenuButton(pygame.Rect(20, y_barra_inf, 80, 45), "D20", self.fontes['menu'])
        self.btn_passar_fase = MenuButton(pygame.Rect(self.largura - 200, y_barra_inf, 180, 45), "PASSAR FASE", self.fontes['menu'])

    def _get_area_jogador(self, id_visual, qtd):
        topo, base = 40, 60
        altura_util = self.altura - topo - base
        meio = altura_util // 2
        if id_visual == 2: return pygame.Rect(0, topo, self.largura, meio)      
        return pygame.Rect(0, topo + meio, self.largura, meio)

    def _inicializar_zonas(self):
        for p_id in self.match.players.keys():
            id_visual = 1 if p_id == "P1" else 2
            area = self._get_area_jogador(id_visual, 2)
            col_w, margin, header_space = area.width * 0.16, 15, 50
            h_esq, h_dir = area.height * 0.35, area.height * 0.22
            
            if id_visual == 1:
                cmd_x, grave_x = area.x + margin, area.right - col_w - margin
                cmd_y, mana_y = area.y + header_space, area.y + header_space + h_esq + 10
                grave_y, exile_y, deck_y = area.y + header_space, area.y + header_space + h_dir + 10, area.y + header_space + (h_dir + 10) * 2
                campo_x = cmd_x + col_w + margin
            else:
                cmd_x, grave_x = area.right - col_w - margin, area.x + margin
                mana_y, cmd_y = area.y + header_space, area.y + header_space + h_esq + 10
                deck_y, exile_y, grave_y = area.y + header_space, area.y + header_space + h_dir + 10, area.y + header_space + (h_dir + 10) * 2
                campo_x = grave_x + col_w + margin
            
            self.zonas[p_id] = {
                "COMANDANTE": ZoneUI(pygame.Rect(cmd_x, cmd_y, col_w, h_esq), "COMANDANTE", (45, 45, 70), "stack"),
                "MANA": ZoneUI(pygame.Rect(cmd_x, mana_y, col_w, h_esq), "MANA", (30, 50, 30), "overlap"),
                "CEMITERIO": ZoneUI(pygame.Rect(grave_x, grave_y, col_w, h_dir), "CEMITÉRIO", (40, 30, 30), "stack"),
                "EXILIO": ZoneUI(pygame.Rect(grave_x, exile_y, col_w, h_dir), "EXÍLIO", (30, 45, 45), "stack"),
                "GRIMORIO": ZoneUI(pygame.Rect(grave_x, deck_y, col_w, h_dir), "GRIMÓRIO", (30, 30, 45), "stack"),
                "CAMPO": ZoneUI(pygame.Rect(campo_x, area.y + header_space, area.width - (col_w * 2) - (margin * 4), area.height * 0.8), "CAMPO", (40, 45, 40), "grid")
            }

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        if self.fase_jogo == "ANIMACAO_EMBARALHAR": return None

        if self.fase_jogo == "DECIDIR_INICIATIVA":
            if self.dice_ui.ativo:
                self.dice_ui.handle_events(events, mouse_pos)
                if not self.dice_ui.ativo:
                    if self.quem_esta_rolando == "VOCÊ":
                        self.quem_esta_rolando = "OPONENTE"; self.dice_ui.rolar(self.res_p2)
                    else: self.fase_jogo = "RESULTADO_INICIATIVA"
                return None
            self.btn_rolar_iniciativa.update(mouse_pos)
            for e in events:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and self.btn_rolar_iniciativa.is_clicked(e):
                    self.res_p1, self.res_p2 = random.randint(1, 20), random.randint(1, 20)
                    while self.res_p1 == self.res_p2: self.res_p2 = random.randint(1, 20)
                    self.vencedor_id = "P1" if self.res_p1 > self.res_p2 else "P2"
                    self.quem_esta_rolando = "VOCÊ"; self.dice_ui.rolar(self.res_p1)
            return None

        if self.fase_jogo == "RESULTADO_INICIATIVA":
            self.btn_comecar_partida.update(mouse_pos)
            for e in events:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and self.btn_comecar_partida.is_clicked(e):
                    self.controller.iniciar_partida(self.vencedor_id)
                    self.fase_jogo = "ANIMACAO_EMBARALHAR"; self.tempo_animacao = pygame.time.get_ticks()
            return None

        if self.fase_jogo == "MULLIGAN":
            self.btn_manter_mao.update(mouse_pos); self.btn_trocar_mao.update(mouse_pos)
            for e in events:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if self.btn_manter_mao.is_clicked(e): self.fase_jogo = "JOGANDO"
                    elif self.mulligans_restantes > 0 and self.btn_trocar_mao.is_clicked(e):
                        self.mulligans_restantes -= 1; self.controller.executar_mulligan("P1")
                        self.fase_jogo = "ANIMACAO_EMBARALHAR"; self.tempo_animacao = pygame.time.get_ticks()
            return None

        if self.dice_ui.ativo: self.dice_ui.handle_events(events, mouse_pos); return None

        self.btn_dado_lateral.update(mouse_pos); self.btn_passar_fase.update(mouse_pos)
        for cui in self.mao_ui: cui.update(mouse_pos)
        
        for e in events:
            if e.type == pygame.QUIT: return "SAIR"
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self.btn_dado_lateral.is_clicked(e): self.dice_ui.rolar(random.randint(1, 20))
                if self.btn_passar_fase.is_clicked(e): self.controller.next_phase()
                for i, cui in enumerate(self.mao_ui):
                    if cui.is_clicked(e) and not getattr(cui, 'is_disabled', False): 
                        self._processar_clique_mao(cui.card, i); break
        return None

    def draw(self):
        self.screen.fill(BG)
        # 1. SINCRONIZAÇÃO: Garante que os modelos do Controller virem UIs nas zonas
        self.controller.sincronizar_view(self.zonas)
        
        # 2. DESENHO DAS MESAS
        for p_id in self.match.players.keys(): 
            self._desenhar_mesa_jogador(p_id)

        # 3. BARRAS FIXAS
        player_ativo = self.match.get_active_player()
        nome_jogador_ativo = player_ativo.name if player_ativo else "PREPARANDO..."
        
        self.phase_bar_ui.draw(self.screen, self.match.phase, nome_jogador_ativo)
        
        pygame.draw.rect(self.screen, (25, 25, 30), (0, self.altura - 60, self.largura, 60))
        pygame.draw.rect(self.screen, ACCENT, (0, self.altura - 60, self.largura, 2))
        self.btn_dado_lateral.draw(self.screen); self.btn_passar_fase.draw(self.screen)

        cx, cy = self.largura // 2, self.altura // 2
        if self.fase_jogo == "DECIDIR_INICIATIVA":
            if self.dice_ui.ativo: self.dice_ui.draw(self.screen)
            else: self.btn_rolar_iniciativa.draw(self.screen)
        elif self.fase_jogo == "RESULTADO_INICIATIVA": self.btn_comecar_partida.draw(self.screen)
        elif self.fase_jogo == "ANIMACAO_EMBARALHAR": self._desenhar_animacao_embaralhar(cx, cy)
        elif self.fase_jogo == "MULLIGAN": self._desenhar_painel_mulligan(cx, cy)
        elif self.dice_ui.ativo: self.dice_ui.draw(self.screen)

    def _desenhar_mesa_jogador(self, p_id):
        player = self.match.players[p_id]
        id_v = 1 if p_id == "P1" else 2
        area = self._get_area_jogador(id_v, 2)
        pygame.draw.rect(self.screen, (30, 30, 45) if id_v==1 else (25, 25, 35), area)
        
        txt = self.fontes['label'].render(f"{player.name.upper()} | {player.life} PV", True, TEXT_PRIMARY)
        self.screen.blit(txt, (area.centerx - txt.get_width()//2, area.y + 10))
        
        self.mana_bar_ui.draw(self.screen, player, area)
        
        for nome, z in self.zonas[p_id].items():
            if nome != "GRIMORIO": z.draw(self.screen)
        
        z_deck = self.zonas[p_id]["GRIMORIO"]
        self._render_grimorio(z_deck.rect.centerx - self.card_w//2, z_deck.rect.centery - self.card_h//2, len(player.deck.library))
        
        if id_v == 1: 
            self._renderizar_mao(player.hand, area)
        else:
            txt_m = self.fontes['label'].render(f"Mão: {len(player.hand)} cartas", True, TEXT_SEC)
            self.screen.blit(txt_m, (area.centerx - txt_m.get_width()//2, area.bottom - 25))

    def _renderizar_mao(self, h_m, area):
        mouse_pos = pygame.mouse.get_pos()
        fase_ok = self.match.phase in ["PRINCIPAL 1", "PRINCIPAL 2"]
        hover_grupo = area.collidepoint(mouse_pos) and fase_ok
        
        posicoes = LayoutEngine.get_hand_layout(area, len(h_m), self.card_w, self.card_h, hover_grupo)
        self.mao_ui.clear()
        
        for i, layout_data in enumerate(posicoes):
            x, y, zoom = layout_data
            model = h_m[i]
            mid = id(model)
            w_z, h_z = int(self.card_w * zoom), int(self.card_h * zoom)
            
            if mid not in self.controller.ui_manager.ui_cards_cache:
                self.controller.ui_manager.ui_cards_cache[mid] = CardUI(model, self.asset_manager, x, y, w_z, h_z)
            
            cui = self.controller.ui_manager.ui_cards_cache[mid]
            cui.rect.width, cui.rect.height = w_z, h_z 
            cui.update_position(x, y)
            
            # 🔥 ARQUITETURA MVC LIMPA: A tela apenas LÊ a propriedade definida pelo Controller!
            cui.is_disabled = not getattr(model, 'playable', False)
            
            self.mao_ui.append(cui)
            cui.draw(self.screen)

    def _render_grimorio(self, x, y, qtd):
        for i in range(min(3, qtd)): self._render_verso_simples(pygame.Rect(x + (i*2), y - (i*2), self.card_w, self.card_h))

    def _render_verso_simples(self, rect):
        if self.img_verso_carta: self.screen.blit(self.img_verso_carta, rect.topleft)
        else: pygame.draw.rect(self.screen, (43, 37, 33), rect, border_radius=6)
        pygame.draw.rect(self.screen, ACCENT, rect, 1, border_radius=4)

    def _desenhar_animacao_embaralhar(self, cx, cy):
        overlay = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA); overlay.fill((0, 0, 0, 200)); self.screen.blit(overlay, (0, 0))
        t = pygame.time.get_ticks() - self.tempo_animacao
        if t > 2000: self.fase_jogo = "MULLIGAN"
        dist = abs(math.sin(t * 0.01)) * 130 
        w, h = self.card_w, self.card_h
        for i in range(5):
            self._render_verso_simples(pygame.Rect(cx - w//2 - dist - (i*6), cy - h//2, w, h))
            self._render_verso_simples(pygame.Rect(cx - w//2 + dist + (i*6), cy - h//2, w, h))
        txt = self.fontes['titulo'].render(f"EMBARALHANDO{'.' * ((t // 300) % 4)}", True, ACCENT)
        self.screen.blit(txt, (cx - txt.get_width()//2, cy + h + 20))

    def _desenhar_painel_mulligan(self, cx, cy):
        caixa = pygame.Rect(cx - 200, cy - 80, 400, 160)
        pygame.draw.rect(self.screen, (30, 30, 35), caixa, border_radius=10)
        pygame.draw.rect(self.screen, ACCENT, caixa, 2, border_radius=10)
        txt = self.fontes['label'].render("MÃO INICIAL ESTÁ BOA?", True, TEXT_PRIMARY)
        self.screen.blit(txt, (cx - txt.get_width()//2, cy - 60))
        self.btn_manter_mao.draw(self.screen); self.btn_trocar_mao.draw(self.screen)

    def _processar_clique_mao(self, card, index):
        """
        🔥 ATUALIZAÇÃO DETERMINÍSTICA:
        A UI não decide mais qual método chamar (play_land, cast_creature, etc).
        Ela apenas informa ao Controller que o jogador tentou jogar a carta do index X.
        O Controller decide se é terreno ou mágica e aplica a regra.
        """
        self.controller.jogar_carta("P1", index)
        self.mao_ui.clear()
