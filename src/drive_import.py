"""Fetch five AI image files from the designated Google Drive source.

Only the exact Drive IDs in versioned slot manifests are allowed; folder
listing/scraping is intentionally avoided. The import is read-only; originals
remain on Drive until the separate cleanup process verifies delivery.
Input: assets/drive_manifests/YYYY-MM-DD_S1.json
Output: transient assets/inbox/YYYY-MM-DD_S1/01.png..05.png

Precondition: only the dedicated incoming subfolder is configured with link
viewing permission. Never grant access to personal Drive/root folders.
"""
import argparse
import json
import os
import re
import tempfile
from datetime import date, timedelta
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image, ImageOps, UnidentifiedImageError
from schedule import ROOT, CONFIG, slots_for

MANIFESTS = ROOT / "assets" / "drive_manifests"
INBOX = ROOT / "assets" / "inbox"
STEM = re.compile(r"^\d{4}-\d{2}-\d{2}_S[1-4]$")
DRIVE_ID = re.compile(r"^[A-Za-z0-9_-]{12,160}$")

class ImportErrorDetail(Exception):
    pass

def parse_manifest(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    day = date.fromisoformat(data["date"])
    slot = data["slot"]
    stem = f"{day.isoformat()}_{slot}"
    if not STEM.fullmatch(stem) or slot not in dict(slots_for(day)):
        raise ImportErrorDetail(f"invalid date or slot: {stem}")
    if Path(path).stem != stem:
        raise ImportErrorDetail("manifest filename does not match date/slot")
    files = data.get("files")
    if not isinstance(files, list) or len(files) != 5:
        raise ImportErrorDetail("exactly five Drive file references required")
    ids = []
    for i, item in enumerate(files, 1):
        name = item.get("name")
        file_id = item.get("id")
        if name not in (f"{i:02d}.png", f"{i:02d}.jpg", f"{i:02d}.jpeg", f"{i:02d}.webp"):
            raise ImportErrorDetail(f"unexpected filename for image {i}: {name}")
        if not isinstance(file_id, str) or not DRIVE_ID.fullmatch(file_id):
            raise ImportErrorDetail("invalid Google Drive file id")
        ids.append(file_id)
    if len(set(ids)) != 5:
        raise ImportErrorDetail("image Drive IDs are not unique")
    return stem, files

def download_image(session, file_id, name):
    # Drive serves publicly accessible, small image files directly with this URL.
    # Requests handles Google's cross-host redirect and HTML failure responses.
    url = "https://drive.google.com/uc"
    response = session.get(url, params={"export":"download", "id":file_id},
                           timeout=45, allow_redirects=True, stream=True)
    response.raise_for_status()
    payload = bytearray()
    max_bytes = 18 * 1024 * 1024
    for chunk in response.iter_content(1024 * 128):
        payload.extend(chunk)
        if len(payload) > max_bytes:
            raise ImportErrorDetail(f"image {name}: file too large")
    response.close()
    if not payload or payload[:100].lstrip().startswith((b"<!DOCTYPE", b"<html", b"<HTML")):
        raise ImportErrorDetail(f"image {name}: Drive returned HTML; verify link access")
    try:
        with Image.open(BytesIO(payload)) as original:
            original.verify()
        with Image.open(BytesIO(payload)) as source:
            img = ImageOps.exif_transpose(source).convert("RGB")
            if img.width < CONFIG["output_width"] or img.height < CONFIG["output_height"]:
                raise ImportErrorDetail(
                    f"image {name}: {img.width}x{img.height} is below minimum "
                    f"{CONFIG['output_width']}x{CONFIG['output_height']}")
            if img.width/img.height < .45 or img.width/img.height > .68:
                raise ImportErrorDetail(f"image {name}: incompatible vertical aspect ratio")
            output = BytesIO()
            img.save(output, format="PNG")
            return output.getvalue()
    except (UnidentifiedImageError, OSError) as exc:
        raise ImportErrorDetail(f"image {name}: invalid image response") from exc

def import_one(path, session):
    stem, files = parse_manifest(path)
    target = INBOX / stem
    if (ROOT/"docs/media"/f"{stem}.json").is_file():
        print("SKIP already rendered:", stem)
        return False
    if target.is_dir() and sorted(x.name for x in target.iterdir() if x.is_file()) == [
        f"{i:02d}.png" for i in range(1, 6)]:
        print("SKIP images already present:", stem)
        return False

    with tempfile.TemporaryDirectory() as tmp:
        scratch = Path(tmp)
        for i, obj in enumerate(files, 1):
            output = download_image(session, obj["id"], obj["name"])
            (scratch/f"{i:02d}.png").write_bytes(output)
        target.mkdir(parents=True, exist_ok=True)
        for i in range(1, 6):
            os.replace(scratch/f"{i:02d}.png", target/f"{i:02d}.png")
    print("IMPORTED:", stem, "five Drive images")
    return True

def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--start", default=str(date.today()))
    cli.add_argument("--days", type=int, default=9)
    args = cli.parse_args()
    start = date.fromisoformat(args.start)
    allowed = {f"{(start + timedelta(days=i)).isoformat()}_{slot}"
               for i in range(args.days)
               for slot, _ in slots_for(start + timedelta(days=i))}
    selected = sorted(path for path in MANIFESTS.glob("*.json") if path.stem in allowed)
    if not selected:
        print("No new Drive manifests found (safe no-op).")
        return 0
    errors = 0
    with requests.Session() as session:
        for path in selected:
            try:
                import_one(path, session)
            except (ImportErrorDetail, requests.RequestException, ValueError, KeyError) as exc:
                errors += 1
                print(f"NOT READY {path.name}: {exc}")
    print(f"Import checked {len(selected)} manifests, errors={errors}")
    # A missing or private source should be visible as a failed CI run, not
    # incorrectly counted as successful production.
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
