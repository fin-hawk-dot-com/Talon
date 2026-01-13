from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class Essence:
    name: str
    type: str  # "Base" or "Confluence"
    rarity: str
    tags: List[str]
    description: str
    bonded_attribute: Optional[str] = None

@dataclass
class AwakeningStone:
    name: str
    function: str
    description: str

@dataclass
class Ability:
    name: str
    description: str
    rank: str  # Iron, Bronze, etc.
    level: int  # 0-9
    parent_essence: Essence
    parent_stone: AwakeningStone
    cooldown: int = 0
    cost: int = 0
    tags: List[str] = field(default_factory=list)
    affinity: Optional[str] = None

@dataclass
class Attribute:
    name: str
    value: float
    growth_multiplier: float = 1.0

@dataclass
class Character:
    name: str
    race: str
    rank: str = "Iron"
    attributes: Dict[str, Attribute] = field(default_factory=lambda: {
        "Power": Attribute("Power", 10.0),
        "Speed": Attribute("Speed", 10.0),
        "Spirit": Attribute("Spirit", 10.0),
        "Recovery": Attribute("Recovery", 10.0)
    })
    base_essences: List[Essence] = field(default_factory=list)
    confluence_essence: Optional[Essence] = None
    abilities: Dict[str, List[Optional[Ability]]] = field(default_factory=dict)

    def add_essence(self, essence: Essence, bond_attribute: str):
        if len(self.base_essences) >= 3 and essence.type == "Base":
            raise ValueError("Cannot have more than 3 Base Essences.")

        essence.bonded_attribute = bond_attribute
        if essence.type == "Base":
            self.base_essences.append(essence)
        elif essence.type == "Confluence":
            self.confluence_essence = essence

        # Initialize ability slots for this essence
        self.abilities[essence.name] = [None] * 5

        # Update growth multiplier
        self._update_growth_multiplier(bond_attribute)

    def _update_growth_multiplier(self, attribute_name: str):
        # Count how many essences are bonded to this attribute
        count = 0
        for e in self.base_essences:
            if e.bonded_attribute == attribute_name:
                count += 1
        if self.confluence_essence and self.confluence_essence.bonded_attribute == attribute_name:
            count += 1

        multipliers = {0: 1.0, 1: 1.2, 2: 1.5, 3: 2.0, 4: 3.0}
        self.attributes[attribute_name].growth_multiplier = multipliers.get(count, 3.0)

    def get_all_essences(self) -> List[Essence]:
        essences = self.base_essences[:]
        if self.confluence_essence:
            essences.append(self.confluence_essence)
        return essences
