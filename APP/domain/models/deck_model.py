import random
from typing import List, Optional
from APP.domain.models.card_model import CardModel

class DeckModel:
    def __init__(self):
        """
        Representa o Grimório (Library) ativo durante a partida.
        Gerencia apenas instâncias vivas de CardModel.
        """
        self.deck_id: Optional[int] = None
        self.name: str = ""
        self.commander_card: Optional[CardModel] = None
        
        # Zonas controladas fisicamente pelo deck
        self.library: List[CardModel] = []
        self.graveyard: List[CardModel] = []
        self.exile: List[CardModel] = []
        
        self.total_cards_initial: int = 0

    def embaralhar(self):
        """Randomiza a ordem das cartas no grimório."""
        if self.library:
            random.shuffle(self.library)
            print(f"[MESA] O grimório '{self.name}' foi embaralhado.")

    def comprar_carta(self) -> Optional[CardModel]:
        """
        Puxa a carta do topo (fim da lista). 
        Retorna None se o deck estiver vazio (o PlayerModel tratará a derrota).
        """
        if self.library:
            return self.library.pop()
        
        print(f"[AVISO] Tentativa de compra em grimório vazio: {self.name}")
        return None

    def get_tamanho_grimorio(self) -> int:
        """Retorna a contagem atual de cartas no deck."""
        return len(self.library)

    def reset_partida(self):
        """
        Recolhe todas as cartas do cemitério e exílio de volta para o deck.
        Mantém o nome e o ID do deck para uma revanche imediata.
        """
        self.library.extend(self.graveyard)
        self.library.extend(self.exile)
        self.graveyard.clear()
        self.exile.clear()
        
        # Reseta o estado de 'tapped' de todas as cartas ao voltarem para o deck
        for card in self.library:
            card.untap()
            card.remove_all_counters()
            
        self.embaralhar()
        print(f"[SISTEMA] Deck '{self.name}' reiniciado para nova partida.")

    def limpar_total(self):
        """Limpa absolutamente tudo (usado ao trocar de deck na galeria)."""
        self.library.clear()
        self.graveyard.clear()
        self.exile.clear()
        self.commander_card = None
        self.name = ""
        self.deck_id = None
        self.total_cards_initial = 0