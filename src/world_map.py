from typing import List, Dict
from src.mechanics import DataLoader

class MapVisualizer:
    def __init__(self, data_loader: DataLoader):
        self.loader = data_loader

    def display_map(self):
        locations = self.loader.get_all_locations()
        # Group by Region
        by_region = {}
        for loc in locations:
            if loc.region not in by_region:
                by_region[loc.region] = []
            by_region[loc.region].append(loc)

        print("\n=== WORLD MAP ===")
        # Custom order: Northern, Central, Eastern, Western, Southern, Deep Earth, Void
        region_order = ["Northern Peaks", "Central Plains", "Western Coast", "Eastern Swamps", "Southern Badlands", "Deep Earth", "Void"]
        sorted_regions = sorted(by_region.keys(), key=lambda r: region_order.index(r) if r in region_order else 99)

        for region in sorted_regions:
            print(f"\n[{region}]")
            for loc in by_region[region]:
                print(f"  * {loc.name} (Rank: {loc.danger_rank})")
                if loc.connected_locations:
                    print("      Connects to:")
                    for conn_name in loc.connected_locations:
                        conn_loc = self.loader.get_location(conn_name)
                        if conn_loc and conn_loc.region != region:
                            print(f"        -> {conn_name} ({conn_loc.region})")
                        else:
                            print(f"        -> {conn_name}")

        print("\n=================")
