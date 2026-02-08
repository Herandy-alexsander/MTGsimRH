import os
import json
import requests
import time
import datetime # Importado para o timestamp do perfil
from datetime import date

class MTGStorageManager:
    def __init__(self, base_path="data"):
        """Gerencia a persistência de dados e integração com API."""
        self.base_path = base_path
        self.profiler_path = os.path.join(base_path, "profiler.json")
        self.decks_path = os.path.join(base_path, "decks")
        self.cards_path = os.path.join(base_path, "cards")
        self.api_url = "https://api.scryfall.com/cards/named?exact="
        
        os.makedirs(self.decks_path, exist_ok=True)
        os.makedirs(self.cards_path, exist_ok=True)

    def carregar_perfil(self):
        """Lê o perfil do utilizador para exibir no menu."""
        if os.path.exists(self.profiler_path):
            with open(self.profiler_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"player_info": {"nickname": "Conjurador"}, "decks_info": {"decks": []}}

    def verificar_perfil_existente(self):
        """Verifica se existe um nickname configurado no sistema."""
        if os.path.exists(self.profiler_path):
            try:
                with open(self.profiler_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return "player_info" in data and bool(data["player_info"].get("nickname"))
            except (json.JSONDecodeError, IOError):
                return False
        return False

    def inicializar_perfil_usuario(self, nickname):
        """Cria ou atualiza o perfil com o nickname fornecido."""
        perfil = self.carregar_perfil()
        perfil["player_info"] = {
            "nickname": nickname,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        try:
            with open(self.profiler_path, 'w', encoding='utf-8') as f:
                json.dump(perfil, f, indent=4, ensure_ascii=False)
            print(f"[OK] Perfil salvo para: {nickname}")
        except Exception as e:
            print(f"[ERRO] Falha ao salvar perfil: {str(e)}")

    def download_deck_from_txt(self, caminho_completo):
        """Extrai dados da API Scryfall incluindo type_line para o filtro."""
        cards_extracted = []
        with open(caminho_completo, 'r', encoding='utf-8') as f:
            linhas = [l.strip() for l in f if l.strip()]

        for linha in linhas:
            parts = linha.split(' ', 1)
            qty = int(parts[0]) if parts[0].isdigit() else 1
            name = parts[1] if parts[0].isdigit() else linha

            response = requests.get(f"{self.api_url}{name}")
            if response.status_code == 200:
                data = response.json()
                cards_extracted.append({
                    "name": data.get("name"),
                    "type_line": data.get("type_line", ""), # Essencial para o seletor
                    "mana_cost": data.get("mana_cost", ""),
                    "image_url": data.get("image_uris", {}).get("normal"),
                    "quantity": qty
                })
                time.sleep(0.1) 
        return cards_extracted

    def salvar_deck_inteligente(self, deck_model):
        """Decide entre registrar novo ou atualizar existente."""
        perfil = self.carregar_perfil()
        decks = perfil.get('decks_info', {}).get('decks', [])
        existe = any(d['name'].lower() == deck_model.name.lower() for d in decks)
        
        if existe:
            self.update_deck_existente(deck_model)
        else:
            self.registrar_novo_deck(deck_model)

    def registrar_novo_deck(self, deck_model):
        """Registra novo deck e gera nova pasta."""
        perfil = self.carregar_perfil()
        novo_id = len(perfil['decks_info']['decks']) + 1
        perfil['decks_info']['decks'].append({
            "id": novo_id, "name": deck_model.name, "created_at": str(date.today())
        })
        with open(self.profiler_path, 'w', encoding='utf-8') as f:
            json.dump(perfil, f, indent=4)
        self._salvar_arquivos_deck(deck_model, f"{novo_id}_{deck_model.deck_id}")

    def update_deck_existente(self, deck_model):
        """Sobrescreve dados do deck na pasta original."""
        perfil = self.carregar_perfil()
        deck_data = next((d for d in perfil['decks_info']['decks'] if d['name'] == deck_model.name), None)
        if deck_data:
            folder_name = f"{deck_data['id']}_{deck_model.deck_id}"
            self._salvar_arquivos_deck(deck_model, folder_name)

    def _salvar_arquivos_deck(self, deck_model, folder_name):
        """Grava os arquivos JSON no disco."""
        path_cards = os.path.join(self.cards_path, folder_name)
        os.makedirs(path_cards, exist_ok=True)
        with open(os.path.join(path_cards, "cards_info.json"), 'w', encoding='utf-8') as f:
            json.dump(deck_model.get_full_json(), f, indent=4, ensure_ascii=False)
        with open(os.path.join(self.decks_path, f"{deck_model.deck_id}.json"), 'w', encoding='utf-8') as f:
            json.dump(deck_model.get_config_data(), f, indent=4, ensure_ascii=False)