import pygame
from APP.UI.screens.base_screens import BaseScreen
from APP.UI.styles.colors import BG, TEXT_PRIMARY, TEXT_SEC
from APP.UI.styles.fonts import get_fonts
from APP.UI.components.card_ui import CardUI
from APP.UI.components.zone_ui import ZoneUI
from APP.UI.layout.grid import LayoutEngine

class MatchView(BaseScreen):
    def __init__(self, screen, controller, asset_manager): 
        """
        Visualização da Mesa de Jogo.
        Gerencia o layout das zonas e a interação com a mão do jogador.
        """
        super().__init__(screen, controller)
        self.asset_manager = asset_manager 
        self.largura, self.altura = self.screen.get_size()
        self.fontes = get_fonts()
        self.match = self.controller.match_model
        
        # Configurações de tamanho das cartas
        self.card_w = 75
        self.card_h = 105
        
        # Estrutura de Zonas de UI
        self.zonas = {}
        self._inicializar_zonas()

        # Cache local para componentes da mão
        self.mao_ui = []

    def _inicializar_zonas(self):
        """Define onde cada zona (Campo, Mana, Cemitério) fica na tela."""
        for p_id in self.match.players.keys():
            # Define se é a parte de cima ou de baixo da tela
            id_visual = 1 if p_id == "P1" else 2
            rect_area = self._get_area_jogador(id_visual, 2)
            
            col_w = rect_area.width * 0.18
            
            # 1. Zona de Comandante
            z_cmd = ZoneUI(pygame.Rect(rect_area.x + 10, rect_area.y + 45, col_w, rect_area.height * 0.38), 
                           "COMANDANTE", (45, 45, 70), "stack")
            
            # 2. Zona de Mana/Terrenos
            z_mana = ZoneUI(pygame.Rect(rect_area.x + 10, z_cmd.rect.bottom + 10, col_w, rect_area.height * 0.38), 
                            "MANA", (30, 50, 30), "overlap")
            
            # 3. Cemitério
            z_grave = ZoneUI(pygame.Rect(rect_area.right - col_w - 10, rect_area.y + 45, col_w, rect_area.height * 0.38), 
                             "CEMITÉRIO", (40, 30, 30), "stack")
            
            # 4. Exílio
            z_exile = ZoneUI(pygame.Rect(rect_area.right - col_w - 10, z_grave.rect.bottom + 10, col_w, rect_area.height * 0.38), 
                             "EXÍLIO", (30, 45, 45), "stack")
            
            # 5. Campo de Batalha (Centro)
            battle_w = rect_area.width - (col_w * 2) - 50
            z_battle = ZoneUI(pygame.Rect(z_cmd.rect.right + 15, rect_area.y + 45, battle_w, rect_area.height * 0.82), 
                              "CAMPO", (40, 45, 40), "grid")

            self.zonas[p_id] = {
                "COMANDANTE": z_cmd,
                "MANA": z_mana,
                "CEMITERIO": z_grave,
                "EXILIO": z_exile,
                "CAMPO": z_battle
            }

    def _get_area_jogador(self, id_visual, qtd):
        """Divide a tela ao meio: P2 em cima, P1 em baixo."""
        w, h = self.largura, self.altura
        if id_visual == 2: return pygame.Rect(0, 0, w, h // 2)      
        return pygame.Rect(0, h // 2, w, h // 2)

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        
        # Atualiza estado de hover das cartas na mão
        for card_ui in self.mao_ui:
            card_ui.update(mouse_pos)

        for event in events:
            if event.type == pygame.QUIT: return "SAIR"
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Clique na mão do Jogador 1 (Humano)
                for i, card_ui in enumerate(self.mao_ui):
                    if card_ui.is_clicked(event):
                        self._processar_clique_mao(card_ui.card, i)
                        break
                
                # Clique em cartas que já estão nas zonas (Campo/Mana)
                for zona_ui in self.zonas["P1"].values():
                    for card_ui in zona_ui.cards_ui:
                        if card_ui.is_clicked(event):
                            # Se clicar no campo, chama a ação de Tap/Ativar no controller
                            if hasattr(self.controller, 'processar_clique_campo'):
                                self.controller.processar_clique_campo("P1", card_ui.card)
        return None

    def _processar_clique_mao(self, card, index):
        """Identifica o tipo de carta e envia a ação correta para o controlador."""
        if card.is_land:
            self.controller.play_land("P1", index)
        elif card.is_creature:
            self.controller.cast_creature("P1", index)
        else:
            # Garante que o MatchController tenha o método cast_other
            self.controller.cast_other("P1", index)

    def draw(self):
        """Renderiza o frame completo da partida."""
        self.screen.fill(BG)
        
        # 1. SINCRONIZAÇÃO: O Controller pede para o UIManager atualizar as listas de CardUI
        self.controller.sincronizar_view(self.zonas)

        # 2. RENDERIZAÇÃO POR JOGADOR
        for p_id in self.match.players.keys():
            self._desenhar_mesa_jogador(p_id)

    def _desenhar_mesa_jogador(self, p_id):
        player = self.match.players[p_id]
        id_visual = 1 if p_id == "P1" else 2
        rect_area = self._get_area_jogador(id_visual, 2)
        eh_humano = (p_id == "P1")

        # Fundo e moldura da área do jogador
        cor_fundo = (35, 35, 50) if eh_humano else (25, 25, 35)
        pygame.draw.rect(self.screen, cor_fundo, rect_area)
        pygame.draw.rect(self.screen, (100, 100, 120), rect_area, 2)
        
        # Barra de Status (Nome e Vida)
        status_txt = f"{player.name.upper()} | {player.life} PV"
        surf = self.fontes['label'].render(status_txt, True, TEXT_PRIMARY)
        self.screen.blit(surf, (rect_area.centerx - surf.get_width()//2, rect_area.y + 10))

        # Desenha as Zonas Populadas
        for zona_ui in self.zonas[p_id].values():
            zona_ui.draw(self.screen)

        # Renderiza a Mão
        if eh_humano:
            self._renderizar_mao(player.hand, rect_area)
        else:
            # Oponente mostra apenas contagem de cartas
            txt_mao = self.fontes['label'].render(f"Mão: {len(player.hand)} cartas", True, TEXT_SEC)
            self.screen.blit(txt_mao, (rect_area.centerx - txt_mao.get_width()//2, rect_area.bottom - 35))

    def _renderizar_mao(self, hand_models, rect_area):
        """Calcula posições e desenha as cartas na mão do jogador humano."""
        posicoes = LayoutEngine.get_hand_layout(rect_area, len(hand_models), self.card_w, self.card_h)
        self.mao_ui.clear()
        
        for i, (x, y) in enumerate(posicoes):
            model = hand_models[i]
            card_id = id(model)
            
            # Busca no cache do UIManager para não recarregar a imagem todo frame
            if card_id not in self.controller.ui_manager.ui_cards_cache:
                new_card = CardUI(model, self.asset_manager, x, y, self.card_w, self.card_h)
                self.controller.ui_manager.ui_cards_cache[card_id] = new_card
            
            card_ui = self.controller.ui_manager.ui_cards_cache[card_id]
            card_ui.update_position(x, y)
            self.mao_ui.append(card_ui)
            card_ui.draw(self.screen)