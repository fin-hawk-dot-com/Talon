import json
import os
import sys

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return []
    with open(path, 'r') as f:
        return json.load(f)

def save_json(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Updated {filename}")

def update_essences():
    data = load_json('essences.json')
    for item in data:
        if 'image_prompt' not in item or not item['image_prompt']:
            tags = ", ".join(item.get('tags', []))
            desc = item.get('description', '')
            rarity = item.get('rarity', 'Common')
            name = item.get('name', 'Unknown')
            prompt = f"An ethereal essence orb representing {name}. Visual style: {rarity} magic, glowing with {tags} energy. {desc}"
            item['image_prompt'] = prompt
    save_json('essences.json', data)

def update_stones():
    data = load_json('awakening_stones.json')
    for item in data:
        if 'image_prompt' not in item or not item['image_prompt']:
            name = item.get('name', 'Stone')
            func = item.get('function', 'Power')
            desc = item.get('description', '')
            rarity = item.get('rarity', 'Common')
            prompt = f"A {rarity} Awakening Stone named {name}, inscribed with runes of {func}. {desc} Glowing magical artifact."
            item['image_prompt'] = prompt
    save_json('awakening_stones.json', data)

def update_monsters():
    data = load_json('monsters.json')
    for item in data:
        # Monster might not have description, so we use name/race
        if 'image_prompt' not in item or not item['image_prompt']:
            name = item.get('name', 'Monster')
            race = item.get('race', 'Beast')
            prompt = f"A dangerous {race} creature known as {name}. High fantasy art style, detailed creature design."
            item['image_prompt'] = prompt

        # Ensure description exists
        if 'description' not in item or not item['description']:
            item['description'] = f"A {item.get('race', 'creature')} known as {item.get('name', 'it')}."

    save_json('monsters.json', data)

def update_factions():
    data = load_json('factions.json')
    for item in data:
        if 'image_prompt' not in item or not item['image_prompt']:
            name = item.get('name', 'Faction')
            desc = item.get('description', '')
            ftype = item.get('type', 'Organization')
            prompt = f"Emblem or headquarters of {name}, a {ftype} faction. {desc} Fantasy setting."
            item['image_prompt'] = prompt
    save_json('factions.json', data)

def update_quests():
    data = load_json('quests.json')
    for item in data:
        if 'image_prompt' not in item or not item['image_prompt']:
            title = item.get('title', 'Quest')
            desc = item.get('description', '')
            prompt = f"Fantasy illustration depicting the quest '{title}'. {desc}"
            item['image_prompt'] = prompt
    save_json('quests.json', data)

def update_lore():
    data = load_json('lore.json')
    for item in data:
        if 'image_prompt' not in item or not item['image_prompt']:
            title = item.get('title', 'Lore')
            cat = item.get('category', 'History')
            prompt = f"An ancient illustration or text related to {title} ({cat}). Parchment style or historical scene."
            item['image_prompt'] = prompt
    save_json('lore.json', data)

def update_characters():
    data = load_json('characters.json')
    for item in data:
        if 'image_prompt' not in item or not item['image_prompt']:
            name = item.get('name', 'Character')
            race = item.get('race', 'Human')
            desc = item.get('description', '')
            prompt = f"A {race} character named {name}. {desc} Fantasy portrait."
            item['image_prompt'] = prompt
    save_json('characters.json', data)

# Locations already have prompts, but we can double check
def update_locations():
    data = load_json('locations.json')
    updated = False
    for item in data:
        if 'image_prompt_positive' not in item:
            item['image_prompt_positive'] = f"A fantasy location: {item.get('name')}. {item.get('description')}"
            updated = True
        if 'image_prompt_negative' not in item:
            item['image_prompt_negative'] = "blurry, low quality, distortion"
            updated = True
    if updated:
        save_json('locations.json', data)

def main():
    print("Updating Essences...")
    update_essences()
    print("Updating Stones...")
    update_stones()
    print("Updating Monsters...")
    update_monsters()
    print("Updating Factions...")
    update_factions()
    print("Updating Quests...")
    update_quests()
    print("Updating Lore...")
    update_lore()
    print("Updating Characters...")
    update_characters()
    print("Updating Locations...")
    update_locations()
    print("All updates complete.")

if __name__ == "__main__":
    main()
