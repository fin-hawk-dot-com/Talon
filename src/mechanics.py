import json
import os
import random
from typing import List, Optional, Union
from src.models import Essence, AwakeningStone, Ability, Character, Faction, Attribute, RANKS, RANK_INDICES
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
        self.factions_data = load_json('factions.json')
        self.characters_data = load_json('characters.json')
        # Optimization: Pre-compute dictionary for O(1) lookup
        self.stones_map = {s['name'].lower(): s for s in self.stones_data}

        # Performance optimization: Create O(1) lookup maps
        self.essences_map = {e['name'].lower(): e for e in self.essences_data}
        self.stones_map = {s['name'].lower(): s for s in self.stones_data}
        self.factions_map = {f['name'].lower(): f for f in self.factions_data}

    def get_essence(self, name: str) -> Optional[Essence]:
        e = self.essences_map.get(name.lower())
        if e:
            return Essence(
                name=e['name'],
                type=e['type'],
                rarity=e['rarity'],
                tags=e['tags'],
                description=e['description'],
                opposite=e.get('opposite'),
                synergy=e.get('synergy', [])
            )
        return None

    def get_stone(self, name: str) -> Optional[AwakeningStone]:
        s = self.stones_map.get(name.lower())
        if s:
            return AwakeningStone(
                name=s['name'],
                function=s['function'],
                description=s['description'],
                rarity=s.get('rarity', "Common"),
                cooldown=s.get('cooldown', "Medium"),
                cost_type=s.get('cost_type', "Mana")
            )
        return None

    def get_faction(self, name: str) -> Optional[Faction]:
        f = self.factions_map.get(name.lower())
        if f:
            return Faction(
                name=f['name'],
                description=f['description'],
                type=f['type'],
                rank_requirement=f.get('rank_requirement')
            )
        return None

    def get_all_factions(self) -> List[Faction]:
        return [
            Faction(
                name=f['name'],
                description=f['description'],
                type=f['type'],
                rank_requirement=f.get('rank_requirement')
            ) for f in self.factions_data
        ]

    def get_character_template(self, name: str) -> Optional[Character]:
        """Loads a pre-defined character. Note: Does not instantiate abilities fully yet."""
        for c in self.characters_data:
            if c['name'].lower() == name.lower():
                char = Character(
                    name=c['name'],
                    race=c['race'],
                    faction=c.get('faction'),
                    affinity=c.get('affinity', 'General')
                )

                # Load Attributes
                if 'attributes' in c:
                    for attr_name, value in c['attributes'].items():
                        if attr_name in char.attributes:
                            char.attributes[attr_name].value = value

                # Load Base Essences
                # We need to assign them to attributes. For simplicity, we might just assign them sequentially to Power, Speed, Spirit for now
                # Or we need the data to specify it. The data I created doesn't specify bonded attribute.
                # I will assign them arbitrarily to Power, Speed, Spirit for now since the JSON didn't specify.
                # Wait, if I want to be robust, I should update the JSON to include bonded attribute info,
                # or just assign them round-robin.

                attributes = ["Power", "Speed", "Spirit", "Recovery"]

                for i, ess_name in enumerate(c.get('base_essences', [])):
                    essence = self.get_essence(ess_name)
                    if essence:
                        # Auto-bond
                        bonded_attr = attributes[i % 4]
                        try:
                            char.add_essence(essence, bonded_attr)
                        except ValueError:
                            pass # Ignore if too many or whatever

                # Load Confluence
                conf_name = c.get('confluence_essence')
                if conf_name:
                    # We need to construct the confluence essence.
                    # If it's a known one, we can try to find it in recipes or just make a placeholder?
                    # Ideally we find it in recipes.
                    # Or simpler: create a dummy confluence essence object if not found.
                    # But wait, `get_essence` searches `essences.json` which are base essences usually.
                    # Confluences are dynamically generated or in `confluences.json`.
                    # Let's try to simulate finding it.

                    # Search recipes to see if we can reconstruct it?
                    # Or maybe I should have put confluence essences in `essences.json`? No, they are generated.
                    # I'll create a generic loader for confluence if I can.

                    # For now, let's just make a basic object.
                    conf_essence = Essence(
                         name=conf_name,
                         type="Confluence",
                         rarity="Rare",
                         tags=["Confluence"],
                         description=f"Pre-defined confluence: {conf_name}"
                    )
                    char.confluence_essence = conf_essence
                    # Also need to bond it.
                    char.confluence_essence.bonded_attribute = "Recovery" # Arbitrary
                    char._update_growth_multiplier("Recovery")
                    if conf_name not in char.abilities:
                         char.abilities[conf_name] = [None] * 5

                return char
        return None

    def get_all_base_essences(self) -> List[str]:
        return [e['name'] for e in self.essences_data if e['type'] == 'Base']

    def get_all_stones(self) -> List[str]:
        return [s['name'] for s in self.stones_data]

