import os
import sys
import random

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import Character, Essence, RANKS
from src.mechanics import DataLoader, ConfluenceManager

def generate_library_md(filepath="LIBRARY.md"):
    loader = DataLoader()
    confluence_mgr = ConfluenceManager(loader)

    lines = []
    lines.append("# HWFWM System Library")
    lines.append("\n## Essences")
    lines.append("| Name | Type | Rarity | Tags | Description | Opposite | Synergy |")
    lines.append("|---|---|---|---|---|---|---|")

    essences = sorted(loader.essences_data, key=lambda x: x['name'])
    for e in essences:
        tags = ", ".join(e['tags'])
        opposite = e.get('opposite', '-')
        synergy = ", ".join(e.get('synergy', []))
        lines.append(f"| {e['name']} | {e['type']} | {e['rarity']} | {tags} | {e['description']} | {opposite} | {synergy} |")

    lines.append("\n## Confluences")
    lines.append("| Result | Base Essences | Archetype |")
    lines.append("|---|---|---|")

    confluences = sorted(loader.confluences_data, key=lambda x: x['result'])
    for c in confluences:
        bases = ", ".join(c['bases'])
        lines.append(f"| {c['result']} | {bases} | {c['archetype']} |")

    lines.append("\n## Awakening Stones")
    lines.append("| Name | Function | Description | Rarity | Cooldown | Cost Type |")
    lines.append("|---|---|---|---|---|---|")

    stones = sorted(loader.stones_data, key=lambda x: x['name'])
    for s in stones:
        rarity = s.get('rarity', "Common")
        cooldown = s.get('cooldown', "Medium")
        cost_type = s.get('cost_type', "Mana")
        lines.append(f"| {s['name']} | {s['function']} | {s['description']} | {rarity} | {cooldown} | {cost_type} |")

    lines.append("\n## Example Builds")

    # Generate some random or preset builds
    example_builds = [
        (["Fire", "Earth", "Potent"], "Power"),
        (["Dark", "Blood", "Sin"], "Recovery"),
        (["Might", "Swift", "Light"], "Speed"),
        (["Gun", "Armor", "Technology"], "Spirit")
    ]

    for i, (bases, bond_attr) in enumerate(example_builds):
        char = Character(name=f"Example {i+1}", race="Human")
        # Add bases
        # We need to fetch Essence objects
        essence_objs = []
        for b_name in bases:
            e = loader.get_essence(b_name)
            if e:
                essence_objs.append(e)
                char.add_essence(e, bond_attr) # Bonding all to same for simplicity in example

        # Confluence
        conf = confluence_mgr.determine_confluence(essence_objs)
        char.add_essence(conf, bond_attr)

        lines.append(f"\n### Build {i+1}: {conf.name} Archetype")
        lines.append(f"- **Base Essences**: {', '.join([e.name for e in essence_objs])}")
        lines.append(f"- **Confluence**: {conf.name} ({conf.description})")
        lines.append(f"- **Primary Attribute Bond**: {bond_attr}")
        lines.append(f"- **Growth Multiplier for {bond_attr}**: {char.attributes[bond_attr].growth_multiplier}x")

    with open(filepath, "w") as f:
        f.write("\n".join(lines))

    print(f"Library generated at {filepath}")

if __name__ == "__main__":
    generate_library_md()
