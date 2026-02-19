import json
import re
from pathlib import Path

class DeckRepository:
    def __init__(self, pasta_decks="data/decks"):
        """
        Repositório especializado apenas na persistência física de decks.
        Focado em ler e escrever arquivos JSON na pasta data/decks.
        """
        self.path_decks = Path(pasta_decks)
        self.path_decks.mkdir(parents=True, exist_ok=True)

    def salvar_deck_físico(self, deck_data):
        """
        Salva o dicionário do deck em um arquivo JSON.
        O nome do arquivo é limpo para evitar erros no Windows.
        """
        try:
            # Limpeza profissional (ex: "Deck Goblin, v1" -> "deck_goblin_v1")
            nome_bruto = deck_data.get('name', 'novo_deck').strip().lower().replace(" ", "_")
            nome_limpo = re.sub(r'[^a-z0-9_]', '', nome_bruto)
            
            caminho_final = self.path_decks / f"{nome_limpo}.json"
            
            with open(caminho_final, 'w', encoding='utf-8') as f:
                json.dump(deck_data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"[ERRO DECK_REPO] Falha ao salvar arquivo físico: {e}")
            return False

    def carregar_deck_completo(self, nome_deck):
        """Lê um deck específico do disco pelo seu nome exato."""
        try:
            nome_bruto = nome_deck.strip().lower().replace(" ", "_")
            nome_limpo = re.sub(r'[^a-z0-9_]', '', nome_bruto)
            caminho = self.path_decks / f"{nome_limpo}.json"
            
            if caminho.exists():
                with open(caminho, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"[AVISO] Arquivo de deck não encontrado: {caminho}")
                return None
        except Exception as e:
            print(f"[ERRO DECK_REPO] Falha ao ler arquivo físico: {e}")
            return None

    def obter_dados_carta_individual(self, card_ref):
        """Lê o JSON individual de uma carta na pasta data/cards/... se existir."""
        path_carta = card_ref.get("ref_json")
        if path_carta:
            caminho_fisico = Path(path_carta)
            if caminho_fisico.exists():
                try:
                    with open(caminho_fisico, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    print(f"Erro ao ler JSON da carta: {e}")
        return card_ref # Fallback: devolve os dados básicos se falhar

    def listar_todos_os_arquivos_deck(self):
        """Retorna uma lista com o caminho de todos os JSONs na pasta decks."""
        return list(self.path_decks.glob("*.json"))