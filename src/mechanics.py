import json
import os
import random
from dataclasses import asdict
from typing import List, Optional, Union, Dict
from src.models import Essence, AwakeningStone, Ability, Character, Faction, Attribute, RANKS, RANK_INDICES, Quest, QuestStage, QuestProgress, QuestChoice, QuestObjective, Location, LoreEntry
from src.ability_templates import ABILITY_TEMPLATES, AbilityTemplate
import dataclasses

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def load_json(filename):
    with open(os.path.join(DATA_DIR, filename), 'r') as f:
        return json.load(f)

class DataLoader:
    _cache = {}

    def __init__(self):
        if not DataLoader._cache:
            DataLoader._cache['essences'] = load_json('essences.json')
            DataLoader._cache['confluences'] = load_json('confluences.json')
            DataLoader._cache['stones'] = load_json('awakening_stones.json')
            DataLoader._cache['factions'] = load_json('factions.json')
            DataLoader._cache['characters'] = load_json('characters.json')
            DataLoader._cache['quests'] = load_json('quests.json')
            DataLoader._cache['locations'] = load_json('locations.json')
            DataLoader._cache['monsters'] = load_json('monsters.json')
            DataLoader._cache['lore'] = load_json('lore.json')

        self.essences_data = DataLoader._cache['essences']
        self.confluences_data = DataLoader._cache['confluences']
        self.stones_data = DataLoader._cache['stones']
        self.factions_data = DataLoader._cache['factions']
        self.characters_data = DataLoader._cache['characters']
        self.quests_data = DataLoader._cache['quests']
        self.locations_data = DataLoader._cache['locations']
        self.monsters_data = DataLoader._cache['monsters']
        self.lore_data = DataLoader._cache['lore']

        # Optimization: Pre-compute dictionary for O(1) lookup
        self.stones_map = {s['name'].lower(): s for s in self.stones_data}

        # Performance optimization: Create O(1) lookup maps
        self.essences_map = {e['name'].lower(): e for e in self.essences_data}
        self.stones_map = {s['name'].lower(): s for s in self.stones_data}
        self.characters_map = {c['name'].lower(): c for c in self.characters_data}
        self.factions_map = {f['name'].lower(): f for f in self.factions_data}
        self.quests_map = {q['id']: q for q in self.quests_data}
        self.locations_map = {l['name'].lower(): l for l in self.locations_data}
        self.monsters_map = {m['name'].lower(): m for m in self.monsters_data}
        self.lore_map = {l['title'].lower(): l for l in self.lore_data}
        self.lore_id_map = {l['id']: l for l in self.lore_data}

    def get_lore(self, identifier: str) -> Optional[LoreEntry]:
        # Try ID first
        l = self.lore_id_map.get(identifier)
        if not l:
            # Try Title
            l = self.lore_map.get(identifier.lower())

        if l:
            return LoreEntry(
                id=l['id'],
                title=l['title'],
                category=l['category'],
                text=l['text']
            )
        return None

    def get_all_lore(self) -> List[LoreEntry]:
        return [
            LoreEntry(id=l['id'], title=l['title'], category=l['category'], text=l['text'])
            for l in self.lore_data
        ]

    def get_quest(self, quest_id: str) -> Optional[Quest]:
        q = self.quests_map.get(quest_id)
        if q:
            stages = {}
            for stage_id, stage_data in q['stages'].items():
                choices = []
                for choice in stage_data.get('choices', []):
                    choices.append(QuestChoice(
                        text=choice['text'],
                        next_stage_id=choice['next_stage_id'],
                        consequence=choice.get('consequence', '')
                    ))

                objectives = []
                for obj in stage_data.get('objectives', []):
                    objectives.append(QuestObjective(
                        type=obj['type'],
                        target=obj['target'],
                        count=obj.get('count', 1)
                    ))

                stages[stage_id] = QuestStage(
                    id=stage_data['id'],
                    description=stage_data['description'],
                    choices=choices,
                    objectives=objectives
                )

            return Quest(
                id=q['id'],
                title=q['title'],
                description=q['description'],
                stages=stages,
                starting_stage_id=q['starting_stage_id'],
                rewards=q.get('rewards', []),
                type=q.get('type', 'Side')
            )
        return None

    def get_all_quests(self) -> List[Quest]:
        quests = []
        for q_data in self.quests_data:
             quests.append(self.get_quest(q_data['id']))
        return quests

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

    def get_location(self, name: str) -> Optional[Location]:
        l = self.locations_map.get(name.lower())
        if l:
            return Location(
                name=l['name'],
                description=l['description'],
                type=l['type'],
                image_prompt_positive=l['image_prompt_positive'],
                image_prompt_negative=l['image_prompt_negative'],
                region=l.get('region', "Unknown"),
                danger_rank=l.get('danger_rank', "Iron"),
                connected_locations=l.get('connected_locations', []),
                resources=l.get('resources', []),
                npcs=l.get('npcs', [])
            )
        return None

    def get_all_locations(self) -> List[Location]:
        return [
            Location(
                name=l['name'],
                description=l['description'],
                type=l['type'],
                image_prompt_positive=l['image_prompt_positive'],
                image_prompt_negative=l['image_prompt_negative'],
                region=l.get('region', "Unknown"),
                danger_rank=l.get('danger_rank', "Iron"),
                connected_locations=l.get('connected_locations', []),
                resources=l.get('resources', []),
                npcs=l.get('npcs', [])
            ) for l in self.locations_data
        ]

    def get_character_template(self, name: str) -> Optional[Character]:
        """Loads a pre-defined character. Note: Does not instantiate abilities fully yet."""
        c = self.characters_map.get(name.lower())
        if c:
            char = Character(
                name=c['name'],
                race=c['race'],
                faction=c.get('faction'),
                affinity=c.get('affinity', 'General'),
                description=c.get('description', ""),
                dialogue=c.get('dialogue', {})
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

    def get_monster(self, name: str) -> Optional[Character]:
        m = self.monsters_map.get(name.lower())
        if m:
            char = Character(
                name=m['name'],
                race=m['race'],
                xp_reward=m.get('xp_reward', 0),
                loot_table=m.get('loot_table', [])
            )
            if 'attributes' in m:
                for attr_name, value in m['attributes'].items():
                    if attr_name in char.attributes:
                        char.attributes[attr_name].value = value
            # Recalculate health
            char.current_health = char.max_health
            return char
        return None

    def get_all_monsters(self) -> List[str]:
        return [m['name'] for m in self.monsters_data]

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

    def _generate_fallback(self, essence: Essence, stone: AwakeningStone, rank: str) -> Ability:
        name = f"{essence.name} {stone.function}"
        description = f"Uses {essence.name} to perform {stone.function}."
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

class QuestManager:
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader

    def get_available_quests(self, character: Character) -> List[Quest]:
        # Return quests that are not started or completed
        all_quests = self.data_loader.get_all_quests()
        available = []
        for q in all_quests:
            if q.id not in character.quests:
                available.append(q)
        return available

    def start_quest(self, character: Character, quest_id: str) -> str:
        if quest_id in character.quests:
            return "Quest already started."

        quest = self.data_loader.get_quest(quest_id)
        if not quest:
            return "Quest not found."

        character.quests[quest_id] = QuestProgress(
            quest_id=quest_id,
            current_stage_id=quest.starting_stage_id,
            status="Active"
        )
        return f"Started quest: {quest.title}"

    def get_quest_status(self, character: Character, quest_id: str) -> str:
        if quest_id not in character.quests:
            return "Not Started"
        return character.quests[quest_id].status

    def make_choice(self, character: Character, quest_id: str, choice_index: int) -> str:
        if quest_id not in character.quests:
            return "Quest not active."

        progress = character.quests[quest_id]
        if progress.status != "Active":
            return f"Quest is {progress.status}."

        quest = self.data_loader.get_quest(quest_id)
        current_stage = quest.stages.get(progress.current_stage_id)

        if not current_stage:
            return "Invalid stage data."

        if choice_index < 0 or choice_index >= len(current_stage.choices):
            return "Invalid choice."

        choice = current_stage.choices[choice_index]

        # Apply consequence (Logic for rewards could go here)
        result_text = choice.consequence

        # Move to next stage
        progress.history.append(progress.current_stage_id)

        if choice.next_stage_id == "COMPLETED":
            progress.status = "Completed"
            progress.current_stage_id = "COMPLETED"
            # Grant rewards
            if quest.rewards:
                 result_text += f"\nRewards: {', '.join(quest.rewards)}"
                 # Logic to actually give items would go here.
                 # For now, we assume simple text feedback or maybe hook into LootManager if we want to be fancy.
                 # Let's try to give rewards if possible.
                 self._grant_rewards(character, quest.rewards)

        else:
            progress.current_stage_id = choice.next_stage_id

        return result_text

    def check_objectives(self, character: Character, event_type: str, target: str) -> List[str]:
        """Updates quest objectives based on events (e.g. kill, collect)."""
        notifications = []
        for q_id, progress in character.quests.items():
            if progress.status != "Active": continue

            quest = self.data_loader.get_quest(q_id)
            if not quest: continue

            stage = quest.stages.get(progress.current_stage_id)
            if not stage or not stage.objectives: continue

            updated = False
            for obj in stage.objectives:
                if obj.type == event_type and obj.target.lower() == target.lower():
                    key = f"{obj.type}:{obj.target}"
                    current = progress.objectives_progress.get(key, 0)
                    if current < obj.count:
                        progress.objectives_progress[key] = current + 1
                        updated = True
                        notifications.append(f"Quest Update: [{quest.title}] {obj.type} {obj.target} ({current + 1}/{obj.count})")

            if updated:
                # Check if all objectives for this stage are met
                all_met = True
                for obj in stage.objectives:
                    key = f"{obj.type}:{obj.target}"
                    if progress.objectives_progress.get(key, 0) < obj.count:
                        all_met = False
                        break

                if all_met:
                    notifications.append(f"Quest Stage Complete: [{quest.title}] - Objectives Met!")
                    if not stage.choices:
                         # Auto-advance logic for stages without choices (linear)
                         # This assumes linear quests might rely on 'next_stage_id' from somewhere,
                         # but currently structure relies on choices.
                         # If no choices, it's stuck unless we define a default transition or it is just waiting for user interaction.
                         pass
        return notifications

    def _grant_rewards(self, character: Character, rewards: List[str]):
        # Supported formats:
        # "Essence: <Name>"
        # "Stone: <Name>"
        # "XP: <Amount>"
        # "Random Essence"
        # "Random Stone"

        for reward in rewards:
            if reward.startswith("Lore:"):
                lore_title = reward.split(":", 1)[1].strip()
                lore_entry = self.data_loader.get_lore(lore_title)
                if lore_entry:
                    if lore_entry.id not in character.lore:
                        character.lore.append(lore_entry.id)
                        print(f"Lore Discovered: {lore_entry.title}")
                    else:
                        print(f"Lore already known: {lore_entry.title}")
                else:
                    print(f"Unknown Lore reward: {lore_title}")

            elif reward.startswith("Essence:"):
                name = reward.split(":", 1)[1].strip()
                item = self.data_loader.get_essence(name)
                if item:
                    character.inventory.append(item)
                    print(f"Received Reward: {item.name}")

            elif reward.startswith("Stone:"):
                name = reward.split(":", 1)[1].strip()
                item = self.data_loader.get_stone(name)
                if item:
                    character.inventory.append(item)
                    print(f"Received Reward: {item.name}")

            elif reward.startswith("XP:"):
                try:
                    amount = int(reward.split(":", 1)[1].strip())
                    print(f"Received {amount} XP (Not implemented on Character yet)")
                except ValueError:
                    pass

            elif "Essence" in reward: # Fallback for generic strings like "Water Essence"
                # Try to match exact name
                item = self.data_loader.get_essence(reward)
                if not item:
                    # Try stripping " Essence"
                    stripped = reward.replace(" Essence", "").strip()
                    item = self.data_loader.get_essence(stripped)

                if item:
                    character.inventory.append(item)
                    print(f"Received Reward: {item.name}")
                else:
                    # Give random essence? Or just log
                    print(f"Reward text: {reward} (Item not found)")

            elif "Stone" in reward:
                item = self.data_loader.get_stone(reward)
                if item:
                    character.inventory.append(item)
                    print(f"Received Reward: {item.name}")
                else:
                    print(f"Reward text: {reward} (Item not found)")
            else:
                 print(f"Reward: {reward}")

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
        if roll < 0.1: # 10% chance for Essence
            essences = self.data_loader.get_all_base_essences()
            if not essences: return None
            name = random.choice(essences)
            return self.data_loader.get_essence(name)
        elif roll < 0.2: # 10% chance for Stone
            stones = self.data_loader.get_all_stones()
            if not stones: return None
            name = random.choice(stones)
            return self.data_loader.get_stone(name)
        else:
            return None

    def get_loot_for_monster(self, monster: Character) -> List[Union[Essence, AwakeningStone]]:
        loot = []
        # 1. Fixed Loot Table
        for item_name in monster.loot_table:
            item = self.data_loader.get_essence(item_name)
            if not item:
                item = self.data_loader.get_stone(item_name)
            if item:
                loot.append(item)

        # 2. Random Drop Chance (based on Rank?)
        # Higher rank = better chance?
        # For now, flat small chance for extra random loot
        random_item = self.generate_random_loot()
        if random_item:
            loot.append(random_item)

        return loot

class CombatManager:
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader

    def calculate_damage(self, attacker: Character, defender: Character, is_magical: bool = False, multiplier: float = 1.0) -> float:
        # Simple damage formula
        # Physical: Power vs 50% Speed (Evasion/Glancing) + Mitigation?
        # Magical: Spirit vs Spirit?
        # For simplicity: Damage = Attack - Defense/2
        # Attacker Damage:
        damage = 0.0
        if is_magical:
             damage = attacker.attributes["Spirit"].value * 1.5
             # Defense
             defense = defender.attributes["Spirit"].value * 0.5
        else:
             damage = attacker.attributes["Power"].value * 1.5
             defense = defender.attributes["Recovery"].value * 0.5 # Toughness

        damage *= multiplier
        final_damage = max(1.0, damage - defense)
        # Variance
        final_damage *= random.uniform(0.9, 1.1)
        return final_damage

    def execute_ability(self, user: Character, target: Character, ability: Ability) -> List[str]:
        log = []

        # Check Cooldown
        if ability.current_cooldown > 0:
            return [f"{ability.name} is on cooldown ({ability.current_cooldown} rounds left)!"]

        # Check Cost
        cost = ability.cost
        cost_type = ability.parent_stone.cost_type

        if cost_type == "Mana":
            if user.current_mana < cost:
                return [f"Not enough Mana to use {ability.name}!"]
            user.current_mana -= cost
        elif cost_type == "Stamina":
            if user.current_stamina < cost:
                return [f"Not enough Stamina to use {ability.name}!"]
            user.current_stamina -= cost
        elif cost_type == "Health":
             if user.current_health < cost:
                 return [f"Not enough Health to use {ability.name}!"]
             user.current_health -= cost

        # Set Cooldown
        ability.current_cooldown = ability.cooldown + 1 # +1 because it decrements at start of next round/end of this one

        # Determine Effect based on Function
        function = ability.parent_stone.function
        rank_mult = 1.0 + (RANK_INDICES[ability.rank] * 0.5)
        level_mult = 1.0 + (ability.level * 0.1)
        power_mult = rank_mult * level_mult

        if "Attack" in function:
            is_magical = "Ranged" in function or "Blast" in ability.parent_stone.name
            dmg = self.calculate_damage(user, target, is_magical, multiplier=1.5 * power_mult)
            target.current_health -= dmg
            log.append(f"Used {ability.name} on {target.name} for {dmg:.1f} damage!")

        elif "Defense" in function:
            # Temporary defense buff or heal? Let's do a heal/shield hybrid for simplicity
            # Or just restore health for now as a "Shield/Heal" abstraction
            heal_amount = user.attributes["Spirit"].value * power_mult
            user.current_health = min(user.max_health, user.current_health + heal_amount)
            log.append(f"Used {ability.name} and restored {heal_amount:.1f} health/shield!")

        elif "Heal" in function or "Sustain" in function:
             heal_amount = user.attributes["Spirit"].value * power_mult
             user.current_health = min(user.max_health, user.current_health + heal_amount)
             log.append(f"Used {ability.name} and healed for {heal_amount:.1f}!")

        elif "Summon" in function:
             log.append(f"Used {ability.name}! A summon appears (flavor only for now).")
             # Could implement actual summons later

        else:
             # Default fallback damage
             dmg = self.calculate_damage(user, target, is_magical=True, multiplier=1.0 * power_mult)
             target.current_health -= dmg
             log.append(f"Used {ability.name} on {target.name} for {dmg:.1f} damage!")

        # Gain XP for ability usage
        if user.abilities: # Only if user is player basically, or tracked
             if ability.gain_xp(5):
                 log.append(f"{ability.name} leveled up to {ability.level}!")

        return log

    def combat_round(self, player: Character, enemy: Character, player_action: Union[str, Ability]) -> tuple[List[str], bool]:
        log = []

        # Decrement Cooldowns for Player
        if player.abilities:
            for ess_name, slots in player.abilities.items():
                for ab in slots:
                    if ab and ab.current_cooldown > 0:
                        ab.current_cooldown -= 1

        # Note: Enemy cooldowns are not tracked in this simplified model as enemies do not persist abilities deeply yet.

        # 1. Player Turn
        if isinstance(player_action, Ability):
             ability_log = self.execute_ability(player, enemy, player_action)
             log.extend(ability_log)
             if "Not enough" in ability_log[0] or "on cooldown" in ability_log[0]: # Failed to use
                 return log, False

        elif player_action == "Attack":
            dmg = self.calculate_damage(player, enemy, is_magical=False)
            enemy.current_health -= dmg
            log.append(f"You attacked {enemy.name} for {dmg:.1f} damage.")
        elif player_action == "Flee":
            # Chance to flee based on Speed
            p_speed = player.attributes["Speed"].value
            e_speed = enemy.attributes["Speed"].value
            chance = 0.5 + (p_speed - e_speed) * 0.01
            if random.random() < chance:
                log.append("You fled successfully!")
                return log, True # Fled
            else:
                log.append("Failed to flee!")

        # Check Enemy Death
        if enemy.current_health <= 0:
            log.append(f"{enemy.name} has been defeated!")
            # Trigger Quest Update
            return log, True # Combat over (Win)

        # 2. Enemy Turn
        # Simple AI: 20% chance to use a special ability if available (simulated), else Attack
        ai_action = "Attack"
        if random.random() < 0.2:
             # Simulate an ability usage
             ai_action = "Special"

        if ai_action == "Special":
             # Flavor text for enemy ability
             ability_names = ["Power Strike", "Shadow Blast", "Roar", "Bite"]
             ab_name = random.choice(ability_names)

             # Calculate slightly higher damage
             is_magical = enemy.attributes["Spirit"].value > enemy.attributes["Power"].value
             dmg = self.calculate_damage(enemy, player, is_magical=is_magical, multiplier=1.3)
             player.current_health -= dmg
             log.append(f"{enemy.name} used {ab_name} on you for {dmg:.1f} damage!")
        else:
             # Standard Attack
             is_magical = enemy.attributes["Spirit"].value > enemy.attributes["Power"].value
             dmg = self.calculate_damage(enemy, player, is_magical=is_magical)
             player.current_health -= dmg
             atk_type = "magically attacked" if is_magical else "attacked"
             log.append(f"{enemy.name} {atk_type} you for {dmg:.1f} damage.")

        # Check Player Death
        if player.current_health <= 0:
            log.append("You have been defeated!")
            return log, True # Combat over (Loss)

        return log, False # Continue

    def check_combat_objectives(self, player: Character, enemy: Character):
        # This should be called by GameEngine after combat
        pass

class InteractionManager:
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader

    def get_npc(self, name: str) -> Optional[Character]:
        return self.data_loader.get_character_template(name)

    def interact(self, player: Character, npc_name: str) -> str:
        npc = self.get_npc(npc_name)
        if not npc:
            return "That person is not here."

        rel = player.relationships.get(npc_name, 0)

        # Determine dialogue key
        key = "default"
        if rel >= 50:
            key = "friendly"
        elif rel <= -50:
            key = "hostile"

        dialogue = npc.dialogue.get(key, npc.dialogue.get("default", "..."))

        # Small relationship boost for talking (capped)
        if rel < 10:
             self.modify_relationship(player, npc_name, 1)

        return f"{npc.name}: \"{dialogue}\""

    def modify_relationship(self, player: Character, npc_name: str, amount: int):
        current = player.relationships.get(npc_name, 0)
        player.relationships[npc_name] = max(-100, min(100, current + amount))

    def modify_reputation(self, player: Character, faction_name: str, amount: int):
        current = player.reputation.get(faction_name, 0)
        player.reputation[faction_name] = max(-100, min(100, current + amount))

class GameEngine:
    def __init__(self):
        self.data_loader = DataLoader()
        self.confluence_mgr = ConfluenceManager(self.data_loader)
        self.ability_gen = AbilityGenerator()
        self.training_mgr = TrainingManager()
        self.loot_mgr = LootManager(self.data_loader)
        self.quest_mgr = QuestManager(self.data_loader)
        self.combat_mgr = CombatManager(self.data_loader)
        self.interaction_mgr = InteractionManager(self.data_loader)
        self.character = None

    def create_character(self, name: str, race: str):
        self.character = Character(name=name, race=race)
        return self.character

    def get_save_files(self) -> List[str]:
        save_dir = os.path.join(DATA_DIR, 'saves')
        if not os.path.exists(save_dir):
            return []
        return [f for f in os.listdir(save_dir) if f.endswith('.json')]

    def save_game(self, filename: str = "savegame.json") -> str:
        if not self.character:
            return "No character to save."

        save_dir = os.path.join(DATA_DIR, 'saves')
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        save_path = os.path.join(save_dir, filename)
        data = asdict(self.character)

        try:
            with open(save_path, 'w') as f:
                json.dump(data, f, indent=4)
            return f"Game saved to {save_path}"
        except Exception as e:
            return f"Failed to save game: {str(e)}"

    def load_game(self, filename: str = "savegame.json") -> str:
        save_path = os.path.join(DATA_DIR, 'saves', filename)
        if not os.path.exists(save_path):
            return "Save file not found."

        try:
            with open(save_path, 'r') as f:
                data = json.load(f)

            # Reconstruct Character object manually to ensure types are correct
            char = Character(
                name=data['name'],
                race=data['race'],
                faction=data.get('faction'),
                affinity=data.get('affinity', "General"),
                xp_reward=data.get('xp_reward', 0),
                loot_table=data.get('loot_table', [])
            )

            # Restore Attributes
            if 'attributes' in data:
                char.attributes = {}
                for k, v in data['attributes'].items():
                    char.attributes[k] = Attribute(**v)

            # Restore Base Essences
            char.base_essences = []
            for e_data in data.get('base_essences', []):
                char.base_essences.append(Essence(**e_data))

            # Restore Confluence Essence
            if data.get('confluence_essence'):
                char.confluence_essence = Essence(**data['confluence_essence'])

            # Restore Inventory (Mixed types)
            char.inventory = []
            for item in data.get('inventory', []):
                # Distinguish between Essence and Stone based on fields
                if 'function' in item: # Stone
                    char.inventory.append(AwakeningStone(**item))
                else: # Essence
                    char.inventory.append(Essence(**item))

            # Restore Abilities
            # Dictionary of list of (Ability or None)
            char.abilities = {}
            for ess_name, slots in data.get('abilities', {}).items():
                restored_slots = []
                for slot in slots:
                    if slot:
                        # Reconstruct Essence and Stone inside Ability
                        p_ess = Essence(**slot['parent_essence'])
                        p_stone = AwakeningStone(**slot['parent_stone'])

                        ab = Ability(
                            name=slot['name'],
                            description=slot['description'],
                            rank=slot['rank'],
                            level=slot['level'],
                            parent_essence=p_ess,
                            parent_stone=p_stone,
                            xp=slot.get('xp', 0.0),
                            cooldown=slot.get('cooldown', 0),
                            cost=slot.get('cost', 0)
                        )
                        restored_slots.append(ab)
                    else:
                        restored_slots.append(None)
                char.abilities[ess_name] = restored_slots

            # Restore Quests
            char.quests = {}
            for q_id, q_data in data.get('quests', {}).items():
                char.quests[q_id] = QuestProgress(**q_data)

            # Restore Stats
            char.current_health = data.get('current_health', -1)
            char.current_mana = data.get('current_mana', -1)
            char.current_stamina = data.get('current_stamina', -1)

            self.character = char
            return f"Game loaded from {save_path}"
        except Exception as e:
            return f"Failed to load game: {str(e)}"

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

    def save_game(self, filename: str):
        if not self.character:
            return "No character to save."

        save_dir = os.path.join(DATA_DIR, 'saves')
        os.makedirs(save_dir, exist_ok=True)
        filepath = os.path.join(save_dir, filename)

        try:
            # Use dataclasses.asdict for serialization
            data = dataclasses.asdict(self.character)
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            return f"Game saved to {filepath}"
        except Exception as e:
            return f"Error saving game: {e}"

    def load_game(self, filename: str):
        save_dir = os.path.join(DATA_DIR, 'saves')
        filepath = os.path.join(save_dir, filename)

        if not os.path.exists(filepath):
            return f"Save file {filename} not found."

        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            # Reconstruct Character object manually because simple assignment won't restore nested dataclasses/objects
            char = Character(
                name=data['name'],
                race=data['race'],
                faction=data.get('faction'),
                affinity=data.get('affinity', 'General'),
                current_health=data.get('current_health', -1),
                current_mana=data.get('current_mana', -1),
                current_stamina=data.get('current_stamina', -1),
                xp_reward=data.get('xp_reward', 0),
                loot_table=data.get('loot_table', []),
                lore=data.get('lore', [])
            )

            # Reconstruct Attributes
            if 'attributes' in data:
                for k, v in data['attributes'].items():
                    char.attributes[k] = Attribute(**v)

            # Reconstruct Essences
            # Base
            for e_data in data.get('base_essences', []):
                char.base_essences.append(Essence(**e_data))
            # Confluence
            if data.get('confluence_essence'):
                char.confluence_essence = Essence(**data['confluence_essence'])

            # Reconstruct Inventory
            for item_data in data.get('inventory', []):
                if not item_data: continue
                # Distinguish Essence vs AwakeningStone
                if 'type' in item_data: # Essence
                    char.inventory.append(Essence(**item_data))
                else:
                    char.inventory.append(AwakeningStone(**item_data))

            # Reconstruct Abilities
            # Dict[str, List[Optional[Ability]]]
            if 'abilities' in data:
                for ess_name, slots in data['abilities'].items():
                    reconstructed_slots = []
                    for slot in slots:
                        if slot:
                            # Reconstruct nested objects in Ability
                            p_ess = Essence(**slot['parent_essence'])
                            p_stone = AwakeningStone(**slot['parent_stone'])
                            # Remove them from kwargs to avoid double assignment or error if Ability __init__ expects objects
                            # Ability is a dataclass, so it expects fields.
                            # We need to filter out keys that might not be in Ability definition if schema changed,
                            # but assuming schema matches.
                            # Need to convert nested dicts to objects
                            slot['parent_essence'] = p_ess
                            slot['parent_stone'] = p_stone
                            reconstructed_slots.append(Ability(**slot))
                        else:
                            reconstructed_slots.append(None)
                    char.abilities[ess_name] = reconstructed_slots

            # Reconstruct Quests
            if 'quests' in data:
                for q_id, q_data in data['quests'].items():
                    char.quests[q_id] = QuestProgress(**q_data)

            # Reconstruct Relationships
            if 'relationships' in data:
                char.relationships = data['relationships']
            if 'reputation' in data:
                char.reputation = data['reputation']

            self.character = char
            return f"Game loaded from {filename}"
        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"Error loading game: {e}"

    def get_save_files(self) -> List[str]:
        save_dir = os.path.join(DATA_DIR, 'saves')
        if not os.path.exists(save_dir):
            return []
        return [f for f in os.listdir(save_dir) if f.endswith('.json')]
