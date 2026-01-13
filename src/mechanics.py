import json
import os
import random
from typing import List, Optional
from src.models import Essence, AwakeningStone, Ability, Character, RANKS
from src.ability_templates import ABILITY_TEMPLATES, AbilityTemplate

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def load_json(filename):
    with open(os.path.join(DATA_DIR, filename), 'r') as f:
        return json.load(f)

class DataLoader:
    def __init__(self):
        self.essences_data = load_json('essences.json')
        self.confluences_data = load_json('confluences.json')
        self.stones_data = load_json('awakening_stones.json')

    def get_essence(self, name: str) -> Optional[Essence]:
        for e in self.essences_data:
            if e['name'].lower() == name.lower():
                return Essence(
                    name=e['name'],
                    type=e['type'],
                    rarity=e['rarity'],
                    tags=e['tags'],
                    description=e['description']
                )
        return None

    def get_stone(self, name: str) -> Optional[AwakeningStone]:
        for s in self.stones_data:
            if s['name'].lower() == name.lower():
                return AwakeningStone(
                    name=s['name'],
                    function=s['function'],
                    description=s['description']
                )
        return None

    def get_all_base_essences(self) -> List[str]:
        return [e['name'] for e in self.essences_data if e['type'] == 'Base']

    def get_all_stones(self) -> List[str]:
        return [s['name'] for s in self.stones_data]

class ConfluenceManager:
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader
        self.recipes = self.data_loader.confluences_data

    def determine_confluence(self, essences: List[Essence]) -> Essence:
        if len(essences) != 3:
            raise ValueError("Confluence requires exactly 3 base essences.")

        essence_names = sorted([e.name for e in essences])

        # 1. Exact Match
        for recipe in self.recipes:
            recipe_bases = sorted(recipe['bases'])
            if recipe_bases == essence_names:
                return Essence(
                    name=recipe['result'],
                    type="Confluence",
                    rarity="Rare",
                    tags=["Confluence", recipe['archetype']],
                    description=f"A confluence of {', '.join(essence_names)}."
                )

        # 2. Thematic Dominance (Tag Matching)
        tag_counts = {}
        for e in essences:
            for tag in e.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        for tag, count in tag_counts.items():
            if count == 3:
                return Essence(
                    name=f"True {tag}",
                    type="Confluence",
                    rarity="Epic",
                    tags=[tag, "Pure"],
                    description=f"A pure manifestation of the {tag} aspect."
                )

        # 3. Fallback
        bonded_counts = {}
        for e in essences:
            if e.bonded_attribute:
                bonded_counts[e.bonded_attribute] = bonded_counts.get(e.bonded_attribute, 0) + 1

        if bonded_counts:
            dominant_stat = sorted(bonded_counts.items(), key=lambda item: item[1], reverse=True)[0][0]
            name_suffix = "Hybrid"
            if dominant_stat == "Power":
                name_suffix = "Force"
            elif dominant_stat == "Speed":
                name_suffix = "Velocity"
            elif dominant_stat == "Spirit":
                name_suffix = "Mystic"
            elif dominant_stat == "Recovery":
                name_suffix = "Vitality"

            return Essence(
                name=f"{name_suffix} Confluence",
                type="Confluence",
                rarity="Common",
                tags=["Hybrid", dominant_stat],
                description=f"A generic confluence based on {dominant_stat}."
            )

        primary = essences[0].name
        return Essence(
            name=f"{primary} Hybrid",
            type="Confluence",
            rarity="Common",
            tags=["Hybrid"],
            description=f"A hybrid confluence dominated by {primary}."
        )

class AbilityGenerator:
    def generate(self, essence: Essence, stone: AwakeningStone, character_rank: str = "Iron", affinity: str = "General") -> Ability:
        candidates = []

        for tmpl in ABILITY_TEMPLATES:
            # 1. Function match
            if tmpl.function != stone.function:
                continue

            # 2. Tag Match (Essence must have all tags required by template)
            if tmpl.essence_tags:
                if not all(tag in essence.tags for tag in tmpl.essence_tags):
                    continue

            candidates.append(tmpl)

        selected_template = None

        if not candidates:
            # Fallback if no specific template matches
            selected_template = AbilityTemplate(
                pattern="{essence} " + stone.function.split(' ')[0], # Simple fallback
                function=stone.function,
                description_template=f"Uses {essence.name} to perform {stone.function}.",
                affinity_weight={"General": 1.0}
            )
        else:
            # Weighted Random Selection
            weights = []
            for c in candidates:
                w = c.affinity_weight.get(affinity, c.affinity_weight.get("General", 1.0))
                weights.append(w)

            selected_template = random.choices(candidates, weights=weights, k=1)[0]

        name = selected_template.pattern.format(essence=essence.name)
        description = selected_template.description_template.format(essence=essence.name)

        return Ability(
            name=name,
            description=description,
            rank=character_rank,
            level=0,
            parent_essence=essence,
            parent_stone=stone
        )

class TrainingManager:
    @staticmethod
    def train_attribute(character: Character, attribute_name: str):
        if attribute_name not in character.attributes:
            return

        attr = character.attributes[attribute_name]

        # Growth is slower as you rank up relative to the stat value
        # But here we use a simple linear gain multiplied by the growth multiplier
        gain = 1.0 * attr.growth_multiplier

        # Optional: Diminishing returns based on rank?
        # For now, keep it simple.
        attr.value += gain

    @staticmethod
    def practice_ability(character: Character, essence_name: str, slot_index: int):
        if essence_name not in character.abilities:
            return

        abilities = character.abilities[essence_name]
        if slot_index < 0 or slot_index >= len(abilities):
            return

        ability = abilities[slot_index]
        if not ability:
            return

        # Gain XP
        xp_gain = 10.0 # Base XP per practice
        leveled_up = ability.gain_xp(xp_gain)

        return leveled_up

    @staticmethod
    def attempt_rank_up_ability(character: Character, essence_name: str, slot_index: int) -> str:
        """
        Attempts to rank up an ability (e.g., Iron -> Bronze).
        Requires Ability to be at max level (9) and XP full (technically handled by cap).
        And Character Rank must be higher than Ability Rank (can't have Bronze ability in Iron body typically,
        unless using special items, but we stick to standard rules).
        """
        abilities = character.abilities.get(essence_name)
        if not abilities: return "Essence not found."

        ability = abilities[slot_index]
        if not ability: return "No ability in slot."

        if ability.level < 9:
            return "Ability not at max level (9)."

        current_rank_idx = RANKS.index(ability.rank)
        char_rank_idx = RANKS.index(character.rank)

        if current_rank_idx >= char_rank_idx:
            return f"Character Rank ({character.rank}) is not high enough to support higher rank ability."

        if current_rank_idx >= len(RANKS) - 1:
            return "Already at max rank."

        # Perform Rank Up
        ability.rank = RANKS[current_rank_idx + 1]
        ability.level = 0
        ability.xp = 0
        return f"Success! Ability ranked up to {ability.rank}."
