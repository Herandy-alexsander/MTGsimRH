from APP.domain.models.card_model import CardModel
from APP.domain.models.deck_model import DeckModel

class DeckBuilderService:
    """
    Serviço de Domínio responsável por ler o dicionário bruto (JSON)
    e fabricar as instâncias vivas (Objetos) das cartas e do baralho.
    """

    @staticmethod
    def build_from_json(deck_data: dict) -> DeckModel:
        """
        Recebe os dados brutos do DeckRepository, cria os objetos Pydantic
        e devolve um DeckModel pronto para o combate.
        """
        deck = DeckModel()
        deck.name = deck_data.get("name", "Sem Nome")
        commander_name = deck_data.get("commander", "")
        
        cartas_brutas = deck_data.get("cards", [])

        for raw_card in cartas_brutas:
            qtd = raw_card.get("quantity", 1)
            
            # Mapeamento seguro para o Pydantic CardModel
            # Isso evita que o jogo quebre se o JSON vier com chaves a mais ou a menos
            card_args = {
                "name": raw_card.get("name", "Desconhecido"),
                "mana_cost": raw_card.get("mana_cost", ""),
                "cmc": float(raw_card.get("cmc", 0.0)),
                "type_line": raw_card.get("type_line", ""),
                "oracle_text": raw_card.get("oracle_text", ""),
                "colors": raw_card.get("colors", []),
                "color_identity": raw_card.get("color_identity", []),
                "power": raw_card.get("power"),
                "toughness": raw_card.get("toughness"),
                "loyalty": raw_card.get("loyalty"),
                # O Downloader salvou o caminho como 'ref_image', o Model espera 'local_image_path'
                "local_image_path": raw_card.get("ref_image") 
            }

            # Verifica se esta carta é o Comandante do deck
            is_commander = (card_args["name"] == commander_name)

            if is_commander:
                # Instancia o objeto vivo da carta e coloca na zona de comando
                deck.commander_card = CardModel(**card_args)
                qtd -= 1 # Retira 1 cópia que iria para o grimório
                
            # Instancia as cópias físicas da carta para o grimório
            for _ in range(qtd):
                nova_carta = CardModel(**card_args)
                deck.library.append(nova_carta)

        # Atualiza a contagem oficial e embaralha o grimório
        deck.total_cards_initial = len(deck.library) + (1 if deck.commander_card else 0)
        deck.embaralhar()

        return deck