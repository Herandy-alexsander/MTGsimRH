import json
import datetime
from pathlib import Path

class ProfileRepository:
    def __init__(self, caminho_padrao="data/profiles/profiler.json"):
        """
        Gerencia a persistência do perfil e o índice global de decks.
        Focado apenas em ler e escrever no profiler.json.
        """
        self.path = Path(caminho_padrao)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._inicializar_estrutura_se_vazio()

    def _inicializar_estrutura_se_vazio(self):
        """Cria o arquivo com campos vazios para forçar o primeiro acesso."""
        if not self.path.exists():
            dados_vazios = {
                "player_info": {
                    "nickname": "", 
                    "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "vitorias": 0
                },
                "decks_info": {
                    "decks": []
                },
                "config": {
                    "volume": 70,
                    "fullscreen": False
                }
            }
            self.salvar_perfil(dados_vazios)

    def inicializar_perfil_usuario(self, nickname):
        """Método chamado pelo WelcomeView/Controller para definir o nome real."""
        dados = self.ler_perfil()
        dados["player_info"]["nickname"] = nickname
        self.salvar_perfil(dados)

    def ler_perfil(self):
        """
        Lê os dados do disco. Substitui o antigo 'carregar_perfil'.
        Possui blindagem contra corrupção de arquivo.
        """
        try:
            if self.path.exists():
                with open(self.path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[AVISO] Perfil corrompido ou ausente: {e}. Recriando padrão.")
            self._inicializar_estrutura_se_vazio()
            
        # Retorna o arquivo recém-criado em caso de falha anterior
        with open(self.path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def salvar_perfil(self, dados):
        """Salva os dados de forma segura no disco."""
        try:
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"[ERRO PROFILE] Falha ao salvar: {e}")
            return False

    def adicionar_referencia_deck(self, deck_data):
        """Registra os metadados de um novo deck na galeria."""
        perfil = self.ler_perfil()
        
        # Garante que a estrutura exista antes de dar append
        if "decks_info" not in perfil:
            perfil["decks_info"] = {"decks": []}
        elif "decks" not in perfil["decks_info"]:
            perfil["decks_info"]["decks"] = []
            
        novo_id = len(perfil['decks_info']['decks']) + 1
        
        referencia = {
            "id": novo_id,
            "name": deck_data.get('name', 'Sem Nome'),
            "commander": deck_data.get('commander', 'Desconhecido'),
            "created_at": datetime.date.today().isoformat()
        }
        
        perfil['decks_info']['decks'].append(referencia)
        self.salvar_perfil(perfil)
        return novo_id