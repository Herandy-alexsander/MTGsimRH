from APP.domain.models.match_model import MatchModel
from APP.domain.models.card_model import CardModel

class RuleEngine:
    @staticmethod
    def validar_descida_terreno(match: MatchModel, player_id: str, card: CardModel):
        """
        Regra: 1 terreno por turno, apenas no seu turno e nas fases MAIN.
        """
        # 1. É o turno do jogador?
        if match.active_player_id != player_id:
            return False, "Não é o seu turno!"

        # 2. Está na fase correta? (Main 1 ou Main 2)
        if match.phase not in ["MAIN1", "MAIN2"]:
            return False, f"Você não pode baixar terrenos na fase de {match.phase}."

        # 3. Já baixou terreno este turno? 
        # (Precisamos que o PlayerModel tenha o atributo 'lands_played_this_turn')
        player = match.players[player_id]
        if hasattr(player, 'lands_played_this_turn') and player.lands_played_this_turn >= 1:
            return False, "Você já baixou um terreno este turno."

        # 4. É realmente um terreno?
        if not card.is_land:
            return False, f"{card.name} não é um terreno!"

        return True, "Jogada permitida."

    @staticmethod
    def validar_conjuracao(match: MatchModel, player_id: str, card: CardModel):
        """
        Regra: Verifica custo de mana e tempo (sorcery speed).
        """
        player = match.players[player_id]

        # 1. Checagem de Turno e Fase (Mágicas normais só na Main Phase)
        if match.active_player_id != player_id:
            # Futuro: Aqui entra a exceção para cartas com 'Flash' ou 'Instant'
            return False, "Você só pode conjurar no seu turno."

        if match.phase not in ["MAIN1", "MAIN2"]:
            return False, "Conjuração permitida apenas nas fases principais."

        # 2. Checagem de Custo de Mana (Simplificada por enquanto)
        # Futuro: Criar lógica para checar cores (W, U, B, R, G)
        if player.mana_pool["C"] < card.cmc:
            return False, f"Mana insuficiente! Você tem {player.mana_pool['C']} e precisa de {card.cmc}."

        return True, "Mana disponível!"

    @staticmethod
    def pode_atacar(match: MatchModel, player_id: str, creature: CardModel):
        """
        Regra: Criaturas não podem atacar no turno em que entram (Enjoô de Invocação).
        """
        if match.phase != "COMBAT":
            return False, "Você só pode declarar ataque na fase de COMBATE."
            
        if creature.is_tapped:
            return False, "A criatura já está virada."

        # Futuro: Checar 'Summoning Sickness' e 'Haste'
        return True, "Ataque disponível."