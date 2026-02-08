import datetime  # Importado para gerenciar timestamps sem depender do pygame

class DeckModel:
    """Modelo de dados para representar um deck de Commander."""
    def __init__(self, name="", commander=""):
        self.name = name
        self.commander = commander
        self.deck_id = "" # Identificador único para pastas (ex: meu_deck_mono_blue)
        
        # Estrutura para armazenar cartas separadas por tipos
        self.deck_data = {
            "Criaturas": [],
            "Terrenos": [],
            "Feiticos": [],
            "Instantes": [],
            "Artefatos": [],
            "Encantamentos": [],
            "Outros": []
        }
        
        # Lista simples para referência rápida no seletor da View
        self.cards = []

    def adicionar_carta(self, carta):
        """Organiza a carta na categoria correta baseada no seu type_line."""
        # Adiciona à lista geral
        self.cards.append(carta)
        
        # Lógica de categorização baseada no tipo da carta vindo da API
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
        """Retorna a estrutura completa para o ficheiro cards_info.json."""
        return {
            "deck_name": self.name,
            "commander": self.commander,
            # Correção do NameError: Usando datetime em vez de pygame
            "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "categories": self.deck_data 
        }

    def get_config_data(self):
        """Retorna os metadados básicos para o ficheiro de configuração do deck."""
        return {
            "name": self.name,
            "commander": self.commander,
            "deck_id": self.deck_id,
            "total_cards": sum(len(v) for v in self.deck_data.values())
        }