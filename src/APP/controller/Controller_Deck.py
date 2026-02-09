import json
import os
from APP.models.deck_model import DeckModel

class DeckController:
    def __init__(self, profiler_path="data/profiler.json"):
        """Controlador que gerencia o carregamento técnico e visual dos decks."""
        self.profiler_path = profiler_path
        self.model = DeckModel()
        self.decks_disponiveis = []
        self.reload_data()

    def reload_data(self):
        """Atualiza a lista de decks cadastrados no profiler global."""
        if os.path.exists(self.profiler_path):
            try:
                with open(self.profiler_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.decks_disponiveis = data.get("decks_info", {}).get("decks", [])
            except Exception as e:
                print(f"[ERRO] Falha ao ler profiler: {e}")
                self.decks_disponiveis = []
        else:
            self.decks_disponiveis = []

    def selecionar_deck(self, deck_id_nome):
        """
        Carrega o deck seguindo as referências para arquivos locais em data/cards/ 
        e assets/cards/.
        """
        path_deck = os.path.join("data", "decks", f"{deck_id_nome}.json")

        if not os.path.exists(path_deck):
            print(f"[ERRO] Ficheiro do deck '{deck_id_nome}' nao encontrado.")
            return False

        try:
            with open(path_deck, 'r', encoding='utf-8') as f:
                deck_config = json.load(f)

            # Sincroniza metadados básicos no modelo
            self.model.name = deck_config.get("name")
            self.model.commander = deck_config.get("commander")
            self.model.deck_id = deck_config.get("deck_id")
            
            # Limpa o estado anterior para evitar mistura de cartas
            self.model.limpar_deck()
            
            # Carrega cada carta seguindo as referências de categorias
            categorias = deck_config.get("categories", {})
            for nome_cat, lista_cartas in categorias.items():
                for ref in lista_cartas:
                    caminho_card_json = ref.get("data_path")
                    
                    if caminho_card_json and os.path.exists(caminho_card_json):
                        with open(caminho_card_json, 'r', encoding='utf-8') as f_card:
                            # Carrega dados detalhados (Power, Toughness, Local Image Path)
                            dados_completos = json.load(f_card)
                            
                            # Aplica a quantidade registrada para este deck específico
                            dados_completos["quantity"] = ref.get("quantity", 1)
                            
                            # Adiciona ao modelo que organiza por categoria internamente
                            self.model.adicionar_carta(dados_completos)
            
            print(f"[OK] Deck '{self.model.name}' carregado com assets locais.")
            return True

        except Exception as e:
            print(f"[ERRO] Falha ao carregar deck por referências: {e}")
            return False

    def has_deck(self):
        """Verifica se existem decks para serem listados no menu."""
        return len(self.decks_disponiveis) > 0

    def get_commander_card(self):
        """Busca os dados técnicos do Comandante (Poder/Resistência/Imagem)."""
        if not self.model.commander:
            return None
            
        # O comandante deve estar na categoria de Criaturas
        for carta in self.model.deck_data.get("Criaturas", []):
            if carta["name"] == self.model.commander:
                return carta
        return None