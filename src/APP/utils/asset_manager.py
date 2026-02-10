import pygame
import os

class AssetManager:
    def __init__(self, storage_manager):
        self.storage = storage_manager
        self._image_cache = {}
        
        # Placeholder caso a imagem não exista (Carta virada para baixo ou erro)
        self.placeholder = pygame.Surface((488, 680))
        self.placeholder.fill((40, 40, 45))
        pygame.draw.rect(self.placeholder, (70, 70, 80), self.placeholder.get_rect(), 3)

    def get_card_image(self, card_name, category="Outros"):
        """
        Busca a imagem no cache ou carrega do disco.
        Lida com a estrutura de subpastas: assets/cards/[Categoria]/nome_da_carta.jpg
        """
        if not card_name:
            return self.placeholder

        file_name = card_name.strip().replace(" ", "_").lower() + ".jpg"
        
        # 1. Verifica Cache
        if file_name in self._image_cache:
            return self._image_cache[file_name]

        # 2. Tenta encontrar o caminho correto (considerando as subpastas)
        # Primeiro tenta na categoria informada, se não achar, tenta em 'Outros'
        possible_paths = [
            os.path.join(self.storage.assets_cards_path, category, file_name),
            os.path.join(self.storage.assets_cards_path, "Outros", file_name)
        ]

        for path in possible_paths:
            if os.path.exists(path):
                try:
                    # .convert() otimiza a imagem para a placa de vídeo/processador
                    img = pygame.image.load(path).convert()
                    self._image_cache[file_name] = img
                    return img
                except Exception as e:
                    print(f"[AssetManager] Erro ao carregar {path}: {e}")

        return self.placeholder

    def clear_unused_cache(self):
        """Limpa a RAM se houver muitas imagens (opcional)"""
        if len(self._image_cache) > 200:
            self._image_cache.clear()
