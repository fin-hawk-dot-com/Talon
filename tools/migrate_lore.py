import json
import os
import re
import shutil

DATA_DIR = 'data'
LORE_LIBRARY_DIR = os.path.join(DATA_DIR, 'lore_library')

def slugify(text):
    text = text.lower()
    return re.sub(r'[\W_]+', '_', text).strip('_')

def load_json(filename):
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print(f"Error decoding {filename}")
                return []
    return []

def main():
    lore_data = load_json('lore.json')
    monsters_data = load_json('monsters.json')
    locations_data = load_json('locations.json')
    characters_data = load_json('characters.json')
    factions_data = load_json('factions.json')

    # Map for specialized data lookup
    monsters_map = {m['name']: m for m in monsters_data}
    locations_map = {l['name']: l for l in locations_data}
    characters_map = {c['name']: c for c in characters_data}
    factions_map = {f['name']: f for f in factions_data}

    # Category mapping
    category_map = {
        'Bestiary': 'monsters',
        'Location': 'locations',
        'Character': 'characters',
        'Faction': 'factions',
        'History': 'history',
        'Magic': 'magic',
        'Artifacts': 'artifacts',
        'Culture': 'culture',
        'Society': 'society',
        'Religion': 'religion'
    }

    processed_entries = set()

    print(f"Starting migration to {LORE_LIBRARY_DIR}...")

    # Process lore.json
    for entry in lore_data:
        title = entry.get('title')
        if not title:
            continue

        slug = slugify(title)
        category = entry.get('category', 'misc')
        folder_category = category_map.get(category, 'misc')

        # Determine specialized data
        specialized_data = {}
        if folder_category == 'monsters':
            if title in monsters_map:
                specialized_data = monsters_map[title]
        elif folder_category == 'locations':
            if title in locations_map:
                specialized_data = locations_map[title]
        elif folder_category == 'characters':
            if title in characters_map:
                 specialized_data = characters_map[title]
        elif folder_category == 'factions':
            if title in factions_map:
                specialized_data = factions_map[title]

        # Merge data
        merged_data = entry.copy()
        if specialized_data:
            merged_data.update(specialized_data)
            # Ensure title from lore.json is preserved if needed, but name is usually same.


        # Create directory
        entry_dir = os.path.join(LORE_LIBRARY_DIR, folder_category, slug)
        os.makedirs(entry_dir, exist_ok=True)

        # Write metadata.json
        with open(os.path.join(entry_dir, 'metadata.json'), 'w') as f:
            json.dump(merged_data, f, indent=4)

        # Create placeholder assets
        for asset in ['image.png', 'info_card.png']:
            asset_path = os.path.join(entry_dir, asset)
            if not os.path.exists(asset_path):
                with open(asset_path, 'wb') as f:
                    pass

        processed_entries.add((folder_category, title))
        # print(f"Processed {title} -> {folder_category}/{slug}")

    # Process remaining specialized data

    # Monsters
    for monster in monsters_data:
        name = monster.get('name')
        if not name: continue
        slug = slugify(name)
        # Check if already processed (could have different title in lore.json, but we can only check exact name match here easily)
        # If the monster was in lore.json with same name, it's in processed_entries.
        # If it had a different name in lore.json, we might duplicate it. That's a risk we accept for now.

        if ('monsters', name) not in processed_entries:
            # Check directory existence to be safe
            entry_dir = os.path.join(LORE_LIBRARY_DIR, 'monsters', slug)
            if os.path.exists(entry_dir):
                continue

            os.makedirs(entry_dir, exist_ok=True)
            with open(os.path.join(entry_dir, 'metadata.json'), 'w') as f:
                json.dump(monster, f, indent=4)

            for asset in ['image.png', 'info_card.png']:
                with open(os.path.join(entry_dir, asset), 'wb') as f: pass

            print(f"Created new monster entry: {name}")

    # Locations
    for location in locations_data:
        name = location.get('name')
        if not name: continue
        slug = slugify(name)
        if ('locations', name) not in processed_entries:
            entry_dir = os.path.join(LORE_LIBRARY_DIR, 'locations', slug)
            if os.path.exists(entry_dir): continue

            os.makedirs(entry_dir, exist_ok=True)
            with open(os.path.join(entry_dir, 'metadata.json'), 'w') as f:
                json.dump(location, f, indent=4)

            for asset in ['image.png', 'info_card.png']:
                with open(os.path.join(entry_dir, asset), 'wb') as f: pass
            print(f"Created new location entry: {name}")

    # Characters
    for char in characters_data:
        name = char.get('name')
        if not name: continue
        slug = slugify(name)
        if ('characters', name) not in processed_entries:
            entry_dir = os.path.join(LORE_LIBRARY_DIR, 'characters', slug)
            if os.path.exists(entry_dir): continue

            os.makedirs(entry_dir, exist_ok=True)
            with open(os.path.join(entry_dir, 'metadata.json'), 'w') as f:
                json.dump(char, f, indent=4)

            for asset in ['image.png', 'info_card.png']:
                with open(os.path.join(entry_dir, asset), 'wb') as f: pass
            print(f"Created new character entry: {name}")

    # Factions
    for faction in factions_data:
        name = faction.get('name')
        if not name: continue
        slug = slugify(name)
        if ('factions', name) not in processed_entries:
            entry_dir = os.path.join(LORE_LIBRARY_DIR, 'factions', slug)
            if os.path.exists(entry_dir): continue

            os.makedirs(entry_dir, exist_ok=True)
            with open(os.path.join(entry_dir, 'metadata.json'), 'w') as f:
                json.dump(faction, f, indent=4)

            for asset in ['image.png', 'info_card.png']:
                with open(os.path.join(entry_dir, asset), 'wb') as f: pass
            print(f"Created new faction entry: {name}")

    print("Migration complete.")

if __name__ == '__main__':
    main()
