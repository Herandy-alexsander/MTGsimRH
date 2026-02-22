from typing import Dict, List
from APP.domain.models.player_model import PlayerModel
from APP.domain.models.card_model import CardModel
from APP.domain.models.game_state import GameState # 🔥 IMPORTANDO O RELÓGIO DO JOGO

class MatchModel:
    def __init__(self, player1: PlayerModel, player2: PlayerModel):
        """
        Guarda o estado físico da mesa (Jogadores e Pilha).
        Delega o controle de tempo/fases para o GameState.
        """
        # Dicionário de Players para acesso rápido via ID (P1, P2)
        self.players: Dict[str, PlayerModel] = {
            player1.player_id: player1,
            player2.player_id: player2
        }
        
        # 🔥 O NOVO MOTOR DE REGRAS DE FASES!
        self.state = GameState()
        
        # A PILHA (Stack): Motor para mágicas e habilidades
        self.stack: List[CardModel] = []

    # =========================================================
    # ATALHOS PARA O GAME STATE (Para a UI e Controller continuarem funcionando)
    # =========================================================
    @property
    def phase(self) -> str:
        """Retorna o nome da fase atual do GameState."""
        return self.state.current_phase

    @property
    def active_player_id(self) -> str:
        return self.state.active_player_id
        
    @active_player_id.setter
    def active_player_id(self, p_id: str):
        self.state.active_player_id = p_id
        self.state.priority_player_id = p_id

    @property
    def current_phase_index(self) -> int:
        return self.state.current_phase_index
        
    @current_phase_index.setter
    def current_phase_index(self, index: int):
        self.state.current_phase_index = index

    # =========================================================
    # LÓGICA DA MESA FÍSICA
    # =========================================================
    def get_active_player(self) -> PlayerModel:
        """Retorna o objeto do jogador que detém o turno, ou None se o jogo não começou."""
        if not self.state.active_player_id:
            return None
        return self.players.get(self.state.active_player_id)
    
    def get_opponent(self) -> PlayerModel:
        """Retorna o objeto do jogador que está na defensiva."""
        for p_id, p in self.players.items():
            if p_id != self.state.active_player_id:
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
        """Pede para o GameState avançar. Se o turno virar, faz a limpeza da mesa."""
        # O GameState retorna True APENAS quando vira o turno (sai do Final pro Inicial)
        turno_mudou = self.state.advance_phase()
        
        if turno_mudou:
            self._pass_turn()

    def _pass_turn(self):
        """Lógica executada apenas na virada de turno."""
        
        # 1. Limpa a mana pool dos jogadores e reseta contadores vitais
        for p in self.players.values():
            p.reset_mana_pool()
            p.lands_played_this_turn = 0 # 🔥 REGRA DO MAGIC: Zera o limite de terrenos!
        
        # 2. Inverte o jogador ativo
        opponent = self.get_opponent()
        if opponent:
            self.state.active_player_id = opponent.player_id
            self.state.priority_player_id = opponent.player_id
        
        # 3. Limpeza de segurança da pilha
        self.stack.clear()
        
        novo_jogador = self.get_active_player()
        print(f"\n[MESA] --- TURNO {self.state.turn_number} --- Ativo: {novo_jogador.name}")