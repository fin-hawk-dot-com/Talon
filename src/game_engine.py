import os
import json
import dataclasses
from typing import List, Optional

from src.models import Character, Attribute, Essence, Ability, AwakeningStone, QuestProgress, StatusEffect, Consumable, RANK_INDICES
from src.data_loader import DataLoader, DATA_DIR
from src.combat_system import CombatManager
from src.quest_system import QuestManager
from src.inventory_system import LootManager, CraftingManager, MarketManager
from src.training_system import TrainingManager, AbilityGenerator, ConfluenceManager
from src.interaction_system import InteractionManager
from src.narrative import NarrativeGenerator

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
        self.crafting_mgr = CraftingManager(self.data_loader)
        self.market_mgr = MarketManager(self.data_loader)
        self.character = None

    def create_character(self, name: str, race: str):
        self.character = Character(name=name, race=race)
        return self.character

    def rest(self) -> str:
        if not self.character: return "No character."

        # Check location type
        loc = self.data_loader.get_location(self.character.current_location)
        is_safe = False
        if loc and loc.type in ["City", "Village", "Outpost"]:
            is_safe = True

        msg = ""
        if is_safe:
            self.character.current_health = self.character.max_health
            self.character.current_mana = self.character.max_mana
            self.character.current_stamina = self.character.max_stamina
            msg = f"Rested at {self.character.current_location}. Health, Mana, and Stamina fully restored."
        else:
            # Wilderness Rest - Partial restore
            h_gain = self.character.max_health * 0.5
            m_gain = self.character.max_mana * 0.5
            s_gain = self.character.max_stamina * 0.5

            self.character.current_health = min(self.character.max_health, self.character.current_health + h_gain)
            self.character.current_mana = min(self.character.max_mana, self.character.current_mana + m_gain)
            self.character.current_stamina = min(self.character.max_stamina, self.character.current_stamina + s_gain)

            msg = f"Camped in the wilderness ({self.character.current_location}). Recovered some vitality."

        return msg

    def travel(self, location_name: str) -> str:
        if not self.character: return "No character."

        current_loc_name = self.character.current_location
        current_loc = self.data_loader.get_location(current_loc_name)

        if not current_loc:
            # Fallback if somehow current location is invalid, allow travel to valid ones?
            # Or just reset to Greenstone City.
            self.character.current_location = "Greenstone City"
            current_loc = self.data_loader.get_location("Greenstone City")

        if location_name == current_loc_name:
            return f"You are already at {location_name}."

        # Check connectivity
        # Note: We compare exact strings, assuming data integrity.
        # Connected locations in JSON are list of strings.
        if location_name not in current_loc.connected_locations:
            return f"You cannot travel to {location_name} directly from {current_loc_name}."

        target_loc = self.data_loader.get_location(location_name)
        if not target_loc:
            return "Location data not found."

        self.character.current_location = location_name
        return f"Traveled to {location_name}."

    def get_monsters_for_location(self, location_name: str) -> List[Character]:
        loc = self.data_loader.get_location(location_name)
        if not loc: return []

        # Danger Rank Mapping
        target_rank = loc.danger_rank # e.g. "Iron", "Bronze"

        rank_idx = RANK_INDICES.get(target_rank, 0)

        valid_monsters = []
        all_monsters = self.data_loader.get_all_monsters()

        for m_name in all_monsters:
            m = self.data_loader.get_monster(m_name)
            if not m: continue

            # Use Character.rank property
            m_rank = m.rank
            m_rank_idx = RANK_INDICES.get(m_rank, 0)

            # Allow monsters of same rank or one rank lower/higher?
            if m_rank == target_rank:
                valid_monsters.append(m)
            elif m_rank_idx == rank_idx - 1: # Also allow slightly weaker ones
                valid_monsters.append(m)

        # If no monsters found for rank, fallback to all (or random subset) to avoid empty list
        if not valid_monsters:
            return [self.data_loader.get_monster(m) for m in all_monsters]

        return valid_monsters

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

            result_msg = f"Absorbed {item.name}."

            # Check for Confluence
            if len(self.character.base_essences) == 3 and not self.character.confluence_essence:
                confluence = self.confluence_mgr.determine_confluence(self.character.base_essences)
                self.character.inventory.append(confluence)

                result_msg += NarrativeGenerator.get_confluence_narrative(confluence)

            return result_msg
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

        return NarrativeGenerator.get_awakening_narrative(essence, stone, ability.name)

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
                lore=data.get('lore', []),
                current_xp=data.get('current_xp', 0)
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
                # Distinguish Essence vs AwakeningStone vs Consumable
                if 'type' in item_data: # Essence
                    char.inventory.append(Essence(**item_data))
                elif 'effect_type' in item_data: # Consumable
                    char.inventory.append(Consumable(**item_data))
                else:
                    char.inventory.append(AwakeningStone(**item_data))

            # Reconstruct Currency and Materials
            char.currency = data.get('currency', 0)
            char.materials = data.get('materials', {})

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

            # Reconstruct Status Effects
            if 'status_effects' in data:
                 for se in data['status_effects']:
                     char.status_effects.append(StatusEffect(**se))

            # Reconstruct Location
            if 'current_location' in data:
                char.current_location = data['current_location']

            # Reconstruct Summons
            if 'summons' in data:
                for s_data in data['summons']:
                    # Basic reconstruction for summons
                    summon = Character(
                        name=s_data['name'],
                        race=s_data['race'],
                        current_health=s_data.get('current_health', -1),
                        current_mana=s_data.get('current_mana', -1),
                        current_stamina=s_data.get('current_stamina', -1),
                        summon_duration=s_data.get('summon_duration', 0)
                    )
                    if 'attributes' in s_data:
                        for k, v in s_data['attributes'].items():
                            summon.attributes[k] = Attribute(**v)
                    char.summons.append(summon)

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
