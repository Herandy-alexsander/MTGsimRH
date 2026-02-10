import random
import os
from APP.models.match_model import PlayerModel

class MatchController:
    def __init__(self, model):
        """
        Controlador responsável pela lógica de jogo e transição de estados da partida.
        """
        self.model = model
        self.total_players = 4  # Ajustado dinamicamente pelo ViewManager conforme o Menu

    def setup_game(self, human_deck_data, commander_name, nickname="Conjurador"):
        """
        Inicializa a partida criando os jogadores, definindo o comandante e preparando as bibliotecas.
        """
        self.model.players = {} # Limpa estados de partidas anteriores
        
        # 1. Registra o Comandante no Modelo
        self.model.commander = commander_name
        
        # 2. Configura o Jogador Humano (ID 1)
        deck_humano = self._expand_deck(human_deck_data)
        random.shuffle(deck_humano) # Embaralhamento inicial
        
        player_1 = PlayerModel(nickname, deck_humano)
        player_1.life = 40 # Vida inicial padrão Commander
        self._realizar_mao_inicial(player_1)
        self.model.players[1] = player_1

        # 3. Configura os Oponentes (Bots) baseado na seleção do Menu
        for i in range(2, self.total_players + 1):
            deck_bot = self._expand_deck(human_deck_data) # Expande novamente para ter cópias limpas
            random.shuffle(deck_bot)
            
            bot = PlayerModel(f"Oponente {i-1}", deck_bot)
            bot.life = 40
            self._realizar_mao_inicial(bot)
            self.model.players[i] = bot
            
        print(f"[OK] Partida Commander iniciada com {self.total_players} jogadores. Comandante: {commander_name}")

    def _realizar_mao_inicial(self, player):
        """Saca as 7 cartas iniciais conforme a regra de jogo."""
        for _ in range(7):
            if player.library:
                player.hand.append(player.library.pop())

    def _expand_deck(self, cards_json):
        """
        Transforma a lista compactada do JSON em objetos individuais e
        atribui o caminho local da imagem para a View.
        """
        deck = []
        for c in cards_json:
            qtd = c.get('quantity', 1)
            for _ in range(qtd):
                carta_instancia = c.copy()
                
                # AÇÃO: Mapeia o caminho da imagem antes de adicionar ao deck
                carta_instancia['image_path'] = self._definir_caminho_imagem(carta_instancia)
                
                deck.append(carta_instancia)
        return deck

    def _definir_caminho_imagem(self, carta):
        """
        Lógica para encontrar a imagem na estrutura de pastas assets/cards/
        """
        tipo = carta.get("type_line", "")
        # Normaliza o nome para o arquivo (remove barras de cartas dupla-face)
        nome_arquivo = carta.get("name", "unknown").replace("/", "_") + ".jpg"
        
        # Mapeamento de pastas baseado no tipo
        pasta = "Outros"
        if "Creature" in tipo: pasta = "Criaturas"
        elif "Land" in tipo: pasta = "Terrenos"
        elif "Instant" in tipo: pasta = "Instantes"
        elif "Sorcery" in tipo: pasta = "Feiticos"
        elif "Enchantment" in tipo: pasta = "Encantamentos"
        elif "Artifact" in tipo: pasta = "Artefatos"
        
        # Retorna o caminho relativo para ser usado pelo pygame.image.load
        return os.path.join("assets", "cards", pasta, nome_arquivo)

    def play_land(self, player_id, card_index):
        """Move um terreno da mão para o campo de batalha."""
        player = self.model.players.get(player_id)
        if player and 0 <= card_index < len(player.hand):
            card = player.hand[card_index]
            if "Land" in card.get("type_line", ""):
                card_movida = player.hand.pop(card_index)
                player.battlefield_lands.append(card_movida)
                print(f"[JOGO] {player.name} jogou Terreno: {card_movida['name']}.")
            else:
                print(f"[AVISO] {card['name']} não é um terreno.")

    def draw_card(self, player_id):
        """Saca uma carta da biblioteca para a mão."""
        player = self.model.players.get(player_id)
        if player and player.library:
            nova_carta = player.library.pop()
            player.hand.append(nova_carta)
            print(f"[JOGO] {player.name} comprou uma carta.")
            
    def mudar_vida(self, player_id, quantidade):
        """Altera o total de vida do jogador."""
        player = self.model.players.get(player_id)
        if player:
            player.life += quantidade
            print(f"[STATUS] {player.name} agora tem {player.life} de vida.")
