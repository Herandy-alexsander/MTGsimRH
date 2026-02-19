import json
from pathlib import Path
import math

class DeckController:
    def __init__(self, deck_model, deck_repo, profile_repo, scryfall, downloader):
        """
        Controlador da Galeria de Decks.
        Gerencia o carregamento, a paginação em grade (2x6) e a seleção para o jogo.
        """
        self.model = deck_model
        self.deck_repo = deck_repo
        self.profile_repo = profile_repo
        self.scryfall = scryfall
        self.downloader = downloader
        
        # --- Configuração da Grade e Paginação ---
        self.decks_disponiveis = [] 
        self.index_deck_atual = 0  # Usado para seleção individual se necessário
        self.pagina_atual = 0
        self.decks_por_pagina = 12  # Layout 2 linhas x 6 colunas
        
        # Carrega os dados iniciais
        self.reload_data()

    def reload_data(self):
        """
        Lê o 'profiler.json' e carrega os metadados dos decks salvos.
        Busca a imagem do comandante para servir de capa na galeria.
        """
        self.decks_disponiveis.clear()
        
        try:
            # Busca a lista de decks no perfil do usuário
            perfil = self.profile_repo.ler_perfil()
            lista_decks_perfil = perfil.get("decks_info", {}).get("decks", [])
        except Exception as e:
            print(f"[AVISO] Erro ao ler perfil na Galeria: {e}")
            lista_decks_perfil = []

        for ref_deck in lista_decks_perfil:
            nome_deck = ref_deck.get("name", "Sem Nome")
            nome_comandante = ref_deck.get("commander", "Desconhecido")
            caminho_capa = ""
            
            # Localiza o arquivo físico para extrair a arte da capa
            nome_arquivo_deck = nome_deck.replace(" ", "_").lower() + ".json"
            caminho_arquivo = Path("data/decks") / nome_arquivo_deck
            
            if caminho_arquivo.exists():
                try:
                    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                        dados_fisicos = json.load(f)
                        # Busca a referência da imagem do comandante
                        for carta in dados_fisicos.get("cards", []):
                            if carta.get("name") == nome_comandante:
                                caminho_capa = carta.get("ref_image", "")
                                break
                except Exception as e:
                    print(f"Erro ao carregar capa de {nome_deck}: {e}")

            self.decks_disponiveis.append({
                "name": nome_deck,
                "commander": nome_comandante,
                "cover_image_path": caminho_capa
            })
            
        # Reseta para a primeira página após recarregar
        self.pagina_atual = 0

    # --- Lógica de Paginação ---

    def obter_decks_pagina_atual(self):
        """Retorna a fatia da lista de decks correspondente à página atual."""
        inicio = self.pagina_atual * self.decks_por_pagina
        fim = inicio + self.decks_por_pagina
        return self.decks_disponiveis[inicio:fim]

    def total_paginas(self):
        """Calcula o número total de páginas baseado na quantidade de decks."""
        return max(1, math.ceil(len(self.decks_disponiveis) / self.decks_por_pagina))

    def mudar_pagina(self, direcao):
        """
        Navega entre as páginas.
        :param direcao: 1 para próxima, -1 para anterior.
        """
        nova_pag = self.pagina_atual + direcao
        if 0 <= nova_pag < self.total_paginas():
            self.pagina_atual = nova_pag

    # --- Lógica de Seleção ---

    def get_deck_atual(self):
        """Retorna o deck selecionado (usado para destaque ou início de jogo)."""
        if self.decks_disponiveis and 0 <= self.index_deck_atual < len(self.decks_disponiveis):
            return self.decks_disponiveis[self.index_deck_atual]
        return None

    def selecionar_deck_por_indice_geral(self, indice):
        """Define qual deck da lista completa está selecionado."""
        if 0 <= indice < len(self.decks_disponiveis):
            self.index_deck_atual = indice
            return True
        return False

    def selecionar_deck_para_jogo(self):
        """Finaliza a escolha e prepara os dados para a MatchController."""
        deck_selecionado = self.get_deck_atual()
        if deck_selecionado:
            print(f"[MESA] Carregando '{deck_selecionado['name']}' para a partida...")
            return True
        return False