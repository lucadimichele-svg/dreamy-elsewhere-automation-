"""Persistent one-theme/five-variants story plans for Dreamy Elsewhere.

The ChatGPT scheduled producer authors creative decisions; code only validates their
structure and gives the renderer authoritative labels. No subjective image scoring.
Every new plan in assets/creative_plans is a durable, inspectable history entry.
"""
import argparse
import json
from datetime import date
from pathlib import Path

from schedule import ROOT, CONFIG, reel_key
from scene_integrity import check_new_plan_fields, SubjectMismatch

PLANS = ROOT / "assets" / "creative_plans"
MEDIA = ROOT / "docs" / "media"
# Preserve completed and in-progress initial launch reels made with old manifests.
NEW_MODE_FROM = (date(2026, 11, 18), "S3")


class CreativePlanError(ValueError):
    pass


def validate_plan(data, stem):
    if not isinstance(data, dict):
        raise CreativePlanError("Creative plan must be a JSON object")
    if stem != f"{data.get('date')}_{data.get('slot')}":
        raise CreativePlanError("Creative plan date/slot differs from filename")
    topic = data.get("topic")
    category = data.get("theme_category")
    variants = data.get("variants")
    if not isinstance(topic, str) or not 8 <= len(topic.strip()) <= 92:
        raise CreativePlanError("Creative plan needs one English theme/question (8-92 chars)")
    if not isinstance(category, str) or not 3 <= len(category.strip()) <= 70:
        raise CreativePlanError("Creative plan needs a descriptive, freely chosen theme_category")
    if not isinstance(variants, list) or len(variants) != 5:
        raise CreativePlanError("Creative plan needs exactly five variants")
    seen = set()
    for index, item in enumerate(variants, 1):
        if not isinstance(item, dict):
            raise CreativePlanError(f"Variant {index} is not an object")
        label = item.get("label")
        brief = item.get("brief")
        if not isinstance(label, str) or not 3 <= len(label.strip()) <= 36:
            raise CreativePlanError(f"Variant {index} needs a 3-36 character English label")
        if not isinstance(brief, str) or not 12 <= len(brief.strip()) <= 800:
            raise CreativePlanError(f"Variant {index} needs a one-scene description")
        prompt = item.get("image_prompt")
        if prompt is not None and (not isinstance(prompt, str) or len(prompt.strip()) < 35):
            raise CreativePlanError(f"Variant {index} has invalid image_prompt")
        canonical = label.casefold().strip()
        if canonical in seen:
            raise CreativePlanError("Two variants have identical labels")
        seen.add(canonical)
    check_new_plan_fields(data, stem)
    return data


def load_for_render(day, slot):
    """Use prewritten new plan, never invent a new theme at render time."""
    stem = reel_key(day, slot)
    path = PLANS / f"{stem}.json"
    if path.exists():
        return validate_plan(json.loads(path.read_text(encoding="utf-8")), stem)
    # Old manifests without plans were already made using the legacy theme cycle.
    if day < NEW_MODE_FROM[0] or (day == NEW_MODE_FROM[0] and slot in ("S1", "S2")):
        legacy = CONFIG.get("legacy_topics", CONFIG.get("topics", []))
        if not legacy:
            raise CreativePlanError("Legacy topic list missing for historical reel")
        offset = (day - date.fromisoformat(CONFIG["launch_date"])).days
        topic = legacy[(offset * 4 + int(slot[1:]) - 1) % len(legacy)]
        return {"date":str(day),"slot":slot,"topic":topic,
                "theme_category":"legacy_cozy",
                "variants":[{"label":f"CHOICE {i:02d}","brief":"Legacy Reel"} for i in range(1,6)],
                "mode":"legacy"}
    raise CreativePlanError(
        f"Missing theme/variant plan assets/creative_plans/{stem}.json — "
        "the fixed 10-topic rotation is retired for new reels.")


def recent_history(limit=50):
    """Recent saved themes from planned and older rendered slots, no fixed pool."""
    entries = {}
    for path in sorted(MEDIA.glob("????-??-??_S?.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data.get("topic"), str):
                entries[path.stem] = {"id":path.stem,"topic":data["topic"],
                    "theme_category":data.get("theme_category", "legacy_cozy"),
                    "variants":data.get("variants", []),"status":"rendered"}
        except (ValueError, OSError):
            pass
    for path in sorted(PLANS.glob("????-??-??_S?.json")):
        try:
            data = validate_plan(json.loads(path.read_text(encoding="utf-8")), path.stem)
            entries[path.stem] = {"id":path.stem,"topic":data["topic"],
                "theme_category":data["theme_category"],
                "variants":[v["label"] for v in data["variants"]],
                "status":"planned" if path.stem not in entries else "rendered"}
        except (CreativePlanError, ValueError, OSError, TypeError):
            pass
    return [entries[k] for k in sorted(entries, reverse=True)[:limit]]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--history", action="store_true")
    parser.add_argument("--check")
    args = parser.parse_args()
    if args.history:
        print(json.dumps(recent_history(),ensure_ascii=False,indent=2))
    if args.check:
        path = Path(args.check)
        data = validate_plan(json.loads(path.read_text(encoding="utf-8")), path.stem)
        print("PASS creative plan:",data["topic"],"/",len(data["variants"]),"variants")


if __name__ == "__main__":
    main()
