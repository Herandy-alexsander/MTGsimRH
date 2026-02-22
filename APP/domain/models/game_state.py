# APP/domain/models/game_state.py

class GameState:
    def __init__(self):
        """
        Gerencia o tempo, as fases e de quem é a vez de jogar.
        Isolado do MatchModel para manter o código limpo (Clean Architecture).
        """
        self.turn_number: int = 1
        self.active_player_id: str = None # Quem é o dono do turno
        self.priority_player_id: str = None # Quem pode jogar mágicas agora
        
        # FASES OFICIAIS DO MTG EM PORTUGUÊS (Sincronizadas com sua UI)
        self.phases = ["INICIAL", "PRINCIPAL 1", "COMBATE", "PRINCIPAL 2", "FINAL"]
        self.current_phase_index: int = 0
        
        self.is_game_over: bool = False
        self.winner_id: str = None

    @property
    def current_phase(self) -> str:
        """Retorna o nome da fase atual em texto."""
        return self.phases[self.current_phase_index]

    def iniciar_jogo(self, starting_player_id: str):
        """Prepara o relógio para o turno 1."""
        self.active_player_id = starting_player_id
        self.priority_player_id = starting_player_id
        # Força o início na fase Principal 1 do primeiro turno
        self.current_phase_index = self.phases.index("PRINCIPAL 1")
        self.turn_number = 1

    def advance_phase(self) -> bool:
        """
        Avança a fase. Retorna True se o turno mudou, False se continuou no mesmo turno.
        """
        if self.is_game_over:
            return False

        self.current_phase_index += 1
        
        # Se passou da última fase ("FINAL"), vira o turno
        if self.current_phase_index >= len(self.phases):
            self.current_phase_index = 0
            self.turn_number += 1
            return True # O turno mudou!
            
        return False