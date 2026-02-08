class DeckController:
    def __init__(self, json_path="data/database.json"):
        with open(json_path, 'r', encoding='utf-8') as f:
            self.db = json.load(f)
        
        self.commander = self.db["commander"]
        self.cards = self.db["cards"]

    def get_commander_data(self):
        for card in self.cards:
            if card["name"] == self.commander:
                return card
        return None

    def get_all_cards(self):
        return self.cards