from typing import List, Dict, Optional
from APP.domain.models.deck_model import DeckModel
from APP.domain.models.card_model import CardModel

class PlayerModel:
    def __init__(self, player_id: str, name: str, deck: DeckModel, starting_life: int = 40):
        """
        Representa um jogador sentado à mesa.
        Gerencia vida, mana e a movimentação de cartas entre as zonas de jogo.
        """
        self.player_id = player_id
        self.name = name
        self.deck = deck
        
        # STATUS DO JOGADOR
        self.life: int = starting_life
        self.poison_counters: int = 0
        self.commander_damage: Dict[str, int] = {}
        self.mana_pool: Dict[str, int] = {"W": 0, "U": 0, "B": 0, "R": 0, "G": 0, "C": 0}
        self.is_alive: bool = True
        
        # Controle de Regras de Turno
        self.lands_played_this_turn: int = 0

        # ZONAS DE JOGO (Separadas para o LayoutEngine e ZoneUI)
        self.hand: List[CardModel] = []
        self.battlefield_creatures: List[CardModel] = []
        self.battlefield_lands: List[CardModel] = []
        self.battlefield_other: List[CardModel] = []
        
        self.graveyard: List[CardModel] = []
        self.exile: List[CardModel] = []
        self.commander_zone: List[CardModel] = []

    # =========================================================
    # AÇÕES COM CARTAS (Movimentação entre Zonas)
    # =========================================================
    
    def return_hand_to_deck(self):
        """
        DEVOLVE A MÃO PARA O GRIMÓRIO E EMBARALHA.
        Essencial para o sistema de Mulligan.
        """
        self.deck.library.extend(self.hand)
        self.hand.clear()
        self.deck.embaralhar()
        print(f"[MODEL] {self.name} devolveu a mão e embaralhou o grimório.")

    def draw_cards(self, amount: int = 1):
        """Puxa cartas do DeckModel. Se o deck acabar, o jogador perde."""
        drawn_cards = []
        for _ in range(amount):
            card = self.deck.comprar_carta()
            if card:
                self.hand.append(card)
                drawn_cards.append(card)
            else:
                self.perder_jogo("Tentou comprar de um grimório vazio (Mill).")
                break
        return drawn_cards

    def play_land(self, card_index: int):
        """Move um terreno da mão para o battlefield_lands."""
        if 0 <= card_index < len(self.hand):
            card = self.hand[card_index]
            if card.is_land:
                card = self.hand.pop(card_index)
                card.untap() # Garante que entra desvirada
                self.battlefield_lands.append(card)
                return card
        return None

    def cast_creature(self, card_index: int):
        """Move uma criatura da mão para o battlefield_creatures."""
        if 0 <= card_index < len(self.hand):
            card = self.hand[card_index]
            if card.is_creature:
                card = self.hand.pop(card_index)
                card.untap()
                self.battlefield_creatures.append(card)
                return card
        return None

    def cast_other(self, card_index: int):
        """Move artefatos/encantamentos para a zona battlefield_other."""
        if 0 <= card_index < len(self.hand):
            card = self.hand.pop(card_index)
            card.untap()
            self.battlefield_other.append(card)
            return card
        return None

    def discard_card(self, card_index: int):
        """Remove da mão e envia para o cemitério, limpando marcadores."""
        if 0 <= card_index < len(self.hand):
            card = self.hand.pop(card_index)
            card.remove_all_counters() # Regra: cartas no GY não mantêm buffs
            self.graveyard.append(card)
            return card
        return None

    # =========================================================
    # GESTÃO DE VIDA E REGRAS DE VITÓRIA
    # =========================================================
    def take_damage(self, amount: int):
        self.life -= amount
        if self.life <= 0:
            self.perder_jogo("Pontos de vida chegaram a zero.")

    def take_commander_damage(self, opponent_id: str, amount: int):
        """Aplica dano e checa a regra dos 21 pontos de Comandante."""
        self.take_damage(amount)
        current_dmg = self.commander_damage.get(opponent_id, 0) + amount
        self.commander_damage[opponent_id] = current_dmg
        if current_dmg >= 21:
            self.perder_jogo(f"Recebeu 21 pontos de dano do Comandante de {opponent_id}.")

    def add_poison(self, amount: int = 1):
        self.poison_counters += amount
        if self.poison_counters >= 10:
            self.perder_jogo("Acumulou 10 contadores de veneno.")

    def reset_mana_pool(self):
        for color in self.mana_pool:
            self.mana_pool[color] = 0

    def perder_jogo(self, motivo: str):
        if self.is_alive:
            self.is_alive = False
            print(f"[MESA] O jogador {self.name} foi ELIMINADO! Motivo: {motivo}")