import requests
import time

class ScryfallClient:
    def __init__(self):
        self.base_url = "https://api.scryfall.com"

    def buscar_carta(self, nome_carta):
        """
        Tenta buscar a carta em Português. 
        Se falhar, busca em Inglês.
        Retorna um dicionário padronizado com url da imagem e dados técnicos.
        """
        # 1. Tenta buscar em PT-BR usando a busca avançada (lang:pt)
        # Usamos !"Nome" para garantir busca exata e evitar cartas parecidas
        query_pt = f'!"{nome_carta}" lang:pt'
        url_search = f"{self.base_url}/cards/search?q={query_pt}"
        
        dados_carta = None
        
        try:
            resp = requests.get(url_search, timeout=5)
            if resp.status_code == 200:
                resultado = resp.json()
                if resultado['total_cards'] > 0:
                    # Pega a primeira versão em PT encontrada
                    dados_carta = resultado['data'][0]
                    # print(f"Achou em PT: {nome_carta}") # Debug
        except Exception as e:
            print(f"Erro na busca PT: {e}")

        # 2. Fallback: Se não achou em PT, busca o padrão (Inglês)
        if not dados_carta:
            # print(f"Fallback para EN: {nome_carta}") # Debug
            url_named = f"{self.base_url}/cards/named?exact={nome_carta}"
            try:
                resp = requests.get(url_named, timeout=5)
                if resp.status_code == 200:
                    dados_carta = resp.json()
            except Exception as e:
                print(f"Erro na busca EN: {e}")

        # 3. Formata o retorno para o nosso sistema
        if dados_carta:
            return self._extrair_dados_uteis(dados_carta)
        
        return None

    def _extrair_dados_uteis(self, data):
        """Limpa o JSON do Scryfall e pega a URL correta da imagem."""
        
        # Tratamento para cartas dupla face (Transform cards)
        img_url = None
        if "image_uris" in data:
            img_url = data["image_uris"]["normal"]
        elif "card_faces" in data:
            # Pega a frente da carta
            img_url = data["card_faces"][0]["image_uris"]["normal"]

        return {
            "name": data.get("name"),
            "printed_name": data.get("printed_name", data.get("name")), # Nome em PT se tiver
            "type_line": data.get("type_line"), # Em PT se tiver
            "printed_type_line": data.get("printed_type_line", data.get("type_line")),
            "oracle_text": data.get("oracle_text", ""),
            "printed_text": data.get("printed_text", data.get("oracle_text", "")),
            "mana_cost": data.get("mana_cost", ""),
            "colors": data.get("colors", []),
            "image_url": img_url
        }