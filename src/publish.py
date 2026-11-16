"""Safely queue only @dreamy_elsewhere on Buffer Free.

Requires BUFFER_API_KEY, AUTO_PUBLISH=true and five finished images per Reel.
Silent clips are permitted under the user's current launch policy. Never targets
@blinkpuzz or another channel.
"""
import json
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo
import requests
from schedule import ROOT, CONFIG, scheduled_at, slots_for, marker

API = "https://api.buffer.com"
EXPECTED_HANDLE = "dreamy_elsewhere"
TZ = ZoneInfo(CONFIG["timezone"])
TOKEN = os.getenv("BUFFER_API_KEY", "")

def gql(query, variables=None):
    response = requests.post(API, json={"query": query, "variables": variables or {}},
                             headers={"Authorization": "Bearer " + TOKEN,
                                      "Content-Type": "application/json"}, timeout=35)
    response.raise_for_status()
    body = response.json()
    if body.get("errors"):
        raise RuntimeError("Buffer: " + str(body["errors"])[:700])
    return body["data"]

def channel():
    organizations = gql("query { account { organizations { id name } } }")["account"]["organizations"]
    query = """query Channels($org: OrganizationId!) {
      channels(input:{organizationId:$org}) {
        id name service isLocked isDisconnected isQueuePaused
      }
    }"""
    matches = []
    for org in organizations:
        for item in gql(query, {"org": org["id"]})["channels"]:
            if item["name"].strip().lower().lstrip("@") == EXPECTED_HANDLE:
                if str(item["service"]).lower() != "instagram":
                    raise RuntimeError("Handle matches but service is not Instagram")
                matches.append((org["id"], item))
    if len(matches) != 1:
        raise RuntimeError(f"Expected one exact Instagram @{EXPECTED_HANDLE}; found {len(matches)}")
    org, item = matches[0]
    if item["isLocked"] or item["isDisconnected"] or item["isQueuePaused"]:
        raise RuntimeError("Target channel unavailable")
    return org, item["id"]

def existing_posts(org, channel_id):
    query = """query Posts($org: OrganizationId!, $channel: ChannelId!, $cursor: String) {
      posts(first:100,after:$cursor,input:{organizationId:$org,filter:{channelIds:[$channel]}}){
        edges{node{id text status dueAt}} pageInfo{hasNextPage endCursor}
      }
    }"""
    result = []
    cursor = None
    for _ in range(10):
        page = gql(query, {"org": org, "channel": channel_id, "cursor": cursor})["posts"]
        result.extend(edge["node"] for edge in page["edges"])
        if not page["pageInfo"]["hasNextPage"]:
            return result
        cursor = page["pageInfo"]["endCursor"]
        if not cursor:
            raise RuntimeError("Invalid Buffer pagination")
    raise RuntimeError("Post list unexpectedly long; aborting safely")

def video_ready(url):
    try:
        response = requests.get(url, headers={"Range": "bytes=0-1023"},
                                stream=True, timeout=25)
        ok = response.status_code in (200, 206) and (
            "video/" in response.headers.get("Content-Type", "").lower()
            or "octet-stream" in response.headers.get("Content-Type", "").lower())
        response.close()
        return ok
    except requests.RequestException:
        return False

def create_post(channel_id, meta, url, when):
    mutation = """mutation CreatePost($input: CreatePostInput!) {
      createPost(input:$input){
        ... on PostActionSuccess { post { id status dueAt } }
        ... on MutationError { message }
      }
    }"""
    payload = {
        "channelId": channel_id,
        "text": meta["caption"] + "\n\nDreamy ID: " + meta["marker"],
        "schedulingType": "automatic", "mode": "customScheduled",
        "dueAt": when.astimezone(ZoneInfo("UTC")).isoformat().replace("+00:00", "Z"),
        "metadata": {"instagram": {"type": "reel", "shouldShareToFeed": True}},
        "assets": [{"video": {"url": url, "metadata": {"thumbnailOffset": 1000}}}],
    }
    result = gql(mutation, {"input": payload})["createPost"]
    if not result.get("post"):
        raise RuntimeError("Buffer refused scheduling: " + str(result.get("message", result)))
    return result["post"]

def main():
    if not TOKEN:
        print("Buffer API token not configured; no publishing or connection verification.")
        return 0
    org, channel_id = channel()
    print(f"Verified EXACT Instagram channel @{EXPECTED_HANDLE}; other accounts excluded.")
    if os.getenv("AUTO_PUBLISH", "").lower() != "true":
        print("CHECK-ONLY: AUTO_PUBLISH not enabled; no posts created.")
        return 0

    posts = existing_posts(org, channel_id)
    markers = set()
    planned_times = set()
    active = 0
    now = datetime.now(TZ)
    for post in posts:
        for line in (post.get("text") or "").splitlines():
            if line.startswith("Dreamy ID: "):
                markers.add(line.split(": ", 1)[1].strip())
        if str(post.get("status", "")).lower() in {"sent", "error", "failed", "draft"}:
            continue
        raw = post.get("dueAt")
        if not raw:
            active += 1
            continue
        try:
            when = datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(TZ)
        except ValueError:
            active += 1
            continue
        if when >= now:
            active += 1
            planned_times.add(when.isoformat())
    capacity = max(0, CONFIG["max_queued"] - active)
    if capacity == 0:
        print("Buffer Free queue full; no new posts.")
        return 0

    candidates = []
    for file in sorted((ROOT / "docs/media").glob("*.json")):
        meta = json.loads(file.read_text(encoding="utf-8"))
        day = date.fromisoformat(meta["date"])
        slot = meta["slot"]
        slots = dict(slots_for(day))
        if slot not in slots or meta.get("marker") != marker(day, slot):
            continue
        when = scheduled_at(day, slots[slot])
        if meta["marker"] in markers or when.isoformat() in planned_times:
            continue
        if not now + timedelta(minutes=5) < when <= now + timedelta(days=9):
            continue
        if meta.get("audio_status") not in {"CLEARED_AUDIO", "SILENT"}:
            print("SKIP", meta["marker"], ": unknown audio status")
            continue
        candidates.append((when, meta))

    count = 0
    for when, meta in sorted(candidates, key=lambda item: item[0])[:capacity]:
        url = CONFIG["public_media_base"].rstrip("/") + "/" + quote(meta["video"])
        if not video_ready(url):
            print("SKIP", meta["marker"], ": video URL not ready")
            continue
        result = create_post(channel_id, meta, url, when)
        print("SCHEDULED", meta["marker"], result["id"])
        count += 1
    print(f"Queued {count} Reels; expected occupied slots {active + count}/{CONFIG['max_queued']}.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
