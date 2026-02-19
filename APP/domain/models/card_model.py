from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict
import os

class CardModel(BaseModel):
    """
    Representa uma única carta física na mesa de jogo.
    Mistura os dados imutáveis do JSON com o estado mutável da partida.
    """
    
    # Ignora campos extras do JSON para evitar quebras
    model_config = ConfigDict(extra='ignore')

    # =========================================================
    # 1. DADOS ESTÁTICOS
    # =========================================================
    name: str
    mana_cost: Optional[str] = ""
    cmc: float = 0.0  
    type_line: Optional[str] = "" 
    oracle_text: Optional[str] = ""
    
    colors: List[str] = Field(default_factory=list)
    color_identity: List[str] = Field(default_factory=list)
    
    power: Optional[str] = None
    toughness: Optional[str] = None
    loyalty: Optional[str] = None
    
    local_image_path: Optional[str] = None

    # =========================================================
    # 2. ESTADO DA PARTIDA
    # =========================================================
    is_tapped: bool = False
    is_face_down: bool = False
    counters: Dict[str, int] = Field(default_factory=dict) 

    # =========================================================
    # 3. MÉTODOS DE AÇÃO
    # =========================================================
    def tap(self):
        if not self.is_tapped:
            self.is_tapped = True
            return True
        return False

    def untap(self):
        if self.is_tapped:
            self.is_tapped = False
            return True
        return False

    def add_counter(self, counter_type: str, amount: int = 1):
        self.counters[counter_type] = self.counters.get(counter_type, 0) + amount
        if self.counters[counter_type] <= 0:
            del self.counters[counter_type]

    def remove_all_counters(self):
        self.counters.clear()

    # =========================================================
    # 4. HELPERS (PULO DO GATO PARA AS IMAGENS)
    # =========================================================
    
    def get_image_filename(self) -> str:
        """
        Extrai o nome do arquivo sem extensão do local_image_path.
        Ex: 'assets/cards/Artefatos/bolas_citadel.jpg' -> 'bolas_citadel'
        """
        if self.local_image_path:
            # Pega o nome do arquivo (ex: bolass_citadel.jpg)
            base = os.path.basename(self.local_image_path)
            # Remove a extensão (.jpg ou .png)
            return os.path.splitext(base)[0]
        return self.name.lower().replace(" ", "_")

    @property
    def is_land(self) -> bool:
        return "Land" in (self.type_line or "")

    @property
    def is_creature(self) -> bool:
        return "Creature" in (self.type_line or "")

    def get_category(self) -> str:
        """Helper para o AssetManager encontrar a pasta correta."""
        tl = (self.type_line or "").lower()
        if "land" in tl: return "Terrenos"
        if "creature" in tl: return "Criaturas"
        if "artifact" in tl: return "Artefatos"
        if "enchantment" in tl: return "Encantamentos"
        if "instant" in tl: return "Instantaneas"
        if "sorcery" in tl: return "Feiticos"
        return "Outros"