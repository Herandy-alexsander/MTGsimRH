import json
import os
from pathlib import Path

class FileManager:
    """
    Utilitário central para manipulação de arquivos JSON e diretórios.
    Garante que o projeto Machete seja portátil e resiliente a erros de I/O.
    """

    @staticmethod
    def salvar_json(caminho, dados):
        """
        Salva dados em formato JSON com codificação UTF-8 e indentação.
        Cria automaticamente as pastas pai se não existirem.
        """
        try:
            path = Path(caminho)
            # Garante que o diretório existe antes de tentar salvar
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[ERRO FILE_MANAGER] Falha ao salvar {caminho}: {e}")
            return False

    @staticmethod
    def carregar_json(caminho, fallback=None):
        """
        Lê um arquivo JSON e retorna um dicionário.
        Aceita um 'fallback' (ex: {}) para retornar caso o arquivo não exista ou esteja corrompido.
        """
        path = Path(caminho)
        if not path.exists():
            return fallback
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"[ERRO FILE_MANAGER] JSON corrompido: {caminho}")
            return fallback
        except Exception as e:
            print(f"[ERRO FILE_MANAGER] Erro de leitura em {caminho}: {e}")
            return fallback

    @staticmethod
    def listar_arquivos(diretorio, extensao=".json", retornar_caminho_completo=False):
        """
        Lista todos os arquivos de uma extensão específica em um diretório.
        :param retornar_caminho_completo: Se True, retorna 'data/decks/deck.json'. Se False, retorna só 'deck.json'.
        """
        path = Path(diretorio)
        if not path.exists():
            return []
            
        if retornar_caminho_completo:
            # Retorna o caminho exato padronizado
            return [f.as_posix() for f in path.glob(f"*{extensao}")]
            
        # Retorna apenas o nome do arquivo
        return [f.name for f in path.glob(f"*{extensao}")]