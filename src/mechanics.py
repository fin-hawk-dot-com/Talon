import json
import os
import random
from typing import List, Optional, Union
from src.models import Essence, AwakeningStone, Ability, Character, RANKS

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
    def generate(self, essence: Essence, stone: AwakeningStone, rank: str = "Iron") -> Ability:
        name_templates = {
            "Melee Attack": "{essence} Strike",
            "Ranged Attack": "{essence} Bolt",
            "Defense": "{essence} Shield",
            "Area Denial": "{essence} Trap",
            "Summoning": "Summon {essence} Spirit",
            "Multi-Hit": "{essence} Swarm",
            "Drain/Sustain": "Feast of {essence}",
            "Body Mod": "{essence} Form",
            "Celestial/Augment": "Avatar of {essence}",
            "Mobility": "{essence} Step",
            "Replication": "{essence} Clone",
            "Terrain Control": "Wall of {essence}",
            "Perception": "{essence} Sight",
            "Execute": "{essence} Execution"
        }

        desc_templates = {
            "Melee Attack": "Strikes the enemy with physical force imbued with {essence}.",
            "Ranged Attack": "Fires a bolt of {essence} energy at the target.",
            "Defense": "Surrounds the user in a protective layer of {essence}.",
            "Area Denial": "Sets a trap that releases {essence} when triggered.",
            "Summoning": "Summons a creature made of {essence}.",
            "Multi-Hit": "Unleashes a flurry of {essence} projectiles.",
            "Drain/Sustain": "Drains energy from the target to fuel {essence}.",
            "Body Mod": "Transforms the user's body to take on properties of {essence}.",
            "Celestial/Augment": "Channels the power of {essence} to greatly enhance stats.",
            "Mobility": "Uses {essence} to move instantly or at great speed.",
            "Replication": "Creates an illusory copy made of {essence}.",
            "Terrain Control": "Raises a wall of {essence} to block movement.",
            "Perception": "Allows the user to sense {essence} and hidden things.",
            "Execute": "Delivers a fatal blow using the power of {essence}."
        }

        func = stone.function
        template_name = name_templates.get(func, "{essence} Ability")
        template_desc = desc_templates.get(func, "Uses {essence} to perform {function}.")

        name = template_name.format(essence=essence.name, function=func)
        description = template_desc.format(essence=essence.name, function=func)

        return Ability(
            name=name,
            description=description,
            rank=rank,
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
