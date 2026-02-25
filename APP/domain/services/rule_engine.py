from typing import Tuple
from APP.domain.models.match_model import MatchModel
from APP.domain.models.card_model import CardModel

class RuleEngine:
    @staticmethod
    def validar_descida_terreno(match: MatchModel, player_id: str, card: CardModel) -> Tuple[bool, str]:
        """
        Regra: 1 terreno por turno, apenas no seu turno e nas fases PRINCIPAIS.
        """
        if match.active_player_id != player_id:
            return False, "Não é o seu turno!"

        if match.phase not in ["PRINCIPAL 1", "PRINCIPAL 2"]:
            return False, f"Você não pode baixar terrenos na fase {match.phase}."

        player = match.players[player_id]
        if hasattr(player, 'lands_played_this_turn') and player.lands_played_this_turn >= 1:
            return False, "BLOQUEADO: Você já baixou um terreno este turno."

        if not card.is_land:
            return False, f"{card.name} não é um terreno!"

        return True, "Jogada permitida."

    @staticmethod
    def validar_conjuracao(match: MatchModel, player_id: str, card: CardModel) -> Tuple[bool, str]:
        """
        [VERSÃO A4] Regra: Verifica se o jogador possui as CORES de mana exatas na pool.
        """
        player = match.players[player_id]

        # 1. Checagem de Turno e Fase
        if match.active_player_id != player_id:
            return False, "Você só pode conjurar no seu turno."

        if match.phase not in ["PRINCIPAL 1", "PRINCIPAL 2"]:
            return False, f"Fora da Fase Principal (Atual: {match.phase})."

        # 2. Checagem de Custo de Mana Específico (Passo 1 da A4)
        # Requisito da carta (ex: {"W": 1, "B": 1, "Generic": 1})
        custo_requisito = getattr(card, 'mana_cost_map', {})
        # Pool atual do jogador (ex: {"W": 1, "R": 5})
        pool_simulada = player.mana_pool.copy()

        # A) Validar Manas Coloridas primeiro
        for cor, qtd_necessaria in custo_requisito.items():
            if cor == "Generic":
                continue # Deixamos para o final
            
            qtd_na_pool = pool_simulada.get(cor, 0)
            if qtd_na_pool < qtd_necessaria:
                return False, f"Falta mana {cor}! Você tem {qtd_na_pool} e precisa de {qtd_necessaria}."
            
            # Removemos da pool simulada para saber o que sobra para o custo genérico
            pool_simulada[cor] -= qtd_necessaria

        # B) Validar Mana Genérica (Custo numérico)
        # Pode ser pago por qualquer cor que sobrou na pool
        custo_generico = custo_requisito.get("Generic", 0)
        total_restante = sum(pool_simulada.values())

        if total_restante < custo_generico:
            return False, f"Mana genérica insuficiente! Sobrou {total_restante} e precisa de {custo_generico}."

        return True, "Mana disponível!"

    @staticmethod
    def pode_atacar(match: MatchModel, player_id: str, creature: CardModel) -> Tuple[bool, str]:
        """
        Regra: Verifica fase de combate e estado da criatura.
        """
        if match.phase != "COMBATE":
            return False, "Ataque permitido apenas na fase de COMBATE."
            
        if creature.is_tapped:
            return False, "Esta criatura está virada."

        return True, "Ataque disponível."
