import json
import os
import random
from typing import List, Optional
from src.models import Essence, AwakeningStone, Ability, Character

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
        # If not found in basic list, check if it is a result of a confluence recipe (dynamic creation)
        # For now, return None if not found in base list
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
                    rarity="Rare", # Defaulting for generated
                    tags=["Confluence", recipe['archetype']], # Adding archetype as tag
                    description=f"A confluence of {', '.join(essence_names)}."
                )

        # 2. Thematic Dominance (Tag Matching)
        # Count all tags
        tag_counts = {}
        for e in essences:
            for tag in e.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        # If any tag appears 3 times, generate a confluence based on that tag
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
        # Generate a name based on the majority bonded attribute bias if available, else first essence
        # Count bonded attributes
        bonded_counts = {}
        for e in essences:
            if e.bonded_attribute:
                bonded_counts[e.bonded_attribute] = bonded_counts.get(e.bonded_attribute, 0) + 1

        # Sort by count
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

        # Ultimate Fallback
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
        # Simple template-based generation

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
