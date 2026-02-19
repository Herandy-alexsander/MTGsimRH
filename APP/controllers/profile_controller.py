# APP/controllers/profile_controller.py

class ProfileController:
    def __init__(self, profile_repo):
        """
        Gerencia a lógica de negócio do perfil do usuário (Conjurador).
        :param profile_repo: Instância da infraestrutura (ProfileRepository).
        """
        self.repo = profile_repo
        # Sincroniza o estado interno usando o nome de método correto do repositório
        self.perfil_atual = self.repo.ler_perfil()

    def carregar_perfil(self):
        """
        Atualiza e retorna os dados brutos do repositório físico.
        Corrigido para usar ler_perfil() do ProfileRepository.
        """
        self.perfil_atual = self.repo.ler_perfil()
        return self.perfil_atual

    def verificar_primeiro_acesso(self):
        """
        Verifica se o jogador já configurou um nickname válido.
        """
        # Sempre recarrega para garantir que pegamos a alteração feita no WelcomeView
        perfil = self.carregar_perfil()
        nickname = perfil.get("player_info", {}).get("nickname", "")
        return len(nickname.strip()) >= 3

    def cadastrar_nickname(self, nickname):
        """
        Valida o nome e utiliza o repositório para criar o arquivo físico.
        """
        nome_limpo = nickname.strip()
        
        # Regra de negócio: Mínimo de 3 caracteres
        if len(nome_limpo) < 3:
            return False, "O nome deve ter pelo menos 3 caracteres."
        
        # Persiste no HD através do repositório
        self.repo.inicializar_perfil_usuario(nome_limpo)
        
        # Sincroniza a memória RAM do controlador
        self.carregar_perfil()
        return True, "Perfil criado com sucesso!"

    def obter_nickname(self) -> str:
        """Retorna o nickname para exibição na interface (UI)."""
        nickname = self.perfil_atual.get("player_info", {}).get("nickname", "Conjurador")
        return nickname if nickname else "Conjurador"

    def obter_estatisticas(self) -> dict:
        """Compila os dados de progresso salvos no profiler.json."""
        info = self.perfil_atual.get("player_info", {})
        # Busca a lista de decks no índice global do perfil
        decks = self.perfil_atual.get("decks_info", {}).get("decks", [])
        
        return {
            "vitorias": info.get("vitorias", 0),
            "total_decks": len(decks),
            "data_criacao": info.get("created_at", "N/A")
        }