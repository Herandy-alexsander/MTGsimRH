import random
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
        
        # 1. Registra o Comandante no Modelo (Correção do erro AttributeError)
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
            # Clona o deck humano para os bots como base de teste
            # (Futuramente você pode carregar decks específicos para bots)
            deck_bot = list(deck_humano) 
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
        Transforma a lista compactada do JSON (com quantidades) em uma lista 
        de objetos de carta individuais para a biblioteca.
        """
        deck = []
        # Garante que percorremos a estrutura de categorias do deck
        for c in cards_json:
            qtd = c.get('quantity', 1)
            for _ in range(qtd):
                # Usamos copy() para que alterações em uma carta (ex: virar) 
                # não afetem outras cópias da mesma carta
                deck.append(c.copy())
        return deck

    def play_land(self, player_id, card_index):
        """
        Move um terreno da mão para o campo de batalha se for válido.
        """
        player = self.model.players.get(player_id)
        # Verifica se o jogador existe e se o índice é válido
        if player and 0 <= card_index < len(player.hand):
            card = player.hand[card_index]
            
            # Verifica se é realmente um terreno antes de mover
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
        """Altera o total de vida do jogador (Dano ou Ganho de Vida)."""
        player = self.model.players.get(player_id)
        if player:
            player.life += quantidade
            print(f"[STATUS] {player.name} agora tem {player.life} de vida.")