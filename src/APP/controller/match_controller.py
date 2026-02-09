import random
from APP.models.match_model import PlayerModel
class MatchController:
    def __init__(self, model):
        self.model = model

    def setup_game(self, players_data):
        """Inicializa os jogadores no model."""
        for i, data in enumerate(players_data, 1):
            deck = self._expand_deck(data['cards'])
            random.shuffle(deck)
            player = PlayerModel(f"Jogador {i}", deck)
            # Compra inicial
            player.hand = [player.library.pop() for _ in range(7)]
            self.model.players[i] = player

    def _expand_deck(self, cards_json):
        deck = []
        for c in cards_json:
            for _ in range(c.get('quantity', 1)):
                deck.append(c.copy())
        return deck

    def play_land(self, player_id, card_index):
        """Move um terreno da mão para a zona de terrenos."""
        player = self.model.players[player_id]
        card = player.hand.pop(card_index)
        player.battlefield_lands.append(card)

    def draw_card(self, player_id):
        player = self.model.players[player_id]
        if player.library:
            player.hand.append(player.library.pop())