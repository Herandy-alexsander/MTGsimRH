class PlayerModel:
    """Representa os dados brutos de um único jogador."""
    def __init__(self, name, deck_list):
        self.name = name
        self.life = 40  # Renomeado de 'hp' para 'life' para compatibilidade com o Controller
        self.library = deck_list  # Lista de objetos de cartas
        self.hand = []
        
        # Zonas de Jogo
        self.battlefield_creatures = []
        self.battlefield_lands = []
        self.graveyard = []
        self.exile = []
        self.commander_zone = [] # Pode guardar o objeto carta do comandante se necessário

class MatchModel:
    """Guarda o estado global da partida."""
    def __init__(self):
        self.players = {} # Dicionário de PlayerModel {id: PlayerModel}
        self.current_turn = 1
        self.current_turn_player = 1
        self.phase = "UNTAP" # UNTAP, UPKEEP, DRAW, MAIN1, COMBAT, MAIN2, END
        self.stack = [] # Pilha de magias
        
        # CORREÇÃO DO ERRO CRÍTICO:
        # Adicionado atributo para guardar o nome do Comandante visualmente
        self.commander = None