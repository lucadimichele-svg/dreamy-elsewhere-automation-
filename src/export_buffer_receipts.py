"""Read-only Buffer delivery confirmation exporter for @dreamy_elsewhere.

Executed only inside the existing isolated Buffer credential bridge. Writes
small public status receipts in the bridge repo (no tokens/private media).
Only a post with Buffer status SENT, sentAt, and a real Instagram Reel URL
can create a cleanup-eligible receipt.
"""
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import publish as buffer
from schedule import ROOT, marker, slots_for
from datetime import date

STEM = re.compile(r"^\d{4}-\d{2}-\d{2}_S[1-4]$")
DREAMY_REPO = "lucadimichele-svg/dreamy-elsewhere-automation-"


def utcstamp(value):
    if not isinstance(value, str) or not value:
        raise ValueError("No verified sentAt timestamp")
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("No sentAt timezone")
    if dt > datetime.now(timezone.utc):
        raise ValueError("Publication time is in the future")
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def verified_permalink(value):
    if not isinstance(value, str):
        return None
    parts = urlsplit(value)
    if (parts.scheme != "https" or parts.hostname not in
            ("instagram.com", "www.instagram.com")):
        return None
    if not re.fullmatch(r"/reel/[A-Za-z0-9_-]+/?", parts.path):
        return None
    return "https://www.instagram.com" + parts.path.rstrip("/") + "/"


def match_post(post):
    if str(post.get("status", "")).lower() != "sent":
        return None
    permalink = verified_permalink(post.get("externalLink"))
    if not permalink:
        return None
    try:
        stamp = utcstamp(post.get("sentAt"))
    except (ValueError, TypeError):
        return None
    lines = (post.get("text") or "").splitlines()
    markers = [v[len("Dreamy ID: "):].strip() for v in lines
               if v.startswith("Dreamy ID: ")]
    if len(markers) != 1:
        return None
    key = markers[0]
    if not re.fullmatch(r"DE\d{8}S[1-4]", key):
        return None
    stem = key[2:6] + "-" + key[6:8] + "-" + key[8:10] + "_" + key[10:]
    if not STEM.fullmatch(stem):
        return None
    return key, stem, stamp, permalink


def export(out):
    if not buffer.TOKEN:
        raise RuntimeError("Missing Buffer token; no receipts written")
    if buffer.EXPECTED_HANDLE != "dreamy_elsewhere":
        raise RuntimeError("Wrong Buffer account identity")
    org, channel_id = buffer.channel()  # Verifies exact Instagram account.
    print("VERIFIED only Instagram @dreamy_elsewhere", flush=True)
    query = """query Posts($org: OrganizationId!, $channel: ChannelId!, $cursor: String) {
      posts(first:100,after:$cursor,input:{organizationId:$org,filter:{channelIds:[$channel]}}){
        edges{node{id channelId text status sentAt externalLink}}
        pageInfo{hasNextPage endCursor}
      }
    }"""
    allposts = []
    cursor = None
    for _ in range(10):
        page = buffer.gql(query, {"org": org, "channel": channel_id,
                                  "cursor": cursor})["posts"]
        allposts.extend(e["node"] for e in page["edges"])
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"].get("endCursor")
        if not cursor:
            raise RuntimeError("Invalid Buffer paging; no receipts")
    else:
        raise RuntimeError("More than 1000 posts; refuse partial confirmation")

    by_stem = {}
    for post in allposts:
        if post.get("channelId") != channel_id:
            continue
        matched = match_post(post)
        if not matched:
            continue
        key, stem, sent, url = matched
        meta_path = ROOT / "docs" / "media" / (stem + ".json")
        if not meta_path.is_file():
            continue
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            day = date.fromisoformat(meta["date"])
            slot = meta["slot"]
            if (meta_path.stem != stem or slot not in dict(slots_for(day))
                    or meta.get("marker") != marker(day,slot)
                    or meta.get("marker") != key
                    or meta.get("audio_status") != "EMBEDDED_AUDIO"
                    or meta.get("image_count") != 5
                    or meta.get("video") != stem + ".mp4"):
                continue
        except (ValueError, KeyError, TypeError):
            continue
        receipt = {
            "schema": 1, "account": "dreamy_elsewhere",
            "source": "verified_buffer_sent_instagram_reel",
            "marker": key, "stem": stem, "buffer_post_id": post["id"],
            "status": "sent", "sent_at": sent, "instagram_url": url
        }
        by_stem.setdefault(stem, []).append(receipt)

    out.mkdir(parents=True, exist_ok=True)
    saved = 0
    for stem, entries in sorted(by_stem.items()):
        if len(entries) != 1:
            print("SKIP duplicate successful posts for", stem)
            continue
        path = out / (stem + ".json")
        expected = entries[0]
        if path.exists():
            try:
                previous = json.loads(path.read_text(encoding="utf-8"))
            except ValueError:
                print("SKIP corrupted existing receipt", stem)
                continue
            if previous != expected:
                print("SKIP changed receipt", stem)
            continue
        path.write_text(json.dumps(expected, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
        saved += 1
        print("RECEIPT confirmed Buffer SENT", stem, expected["sent_at"])
    print("Confirmed new Dreamy Instagram receipt files:", saved)
    return saved


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", required=True)
    args = p.parse_args()
    export(Path(args.output))


if __name__ == "__main__":
    main()
