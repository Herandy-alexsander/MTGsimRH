import json
import os
from APP.models.deck_model import DeckModel

class DeckController:
    def __init__(self, model, storage_manager):
        """
        Controlador que gerencia o carregamento técnico e visual dos decks.
        """
        self.storage = storage_manager
        self.model = model
        self.decks_disponiveis = []
        self.reload_data()

    def reload_data(self):
        """Atualiza a lista de decks cadastrados no profiler global."""
        perfil = self.storage.carregar_perfil()
        self.decks_disponiveis = perfil.get("decks_info", {}).get("decks", [])

    def has_deck(self):
        """Verifica se existem decks para liberar o botão no menu."""
        self.reload_data()
        return len(self.decks_disponiveis) > 0

    def get_current_deck_id(self):
        """Retorna o ID do deck atualmente carregado no modelo."""
        return self.model.deck_id

    def carregar_deck_para_jogo(self, deck_id):
        """
        Carrega o JSON do deck selecionado e preenche o Model com as cartas reais.
        """
        # 1. Busca metadados do deck no perfil pelo ID
        deck_info = next((d for d in self.decks_disponiveis if str(d['id']) == str(deck_id)), None)
        
        if not deck_info:
            print(f"[ERRO] Deck ID {deck_id} não encontrado no perfil.")
            return False
            
        # 2. Monta o caminho do arquivo JSON (usando a mesma lógica de nome do storage)
        nome_arquivo = deck_info['name'].strip().replace(" ", "_").lower() + ".json"
        caminho_arquivo = os.path.join(self.storage.decks_path, nome_arquivo)
        
        if not os.path.exists(caminho_arquivo):
            print(f"[ERRO] Arquivo físico não encontrado: {caminho_arquivo}")
            return False
            
        # 3. Lê o JSON e extrai as cartas
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                dados_deck = json.load(f)
            
            cartas_para_jogo = []
            
            # Percorre todas as categorias (Criaturas, Terrenos, etc) e unifica numa lista só
            categorias = dados_deck.get('categories', {})
            for nome_cat, lista_cartas in categorias.items():
                for card_ref in lista_cartas:
                    # Se o JSON salvar apenas referências, precisamos carregar o arquivo da carta
                    # Mas no seu storage atual, salvamos os dados completos dentro da referência ou path
                    # Vamos assumir que precisamos ler o arquivo da carta se 'data_path' existir
                    
                    dados_carta = card_ref
                    
                    # Se houver um caminho para o JSON individual da carta, carregamos ele
                    if "data_path" in card_ref and os.path.exists(card_ref["data_path"]):
                        try:
                            with open(card_ref["data_path"], 'r', encoding='utf-8') as f_card:
                                dados_carta = json.load(f_card)
                        except:
                            pass # Usa os dados parciais se falhar
                    
                    quantidade = card_ref.get('quantity', 1)
                    
                    # Adiciona N cópias da carta na lista final (Expandir deck)
                    for _ in range(quantidade):
                        cartas_para_jogo.append(dados_carta)
            
            # 4. Atualiza o Model (Isso é o que o MatchController vai ler depois)
            self.model.cards = cartas_para_jogo
            self.model.commander = dados_deck.get("commander", "")
            self.model.name = dados_deck.get("name", "")
            self.model.deck_id = deck_id
            
            print(f"[OK] Deck carregado: {self.model.name} ({len(self.model.cards)} cartas)")
            return True
            
        except Exception as e:
            print(f"[CRÍTICO] Falha ao processar deck: {str(e)}")
            return False

    def get_commander_card(self):
        """Busca os dados técnicos do Comandante na lista de cartas carregada."""
        if not self.model.commander or not self.model.cards:
            return None
            
        for carta in self.model.cards:
            if carta.get("name") == self.model.commander:
                return carta
        return None