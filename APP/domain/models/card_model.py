from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict
import os

class CardModel(BaseModel):
    """
    Representa uma única carta física na mesa de jogo.
    Molde feito sob medida para o JSON do MTG Simulator.
    """
    
    # Ignora campos extras do JSON para evitar quebras
    model_config = ConfigDict(extra='ignore', populate_by_name=True)

    # =========================================================
    # 1. DADOS ESTÁTICOS (Exatamente como no seu JSON)
    # =========================================================
    name: str
    printed_name: Optional[str] = ""
    type_line: Optional[str] = "" 
    categoria: Optional[str] = ""  # Captura a categoria em português do seu JSON
    mana_cost: Optional[str] = ""
    cmc: float = 0.0  
    oracle_text: Optional[str] = ""
    
    colors: List[str] = Field(default_factory=list)
    color_identity: List[str] = Field(default_factory=list)
    produced_mana: List[str] = Field(default_factory=list)
    
    power: Optional[str] = None
    toughness: Optional[str] = None
    loyalty: Optional[str] = None
    
    # Imagens e Raridade
    image_url: Optional[str] = ""
    rarity: Optional[str] = ""
    local_image_path: Optional[str] = None
    
    is_commander: bool = False

    # =========================================================
    # 2. ESTADO DA PARTIDA (Mutável durante o jogo)
    # =========================================================
    is_tapped: bool = False
    is_face_down: bool = False
    counters: Dict[str, int] = Field(default_factory=dict) 
    summoning_sickness: bool = False
    
    # PULO DO GATO: A flag que conecta a Regra com o Visual sem misturar código!
    playable: bool = False 

    def model_post_init(self, __context):
        """Garante que criaturas entrem com enjoo de invocação."""
        if self.is_creature:
            self.summoning_sickness = True

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
    # 4. HELPERS DE TIPO (Blindados: Inglês e Português)
    # =========================================================
    @property
    def is_land(self) -> bool:
        tl = (self.type_line or "").lower()
        cat = (self.categoria or "").lower()
        return "land" in tl or "terreno" in cat or "terreno" in tl

    @property
    def is_creature(self) -> bool:
        tl = (self.type_line or "").lower()
        cat = (self.categoria or "").lower()
        return "creature" in tl or "criatura" in cat or "criatura" in tl

    @property
    def is_instant(self) -> bool:
        tl = (self.type_line or "").lower()
        cat = (self.categoria or "").lower()
        return "instant" in tl or "mágica instantânea" in cat or "instantanea" in cat

    @property
    def is_sorcery(self) -> bool:
        tl = (self.type_line or "").lower()
        cat = (self.categoria or "").lower()
        return "sorcery" in tl or "feitiço" in cat or "feitico" in cat

    @property
    def is_artifact(self) -> bool:
        tl = (self.type_line or "").lower()
        cat = (self.categoria or "").lower()
        return "artifact" in tl or "artefato" in cat

    @property
    def is_enchantment(self) -> bool:
        tl = (self.type_line or "").lower()
        cat = (self.categoria or "").lower()
        return "enchantment" in tl or "encantamento" in cat

    @property
    def is_planeswalker(self) -> bool:
        tl = (self.type_line or "").lower()
        cat = (self.categoria or "").lower()
        return "planeswalker" in tl or "planeswalker" in cat

    # =========================================================
    # 5. ASSET HELPERS
    # =========================================================
    def get_image_filename(self) -> str:
        """Extrai o nome do arquivo sem extensão."""
        if self.local_image_path:
            base = os.path.basename(self.local_image_path)
            return os.path.splitext(base)[0]
        return self.name.lower().replace(" ", "_")

    def get_category(self) -> str:
        """Retorna a categoria limpa para uso do AssetManager."""
        if self.categoria:
            return self.categoria
        if self.is_land: return "Terrenos"
        if self.is_creature: return "Criaturas"
        if self.is_artifact: return "Artefatos"
        if self.is_enchantment: return "Encantamentos"
        if self.is_instant: return "Instantaneas"
        if self.is_sorcery: return "Feiticos"
        return "Outros"
