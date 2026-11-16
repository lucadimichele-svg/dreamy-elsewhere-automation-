"""Publishing cadence for Dreamy Elsewhere; local Europe/Berlin time."""
import json
from pathlib import Path
from datetime import date, datetime, time
from zoneinfo import ZoneInfo
ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
TZ = ZoneInfo(CONFIG["timezone"])
START = date.fromisoformat(CONFIG["launch_date"])
END = START.toordinal() + CONFIG["boost_days"]
def slots_for(day):
    clocks = CONFIG["boost_times"] if START <= day and day.toordinal() < END else CONFIG["ongoing_times"]
    return [(f"S{i}", clock) for i, clock in enumerate(clocks, 1)]
def scheduled_at(day, clock):
    hh, mm = map(int, clock.split(":"))
    return datetime.combine(day, time(hh, mm), tzinfo=TZ)
def reel_key(day, slot):
    return f"{day.isoformat()}_{slot}"
def marker(day, slot):
    return "DE" + day.strftime("%Y%m%d") + slot
