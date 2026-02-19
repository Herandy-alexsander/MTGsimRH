from typing import Dict, List
# CORREÇÃO: Importando dos nomes de arquivos exatos que você criou (player_model e card_model)
from APP.domain.models.player_model import PlayerModel
from APP.domain.models.card_model import CardModel

class MatchModel:
    def __init__(self, player1: PlayerModel, player2: PlayerModel):
        """
        Guarda o estado global da partida e gerencia as regras e a Pilha.
        Centraliza quem é o jogador ativo e em qual fase o jogo está.
        """
        # Dicionário de Players: Excelente para acesso rápido via ID (P1, P2)
        self.players: Dict[str, PlayerModel] = {
            player1.player_id: player1,
            player2.player_id: player2
        }
        
        self.current_turn: int = 1
        self.active_player_id: str = player1.player_id
        
        # FASES OFICIAIS (Manutenção do estado de jogo)
        self.phases = ["UNTAP", "UPKEEP", "DRAW", "MAIN1", "COMBAT", "MAIN2", "END"]
        self.current_phase_index: int = 0
        
        # A PILHA (Stack): Motor para mágicas e habilidades
        self.stack: List[CardModel] = []
        
        self.match_is_over: bool = False

    @property
    def phase(self) -> str:
        """Retorna o nome da fase atual (Ex: 'COMBAT')."""
        return self.phases[self.current_phase_index]

    def get_active_player(self) -> PlayerModel:
        """Retorna o objeto do jogador que detém o turno."""
        return self.players[self.active_player_id]

    def get_opponent(self) -> PlayerModel:
        """Retorna o objeto do jogador que está na defensiva."""
        for p_id, p in self.players.items():
            if p_id != self.active_player_id:
                return p
        return None

    def put_on_stack(self, card: CardModel):
        """Adiciona uma carta ou habilidade à pilha de resolução."""
        self.stack.append(card)
        print(f"[PILHA] {card.name} aguardando resolução...")

    def resolve_top_of_stack(self) -> CardModel:
        """Resolve o topo da pilha (LIFO)."""
        if self.stack:
            resolved_card = self.stack.pop()
            print(f"[PILHA] Resolvido: {resolved_card.name}")
            return resolved_card
        return None

    def next_phase(self):
        """Avança o ponteiro de fases ou passa o turno se chegar ao fim."""
        if self.match_is_over: 
            return
        
        self.current_phase_index += 1
        
        # Se ultrapassou a fase 'END', reinicia e vira o turno
        if self.current_phase_index >= len(self.phases):
            self._pass_turn()

    def _pass_turn(self):
        """Lógica interna de transição de turno."""
        self.current_phase_index = 0
        self.current_turn += 1
        
        # Limpa a mana pool dos jogadores ao trocar de turno (Regra MTG)
        for p in self.players.values():
            p.reset_mana_pool()
        
        # Inverte o ID do jogador ativo
        opponent = self.get_opponent()
        if opponent:
            self.active_player_id = opponent.player_id
        
        # Limpeza de segurança da pilha
        self.stack.clear()
        
        novo_jogador = self.get_active_player()
        print(f"\n[MESA] --- TURNO {self.current_turn} --- Ativo: {novo_jogador.name}")