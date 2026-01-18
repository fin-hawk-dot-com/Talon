import os
import sys
import random

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import Character, Essence, RANKS
from src.mechanics import DataLoader, ConfluenceManager
from src.ability_templates import ABILITY_TEMPLATES

def generate_library_md(filepath="LIBRARY.md"):
    loader = DataLoader()
    confluence_mgr = ConfluenceManager(loader)

    lines = []
    lines.append("# HWFWM System Library")

    # --- System Mechanics ---
    lines.append("\n## System Mechanics")
    lines.append("### Ranks")
    lines.append("The progression system is divided into major ranks. Each rank represents a significant leap in power.")
    rank_list = ["Normal", "Iron", "Bronze", "Silver", "Gold", "Diamond"]
    for i, rank in enumerate(rank_list):
        lines.append(f"- **{rank}**: Rank {i}")

    lines.append("\n### Attributes")
    lines.append("Characters have 4 main attributes:")
    lines.append("- **Power**: Physical strength and damage.")
    lines.append("- **Speed**: Movement and reaction time.")
    lines.append("- **Spirit**: Magical power and mana pool.")
    lines.append("- **Recovery**: Health regeneration and stamina.")

    lines.append("\n### Ability Generation")
    lines.append("Abilities are awakened by combining an **Essence** with an **Awakening Stone**.")
    lines.append("- **Essence**: Determines the elemental flavor and tags (e.g., Fire, Dark).")
    lines.append("- **Awakening Stone**: Determines the function (e.g., Attack, Defense).")
    lines.append("- **Template**: The system selects an ability template that matches the Stone's function and the Essence's tags.")

    # --- Essences ---
    lines.append("\n## Essences")

    # Collect all tags
    all_tags = set()
    for e in loader.essences_data:
        for t in e['tags']:
            all_tags.add(t)

    lines.append(f"\n**Known Tags**: {', '.join(sorted(list(all_tags)))}")
    lines.append("\n| Name | Type | Rarity | Tags | Description | Visual Prompt | Opposite | Synergy |")
    lines.append("|---|---|---|---|---|---|---|---|")

    essences = sorted(loader.essences_data, key=lambda x: x['name'])
    for e in essences:
        tags = ", ".join(e['tags'])
        opposite = e.get('opposite', '-') or '-'
        synergy = ", ".join(e.get('synergy', []))
        prompt = e.get('image_prompt', '')
        lines.append(f"| {e['name']} | {e['type']} | {e['rarity']} | {tags} | {e['description']} | {prompt} | {opposite} | {synergy} |")

    # --- Confluences ---
    lines.append("\n## Confluences")
    lines.append("| Result | Base Essences | Archetype |")
    lines.append("|---|---|---|")

    confluences = sorted(loader.confluences_data, key=lambda x: x['result'])
    for c in confluences:
        bases = ", ".join(c['bases'])
        lines.append(f"| {c['result']} | {bases} | {c['archetype']} |")

    # --- Awakening Stones ---
    lines.append("\n## Awakening Stones")
    lines.append("| Name | Function | Description | Visual Prompt | Rarity | Cooldown | Cost Type |")
    lines.append("|---|---|---|---|---|---|---|")

    stones = sorted(loader.stones_data, key=lambda x: x['name'])
    for s in stones:
        rarity = s.get('rarity', "Common")
        cooldown = s.get('cooldown', "Medium")
        cost_type = s.get('cost_type', "Mana")
        prompt = s.get('image_prompt', '')
        lines.append(f"| {s['name']} | {s['function']} | {s['description']} | {prompt} | {rarity} | {cooldown} | {cost_type} |")

    # --- Ability Templates ---
    lines.append("\n## Ability Templates")
    lines.append("When an Essence and Stone are combined, one of the following templates is chosen based on the function and tags.")
    lines.append("\n| Function | Pattern | Description | Required Tags | Affinity Preference |")
    lines.append("|---|---|---|---|---|")

    sorted_templates = sorted(ABILITY_TEMPLATES, key=lambda x: x.function)

    for t in sorted_templates:
        tags = ", ".join(t.essence_tags) if t.essence_tags else "None"
        affinities = []
        for k, v in t.affinity_weight.items():
            if v > 5.0:
                affinities.append(f"**{k}**")
            elif v > 1.0:
                 affinities.append(k)
        affinity_str = ", ".join(affinities) if affinities else "General"

        lines.append(f"| {t.function} | `{t.pattern}` | {t.description_template} | {tags} | {affinity_str} |")

    # --- Bestiary ---
    lines.append("\n## Bestiary")
    lines.append("| Name | Race | Description | Visual Prompt | Attributes (P/S/Sp/R) | XP | Loot |")
    lines.append("|---|---|---|---|---|---|---|")

    monsters = sorted(loader.monsters_data, key=lambda x: x['name'])
    for m in monsters:
        attrs = m.get('attributes', {})
        attr_str = f"{attrs.get('Power',0)}/{attrs.get('Speed',0)}/{attrs.get('Spirit',0)}/{attrs.get('Recovery',0)}"
        loot = ", ".join(m.get('loot_table', []))
        desc = m.get('description', '')
        prompt = m.get('image_prompt', '')
        lines.append(f"| {m['name']} | {m['race']} | {desc} | {prompt} | {attr_str} | {m.get('xp_reward',0)} | {loot} |")

    # --- Quests ---
    lines.append("\n## Quests")
    lines.append("| Title | Type | Description | Visual Prompt | Rewards |")
    lines.append("|---|---|---|---|---|")

    quests = sorted(loader.quests_data, key=lambda x: x['title'])
    for q in quests:
        rewards = ", ".join(q.get('rewards', []))
        prompt = q.get('image_prompt', '')
        lines.append(f"| {q['title']} | {q.get('type','Side')} | {q['description']} | {prompt} | {rewards} |")

    # --- Locations ---
    lines.append("\n## Locations")
    lines.append("| Name | Type | Description | Positive Prompt | Negative Prompt |")
    lines.append("|---|---|---|---|---|")

    locations = sorted(loader.locations_data, key=lambda x: x['name'])
    for l in locations:
        lines.append(f"| {l['name']} | {l['type']} | {l['description']} | {l['image_prompt_positive']} | {l['image_prompt_negative']} |")

    # --- Lore ---
    lines.append("\n## Lore")
    lines.append("| Title | Category | Text | Visual Prompt |")
    lines.append("|---|---|---|---|")

    lore = sorted(loader.lore_data, key=lambda x: x['title'])
    for l in lore:
        prompt = l.get('image_prompt', '')
        lines.append(f"| {l['title']} | {l['category']} | {l['text']} | {prompt} |")

    # --- Characters ---
    lines.append("\n## Characters")
    lines.append("| Name | Race | Faction | Description | Visual Prompt |")
    lines.append("|---|---|---|---|---|")

    chars = sorted(loader.characters_data, key=lambda x: x['name'])
    for c in chars:
        prompt = c.get('image_prompt', '')
        desc = c.get('description', '')
        faction = c.get('faction', 'None')
        lines.append(f"| {c['name']} | {c['race']} | {faction} | {desc} | {prompt} |")

    # --- Example Builds ---
    lines.append("\n## Example Builds")

    example_builds = [
        (["Fire", "Earth", "Potent"], "Power"),
        (["Dark", "Blood", "Sin"], "Recovery"),
        (["Might", "Swift", "Light"], "Speed"),
        (["Gun", "Armor", "Technology"], "Spirit")
    ]

    for i, (bases, bond_attr) in enumerate(example_builds):
        char = Character(name=f"Example {i+1}", race="Human")
        # Add bases
        essence_objs = []
        for b_name in bases:
            e = loader.get_essence(b_name)
            if e:
                essence_objs.append(e)
                char.add_essence(e, bond_attr)

        # Confluence
        try:
            conf = confluence_mgr.determine_confluence(essence_objs)
            char.add_essence(conf, bond_attr)

            lines.append(f"\n### Build {i+1}: {conf.name} Archetype")
            lines.append(f"- **Base Essences**: {', '.join([e.name for e in essence_objs])}")
            lines.append(f"- **Confluence**: {conf.name} ({conf.description})")
            lines.append(f"- **Primary Attribute Bond**: {bond_attr}")
            lines.append(f"- **Growth Multiplier for {bond_attr}**: {char.attributes[bond_attr].growth_multiplier}x")
        except Exception as e:
            lines.append(f"\n### Build {i+1}: Failed to generate ({str(e)})")

    with open(filepath, "w") as f:
        f.write("\n".join(lines))

    print(f"Library generated at {filepath}")

if __name__ == "__main__":
    generate_library_md()
