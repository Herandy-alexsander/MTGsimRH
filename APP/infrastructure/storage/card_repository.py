import os
import re
from pathlib import Path
from .file_manager import FileManager

class CardRepository:
    def __init__(self):
        """
        Gerencia o banco de dados local de cartas individuais.
        Busca e salva metadados de forma dinâmica na infraestrutura de pastas.
        """
        self.base_data_path = Path("data/cards")
        self.base_img_path = Path("assets/cards")

    def _limpar_nome(self, nome_bruto):
        """
        Padroniza o nome do arquivo EXATAMENTE como o ImageDownloader faz.
        Garante que o repositório consiga achar o arquivo que o downloader criou.
        """
        nome_min = nome_bruto.strip().lower().replace(" ", "_")
        return re.sub(r'[^a-z0-9_]', '', nome_min)

    def buscar_carta_local(self, nome_carta):
        """
        Procura o JSON da carta varrendo TODAS as pastas de categorias.
        Retorna os dados se encontrar, ou None se precisar baixar.
        """
        nome_arquivo = f"{self._limpar_nome(nome_carta)}.json"
        
        # Previne erro se a pasta data/cards ainda não existir
        if not self.base_data_path.exists():
            return None
            
        # Busca Dinâmica: Olha em todas as pastas que existirem no HD
        for pasta_categoria in self.base_data_path.iterdir():
            if pasta_categoria.is_dir():
                caminho = pasta_categoria / nome_arquivo
                if caminho.exists():
                    return FileManager.carregar_json(caminho)
                    
        return None

    def salvar_carta_local(self, card_data, categoria="Outros"):
        """Salva os metadados da carta para uso futuro (Offline)."""
        nome_limpo = self._limpar_nome(card_data.get("name", "unk_card"))
        caminho = self.base_data_path / categoria / f"{nome_limpo}.json"
        
        return FileManager.salvar_json(caminho, card_data)

    def obter_caminho_imagem(self, nome_carta, categoria="Outros"):
        """Retorna o caminho do asset .jpg local com formatação multiplataforma."""
        nome_limpo = self._limpar_nome(nome_carta)
        caminho_img = self.base_img_path / categoria / f"{nome_limpo}.jpg"
        
        # Verifica se o arquivo físico de fato existe no HD antes de devolver a rota
        if caminho_img.exists():
            return caminho_img.as_posix() # Garante o formato com barras seguras (/)
        return None