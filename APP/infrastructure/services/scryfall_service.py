# APP/infrastructure/services/scryfall_service.py

import requests
import time

class ScryfallService:
    def __init__(self):
        self.base_url = "https://api.scryfall.com"
        self.headers = {'User-Agent': 'MTK-Simulador/1.0 (Machete-Dev)'}

    def buscar_lote_cartas(self, lista_nomes):
        if not lista_nomes: return []
        url = f"{self.base_url}/cards/collection"
        identificadores = [{"name": n.strip()} for n in lista_nomes if n.strip()]
        payload = {"identifiers": identificadores}
        try:
            resp = requests.post(url, json=payload, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                resultado = resp.json()
                return [self._formatar_dados(carta) for carta in resultado.get('data', []) if carta.get('object') != 'error']
        except Exception as e:
            print(f"[ERRO BATCH] Falha na conexão: {e}")
        return []

    def buscar_carta(self, nome_input):
        url_named = f"{self.base_url}/cards/named?exact={nome_input}"
        try:
            resp = requests.get(url_named, headers=self.headers, timeout=5)
            if resp.status_code == 200:
                return self._formatar_dados(resp.json())
        except Exception as e:
            print(f"[ERRO API] {nome_input}: {e}")
        return None

    def _determinar_categoria(self, type_line):
        """Define a pasta/categoria baseada no Type Line da Scryfall."""
        tl = type_line.lower()
        if "land" in tl: return "Terrenos"
        if "creature" in tl: return "Criaturas"
        if "artifact" in tl: return "Artefatos"
        if "enchantment" in tl: return "Encantamentos"
        if "planeswalker" in tl: return "Planeswalkers"
        if "instant" in tl: return "Instantaneas"
        if "sorcery" in tl: return "Feiticos"
        return "Outros"

    def _formatar_dados(self, data):
        if not data: return None
        
        img_url = data.get("image_uris", {}).get("normal")
        if not img_url and "card_faces" in data:
            img_url = data["card_faces"][0].get("image_uris", {}).get("normal")

        type_line = data.get("type_line", "")
        
        # Estrutura base da carta
        return {
            "name": data.get("name"),
            "printed_name": data.get("printed_name", data.get("name")),
            "type_line": type_line,
            "categoria": self._determinar_categoria(type_line), # Classificação Automática
            "mana_cost": data.get("mana_cost", ""),
            "colors": data.get("colors", []),
            "image_url": img_url, 
            "oracle_text": data.get("oracle_text", ""),
            "rarity": data.get("rarity", "common")
        }