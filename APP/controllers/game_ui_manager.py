import pygame
from APP.UI.components.card_ui import CardUI

class GameUIManager:
    def __init__(self, asset_manager):
        """
        O Diretor de Cena: Gerencia a criação e o cache dos componentes visuais.
        Evita sobrecarga de memória e garante que as imagens apareçam.
        """
        self.asset_manager = asset_manager
        
        # Cache de componentes: {id(model): instancia_CardUI}
        # Isso garante que cada carta física tenha apenas UM objeto visual na RAM
        self.ui_cards_cache = {}

    def sincronizar_zona_visual(self, zona_ui, lista_modelos_cards):
        """
        Pega as cartas do Modelo (dados) e as injeta na Zona da Interface.
        :param zona_ui: Instância de ZoneUI (Campo, Mana, etc)
        :param lista_modelos_cards: Lista de objetos CardModel vindo do PlayerModel
        """
        zona_ui.clear_cards()
        
        for model in lista_modelos_cards:
            # Usamos o ID único do objeto na memória como chave do cache
            card_id = id(model)
            
            if card_id not in self.ui_cards_cache:
                # Se a carta é nova, criamos o componente visual dela
                # O tamanho (w, h) aqui é o padrão, a ZoneUI pode ajustar depois
                novo_card_ui = CardUI(model, self.asset_manager, 0, 0)
                self.ui_cards_cache[card_id] = novo_card_ui
            
            # Adiciona o componente visual na zona correspondente
            zona_ui.add_card_ui(self.ui_cards_cache[card_id])

    def preparar_mesa_inicial(self, match_model, zonas_por_jogador):
        """
        Faz a primeira sincronização de todas as zonas da mesa.
        :param zonas_por_jogador: O dicionário de zonas que criamos na MatchView
        """
        for p_id, zonas in zonas_por_jogador.items():
            player = match_model.players[p_id]
            
            # Sincroniza cada parte do campo
            self.sincronizar_zona_visual(zonas["CAMPO"], player.battlefield_creatures)
            self.sincronizar_zona_visual(zonas["MANA"], player.battlefield_lands)
            self.sincronizar_zona_visual(zonas["CEMITERIO"], player.graveyard)
            self.sincronizar_zona_visual(zonas["EXILIO"], player.exile)
            
            # Comandante (Tratado como uma lista de 1 carta para reaproveitar a lógica)
            if player.deck.commander_card:
                self.sincronizar_zona_visual(zonas["COMANDANTE"], [player.deck.commander_card])

    def limpar_cache_obsoleto(self, match_model):
        """
        (Opcional) Remove do cache cartas que não estão em nenhuma zona 
        para liberar memória em partidas muito longas.
        """
        # Futura implementação de limpeza de RAM
        pass