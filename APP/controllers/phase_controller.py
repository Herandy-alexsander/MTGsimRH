from APP.core.game_rules import Phase

class PhaseController:
    def __init__(self, model):
        self.model = model
        # Ordem cronológica das fases do Magic
        self.phase_order = [
            Phase.UNTAP, Phase.UPKEEP, Phase.DRAW,
            Phase.MAIN_1,
            Phase.BEGIN_COMBAT, Phase.DECLARE_ATTACKERS, Phase.DECLARE_BLOCKERS, Phase.DAMAGE, Phase.END_COMBAT,
            Phase.MAIN_2,
            Phase.END_STEP, Phase.CLEANUP
        ]

    def next_phase(self):
        """Avança para a próxima fase e executa gatilhos automáticos."""
        current_index = self.phase_order.index(self.model.current_phase)
        
        # Se for a última fase (CLEANUP), volta para UNTAP e muda o turno
        if self.model.current_phase == Phase.CLEANUP:
            self._reset_turn_state()
            self.model.current_phase = Phase.UNTAP
            self._pass_turn()
        else:
            self.model.current_phase = self.phase_order[current_index + 1]
        
        self._handle_phase_automated_actions()
        print(f"[FASE] Mudou para: {self.model.current_phase.name}")

    def _handle_phase_automated_actions(self):
        """Lógica automática que acontece ao entrar em certas fases."""
        phase = self.model.current_phase
        player = self.model.get_current_player()

        # 1. Limpeza de Mana (Acontece ao mudar de QUALQUER fase)
        player.mana_pool = {"W": 0, "U": 0, "B": 0, "R": 0, "G": 0, "C": 0}

        # 2. Ações específicas de fase
        if phase == Phase.UNTAP:
            self._execute_untap(player)
        
        elif phase == Phase.DRAW:
            # 🔥 CORREÇÃO: Chama diretamente o método que funciona no seu PlayerModel
            # Implementamos a regra de pular a compra no primeiro turno se for 1v1
            turno_atual = getattr(self.model, 'turn_count', 1)
            quem_comecou = getattr(self.model, 'starting_player_id', None)

            if turno_atual == 1 and player.player_id == quem_comecou:
                print(f"[REGRAS] {player.name} pula a compra por ser o primeiro a jogar.")
            else:
                player.draw_cards(1)
                print(f"[SISTEMA] {player.name} comprou a carta do turno automaticamente.")

    def _reset_turn_state(self):
        """Limpa restrições por turno (ex: terrenos jogados)."""
        player = self.model.get_current_player()
        player.lands_played_this_turn = 0

    def _execute_untap(self, player):
        """Desvira todas as cartas nas listas de campo do jogador."""
        # Como o seu PlayerModel separa por tipos, iteramos em todas as zonas de campo
        zonas_de_campo = [
            player.battlefield_lands, 
            player.battlefield_creatures, 
            player.battlefield_other
        ]
        
        for zona in zonas_de_campo:
            for card in zona:
                # CardModel usa o atributo 'tapped' (booleano)
                card.tapped = False

    def _pass_turn(self):
        """Alterna o ID do jogador ativo no modelo e incrementa o turno global."""
        # Se o seu MatchModel tiver turn_count, nós o aumentamos aqui
        if hasattr(self.model, 'turn_count'):
            self.model.turn_count += 1
            print(f"\n--- INÍCIO DO TURNO {self.model.turn_count} ---")

        # Lógica de alternância (P1 -> P2 ou numérico 1 -> 2)
        if isinstance(self.model.active_player_id, int):
            self.model.active_player_id = (self.model.active_player_id % self.model.total_players) + 1
        else:
            # Caso use strings "P1" e "P2"
            self.model.active_player_id = "P2" if self.model.active_player_id == "P1" else "P1"
