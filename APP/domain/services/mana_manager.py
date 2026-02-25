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

        # 2. No Magic básico, terrenos geram 1 mana.
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
        [PASSO 2 - VERSÃO A4]
        Consome os recursos da mana_pool do jogador para pagar a carta.
        Prioriza pagar cores específicas e usa o saldo restante para o custo genérico.
        """
        custo = card.mana_cost_map  # Pega o dicionário ex: {'W': 1, 'Generic': 2}
        pool = player.mana_pool

        # 1. Pagar os custos coloridos específicos (W, U, B, R, G, C)
        for cor, qtd in custo.items():
            if cor == "Generic":
                continue
            
            # Subtrai da pool (a validação no RuleEngine já garantiu que existe saldo)
            if cor in pool:
                pool[cor] = max(0, pool[cor] - qtd)

        # 2. Pagar o custo Genérico (números como {1}, {2}, etc.)
        # Pode ser pago por qualquer cor restante na pool.
        custo_generico = custo.get("Generic", 0)
        
        if custo_generico > 0:
            # Lista de cores para tentar descontar (priorizando Incolor 'C' primeiro)
            ordem_desconto = ["C", "W", "U", "B", "R", "G"]
            
            for cor in ordem_desconto:
                if custo_generico <= 0:
                    break
                
                if pool.get(cor, 0) > 0:
                    saldo_na_pool = pool[cor]
                    # Vê quanto pode tirar dessa cor
                    gasto = min(saldo_na_pool, custo_generico)
                    
                    pool[cor] -= gasto
                    custo_generico -= gasto

        print(f"[MANA] Custo de {card.name} descontado da pool de {player.name}.")
