from APP.domain.models.match_model import MatchModel
from APP.domain.models.player_model import PlayerModel
from APP.domain.services.deck_builder import DeckBuilderService
from APP.domain.services.rule_engine import RuleEngine

class MatchController:
    def __init__(self, ui_manager):
        """
        Orquestrador da Partida.
        Conecta a lógica de regras (RuleEngine) com a interface (UIManager).
        """
        self.match_model = None
        self.ui_manager = ui_manager 
        self.total_players = 2

    def setup_game(self, human_deck_data: dict, nickname: str = "Conjurador"):
        """
        Inicializa os modelos de jogo e prepara os grimórios.
        """
        print(f"[CONTROLLER] Setup da partida para {nickname}...")

        deck_p1 = DeckBuilderService.build_from_json(human_deck_data)
        deck_p2 = DeckBuilderService.build_from_json(human_deck_data)
        
        player_1 = PlayerModel(player_id="P1", name=nickname, deck=deck_p1)
        player_2 = PlayerModel(player_id="P2", name="Oponente 1", deck=deck_p2)
        
        self.match_model = MatchModel(player1=player_1, player2=player_2)
        print(f"[OK] Mesa montada. Aguardando rolagem de iniciativa.")

    def iniciar_partida(self, primeiro_jogador_id: str):
        """
        Chamado após o vencedor do dado ser decidido.
        Prepara a mão inicial e força o início na fase correta.
        """
        self.match_model.active_player_id = primeiro_jogador_id
        
        p1 = self.match_model.players["P1"]
        p2 = self.match_model.players["P2"]
        
        p1.deck.embaralhar()
        p2.deck.embaralhar()
        
        p1.draw_cards(7)
        p2.draw_cards(7)
        
        self._simular_mesa_bot(p2)
        
        # Sincroniza com as 5 fases em Português conforme o PhaseBarUI
        try:
            self.match_model.current_phase_index = self.match_model.phases.index("PRINCIPAL 1")
        except ValueError:
            self.match_model.current_phase_index = 0

        primeiro_nome = self.match_model.players[primeiro_jogador_id].name
        print(f"\n[TURNO 1] {primeiro_nome} começa na fase {self.match_model.phase}!")

    # =========================================================
    # SINCRONIZAÇÃO (Ponto vital para o Zoom e Destino das Cartas)
    # =========================================================
    def sincronizar_view(self, zonas_view):
        """
        Distribui as cartas do modelo para as zonas visuais (ZoneUI).
        AJUSTE MACHETE: Separação rigorosa entre MANA e CAMPO central.
        """
        if not self.match_model or not self.ui_manager: return

        for p_id, player in self.match_model.players.items():
            # 1. ZONA DE MANA: Apenas terrenos (battlefield_lands)
            # Isso impede que o terreno vá para o centro da tela
            self.ui_manager.sincronizar_zona_visual(zonas_view[p_id]["MANA"], player.battlefield_lands)
            
            # 2. ZONA DE CAMPO: Criaturas + Artefatos/Encantamentos
            # PULO DO GATO: battlefield_other corrigido (sem o 's') para evitar AttributeError
            campo_total = player.battlefield_creatures + player.battlefield_other
            self.ui_manager.sincronizar_zona_visual(zonas_view[p_id]["CAMPO"], campo_total)
            
            # 3. ZONAS DE APOIO (Cemitério, Exílio e Comando)
            self.ui_manager.sincronizar_zona_visual(zonas_view[p_id]["CEMITERIO"], player.graveyard)
            self.ui_manager.sincronizar_zona_visual(zonas_view[p_id]["EXILIO"], player.exile)
            
            # Comandante (Tratado como uma lista de 1 carta para a ZoneUI)
            self.ui_manager.sincronizar_zona_visual(zonas_view[p_id]["COMANDANTE"], player.commander_zone)

    # =========================================================
    # AÇÕES DO JOGADOR (Cliques na Mão)
    # =========================================================
    def play_land(self, player_id: str, hand_index: int):
        player = self.match_model.players.get(player_id)
        if not player or hand_index >= len(player.hand): return

        card = player.hand[hand_index]
        # O RuleEngine valida se já baixou terreno este turno ou se está na fase errada
        permitido, motivo = RuleEngine.validar_descida_terreno(self.match_model, player_id, card)
        
        if permitido:
            player.play_land(hand_index)
            player.lands_played_this_turn += 1
            print(f"[AÇÃO] {player.name} desceu terreno: {card.name}")
        else:
            print(f"[BLOQUEADO] {motivo}")

    def cast_creature(self, player_id: str, hand_index: int):
        player = self.match_model.players.get(player_id)
        if not player or hand_index >= len(player.hand): return

        card = player.hand[hand_index]
        permitido, motivo = RuleEngine.validar_conjuracao(self.match_model, player_id, card)
        
        if permitido:
            player.cast_creature(hand_index)
            print(f"[AÇÃO] {player.name} conjurou criatura: {card.name}")
        else:
            print(f"[BLOQUEADO] {motivo}")

    def cast_other(self, player_id: str, hand_index: int):
        player = self.match_model.players.get(player_id)
        if not player or hand_index >= len(player.hand): return

        card = player.hand[hand_index]
        permitido, motivo = RuleEngine.validar_conjuracao(self.match_model, player_id, card)
        
        if permitido:
            player.cast_other(hand_index)
            print(f"[AÇÃO] {player.name} usou: {card.name}")
        else:
            print(f"[BLOQUEADO] {motivo}")

    # =========================================================
    # CONTROLE DE TURNOS E IA BÁSICA
    # =========================================================
    def next_phase(self):
        """Avança a fase e notifica o log."""
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
        """Prepara o campo do bot para o início do jogo."""
        if len(bot.hand) >= 3:
            # Bot desce terreno na zona de mana e criatura no campo para teste visual
            bot.battlefield_lands.append(bot.hand.pop())
            bot.battlefield_creatures.append(bot.hand.pop())