import pygame
from pathlib import Path

class AssetManager:
    def __init__(self, base_assets="assets/cards"):
        """
        Gestor central de mídia para o simulador.
        Focado em carregar caminhos diretos vindos do banco de dados (JSON).
        """
        self.base_assets = Path(base_assets)
        self.image_cache = {}

    def get_card_image(self, local_path: str):
        """
        Carrega a imagem usando o caminho exato armazenado no JSON (local_image_path).
        """
        if not local_path:
            return None

        # 1. Verifica se a imagem já está no cache (RAM) para economizar CPU
        if local_path in self.image_cache:
            return self.image_cache[local_path]
            
        # 2. Se não estiver no cache, tenta carregar do HD
        # O Path garante que funcione tanto no Windows quanto no Linux
        caminho_img = Path(local_path)
        
        if caminho_img.exists():
            try:
                # convert_alpha() é vital: aumenta o FPS e aceita transparência
                img_surface = pygame.image.load(str(caminho_img)).convert_alpha()
                self.image_cache[local_path] = img_surface
                return img_surface
            except Exception as e:
                print(f"[ERRO ASSET] Falha técnica ao ler {caminho_img}: {e}")
        else:
            # Se cair aqui, o arquivo não está onde o JSON diz que está
            print(f"[DEBUG ASSET] Arquivo não encontrado no caminho do JSON: {local_path}")
        
        return None

    def limpar_cache(self):
        """Libera a memória RAM, limpando as superfícies carregadas."""
        self.image_cache.clear()