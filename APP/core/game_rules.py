from enum import Enum, auto

class Phase(Enum):
    UNTAP = auto()      # Desvirar permanentes
    UPKEEP = auto()     # Manutenção
    DRAW = auto()       # Compra do turno
    MAIN_1 = auto()     # Fase Principal 1 (Feitiços/Terrenos)
    BEGIN_COMBAT = auto()
    DECLARE_ATTACKERS = auto()
    DECLARE_BLOCKERS = auto()
    DAMAGE = auto()
    END_COMBAT = auto()
    MAIN_2 = auto()     # Fase Principal 2 (Pós-combate)
    END_STEP = auto()
    CLEANUP = auto()    # Limpeza (descarte, fim de efeitos)

class CardType(Enum):
    LAND = "Terrenos"
    CREATURE = "Criaturas"
    ARTIFACT = "Artefatos"
    ENCHANTMENT = "Encantamentos"
    SORCERY = "Feiticos"
    INSTANT = "Instantes"

class GameRules:
    """Configurações globais de regras do Commander"""
    MAX_LANDS_PER_TURN = 1
    STARTING_LIFE = 40
    MAX_HAND_SIZE = 7
    
    @staticmethod
    def can_play_sorcery_speed(phase: Phase) -> bool:
        """Verifica se a fase atual permite feitiços e criaturas (Velocidade Sorcery)"""
        return phase in [Phase.MAIN_1, Phase.MAIN_2]

    @staticmethod
    def can_play_land(phase: Phase, lands_played: int) -> bool:
        """Valida a regra de jogar terrenos"""
        return (phase in [Phase.MAIN_1, Phase.MAIN_2] and 
                lands_played < GameRules.MAX_LANDS_PER_TURN)
