import os
import json
import requests
import time
import datetime
from datetime import date

class MTGStorageManager:
    def __init__(self, base_path="data"):
        """
        Gerencia o armazenamento técnico e o download de assets (imagens).
        Estrutura de dados: data/cards/[Categoria]/
        Estrutura de imagens: assets/cards/[Categoria]/.
        """
        self.base_path = base_path
        self.profiler_path = os.path.join(base_path, "profiler.json")
        self.decks_path = os.path.join(base_path, "decks")
        self.cards_repository = os.path.join(base_path, "cards")
        self.assets_cards_path = os.path.join("assets", "cards")
        self.api_url = "https://api.scryfall.com/cards/named?exact="
        
        # Garante a existência das pastas raiz
        os.makedirs(self.decks_path, exist_ok=True)
        os.makedirs(self.cards_repository, exist_ok=True)
        os.makedirs(self.assets_cards_path, exist_ok=True)

    # --- LÓGICA DE SEGURANÇA EM DUAS ETAPAS ---

    def analisar_txt(self, caminho_txt):
        """
        ETAPA 1: Pré-carga. Valida o arquivo e retorna os dados para a interface.
        """
        try:
            if not os.path.exists(caminho_txt):
                return 0, []
            with open(caminho_txt, 'r', encoding='utf-8') as f:
                linhas = [l.strip() for l in f if l.strip()]
            return len(linhas), linhas
        except Exception as e:
            print(f"[ERRO] Falha ao analisar TXT: {e}")
            return 0, []

    def processar_download_com_progresso(self, lista_nomes, callback_progresso):
        """
        ETAPA 2: Download real com reporte de progresso para a View.
        """
        total = len(lista_nomes)
        cards_extraidos = []

        for i, linha in enumerate(lista_nomes):
            parts = linha.split(' ', 1)
            qty = int(parts[0]) if parts[0].isdigit() else 1
            name = parts[1] if parts[0].isdigit() else linha
            
            # Notifica a tela de progresso
            if callback_progresso:
                callback_progresso(i + 1, total, name)

            try:
                response = requests.get(f"{self.api_url}{name}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    # Tratamento de imagem para cartas de dupla face
                    img = data.get("image_uris", {}).get("normal")
                    if not img and "card_faces" in data:
                        img = data["card_faces"][0].get("image_uris", {}).get("normal")

                    cards_extraidos.append({
                        "name": data.get("name"),
                        "type_line": data.get("type_line", ""),
                        "mana_cost": data.get("mana_cost", ""),
                        "cmc": data.get("cmc"),
                        "oracle_text": data.get("oracle_text", ""),
                        "power": data.get("power"),
                        "toughness": data.get("toughness"),
                        "rarity": data.get("rarity"),
                        "colors": data.get("colors", []),
                        "image_url": img,
                        "quantity": qty
                    })
                    time.sleep(0.08) # Delay cortês Scryfall
            except Exception as e:
                print(f"[ERRO] Falha ao baixar {name}: {e}")
                
        return cards_extraidos

    # --- LÓGICA DE CATEGORIAS E ASSETS ---

    def _get_categoria(self, type_line):
        tl = type_line.lower() if type_line else ""
        if "land" in tl: return "Terrenos"
        if "creature" in tl: return "Criaturas"
        if "sorcery" in tl: return "Feiticos"
        if "instant" in tl: return "Instantes"
        if "artifact" in tl: return "Artefatos"
        if "enchantment" in tl: return "Encantamentos"
        return "Outros"

    def _baixar_imagem_local(self, url, categoria, nome_arquivo):
        """Salva a imagem fisicamente em assets/cards/[Categoria]/."""
        if not url: return None
        pasta_destino = os.path.join(self.assets_cards_path, categoria)
        os.makedirs(pasta_destino, exist_ok=True)
        caminho_local = os.path.join(pasta_destino, f"{nome_arquivo}.jpg")
        
        if not os.path.exists(caminho_local):
            try:
                response = requests.get(url, stream=True, timeout=10)
                if response.status_code == 200:
                    with open(caminho_local, 'wb') as f:
                        for chunk in response.iter_content(1024):
                            f.write(chunk)
            except Exception as e:
                print(f"[ERRO] Imagem {nome_arquivo}: {e}")
                return url 
        return caminho_local

    def _salvar_arquivos_deck(self, deck_model):
        """Gera os arquivos JSON e vincula as imagens locais."""
        deck_config = {
            "name": deck_model.name,
            "commander": deck_model.commander,
            "deck_id": deck_model.deck_id,
            "total_cards": len(deck_model.cards),
            "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "categories": {}
        }

        for card in deck_model.cards:
            categoria = self._get_categoria(card.get("type_line", ""))
            nome_base = card.get("name").replace(" ", "_").lower().replace("/", "")
            
            # Download/Vinculação de imagem local
            caminho_img = self._baixar_imagem_local(card.get("image_url"), categoria, nome_base)
            card["image_url"] = caminho_img

            dir_data_cat = os.path.join(self.cards_repository, categoria)
            os.makedirs(dir_data_cat, exist_ok=True)
            card_json_path = os.path.join(dir_data_cat, f"{nome_base}.json")
            
            if not os.path.exists(card_json_path):
                self._salvar_json(card_json_path, card)

            if categoria not in deck_config["categories"]:
                deck_config["categories"][categoria] = []

            deck_config["categories"][categoria].append({
                "name": card.get("name"),
                "quantity": card.get("quantity", 1),
                "data_path": card_json_path
            })

        self._salvar_json(os.path.join(self.decks_path, f"{deck_model.deck_id}.json"), deck_config)

    # --- LÓGICA DE PERFIL (PROFILER) ---

    def carregar_perfil(self):
        """Lê os dados do conjurador."""
        if os.path.exists(self.profiler_path):
            try:
                with open(self.profiler_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: pass
        return {"player_info": {"nickname": ""}, "decks_info": {"decks": []}}

    def verificar_perfil_existente(self):
        """Verifica se o nickname existe no sistema."""
        return bool(self.carregar_perfil().get("player_info", {}).get("nickname"))

    def inicializar_perfil_usuario(self, nickname):
        """
        RESOLVE O ERRO DE ATRIBUTO: Salva o nome do novo conjurador.
        """
        perfil = self.carregar_perfil()
        perfil["player_info"] = {
            "nickname": nickname,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self._salvar_json(self.profiler_path, perfil)
        print(f"[OK] Perfil criado para: {nickname}")

    def salvar_deck_inteligente(self, deck_model):
        """Sincroniza o deck com o profiler."""
        perfil = self.carregar_perfil()
        existe = any(d['name'].lower() == deck_model.name.lower() for d in perfil.get('decks_info', {}).get('decks', []))
        if existe:
            self._salvar_arquivos_deck(deck_model)
        else:
            self.registrar_novo_deck(deck_model)

    def registrar_novo_deck(self, deck_model):
        perfil = self.carregar_perfil()
        novo_id = len(perfil['decks_info']['decks']) + 1
        perfil['decks_info']['decks'].append({
            "id": novo_id, "name": deck_model.name, 
            "commander": deck_model.commander, "created_at": str(date.today())
        })
        self._salvar_json(self.profiler_path, perfil)
        self._salvar_arquivos_deck(deck_model)

    def _salvar_json(self, caminho, dados):
        """Escrita segura de JSON com suporte a UTF-8."""
        try:
            with open(caminho, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[ERRO] Falha ao salvar JSON em {caminho}: {e}")