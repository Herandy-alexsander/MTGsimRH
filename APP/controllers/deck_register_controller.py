import threading
import time
from datetime import datetime

class DeckRegisterController:
    def __init__(self, scryfall_service, deck_repo, profile_repo, image_downloader):
        """
        Motor de registro de decks. Orquestra a análise de TXT, consulta à Scryfall 
        e o download físico de assets em background.
        """
        self.scryfall = scryfall_service
        self.deck_repo = deck_repo
        self.profile_repo = profile_repo
        self.image_downloader = image_downloader 
        
        self.estado = "INICIAL"
        self.progresso = 0
        self.carta_atual_nome = ""
        self.nome_deck_temp = ""
        self.mensagem_erro = "" 
        
        self.cartas_processadas = []
        self.lendas_encontradas = []
        self.index_lenda = 0

    def limpar_dados(self):
        """Zera o estado para um novo cadastro, liberando memória RAM."""
        self.estado = "INICIAL"
        self.progresso = 0
        self.carta_atual_nome = ""
        self.nome_deck_temp = ""
        self.mensagem_erro = ""
        self.cartas_processadas.clear()
        self.lendas_encontradas.clear()
        self.index_lenda = 0

    def iniciar_analise(self, nome_deck, linhas_txt):
        """Dispara a thread de consulta à API."""
        self.limpar_dados()
        self.nome_deck_temp = nome_deck if nome_deck else "Novo Deck"
        self.estado = "ANALISANDO"
        
        thread = threading.Thread(target=self._processar_lista_batch, args=(linhas_txt,))
        thread.daemon = True 
        thread.start()

    def _processar_lista_batch(self, linhas):
        """Consulta ultra-rápida via API Scryfall (Batch mode)."""
        time.sleep(0.5) 
        try:
            linhas_validas = [l.strip() for l in linhas if l.strip()]
            if not linhas_validas:
                self.mensagem_erro = "Arquivo TXT vazio ou inválido."
                self.estado = "INICIAL"
                return

            nomes_lista = []
            mapa_quantidades = {}
            total_cartas_txt = 0

            # 1. Parsing do TXT (Formato: 'Quantidade Nome')
            for linha in linhas_validas:
                partes = linha.split(' ', 1)
                qtd = int(partes[0]) if partes[0].isdigit() else 1
                nome = partes[1] if partes[0].isdigit() else linha
                nomes_lista.append(nome)
                mapa_quantidades[nome] = qtd
                total_cartas_txt += qtd

            # 2. Validação básica de Commander
            if total_cartas_txt != 100:
                print(f"[AVISO] Deck com {total_cartas_txt} cartas detectado.")

            self.progresso = 10
            self.carta_atual_nome = "Consultando Scryfall..."

            # 3. Consulta em lotes (limite de 75 cartas por requisição da Scryfall)
            cartas_retornadas = []
            for i in range(0, len(nomes_lista), 75):
                lote = nomes_lista[i:i+75]
                resultados = self.scryfall.buscar_lote_cartas(lote)
                if resultados:
                    cartas_retornadas.extend(resultados)
                self.progresso = 15 + int((i / len(nomes_lista)) * 60)

            # 4. Processamento dos resultados e detecção de Lendas
            for dados in cartas_retornadas:
                if not dados or not isinstance(dados, dict): continue
                
                nome_card = dados.get('name', 'Desconhecido')
                self.carta_atual_nome = nome_card
                dados['quantity'] = mapa_quantidades.get(nome_card, 1)
                self.cartas_processadas.append(dados)

                type_line = dados.get('type_line', '')
                if "Legendary" in type_line and "Creature" in type_line:
                    self.lendas_encontradas.append({
                        "name": nome_card,
                        "url_temp": dados.get('image_url')
                    })

            if not self.lendas_encontradas:
                self.mensagem_erro = "Nenhuma Criatura Lendária encontrada no deck."
                self.estado = "INICIAL"
            else:
                self.progresso = 100
                self.estado = "SELECAO"
            
        except Exception as e:
            print(f"[ERRO BATCH] {e}")
            self.mensagem_erro = "Falha crítica na conexão com a API."
            self.estado = "INICIAL"

    def obter_comandante_atual(self):
        if self.lendas_encontradas and 0 <= self.index_lenda < len(self.lendas_encontradas):
            return self.lendas_encontradas[self.index_lenda]
        return None

    def navegar_lendas(self, direcao):
        if self.lendas_encontradas:
            self.index_lenda = (self.index_lenda + direcao) % len(self.lendas_encontradas)

    def finalizar_registro(self):
        """Inicia a fase de estruturação offline (Download de imagens)."""
        comandante = self.obter_comandante_atual()
        if not comandante: return False
        
        total_cartas = sum(c.get('quantity', 1) for c in self.cartas_processadas)
        
        try:
            deck_final = {
                "name": self.nome_deck_temp,
                "commander": comandante['name'],
                "commander_url": comandante['url_temp'], 
                "total_cards": total_cartas,
                "cards": self.cartas_processadas, 
                "created_at": datetime.now().strftime("%Y-%m-%d")
            }

            self.estado = "SALVANDO"
            self.progresso = 0
            
            thread_offline = threading.Thread(target=self._estruturar_dados_offline, args=(deck_final,))
            thread_offline.daemon = True
            thread_offline.start()
            return True
            
        except Exception as e:
            print(f"[ERRO FINALIZAR] {e}")
            self.mensagem_erro = "Erro ao preparar salvamento."
            self.estado = "SELECAO"
        return False

    def _estruturar_dados_offline(self, deck_final):
        """Faz o download físico das cartas e salva os JSONs locais."""
        cartas_estruturadas = []
        total = len(deck_final['cards'])
        
        for index, carta_data in enumerate(deck_final['cards']):
            self.carta_atual_nome = carta_data.get('name', 'Desconhecido')
            self.progresso = int(((index + 1) / total) * 100)
            
            # Chama o downloader físico (Garante imagens em assets e JSON em data)
            dados_locais = self.image_downloader.garantir_imagem_e_dados(carta_data)
            if dados_locais:
                cartas_estruturadas.append(dados_locais)
        
        deck_final['cards'] = cartas_estruturadas
        
        # Persistência final no disco
        self.deck_repo.salvar_deck_físico(deck_final)
        self.profile_repo.adicionar_referencia_deck(deck_final)
        
        print(f"[OK] Deck '{deck_final['name']}' salvo com sucesso!")
        self.estado = "CONCLUIDO"