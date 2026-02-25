from APP.domain.models.match_model import MatchModel
from APP.domain.models.player_model import PlayerModel
from APP.domain.services.deck_builder import DeckBuilderService
from APP.domain.services.rule_engine import RuleEngine
from APP.domain.services.mana_manager import ManaManager 

class MatchController:
    def __init__(self, ui_manager):
        self.match_model = None
        self.ui_manager = ui_manager 
        self.total_players = 2

    # =========================================================
    # CONFIGURAÇÃO E INÍCIO
    # =========================================================

    def setup_game(self, human_deck_data: dict, nickname: str = "Conjurador"):
        print(f"[CONTROLLER] Setup da partida para {nickname}...")
        deck_p1 = DeckBuilderService.build_from_json(human_deck_data)
        deck_p2 = DeckBuilderService.build_from_json(human_deck_data)
        
        player_1 = PlayerModel(player_id="P1", name=nickname, deck=deck_p1)
        player_2 = PlayerModel(player_id="P2", name="Oponente 1", deck=deck_p2)
        
        self.match_model = MatchModel(player1=player_1, player2=player_2)
        print(f"[OK] Mesa montada. Aguardando rolagem de iniciativa.")

    def iniciar_partida(self, primeiro_jogador_id: str):
        p1 = self.match_model.players["P1"]
        p2 = self.match_model.players["P2"]
        p1.deck.embaralhar()
        p2.deck.embaralhar()
        p1.draw_cards(7)
        p2.draw_cards(7)
        
        self._simular_mesa_bot(p2)
        
        self.match_model.state.iniciar_jogo(primeiro_jogador_id)
        self.match_model.starting_player_id = primeiro_jogador_id
        
        primeiro_nome = self.match_model.players[primeiro_jogador_id].name
        print(f"\n[TURNO 1] {primeiro_nome} começa na fase {self.match_model.phase}!")
        self.atualizar_playables()

    # =========================================================
    # LÓGICA DE REGRAS E GESTÃO DE MANA
    # =========================================================

    def atualizar_playables(self):
        if not self.match_model: return
        for p_id, player in self.match_model.players.items():
            for card in player.hand:
                tipo = getattr(card, 'type_line', "").lower()
                is_land = "land" in tipo or getattr(card, 'is_land', False)
                
                if is_land:
                    pode, _ = RuleEngine.validar_descida_terreno(self.match_model, p_id, card)
                else:
                    pode, _ = RuleEngine.validar_conjuracao(self.match_model, p_id, card)
                card.playable = pode

    def virar_terreno_para_mana(self, player_id: str, card):
        player = self.match_model.players.get(player_id)
        if not player or not card.is_land or card.is_tapped:
            return
        cor_gerada = ManaManager.gerar_mana(player, card)
        if cor_gerada:
            card.tap()
            print(f"[MANA] {player.name} virou {card.name} (+1 {cor_gerada})")
            self.atualizar_playables()

    # =========================================================
    # AÇÕES DE JOGO E MUDANÇA DE FASE
    # =========================================================

    def jogar_carta(self, player_id: str, hand_index: int):
        player = self.match_model.players.get(player_id)
        if not player or hand_index >= len(player.hand): return
        
        card = player.hand[hand_index]
        is_land = card.is_land
        is_creature = card.is_creature

        if is_land:
            pode, motivo = RuleEngine.validar_descida_terreno(self.match_model, player_id, card)
            if pode:
                player.play_land(hand_index)
                player.lands_played_this_turn += 1
                print(f"[AÇÃO] {player.name} jogou TERRENO: {card.name}")
            else:
                print(f"[BLOQUEADO] {card.name}: {motivo}")
        else:
            pode, motivo = RuleEngine.validar_conjuracao(self.match_model, player_id, card)
            if pode:
                ManaManager.descontar_custo(player, card)
                if is_creature:
                    player.cast_creature(hand_index)
                else:
                    player.cast_other(hand_index)
                print(f"[AÇÃO] {player.name} pagou custo e conjurou: {card.name}")
            else:
                print(f"[BLOQUEADO] {card.name}: {motivo}")

        self.atualizar_playables()

    def next_phase(self):
        """Avança as fases e processa regras de manutenção (Untap e Draw)."""
        # 1. Avança o estado no modelo
        self.match_model.next_phase()
        
        # 2. Captura dados do estado atualizado
        fase_atual = str(self.match_model.phase).upper()
        active_id = self.match_model.active_player_id
        player = self.match_model.players.get(active_id)
        
        if not player: return

        # 3. Processa a Fase INICIAL (Untap + Draw unificados)
        if "INICIAL" in fase_atual or "UNTAP" in fase_atual:
            # A) DESVIRAR E RESETAR POOL
            todas_cartas = player.battlefield_lands + player.battlefield_creatures + player.battlefield_other
            for c in todas_cartas:
                c.untap()
            
            player.lands_played_this_turn = 0
            player.mana_pool = {k: 0 for k in player.mana_pool}
            print(f"[REGRAS] Turno de {player.name}: Tudo desvirado e Pool resetada.")

            # B) COMPRA AUTOMÁTICA (Regra Turno 1)
            turno_global = getattr(self.match_model, 'turn_count', 1)
            starter_id = getattr(self.match_model, 'starting_player_id', None)

            if turno_global == 1 and active_id == starter_id:
                print(f"[REGRAS] {player.name} pula a compra no Turno 1.")
            else:
                player.draw_cards(1)
                print(f"[REGRAS] {player.name} comprou a carta do turno.")

        # 4. LIMPEZA DE MANA (Sempre ocorre ao mudar de qualquer fase)
        player.mana_pool = {k: 0 for k in player.mana_pool}
        
        self.atualizar_playables()
        print(f"[TURNO] Fase atual: {fase_atual}")

    # =========================================================
    # UTILITÁRIOS E SINCRONIZAÇÃO
    # =========================================================

    def sincronizar_view(self, zones_view):
        if not self.match_model or not self.ui_manager: return
        self.atualizar_playables()
        for p_id, player in self.match_model.players.items():
            for zona in zones_view[p_id].values():
                zona.clear_cards() 
            self.ui_manager.sincronizar_zona_visual(zones_view[p_id]["MANA"], player.battlefield_lands)
            campo_total = player.battlefield_creatures + player.battlefield_other
            self.ui_manager.sincronizar_zona_visual(zones_view[p_id]["CAMPO"], campo_total)
            self.ui_manager.sincronizar_zona_visual(zones_view[p_id]["CEMITERIO"], player.graveyard)
            self.ui_manager.sincronizar_zona_visual(zones_view[p_id]["EXILIO"], player.exile)
            self.ui_manager.sincronizar_zona_visual(zones_view[p_id]["COMANDANTE"], player.commander_zone)

    def executar_mulligan(self, player_id: str):
        player = self.match_model.players.get(player_id)
        if player:
            player.return_hand_to_deck()
            player.draw_cards(7)
            self.atualizar_playables()
            print(f"[MESA] {player.name} realizou Mulligan.")

    def mudar_vida(self, player_id: str, quantidade: int):
        player = self.match_model.players.get(player_id)
        if player:
            if quantidade > 0: player.life += quantidade
            else: player.take_damage(abs(quantidade))

    def _simular_mesa_bot(self, bot: PlayerModel):
        if len(bot.hand) >= 3:
            bot.battlefield_lands.append(bot.hand.pop())
            bot.battlefield_creatures.append(bot.hand.pop())
