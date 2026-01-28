import random
from typing import List, Optional
from src.models import Character, Essence, Ability, AwakeningStone, RANK_INDICES, RANKS
from src.data_loader import DataLoader
from src.ability_templates import ABILITY_TEMPLATES, AbilityTemplate
from src.narrative import NarrativeGenerator

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
                    image_prompt=f"Abstract representation of {recipe['result']}, combining elements of {', '.join(essence_names)}.",
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
                    image_prompt=f"A pure, intense manifestation of {tag}, radiating power.",
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
                image_prompt=f"A swirling mix of energies dominated by {dominant_stat}.",
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
            image_prompt=f"A chaotic blend of essences, with {primary} being the most visible.",
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

        # Calculate Cost
        base_cost = 10
        if stone.rarity == "Uncommon": base_cost = 20
        elif stone.rarity == "Rare": base_cost = 40
        elif stone.rarity == "Epic": base_cost = 80

        # Calculate Cooldown
        base_cooldown = 2 # Rounds
        if stone.cooldown == "Short": base_cooldown = 1
        elif stone.cooldown == "Medium": base_cooldown = 3
        elif stone.cooldown == "Long": base_cooldown = 5
        elif stone.cooldown == "Very Long": base_cooldown = 8

        return Ability(
            name=name,
            description=description,
            rank=character_rank,
            level=0,
            parent_essence=essence,
            parent_stone=stone,
            cost=base_cost,
            cooldown=base_cooldown,
            current_cooldown=0
        )

class TrainingManager:
    @staticmethod
    def get_attribute_training_cost(character: Character, attribute_name: str) -> int:
        if attribute_name not in character.attributes:
            return 999999 # Should not happen

        attr = character.attributes[attribute_name]
        rank_idx = RANK_INDICES.get(attr.rank, 0)
        return 100 * (rank_idx + 1)

    @staticmethod
    def train_attribute(character: Character, attribute_name: str) -> str:
        if attribute_name not in character.attributes:
            return "Invalid attribute."

        xp_cost = TrainingManager.get_attribute_training_cost(character, attribute_name)

        if character.current_xp < xp_cost:
            return f"Not enough XP to train. Need {xp_cost}, have {character.current_xp}."

        character.current_xp -= xp_cost
        attr = character.attributes[attribute_name]
        old_rank = attr.rank

        # Diminishing returns based on rank: higher rank attributes are harder to train
        rank_idx = RANK_INDICES.get(attr.rank, 0)
        # 1.0 (Normal) -> 0.8 (Iron) -> 0.6 (Bronze) -> 0.4 (Silver) -> 0.2 (Gold) -> 0.1 (Diamond)
        diminishing_factor = max(0.1, 1.0 - (rank_idx * 0.2))

        gain = 1.0 * attr.growth_multiplier * diminishing_factor
        attr.value += gain

        narrative = NarrativeGenerator.get_training_narrative(attribute_name, attr.value)
        narrative = f"[XP -{xp_cost}] " + narrative

        new_rank = attr.rank
        if new_rank != old_rank:
            narrative += NarrativeGenerator.get_rank_up_narrative(new_rank, f"{attribute_name} Attribute")

        return narrative

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
    def can_rank_up(character: Character, ability: Ability) -> bool:
        if ability.level < 9:
            return False

        if ability.xp < ability.max_xp:
            return False

        current_rank_idx = RANK_INDICES.get(ability.rank, 0)
        char_rank_idx = RANK_INDICES.get(character.rank, 0)

        if current_rank_idx >= char_rank_idx:
            return False

        if current_rank_idx >= len(RANKS) - 1:
            return False

        return True

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

        if ability.xp < ability.max_xp:
            return "Ability XP not full."

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