class ConfluenceManager:
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader
        self.recipes = self.data_loader.confluences_data
        for recipe in self.recipes:
            recipe['bases'] = sorted(recipe['bases'])

    def determine_confluence(self, essences: List[Essence]) -> Essence:
        if len(essences) != 3:
            raise ValueError("Confluence requires exactly 3 base essences.")

        essence_names = sorted([e.name for e in essences])

        # 1. Exact Match
        for recipe in self.recipes:
            if recipe['bases'] == essence_names:
                return Essence(
                    name=recipe['result'],
                    type="Confluence",
                    rarity="Rare",
                    tags=["Confluence", recipe['archetype']],
                    description=f"A confluence of {', '.join(essence_names)}.",
                    opposite=None,
                    synergy=[]
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
                    description=f"A pure manifestation of the {tag} aspect.",
                    opposite=None,
                    synergy=[]
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
                description=f"A generic confluence based on {dominant_stat}.",
                opposite=None,
                synergy=[]
            )

        primary = essences[0].name
        return Essence(
            name=f"{primary} Hybrid",
            type="Confluence",
            rarity="Common",
            tags=["Hybrid"],
            description=f"A hybrid confluence dominated by {primary}.",
            opposite=None,
            synergy=[]
        )

class AbilityGenerator:
    def generate(self, essence: Essence, stone: AwakeningStone, character_rank: str = "Iron", affinity: str = "General") -> Ability:
        candidates = []

        essence_tags_set = set(essence.tags)
        for tmpl in ABILITY_TEMPLATES:
            # 1. Function match
            if tmpl.function != stone.function:
                continue

            # 2. Tag Match (Essence must have all tags required by template)
            if tmpl.essence_tags:
                if not all(tag in essence_tags_set for tag in tmpl.essence_tags):
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

        current_rank_idx = RANK_INDICES[ability.rank]
        char_rank_idx = RANK_INDICES[character.rank]

        if current_rank_idx >= char_rank_idx:
            return f"Character Rank ({character.rank}) is not high enough to support higher rank ability."

        if current_rank_idx >= len(RANKS) - 1:
            return "Already at max rank."

        # Perform Rank Up
        ability.rank = RANKS[current_rank_idx + 1]
        ability.level = 0
        ability.xp = 0
        return f"Success! Ability ranked up to {ability.rank}."

class LootManager:
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader

    def generate_random_loot(self) -> Optional[Union[Essence, AwakeningStone]]:
        """Generates a random Essence or Awakening Stone."""
        roll = random.random()
        if roll < 0.3: # 30% chance for Essence
            essences = self.data_loader.get_all_base_essences()
            if not essences: return None
            name = random.choice(essences)
            return self.data_loader.get_essence(name)
        elif roll < 0.6: # 30% chance for Stone
            stones = self.data_loader.get_all_stones()
            if not stones: return None
            name = random.choice(stones)
            return self.data_loader.get_stone(name)
        else:
            return None # 40% chance for nothing

class GameEngine:
    def __init__(self):
        self.data_loader = DataLoader()
        self.confluence_mgr = ConfluenceManager(self.data_loader)
        self.ability_gen = AbilityGenerator()
        self.training_mgr = TrainingManager()
        self.loot_mgr = LootManager(self.data_loader)
        self.character = None

    def create_character(self, name: str, race: str):
        self.character = Character(name=name, race=race)
        return self.character

    def absorb_essence(self, essence_index: int, attribute: str) -> str:
        if not self.character: return "No character."
        if essence_index < 0 or essence_index >= len(self.character.inventory):
            return "Invalid inventory index."

        item = self.character.inventory[essence_index]
        if not isinstance(item, Essence):
            return "That is not an Essence."

        try:
            self.character.add_essence(item, attribute)
            self.character.inventory.pop(essence_index)

            # Check for Confluence
            if len(self.character.base_essences) == 3 and not self.character.confluence_essence:
                confluence = self.confluence_mgr.determine_confluence(self.character.base_essences)
                # Auto-add confluence or let user choose? Spec says 3+1. Let's auto-add for now, but user needs to pick attribute.
                # Actually, wait. Confluence usually manifests automatically. But it also needs a bonded attribute.
                # For simplicity, let's just add it to inventory so user can bond it manually.
                self.character.inventory.append(confluence)
                return f"Absorbed {item.name}. A Confluence Essence has manifested in your inventory!"

            return f"Absorbed {item.name}."
        except ValueError as e:
            return str(e)

    def awaken_ability(self, essence_name: str, stone_index: int, slot_index: int) -> str:
        if not self.character: return "No character."

        # Validate Stone
        if stone_index < 0 or stone_index >= len(self.character.inventory):
            return "Invalid inventory index."
        stone = self.character.inventory[stone_index]
        if not isinstance(stone, AwakeningStone):
            return "That is not an Awakening Stone."

        # Validate Essence
        if essence_name not in self.character.abilities:
            return "You do not have that Essence bonded."

        # Validate Slot
        slots = self.character.abilities[essence_name]
        if slot_index < 0 or slot_index >= 5:
            return "Invalid slot index (0-4)."
        if slots[slot_index] is not None:
            return "Slot is already occupied."

        # Find the essence object
        essence = next((e for e in self.character.get_all_essences() if e.name == essence_name), None)
        if not essence:
            return "Essence data not found."

        # Generate Ability
        ability = self.ability_gen.generate(essence, stone, self.character.rank)
        self.character.abilities[essence_name][slot_index] = ability

        # Remove stone
        self.character.inventory.pop(stone_index)

        return f"Awakened {ability.name}!"
