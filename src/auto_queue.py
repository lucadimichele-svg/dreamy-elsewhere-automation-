"""Automatic Buffer queue for only the Dreamy Elsewhere Instagram profile.

Invoked from a segregated GitHub Actions bridge holding an existing Buffer
credential. Never reads or mutates BlinkPuzz posts. Duplicate-safe by marker.
Only posts genuinely rendered Dreamy Reels with licensed embedded audio.
"""
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import quote

import requests
from zoneinfo import ZoneInfo

import publish as buffer
from schedule import CONFIG, scheduled_at, slots_for, marker

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "docs" / "media"
TZ = ZoneInfo("Europe/Berlin")
VIDEO_BASE = (
    "https://raw.githubusercontent.com/"
    "lucadimichele-svg/dreamy-elsewhere-automation-/main/docs/media"
)
LIMIT_PER_RUN = 3
FREE_QUEUE_LIMIT = 10

def video_ready(url):
    try:
        with requests.get(url, headers={"Range": "bytes=0-2047"}, timeout=25, stream=True) as response:
            if response.status_code not in (200, 206):
                return False
            ctype = response.headers.get("Content-Type", "").lower()
            if not ("video/" in ctype or "octet-stream" in ctype):
                return False
            data = bytearray()
            for chunk in response.iter_content(2048):
                data.extend(chunk)
                if len(data) >= 16:
                    break
            return len(data) >= 16 and data[4:8] == b"ftyp"
    except requests.RequestException:
        return False

def main():
    if not buffer.TOKEN:
        raise SystemExit("Missing BUFFER_API_KEY; no publication attempted")
    if buffer.EXPECTED_HANDLE != "dreamy_elsewhere":
        raise SystemExit("Wrong target handle; no publication attempted")
    org, channel_id = buffer.channel()  # Exact handle + Instagram + active checks.
    print("PASS: verified exact Instagram @dreamy_elsewhere")
    posts = buffer.existing_posts(org, channel_id)
    existing_markers = set()
    planned_times = set()
    active = 0
    now = datetime.now(TZ)

    for post in posts:
        for line in (post.get("text") or "").splitlines():
            if line.startswith("Dreamy ID: "):
                existing_markers.add(line[len("Dreamy ID: "):].strip())
        status = str(post.get("status", "")).lower()
        if status in ("sent", "error", "failed", "draft"):
            continue
        due = post.get("dueAt")
        if not due:
            active += 1
            continue
        try:
            dt = datetime.fromisoformat(due.replace("Z", "+00:00")).astimezone(TZ)
            if dt >= now:
                active += 1
                planned_times.add(dt.isoformat())
        except (ValueError, TypeError):
            active += 1

    capacity = max(0, FREE_QUEUE_LIMIT - active)
    if not capacity:
        print("Buffer queue full; no new Dreamy posts")
        return 0

    candidates = []
    for p in sorted(MEDIA.glob("????-??-??_S?.json")):
        try:
            metadata = json.loads(p.read_text(encoding="utf-8"))
            day = date.fromisoformat(metadata["date"])
            slot = metadata["slot"]
            key = marker(day, slot)
            clocks = dict(slots_for(day))
            if (slot not in clocks or metadata.get("marker") != key or
                    metadata.get("image_count") != 5 or
                    metadata.get("audio_status") != "EMBEDDED_AUDIO" or
                    metadata.get("duration_seconds") != 15):
                continue
            if metadata.get("video") != p.stem + ".mp4":
                continue
            if key in existing_markers:
                continue
            when = scheduled_at(day, clocks[slot])
            if when.isoformat() in planned_times:
                continue
            # Do not post stale content. Slightly late slots are shared right away.
            # A delayed scheduled GitHub run must not silently discard a valid
            # finished Reel after only three hours. Six-hour same-day
            # recovery is bounded; older missed slots are never revived.
            if not now - timedelta(hours=6) <= when <= now + timedelta(days=2):
                continue
            if not (MEDIA / metadata["video"]).is_file():
                continue
            candidates.append((when, key, metadata))
        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            continue

    created = 0
    for when, key, metadata in sorted(candidates, key=lambda x: (x[0], x[1])):
        if created >= min(LIMIT_PER_RUN, capacity):
            break
        url = VIDEO_BASE + "/" + quote(metadata["video"])
        if not video_ready(url):
            print("NOT READY", key, "public MP4 unavailable; no Buffer post")
            continue
        if when > now + timedelta(minutes=5):
            result = buffer.create_post(channel_id, metadata, url, when)
            print("BUFFER SCHEDULED", key, result["id"], when.isoformat(),
                  result.get("status"))
        else:
            query = """mutation CreatePost($input: CreatePostInput!) {
              createPost(input:$input) {
                ... on PostActionSuccess { post { id status } }
                ... on MutationError { message }
              }
            }"""
            payload = {
                "channelId": channel_id,
                "text": metadata["caption"] + "\n\nDreamy ID: " + key,
                "schedulingType": "automatic",
                "mode": "shareNow",
                "metadata": {"instagram": {"type": "reel", "shouldShareToFeed": True}},
                "assets": [{"video": {"url": url, "metadata": {"thumbnailOffset": 1000}}}],
            }
            result = buffer.gql(query, {"input": payload})["createPost"]
            if not result.get("post"):
                raise RuntimeError("Buffer rejected Dreamy post " + key + ": " +
                                   str(result.get("message", result)))
            print("BUFFER SHARE NOW", key, result["post"]["id"], result["post"].get("status"))
        created += 1

    print("Dreamy new Buffer posts:", created, "previously queued:", active,
          "available slots before run:", capacity)
    return 0

if __name__ == "__main__":
    sys.exit(main())
