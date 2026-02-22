from APP.domain.models.match_model import MatchModel
from APP.domain.models.player_model import PlayerModel
from APP.domain.services.deck_builder import DeckBuilderService
from APP.domain.services.rule_engine import RuleEngine

class MatchController:
    def __init__(self, ui_manager):
        """
        Orquestrador da Partida (Cérebro).
        Conecta a lógica de regras (RuleEngine) com a interface (UIManager).
        """
        self.match_model = None
        self.ui_manager = ui_manager 
        self.total_players = 2

    def setup_game(self, human_deck_data: dict, nickname: str = "Conjurador"):
        """Inicializa os modelos de jogo e prepara os grimórios."""
        print(f"[CONTROLLER] Setup da partida para {nickname}...")

        deck_p1 = DeckBuilderService.build_from_json(human_deck_data)
        deck_p2 = DeckBuilderService.build_from_json(human_deck_data)
        
        player_1 = PlayerModel(player_id="P1", name=nickname, deck=deck_p1)
        player_2 = PlayerModel(player_id="P2", name="Oponente 1", deck=deck_p2)
        
        self.match_model = MatchModel(player1=player_1, player2=player_2)
        print(f"[OK] Mesa montada. Aguardando rolagem de iniciativa.")

    def iniciar_partida(self, primeiro_jogador_id: str):
        """Prepara a mão inicial e liga o motor do GameState."""
        p1 = self.match_model.players["P1"]
        p2 = self.match_model.players["P2"]
        
        p1.deck.embaralhar()
        p2.deck.embaralhar()
        
        p1.draw_cards(7)
        p2.draw_cards(7)
        
        self._simular_mesa_bot(p2)
        
        # 🔥 PULO DO GATO: Deixa o GameState assumir o controle total do tempo!
        # Isso arruma o erro e já seta a fase para "PRINCIPAL 1" no turno 1
        self.match_model.state.iniciar_jogo(primeiro_jogador_id)

        primeiro_nome = self.match_model.players[primeiro_jogador_id].name
        print(f"\n[TURNO 1] {primeiro_nome} começa na fase {self.match_model.phase}!")
        
        # O Cérebro analisa as regras logo no primeiro frame
        self.atualizar_playables()

    # =========================================================
    # ATUALIZAÇÃO DE ESTADO (O Cérebro pensa aqui)
    # =========================================================
    def atualizar_playables(self):
        """
        Avalia as regras e define card.playable para as cartas na mão.
        Isso retira a responsabilidade da UI de entender as regras de Magic.
        """
        if not self.match_model: return

        for p_id, player in self.match_model.players.items():
            for card in player.hand:
                if card.is_land:
                    pode, _ = RuleEngine.validar_descida_terreno(self.match_model, p_id, card)
                else:
                    pode, _ = RuleEngine.validar_conjuracao(self.match_model, p_id, card)
                
                # Injeta a decisão final na carta para a UI apenas ler
                card.playable = pode

    # =========================================================
    # SINCRONIZAÇÃO DETERMINÍSTICA (Model -> View)
    # =========================================================
    def sincronizar_view(self, zonas_view):
        """Garante que a UI reflita estritamente o Model atual, sem lixo."""
        if not self.match_model or not self.ui_manager: return

        # 1. Pensa nas regras antes de mandar a UI desenhar
        self.atualizar_playables()

        # 2. Distribui as cartas exatamente para onde pertencem
        for p_id, player in self.match_model.players.items():
            
            # Limpeza completa (Garante que a UI zere e não crie fantasmas)
            for zona in zonas_view[p_id].values():
                zona.clear_cards() 

            self.ui_manager.sincronizar_zona_visual(zonas_view[p_id]["MANA"], player.battlefield_lands)
            
            campo_total = player.battlefield_creatures + player.battlefield_other
            self.ui_manager.sincronizar_zona_visual(zonas_view[p_id]["CAMPO"], campo_total)
            
            self.ui_manager.sincronizar_zona_visual(zonas_view[p_id]["CEMITERIO"], player.graveyard)
            self.ui_manager.sincronizar_zona_visual(zonas_view[p_id]["EXILIO"], player.exile)
            self.ui_manager.sincronizar_zona_visual(zonas_view[p_id]["COMANDANTE"], player.commander_zone)

    # =========================================================
    # AÇÕES DO JOGADOR
    # =========================================================
    def play_land(self, player_id: str, hand_index: int):
        player = self.match_model.players.get(player_id)
        if not player or hand_index >= len(player.hand): return

        card = player.hand[hand_index]
        # Agora o Controller só confia na flag playable que ele mesmo calculou
        if card.playable:
            player.play_land(hand_index)
            player.lands_played_this_turn += 1
            print(f"[AÇÃO] {player.name} desceu terreno: {card.name}")
        else:
            _, motivo = RuleEngine.validar_descida_terreno(self.match_model, player_id, card)
            print(f"[BLOQUEADO] {motivo}")

    def cast_creature(self, player_id: str, hand_index: int):
        player = self.match_model.players.get(player_id)
        if not player or hand_index >= len(player.hand): return

        card = player.hand[hand_index]
        if card.playable:
            player.cast_creature(hand_index)
            print(f"[AÇÃO] {player.name} conjurou criatura: {card.name}")
        else:
            _, motivo = RuleEngine.validar_conjuracao(self.match_model, player_id, card)
            print(f"[BLOQUEADO] {motivo}")

    def cast_other(self, player_id: str, hand_index: int):
        player = self.match_model.players.get(player_id)
        if not player or hand_index >= len(player.hand): return

        card = player.hand[hand_index]
        if card.playable:
            player.cast_other(hand_index)
            print(f"[AÇÃO] {player.name} usou: {card.name}")
        else:
            _, motivo = RuleEngine.validar_conjuracao(self.match_model, player_id, card)
            print(f"[BLOQUEADO] {motivo}")

    # =========================================================
    # CONTROLE DE SISTEMA
    # =========================================================
    def next_phase(self):
        self.match_model.next_phase()
        print(f"[TURNO] Avançando para: {self.match_model.phase}")

    def executar_mulligan(self, player_id: str):
        player = self.match_model.players.get(player_id)
        if player:
            player.return_hand_to_deck()
            player.draw_cards(7)
            print(f"[MESA] {player.name} refez a mão (Mulligan).")

    def mudar_vida(self, player_id: str, quantidade: int):
        player = self.match_model.players.get(player_id)
        if player:
            if quantidade > 0: player.life += quantidade
            else: player.take_damage(abs(quantidade))

    def _simular_mesa_bot(self, bot: PlayerModel):
        if len(bot.hand) >= 3:
            bot.battlefield_lands.append(bot.hand.pop())
            bot.battlefield_creatures.append(bot.hand.pop())