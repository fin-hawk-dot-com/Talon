from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union

RANKS = ["Iron", "Bronze", "Silver", "Gold", "Diamond"]

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
    level: int  # 0-9 (Iron 0, Iron 1, ... Iron 9)
    parent_essence: Essence
    parent_stone: AwakeningStone
    xp: float = 0.0
    cooldown: int = 0
    cost: int = 0

    @property
    def max_xp(self) -> float:
        # Simple XP curve: 100 * (level + 1) * rank_multiplier
        rank_idx = RANKS.index(self.rank)
        return 100.0 * (self.level + 1) * (rank_idx + 1)

    def gain_xp(self, amount: float) -> bool:
        """Returns True if leveled up. Can handle multiple level ups."""
        self.xp += amount
        leveled_up = False
        while self.xp >= self.max_xp:
            self.xp -= self.max_xp
            if self.level_up():
                leveled_up = True
            else:
                # Cap reached
                break
        return leveled_up

    def level_up(self) -> bool:
        """Increments level. Returns True if leveled up.
        Does not handle Rank Up automatically (needs external logic/check).
        """
        if self.level < 9:
            self.level += 1
            return True
        return False

@dataclass
class Attribute:
    name: str
    value: float
    growth_multiplier: float = 1.0

    @property
    def rank(self) -> str:
        # 0-99: Iron, 100-199: Bronze, etc.
        idx = int(self.value / 100)
        if idx >= len(RANKS):
            return RANKS[-1]
        return RANKS[idx]

    @property
    def rank_level(self) -> int:
        # Returns 0-99 representing progress through the rank
        # Or maybe 0-9 to match the book style (Iron 1, Iron 2... Iron 9)
        # Let's say every 10 points is a sub-rank.
        val_in_rank = self.value % 100
        return int(val_in_rank / 10)

@dataclass
class Character:
    name: str
    race: str
    affinity: str = "General"  # Warrior, Mage, Rogue, Guardian, Support, General
    attributes: Dict[str, Attribute] = field(default_factory=lambda: {
        "Power": Attribute("Power", 10.0),
        "Speed": Attribute("Speed", 10.0),
        "Spirit": Attribute("Spirit", 10.0),
        "Recovery": Attribute("Recovery", 10.0)
    })
    base_essences: List[Essence] = field(default_factory=list)
    confluence_essence: Optional[Essence] = None
    abilities: Dict[str, List[Optional[Ability]]] = field(default_factory=dict)
    inventory: List[Union[Essence, AwakeningStone]] = field(default_factory=list)

    @property
    def rank(self) -> str:
        # Character rank is the lowest rank of their attributes
        min_val = min(attr.value for attr in self.attributes.values())
        idx = int(min_val / 100)
        if idx >= len(RANKS):
            return RANKS[-1]
        return RANKS[idx]

    def add_essence(self, essence: Essence, bond_attribute: str):
        if len(self.base_essences) >= 3 and essence.type == "Base":
            raise ValueError("Cannot have more than 3 Base Essences.")

        essence.bonded_attribute = bond_attribute
        if essence.type == "Base":
            self.base_essences.append(essence)
        elif essence.type == "Confluence":
            self.confluence_essence = essence

        # Initialize ability slots for this essence if not present
        if essence.name not in self.abilities:
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

        # Multipliers based on number of bonds
        multipliers = {0: 1.0, 1: 1.2, 2: 1.5, 3: 2.0, 4: 3.0}
        self.attributes[attribute_name].growth_multiplier = multipliers.get(count, 3.0)

    def get_all_essences(self) -> List[Essence]:
        essences = self.base_essences[:]
        if self.confluence_essence:
            essences.append(self.confluence_essence)
        return essences
