"""Import five temporary GitHub blobs from an image task's Drive handoff.

The scheduled ChatGPT job can privately read files from Google Drive and
create GitHub blobs using its connected apps; it then commits only a tiny JSON
manifest to this repository, which triggers the GitHub Actions renderer.

Images are NOT committed as source files to Git history. No Drive folder
needs to become public. The blobs must be fetched promptly: unreferenced
Git objects are not promised permanent retention.
"""
import argparse
import base64
import binascii
import hashlib
import io
import json
import os
import re
import tempfile
from datetime import date, timedelta
from pathlib import Path

import requests
from PIL import Image, ImageOps, UnidentifiedImageError
from schedule import CONFIG, ROOT, slots_for

SOURCE = ROOT / "assets" / "drive_manifests"
INBOX = ROOT / "assets" / "inbox"
REPO = "lucadimichele-svg/dreamy-elsewhere-automation-"
SHA = re.compile(r"^[0-9a-f]{40}$")
DRIVE_ID = re.compile(r"^[A-Za-z0-9_-]{12,160}$")
MAX_IMAGE = 20 * 1024 * 1024

class ImageTransferError(Exception):
    pass

def parse_manifest(path):
    obj = json.loads(path.read_text(encoding="utf-8"))
    day = date.fromisoformat(obj["date"])
    slot = obj["slot"]
    stem = f"{day.isoformat()}_{slot}"
    if path.stem != stem or slot not in dict(slots_for(day)):
        raise ImageTransferError("manifest date or slot is invalid")
    files = obj.get("files")
    if not isinstance(files, list) or len(files) != 5:
        raise ImageTransferError("five images required")
    blob_ids = []
    drive_ids = []
    for i, item in enumerate(files, 1):
        name = item.get("name")
        sha = item.get("blob_sha")
        drive = item.get("drive_id")
        if name not in (f"{i:02d}.jpg", f"{i:02d}.jpeg", f"{i:02d}.png", f"{i:02d}.webp"):
            raise ImageTransferError("incorrect sequence or filename")
        if not isinstance(sha, str) or not SHA.fullmatch(sha):
            raise ImageTransferError("missing or invalid GitHub blob SHA")
        if not isinstance(drive, str) or not DRIVE_ID.fullmatch(drive):
            raise ImageTransferError("missing Drive source ID")
        blob_ids.append(sha)
        drive_ids.append(drive)
    if len(set(blob_ids)) != 5 or len(set(drive_ids)) != 5:
        raise ImageTransferError("duplicate image identifiers")
    return stem, files

def get_blob(session, sha):
    headers = {"Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    url = f"https://api.github.com/repos/{REPO}/git/blobs/{sha}"
    response = session.get(url, headers=headers, timeout=60)
    response.raise_for_status()
    if response.headers.get("Content-Type", "").startswith("application/json"):
        obj = response.json()
        if obj.get("encoding") != "base64":
            raise ImageTransferError("GitHub blob did not return base64")
        try:
            image = base64.b64decode(obj["content"], validate=False)
        except (binascii.Error, KeyError) as exc:
            raise ImageTransferError("Invalid GitHub blob content") from exc
    else:
        image = response.content
    if not image or len(image) > MAX_IMAGE:
        raise ImageTransferError("Image blob missing or too large")
    marker = f"blob {len(image)}\0".encode("ascii")
    checksum = hashlib.sha1(marker + image).hexdigest()
    if checksum != sha:
        raise ImageTransferError("GitHub blob SHA verification failed")
    return image

def validate_image(content, ordinal):
    try:
        with Image.open(io.BytesIO(content)) as img:
            img.verify()
        with Image.open(io.BytesIO(content)) as img:
            img = ImageOps.exif_transpose(img).convert("RGB")
            if img.width < CONFIG["output_width"] or img.height < CONFIG["output_height"]:
                raise ImageTransferError(f"image {ordinal} below minimum size")
            ratio = img.width / img.height
            if not (0.45 <= ratio <= 0.68):
                raise ImageTransferError(f"image {ordinal} is not 9:16-compatible")
            out = io.BytesIO()
            img.save(out, format="PNG")
            return out.getvalue()
    except (UnidentifiedImageError, OSError) as exc:
        raise ImageTransferError(f"image {ordinal} invalid image format") from exc

def import_one(path, session):
    stem, items = parse_manifest(path)
    if (ROOT/"docs/media"/f"{stem}.json").is_file():
        print("SKIP already rendered", stem)
        return False
    final = INBOX/stem
    names = [f"{i:02d}.png" for i in range(1, 6)]
    if final.is_dir() and sorted(x.name for x in final.iterdir() if x.is_file()) == names:
        print("SKIP already imported", stem)
        return False
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for i, item in enumerate(items, 1):
            data = validate_image(get_blob(session, item["blob_sha"]), i)
            (tmp_path/f"{i:02d}.png").write_bytes(data)
        final.mkdir(parents=True, exist_ok=True)
        for name in names:
            os.replace(tmp_path/name, final/name)
    print("IMPORTED", stem, "five genuine images")
    return True

def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--start", default=str(date.today()))
    cli.add_argument("--days", type=int, default=9)
    args = cli.parse_args()
    start = date.fromisoformat(args.start)
    permitted = {f"{(start+timedelta(days=i)).isoformat()}_{slot}"
                 for i in range(args.days) for slot,_ in slots_for(start+timedelta(days=i))}
    inputs = sorted(p for p in SOURCE.glob("*.json") if p.stem in permitted)
    if not inputs:
        print("No new transfer manifests. Safe no-op.")
        return 0
    errors = 0
    with requests.Session() as session:
        for path in inputs:
            try:
                import_one(path, session)
            except (ImageTransferError, requests.RequestException, ValueError, KeyError) as exc:
                errors += 1
                print("TRANSFER FAILED", path.name, str(exc))
    print("Checked", len(inputs), "manifests; errors", errors)
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
