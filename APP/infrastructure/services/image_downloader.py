import requests
import json
import time
import re
from pathlib import Path

class ImageDownloader:
    def __init__(self, base_assets="assets/cards", base_data="data/cards"):
        """
        Inicializa o gerenciador com separação ESTRITA: 
        Mídia EXCLUSIVAMENTE para 'assets', Dados EXCLUSIVAMENTE para 'data'.
        """
        self.base_img_path = Path(base_assets)
        self.base_data_path = Path(base_data)

    def garantir_imagem_e_dados(self, carta_data):
        """
        Salva a imagem fisicamente e cria um JSON individual separado.
        Retorna os caminhos locais exatos para o arquivo mestre do deck.
        """
        categoria = carta_data.get("categoria", "Outros")
        
        # Limpeza PROFISSIONAL de nome de arquivo (evita erros no Windows/Linux)
        # Ex: "Krenko, Mob Boss" -> "krenko_mob_boss"
        nome_bruto = carta_data.get("name", "unk_card").lower().replace(" ", "_")
        nome_limpo = re.sub(r'[^a-z0-9_]', '', nome_bruto) # Mantém só letras, números e underline
        
        # 1. Cria a pasta da categoria APENAS para a IMAGEM
        dir_img = self.base_img_path / categoria
        dir_img.mkdir(parents=True, exist_ok=True)
        
        # 2. Cria a pasta da categoria APENAS para o JSON
        dir_json = self.base_data_path / categoria
        dir_json.mkdir(parents=True, exist_ok=True)
        
        # Define os caminhos finais fisicos
        caminho_imagem = dir_img / f"{nome_limpo}.jpg"
        caminho_json = dir_json / f"{nome_limpo}.json"

        # --- Etapa 1: Download da Arte (Pasta ASSETS) ---
        url = carta_data.get("image_url")
        caminho_img_final = caminho_imagem.as_posix() # Formata com barras seguras (/)

        if url and not caminho_imagem.exists():
            try:
                headers = {'User-Agent': 'MTK-Simulador/1.0'}
                time.sleep(0.1) # Respeito ao limite da API da Scryfall
                resp = requests.get(url, headers=headers, stream=True, timeout=10)
                if resp.status_code == 200:
                    with open(caminho_imagem, 'wb') as f:
                        for chunk in resp.iter_content(1024):
                            f.write(chunk)
            except Exception as e:
                print(f"[ERRO IMG] Falha ao baixar arte de {nome_limpo}: {e}")
                caminho_img_final = url # Fallback de segurança para a URL da web
        elif not url:
            caminho_img_final = "" # Sem imagem disponível

        # --- Etapa 2: Salvamento do JSON de Dados (Pasta DATA) ---
        caminho_json_final = caminho_json.as_posix()

        if not caminho_json.exists():
            carta_fisica = carta_data.copy()
            # O JSON da carta aponta para onde a imagem foi salva no assets
            carta_fisica["local_image_path"] = caminho_img_final
            
            try:
                # Salva o arquivo EXCLUSIVAMENTE no dir_json (data/cards/...)
                with open(caminho_json, 'w', encoding='utf-8') as f:
                    json.dump(carta_fisica, f, ensure_ascii=False, indent=4)
            except Exception as e:
                print(f"[ERRO JSON] Falha ao salvar dados de {nome_limpo}: {e}")

        # Retorna as referências limpas para o DeckModel
        return {
            "name": carta_data["name"],
            "quantity": carta_data.get("quantity", 1),
            "ref_json": caminho_json_final,  # Ex: data/cards/criaturas/krenko_mob_boss.json
            "ref_image": caminho_img_final   # Ex: assets/cards/criaturas/krenko_mob_boss.jpg
        }