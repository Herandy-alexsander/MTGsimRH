import datetime

class DeckModel:
    """Modelo de dados para representar um deck de Commander com atributos técnicos."""
    def __init__(self, name="", commander=""):
        self.name = name
        self.commander = commander
        self.deck_id = "" # Identificador sanitizado (ex: teysa_karlov)
        self.limpar_deck()

    def limpar_deck(self):
        """Reinicia o estado do deck para um novo carregamento ou rastreio."""
        self.cards = [] # Lista plana para embaralhamento e compra
        self.deck_data = {
            "Criaturas": [],
            "Terrenos": [],
            "Feiticos": [],
            "Instantes": [],
            "Artefatos": [],
            "Encantamentos": [],
            "Outros": []
        }

    def adicionar_carta(self, carta):
        """
        Organiza a carta na categoria correta e preserva os dados técnicos
        como Power, Toughness e CMC.
        """
        # Adiciona à lista geral para o deck (baralho)
        # Se a quantidade for > 1 (ex: terrenos), adiciona múltiplas vezes
        qtd = carta.get('quantity', 1)
        for _ in range(qtd):
            self.cards.append(carta)
        
        # Lógica de categorização baseada no type_line
        tipo = carta.get('type_line', '').lower()
        
        if 'creature' in tipo:
            self.deck_data["Criaturas"].append(carta)
        elif 'land' in tipo:
            self.deck_data["Terrenos"].append(carta)
        elif 'sorcery' in tipo:
            self.deck_data["Feiticos"].append(carta)
        elif 'instant' in tipo:
            self.deck_data["Instantes"].append(carta)
        elif 'artifact' in tipo:
            self.deck_data["Artefatos"].append(carta)
        elif 'enchantment' in tipo:
            self.deck_data["Encantamentos"].append(carta)
        else:
            self.deck_data["Outros"].append(carta)

    def get_full_json(self):
        """Retorna a estrutura completa compatível com cards_info.json."""
        return {
            "deck_name": self.name,
            "commander": self.commander,
            "deck_id": self.deck_id,
            "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_cards": len(self.cards),
            "categories": self.deck_data 
        }

    def get_config_data(self):
        """Retorna metadados básicos para o indexador em data/decks/."""
        return {
            "name": self.name,
            "commander": self.commander,
            "deck_id": self.deck_id,
            "total_cards": len(self.cards)
        }