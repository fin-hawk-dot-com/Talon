import pytest
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.mechanics import DataLoader

@pytest.fixture
def data_loader():
    return DataLoader()

def test_quest_loading(data_loader):
    quests = data_loader.get_all_quests()
    assert len(quests) > 0, "No quests loaded"

    # Check specifically for new quests
    new_ids = ["faction_artifact_dispute", "faction_cold_commerce", "faction_beast_honor"]
    for qid in new_ids:
        q = data_loader.get_quest(qid)
        assert q is not None, f"Quest {qid} not found"
        assert len(q.stages) > 0, f"Quest {qid} has no stages"

def test_npc_locations(data_loader):
    # Check if new NPCs are in their locations
    checks = {
        "Ironhold": "Trader Midas",
        "Greenstone City": "Huntsman Valerius"
    }

    for loc_name, npc_name in checks.items():
        loc = data_loader.get_location(loc_name)
        assert loc is not None, f"Location {loc_name} not found"
        assert npc_name in loc.npcs, f"{npc_name} not found in {loc_name}"

def test_dialogues_exist(data_loader):
    npcs = ["Thadwick", "Professor Vane", "Elara", "Trader Midas", "Huntsman Valerius"]
    for npc in npcs:
        tree = data_loader.get_dialogue_tree(npc)
        assert tree is not None, f"Dialogue tree for {npc} not found"
        assert "root" in tree, f"Dialogue tree for {npc} missing root node"

def test_dialogue_links(data_loader):
    # Thadwick should link to artifact_quest_intro
    thadwick = data_loader.get_dialogue_tree("Thadwick")
    root_choices = thadwick["root"]["choices"]
    found = False
    for c in root_choices:
        if c['next_id'] == "artifact_quest_intro":
            found = True
            break
    assert found, "Thadwick root choice does not link to artifact_quest_intro"
