# APP/domain/services/mana_manager.py

class ManaManager:
    """
    Especialista em gerir a economia de mana.
    Isola a lógica de adição e consumo de recursos.
    """

    @staticmethod
    def gerar_mana(player, card):
        """
        Lê o 'produced_mana' da carta e injeta na pool do jogador.
        """
        # 1. Verifica se a carta tem o dado de produção que salvamos no JSON
        producao = getattr(card, 'produced_mana', [])
        
        if not producao:
            # Se for um terreno sem dado, assume Incolor (C) por segurança
            producao = ["C"]

        # 2. No Magic básico (e no nosso simulador agora), terrenos geram 1 mana.
        # Em terrenos duplos, pegamos a primeira cor (futuramente abriremos um menu)
        cor_gerada = producao[0]

        # 3. Alimenta a reserva do jogador
        if cor_gerada in player.mana_pool:
            player.mana_pool[cor_gerada] += 1
            return cor_gerada
        
        return None

    @staticmethod
    def descontar_custo(player, card):
        """
        (Para o próximo passo): Verifica se o jogador tem mana e subtrai.
        """
        # Aqui entrará a lógica de RuleEngine + ManaManager
        pass
