import json
import os
import sys
from typing import List, Optional, Dict, Any
from src.models import Essence, AwakeningStone, Character, Faction, Quest, QuestStage, QuestObjective, QuestChoice, Location, LoreEntry, PointOfInterest, Consumable, DialogueNode, DialogueChoice

if hasattr(sys, '_MEIPASS'):
    DATA_DIR = os.path.join(sys._MEIPASS, 'data')
else:
    DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def load_json(filename):
    with open(os.path.join(DATA_DIR, filename), 'r') as f:
        return json.load(f)

class DataLoader:
    """
    Loads game data from JSON files.
    Used by generate_library.py to populate the library with Essences, Stones, Monsters, Quests, etc.
    """
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
            DataLoader._cache['dialogues'] = load_json('dialogues.json')

        self.essences_data = DataLoader._cache['essences']
        self.confluences_data = DataLoader._cache['confluences']
        self.stones_data = DataLoader._cache['stones']
        self.factions_data = DataLoader._cache['factions']
        self.characters_data = DataLoader._cache['characters']
        self.quests_data = DataLoader._cache['quests']
        self.locations_data = DataLoader._cache['locations']
        self.monsters_data = DataLoader._cache['monsters']
        self.lore_data = DataLoader._cache['lore']
        self.dialogues_data = DataLoader._cache['dialogues']

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
                text=l['text'],
                image_prompt=l.get('image_prompt', "")
            )
        return None

    def get_all_lore(self) -> List[LoreEntry]:
        return [
            LoreEntry(id=l['id'], title=l['title'], category=l['category'], text=l['text'], image_prompt=l.get('image_prompt', ""))
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
                type=q.get('type', 'Side'),
                image_prompt=q.get('image_prompt', ""),
                location=q.get('location')
            )
        return None

    def get_all_quests(self) -> List[Quest]:
        quests = []
        for q_data in self.quests_data:
             quests.append(self.get_quest(q_data['id']))
        return quests

    def get_essence(self, name: str) -> Optional[Essence]:
        e = self.essences_map.get(name.lower())
        if not e and " essence" in name.lower():
            e = self.essences_map.get(name.lower().replace(" essence", ""))

        if e:
            return Essence(
                name=e['name'],
                type=e['type'],
                rarity=e['rarity'],
                tags=e['tags'],
                description=e['description'],
                image_prompt=e.get('image_prompt', ""),
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
                image_prompt=s.get('image_prompt', ""),
                rarity=s.get('rarity', "Common"),
                cooldown=s.get('cooldown', "Medium"),
                cost_type=s.get('cost_type', "Mana"),
                value=s.get('value', 100)
            )
        return None

    def get_consumable(self, name: str) -> Optional[Consumable]:
        # Hardcoded for now, could be JSON
        consumables = {
            "healing potion": Consumable("Healing Potion", "Heal", 50.0, "Restores 50 Health.", price=20),
            "mana potion": Consumable("Mana Potion", "RestoreMana", 30.0, "Restores 30 Mana.", price=20),
            "antidote": Consumable("Antidote", "Cure", 0.0, "Cures Poison.", price=15),
            "iron skin elixir": Consumable("Iron Skin Elixir", "Buff", 10.0, "Increases defense.", duration=5, price=50)
        }
        return consumables.get(name.lower())

    def get_faction(self, name: str) -> Optional[Faction]:
        f = self.factions_map.get(name.lower())
        if f:
            return Faction(
                name=f['name'],
                description=f['description'],
                type=f['type'],
                image_prompt=f.get('image_prompt', ""),
                rank_requirement=f.get('rank_requirement')
            )
        return None

    def get_all_factions(self) -> List[Faction]:
        return [
            Faction(
                name=f['name'],
                description=f['description'],
                type=f['type'],
                image_prompt=f.get('image_prompt', ""),
                rank_requirement=f.get('rank_requirement')
            ) for f in self.factions_data
        ]

    def get_location(self, name: str) -> Optional[Location]:
        l = self.locations_map.get(name.lower())
        if l:
            pois = []
            for p in l.get('points_of_interest', []):
                pois.append(PointOfInterest(
                    name=p['name'],
                    description=p['description'],
                    type=p['type'],
                    image_prompt=p.get('image_prompt', "")
                ))

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
                npcs=l.get('npcs', []),
                narrative=l.get('narrative', ""),
                points_of_interest=pois
            )
        return None

    def get_all_locations(self) -> List[Location]:
        result = []
        for l in self.locations_data:
            pois = []
            for p in l.get('points_of_interest', []):
                pois.append(PointOfInterest(
                    name=p['name'],
                    description=p['description'],
                    type=p['type'],
                    image_prompt=p.get('image_prompt', "")
                ))

            result.append(Location(
                name=l['name'],
                description=l['description'],
                type=l['type'],
                image_prompt_positive=l['image_prompt_positive'],
                image_prompt_negative=l['image_prompt_negative'],
                region=l.get('region', "Unknown"),
                danger_rank=l.get('danger_rank', "Iron"),
                connected_locations=l.get('connected_locations', []),
                resources=l.get('resources', []),
                npcs=l.get('npcs', []),
                narrative=l.get('narrative', ""),
                points_of_interest=pois
            ))
        return result

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
                image_prompt=c.get('image_prompt', ""),
                dialogue=c.get('dialogue', {})
            )

            # Load Attributes
            if 'attributes' in c:
                for attr_name, value in c['attributes'].items():
                    if attr_name in char.attributes:
                        char.attributes[attr_name].value = value

            attributes = ["Power", "Speed", "Spirit", "Recovery"]

            for i, ess_name in enumerate(c.get('base_essences', [])):
                essence = self.get_essence(ess_name)
                if essence:
                    # Auto-bond
                    bonded_attr = attributes[i % 4]
                    try:
                        char.add_essence(essence, bonded_attr)
                    except ValueError:
                        pass

            # Load Confluence
            conf_name = c.get('confluence_essence')
            if conf_name:
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
                description=m.get('description', ""),
                image_prompt=m.get('image_prompt', ""),
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

    def get_dialogue_tree(self, npc_name: str) -> Dict[str, Any]:
        return self.dialogues_data.get(npc_name)
