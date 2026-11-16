"""Build five distinct visual briefs around one Reel theme; no image generation."""
import argparse
import json
from datetime import date
from pathlib import Path
from schedule import ROOT, CONFIG

SCENES = {
    "Which cozy bed would you choose?": [
        ("Snowbound alpine loft", "rustic timber attic", "low view from foot of bed", "snowy mountain ridge", "blue dawn and firelight"),
        ("Rainforest treehouse", "circular timber room", "high angle from stair landing", "misty canopy", "soft overcast morning"),
        ("City skyline retreat", "minimalist concrete penthouse", "wide diagonal view from doorway", "rainy city skyline", "deep blue night"),
        ("Mediterranean hideaway", "whitewashed stone room", "side view from open balcony", "sea cliffs", "warm sunset"),
        ("Desert stargazing suite", "adobe and glass room", "view inward from courtyard", "desert night sky", "moonlight"),
    ]
}
ARCH = ["alpine stone cottage", "Japanese timber pavilion", "Mediterranean whitewashed villa", "Nordic lakeside cabin", "industrial glass loft"]
VIEWS = ["eye-level view from doorway", "wide view from outdoor terrace", "low side-angle from seating area", "diagonal composition from upper landing", "framed view through arched entrance"]
SETTINGS = ["snowy mountains", "rain-soaked woodland", "still lake", "misty coastal cliffs", "rolling cloud-covered hills"]
LIGHTS = ["winter twilight", "rainy blue hour", "soft sunrise", "foggy morning", "golden sunset"]

def plan(day, slot):
    offset = (day - date.fromisoformat(CONFIG["launch_date"])).days
    index = offset * 4 + int(slot[1:]) - 1
    theme = CONFIG["topics"][index % len(CONFIG["topics"])]
    entries = SCENES.get(theme)
    if not entries:
        entries = [
            (f"Interpretation {i+1}", ARCH[(index+i)%5], VIEWS[(index+i)%5],
             SETTINGS[(index+i)%5], LIGHTS[(index+i)%5])
            for i in range(5)
        ]
    return {
        "reel_id": f"{day.isoformat()}_{slot}", "theme": theme,
        "status": "BRIEFS_ONLY_NOT_GENERATED",
        "scenes": [
            {"number": i, "name": name,
             "prompt": (f"Photorealistic cinematic vertical 9:16 scene for theme '{theme}'. "
                        f"Scene: {name}. Plausible architecture: {arch}. Camera: {camera}. "
                        f"Surroundings: {setting}. Lighting: {light}. "
                        "Distinctive layout and color palette. Realistic materials and structural support. "
                        "No floating furniture, no writing, no typography, no watermarks."),
             "target_path": f"assets/inbox/{day.isoformat()}_{slot}/{i:02d}.jpg"}
            for i, (name, arch, camera, setting, light) in enumerate(entries, 1)
        ]
    }

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--reel", required=True)
    args = p.parse_args()
    day, slot = args.reel.split("_")
    print(json.dumps(plan(date.fromisoformat(day), slot), ensure_ascii=False, indent=2))
