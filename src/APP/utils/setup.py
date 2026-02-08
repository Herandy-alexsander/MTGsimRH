import os
import json

def inicializar_sistema():
    """
    Gera os diretorios e arquivos base na raiz do projeto.
    Garante a persistencia de dados para o storage e manager.
    """
    # 1. Lista de pastas essenciais na raiz (fora do src)
    diretorios = [
        "data",
        "data/decks",   
        "data/cards",   
        "data/assets",
        "data/cache"
    ]

    for pasta in diretorios:
        if not os.path.exists(pasta):
            os.makedirs(pasta)
            print(f"[OK] Pasta criada na raiz: {pasta}")

    # 2. Inicializacao do Profiler com suporte ao Nickname
    profiler_path = "data/profiler.json"
    if not os.path.exists(profiler_path):
        default_profile = {
            "player_info": {
                "nickname": "",  # Sera preenchido pela WelcomeView
                "created_at": ""
            },
            "player_stats": {
                "total_matches": 0, 
                "wins": 0, 
                "losses": 0
            },
            "decks_info": {
                "total_decks": 0, 
                "decks": []
            }
        }
        try:
            with open(profiler_path, 'w', encoding='utf-8') as f:
                json.dump(default_profile, f, indent=4, ensure_ascii=False)
            print("[OK] Arquivo data/profiler.json inicializado.")
        except Exception as e:
            print(f"[ERRO] Falha ao criar profiler: {str(e)}")

# Se rodar este arquivo sozinho, ele executa a criacao
if __name__ == "__main__":
    inicializar_sistema()