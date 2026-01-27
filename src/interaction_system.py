from typing import Optional, Dict
from src.models import Character, DialogueNode, DialogueChoice
from src.data_loader import DataLoader

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

        # Legacy behavior for simple interact call, or fallback
        # Ideally we want the caller to use get_dialogue_node for full tree
        # But this function returns a string.
        # We can fetch the 'root' node text if available.

        tree = self.data_loader.get_dialogue_tree(npc_name)
        if tree and 'root' in tree:
            return f"{npc.name}: \"{tree['root']['text']}\" (Use interaction menu for options)"

        # Fallback to old system
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

    def get_dialogue_node(self, npc_name: str, node_id: str) -> Optional[DialogueNode]:
        tree = self.data_loader.get_dialogue_tree(npc_name)

        if not tree:
             # Legacy fallback: Create a dummy node from character.dialogue
             npc = self.get_npc(npc_name)
             if npc and npc.dialogue:
                 if node_id == "root":
                     text = npc.dialogue.get("default", "...")
                     return DialogueNode(text, [DialogueChoice("Leave", "exit")])
             return None

        node_data = tree.get(node_id)
        if not node_data:
            return None

        choices = [DialogueChoice(**c) for c in node_data['choices']]
        hub_text = node_data.get('hub_text')
        return DialogueNode(text=node_data['text'], choices=choices, hub_text=hub_text)

    def modify_relationship(self, player: Character, npc_name: str, amount: int):
        current = player.relationships.get(npc_name, 0)
        player.relationships[npc_name] = max(-100, min(100, current + amount))

    def modify_reputation(self, player: Character, faction_name: str, amount: int):
        current = player.reputation.get(faction_name, 0)
        player.reputation[faction_name] = max(-100, min(100, current + amount))
