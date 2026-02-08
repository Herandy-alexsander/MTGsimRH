from pydantic import BaseModel
from typing import List, Optional

class MTGCard(BaseModel):
    name: str
    mana_cost: Optional[str]
    type_line: str
    oracle_text: Optional[str]
    colors: List[str]
    color_identity: List[str]
    commander_legal: bool
