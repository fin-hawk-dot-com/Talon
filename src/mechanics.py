import json
import os
import random
from typing import List, Optional, Tuple
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
    def __init__(self):
        self.templates = ABILITY_TEMPLATES

    def generate(self, essence: Essence, stone: AwakeningStone, rank: str = "Iron", focus: Optional[str] = None) -> Ability:
        """
        Generates an ability based on Essence, Stone, and optional Focus.
        Uses a weighted random selection process to simulate 'magic' influenced by 'focus'.
        """

        valid_templates = []

        for tmpl in self.templates:
            # Check Stone Function Match
            if tmpl.required_stone_function != stone.function:
                continue

            # Check Essence Tag Match (if template has requirements)
            if tmpl.required_essence_tags:
                # Must match at least one of the required tags (or all? Usually ANY is flexible, ALL is specific)
                # Let's assume ANY for now to allow "Elemental" template to match Fire or Water
                # But my templates currently have specific lists like ["Fire"].
                # Let's check if the essence has ALL the required tags from the template to be a candidate?
                # Actually, usually specific templates require specific tags.
                # Example: Template requires ["Fire"]. Essence must have "Fire".

                # If template has ["Fire", "Melee"], Essence needs both? No, "Melee" is likely a tag added BY the template.
                # The `required_essence_tags` in AbilityTemplate definition was:
                # "required_essence_tags: List[str] # Empty list means "Generic""

                has_all_requirements = True
                for req_tag in tmpl.required_essence_tags:
                    if req_tag not in essence.tags:
                        has_all_requirements = False
                        break

                if not has_all_requirements:
                    continue

            valid_templates.append(tmpl)

        if not valid_templates:
            # Fallback to a basic generic generation if no templates match
            # This shouldn't happen with good Generic templates, but safety first.
            return self._generate_fallback(essence, stone, rank)

        # Calculate Weights
        weights = []
        for tmpl in valid_templates:
            w = tmpl.weight

            # Influence: Attribute Focus
            if focus and tmpl.affinity == focus:
                w *= 3.0  # Significant boost for matching focus

            # Influence: Tag Matching Specificity
            # Reward templates that match more specific tags of the essence
            # e.g. "Fire" template is better for Fire essence than "Generic" template
            if tmpl.required_essence_tags:
                w *= 2.0 # Specific templates are more likely than generic ones usually

            weights.append(w)

        # Select one
        selected_template = random.choices(valid_templates, weights=weights, k=1)[0]

        # Manifest the Ability
        name = selected_template.name_pattern.format(essence=essence.name, function=stone.function)
        description = selected_template.description_pattern.format(essence=essence.name, function=stone.function)

        return Ability(
            name=name,
            description=description,
            rank=rank,
            level=0,
            parent_essence=essence,
            parent_stone=stone,
            tags=selected_template.tags,
            affinity=selected_template.affinity
        )

    def _generate_fallback(self, essence: Essence, stone: AwakeningStone, rank: str) -> Ability:
        name = f"{essence.name} {stone.function}"
        description = f"Uses {essence.name} to perform {stone.function}."
        return Ability(
            name=name,
            description=description,
            rank=rank,
            level=0,
            parent_essence=essence,
            parent_stone=stone
        )

class TrainingManager:
    def __init__(self, data_loader: DataLoader):
        self.ability_generator = AbilityGenerator()
        self.data_loader = data_loader

    def awaken_ability(self, character: Character, essence_name: str, stone_name: str, slot_index: int, focus: Optional[str] = None) -> Ability:
        """
        Attempts to awaken an ability for the character.
        """
        # validations
        essence = next((e for e in character.get_all_essences() if e.name == essence_name), None)
        if not essence:
            raise ValueError(f"Character does not possess essence {essence_name}")

        stone = self.data_loader.get_stone(stone_name)
        if not stone:
             raise ValueError(f"Stone {stone_name} not found")

        if slot_index < 0 or slot_index >= 5:
            raise ValueError("Slot index must be between 0 and 4")

        if character.abilities[essence_name][slot_index] is not None:
             raise ValueError("Slot is already occupied")

        # Generate
        ability = self.ability_generator.generate(essence, stone, character.rank, focus)

        # Assign
        character.abilities[essence_name][slot_index] = ability

        return ability

    def train_attribute(self, character: Character, attribute_name: str):
        if attribute_name not in character.attributes:
            return

        attr = character.attributes[attribute_name]

        # Growth is slower as you rank up relative to the stat value
        # But here we use a simple linear gain multiplied by the growth multiplier
        gain = 1.0 * attr.growth_multiplier

        # Optional: Diminishing returns based on rank?
        # For now, keep it simple.
        attr.value += gain

    def practice_ability(self, character: Character, essence_name: str, slot_index: int):
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

    def attempt_rank_up_ability(self, character: Character, essence_name: str, slot_index: int) -> str:
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
