class PlayerModel:
    """Representa os dados brutos de um único jogador."""
    def __init__(self, name, deck_list):
        self.name = name
        self.hp = 40
        self.library = deck_list  # Lista de objetos de cartas
        self.hand = []
        self.battlefield_creatures = []
        self.battlefield_lands = []
        self.graveyard = []
        self.exile = []
        self.commander_zone = []

class MatchModel:
    """Guarda o estado global da partida."""
    def __init__(self):
        self.players = {} # Dicionário de PlayerModel
        self.current_turn_player = 1
        self.phase = "UPKEEP" # UNTAP, UPKEEP, DRAW, MAIN1, COMBAT...
        self.stack = [] # Pilha de magias