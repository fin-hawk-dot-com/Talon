from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union

RANKS = ["Normal", "Iron", "Bronze", "Silver", "Gold", "Diamond"]
RANK_INDICES = {rank: i for i, rank in enumerate(RANKS)}

@dataclass
class Essence:
    name: str
    type: str  # "Base" or "Confluence"
    rarity: str
    tags: List[str]
    description: str
    image_prompt: str = ""
    bonded_attribute: Optional[str] = None
    opposite: Optional[str] = None
    synergy: List[str] = field(default_factory=list)

@dataclass
class Faction:
    name: str
    description: str
    type: str
    image_prompt: str = ""
    rank_requirement: Optional[str] = None

@dataclass
class PointOfInterest:
    name: str
    description: str
    type: str  # "Landmark", "Shop", "Building", "Area"
    image_prompt: str = ""

@dataclass
class Location:
    name: str
    description: str
    type: str
    image_prompt_positive: str
    image_prompt_negative: str
    region: str = "Unknown"
    danger_rank: str = "Iron"
    connected_locations: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)
    npcs: List[str] = field(default_factory=list)
    narrative: str = ""
    points_of_interest: List[PointOfInterest] = field(default_factory=list)

@dataclass
class LoreEntry:
    id: str
    title: str
    category: str
    text: str
    image_prompt: str = ""

@dataclass
class QuestChoice:
    text: str
    next_stage_id: str
    consequence: str

@dataclass
class QuestObjective:
    type: str # "kill", "collect", "visit"
    target: str # Monster name, Item name, Location name
    count: int = 1

@dataclass
class QuestStage:
    id: str
    description: str
    choices: List[QuestChoice] = field(default_factory=list)
    objectives: List[QuestObjective] = field(default_factory=list)

@dataclass
class Quest:
    id: str
    title: str
    description: str
    stages: Dict[str, QuestStage]
    starting_stage_id: str
    rewards: List[str]
    image_prompt: str = ""
    type: str = "Side"

@dataclass
class QuestProgress:
    quest_id: str
    current_stage_id: str
    status: str = "Active"  # Active, Completed, Failed
    history: List[str] = field(default_factory=list)
    objectives_progress: Dict[str, int] = field(default_factory=dict) # key: "type:target", value: current_count

@dataclass
class AwakeningStone:
    name: str
    function: str
    description: str
    image_prompt: str = ""
    rarity: str = "Common"
    cooldown: str = "Medium"
    cost_type: str = "Mana"

@dataclass
class Ability:
    name: str
    description: str
    rank: str  # Iron, Bronze, etc.
    level: int  # 0-9 (Iron 0, Iron 1, ... Iron 9)
    parent_essence: Essence
    parent_stone: AwakeningStone
    xp: float = 0.0
    cooldown: int = 0 # Static Max Cooldown from Stone/Rank
    cost: int = 0
    current_cooldown: int = 0 # Dynamic Runtime Cooldown

    @property
    def max_xp(self) -> float:
        # Simple XP curve: 100 * (level + 1) * rank_multiplier
        rank_idx = RANK_INDICES[self.rank]
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
        # Normal: 0 - 99
        # Iron: 100 - 199
        # Bronze: 200 - 299
        # ... and so on.
        idx = int(self.value / 100)
        if idx >= len(RANKS):
            return RANKS[-1]
        return RANKS[idx]

    @property
    def rank_level(self) -> int:
        # Returns 0-9 representing progress through the rank
        val_in_rank = self.value % 100
        return int(val_in_rank / 10)

@dataclass
class Character:
    name: str
    race: str
    faction: Optional[str] = None
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
    quests: Dict[str, QuestProgress] = field(default_factory=dict)
    current_health: float = field(default=-1.0)
    current_mana: float = field(default=-1.0)
    current_stamina: float = field(default=-1.0)
    xp_reward: int = 0
    loot_table: List[str] = field(default_factory=list)
    lore: List[str] = field(default_factory=list)
    relationships: Dict[str, int] = field(default_factory=dict) # key: NPC Name, value: -100 to 100
    reputation: Dict[str, int] = field(default_factory=dict) # key: Faction Name, value: -100 to 100
    dialogue: Dict[str, str] = field(default_factory=dict) # key: trigger/status, value: text
    description: str = "" # NPC Description
    image_prompt: str = ""

    def __post_init__(self):
        if self.current_health < 0:
            self.current_health = self.max_health
        if self.current_mana < 0:
            self.current_mana = self.max_mana
        if self.current_stamina < 0:
            self.current_stamina = self.max_stamina

    @property
    def max_health(self) -> float:
        return self.attributes["Recovery"].value * 10.0

    @property
    def max_mana(self) -> float:
        return self.attributes["Spirit"].value * 10.0

    @property
    def max_stamina(self) -> float:
        return self.attributes["Recovery"].value * 10.0

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
