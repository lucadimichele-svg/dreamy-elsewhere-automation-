"""Publish exactly one finished Dreamy Elsewhere Reel through Buffer, once.

Only @dreamy_elsewhere. Never accesses any other channel's posts or secrets.
Refuses to post without the exact media marker, five images, embedded audio
and a directly downloadable MP4. A repeated run is duplicate-safe.
"""
import json
import os
import sys
import time
from pathlib import Path

import requests
import publish as buffer

MARKER = "DE20261117S1"
MANIFEST = Path("docs/media/2026-11-17_S1.json")
EXPECTED_VIDEO = "2026-11-17_S1.mp4"
VIDEO_URLS = [
    "https://lucadimichele-svg.github.io/dreamy-elsewhere-automation-/media/" + EXPECTED_VIDEO,
    "https://raw.githubusercontent.com/lucadimichele-svg/dreamy-elsewhere-automation-/main/docs/media/" + EXPECTED_VIDEO,
]

def playable_mp4(url):
    try:
        with requests.get(url, timeout=30, headers={"Range": "bytes=0-4095"}, stream=True) as response:
            if response.status_code not in (200, 206):
                print("Media candidate unavailable:", response.status_code)
                return False
            mime = response.headers.get("Content-Type", "").split(";")[0].strip().lower()
            if mime not in {"video/mp4", "application/octet-stream", "binary/octet-stream"}:
                print("Media candidate not a direct video download:", mime)
                return False
            data = bytearray()
            for chunk in response.iter_content(chunk_size=4096):
                data += chunk
                if len(data) >= 16:
                    break
            return len(data) >= 12 and data[4:8] == b"ftyp"
    except requests.RequestException as error:
        print("Media candidate unavailable:", type(error).__name__)
        return False

def main():
    if os.getenv("DREAMY_POST_ONCE", "").lower() != "true":
        raise SystemExit("Not enabled: DREAMY_POST_ONCE is not true")
    if not os.getenv("BUFFER_API_KEY"):
        raise SystemExit("Missing Buffer API key")
    if buffer.EXPECTED_HANDLE != "dreamy_elsewhere":
        raise SystemExit("Wrong target handle; refusing to post")

    meta = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if (meta.get("marker"), meta.get("video"), meta.get("image_count"), meta.get("audio_status")) != (
        MARKER, EXPECTED_VIDEO, 5, "EMBEDDED_AUDIO"
    ):
        raise SystemExit("Wrong Reel or incomplete media; refusing to post")
    caption = meta["caption"] + "\n\nDreamy ID: " + MARKER
    org, channel_id = buffer.channel()
    print("PASS: exact Instagram @dreamy_elsewhere verified")

    posts = buffer.existing_posts(org, channel_id)
    duplicates = [p for p in posts if ("Dreamy ID: " + MARKER) in (p.get("text") or "")]
    if duplicates:
        print("SKIP duplicate Reel; existing Buffer post(s):", [(p["id"], p["status"]) for p in duplicates])
        return 0

    video_url = next((url for url in VIDEO_URLS if playable_mp4(url)), None)
    if not video_url:
        raise SystemExit("No publicly downloadable MP4; Buffer posting stopped")
    print("PASS: full Reel is publicly downloadable from:", video_url)

    if len([p for p in posts if str(p.get("status", "")).lower() in {"sending", "scheduled"}]) >= 10:
        print("Note: channel has ten scheduled posts, attempting shareNow for this one-off user-requested publication")

    mutation = """mutation CreatePost($input: CreatePostInput!) {
      createPost(input: $input) {
        ... on PostActionSuccess { post { id status sentAt externalLink } }
        ... on MutationError { message }
      }
    }"""
    args = {
        "channelId": channel_id,
        "text": caption,
        "schedulingType": "automatic",
        "mode": "shareNow",
        "aiAssisted": True,
        "metadata": {"instagram": {"type": "reel", "shouldShareToFeed": True}},
        "assets": [{"video": {"url": video_url, "metadata": {"thumbnailOffset": 1000}}}],
    }
    result = buffer.gql(mutation, {"input": args})["createPost"]
    if not result.get("post"):
        raise RuntimeError("Buffer rejected the Dreamy Reel: " + str(result.get("message", result)))
    post = result["post"]
    print("BUFFER ACCEPTED", MARKER, "post_id=", post["id"], "status=", post.get("status"))
    if post.get("externalLink"):
        print("INSTAGRAM LINK:", post["externalLink"])
    if str(post.get("status")).lower() == "sent":
        print("CONFIRMED PUBLISHED by Buffer")
        return 0
    if str(post.get("status")).lower() == "error":
        raise RuntimeError("Buffer reports publication error for post " + post["id"])

    # Poll only; do not resend even if Buffer remains pending.
    for attempt in range(8):
        time.sleep(10)
        current = next((p for p in buffer.existing_posts(org, channel_id) if p["id"] == post["id"]), None)
        if not current:
            print("Delivery status not available yet; no repeat submission.")
            continue
        status = str(current.get("status") or "").lower()
        print("Delivery verification", attempt + 1, status)
        if status == "sent":
            print("CONFIRMED PUBLISHED by Buffer; post_id=", post["id"])
            return 0
        if status == "error":
            raise RuntimeError("Buffer delivery failed for post " + post["id"])
    print("Buffer has accepted the post but Instagram delivery is not yet verified.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
