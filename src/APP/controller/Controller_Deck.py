import json
import os
from mtg_commander_app.models.deck_model import DeckModel

class DeckController:
    def __init__(self, json_path="data/database.json"):
        self.json_path = json_path
        self.model = DeckModel() # Instancia o modelo
        self.reload_data()

    def reload_data(self):
        """Lê o JSON e preenche o DeckModel."""
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.model.name = data.get("deck_name", "Sem Nome")
                    self.model.commander = data.get("commander")
                    self.model.cards = data.get("cards", [])
            except:
                self.model = DeckModel()
        else:
            self.model = DeckModel()

    def has_deck(self):
        """Verifica se o modelo tem os dados mínimos para jogar."""
        return self.model.commander is not None and len(self.model.cards) > 0

    def get_all_cards(self):
        return self.model.cards