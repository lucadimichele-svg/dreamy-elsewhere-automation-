"""Import exact five 9:16 scene images from private Drive with service-account authentication.

Read-only on Drive. Only the selected reel's folder under the project incoming
folder is accepted. Source binaries are never committed into Git history.
"""
import argparse
import io
import json
import os
import re
import tempfile
from datetime import date, timedelta
from pathlib import Path

import requests
from PIL import Image, ImageOps
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from schedule import ROOT, CONFIG, slots_for
from creative_plan import load_for_render
from scene_integrity import required as subject_audit_required, load_audit, check_payload

MANIFESTS = ROOT / "assets" / "drive_manifests"
INBOX = ROOT / "assets" / "inbox"
INCOMING_FOLDER_ID = "1c_nwLIkqHANFUtCCQhT6waEj57q4XA7m"
DRIVE_API = "https://www.googleapis.com/drive/v3/files"
DRIVE_ID = re.compile(r"^[A-Za-z0-9_-]{12,160}$")
MAX_BYTES = 20 * 1024 * 1024

class ImportFailure(RuntimeError):
    pass

def api_get(session, url, **kwargs):
    response = session.get(url, timeout=60, **kwargs)
    response.raise_for_status()
    return response

def list_one_folder(session, stem):
    r = api_get(session, DRIVE_API, params={
        "q": f"name = '{stem}' and '{INCOMING_FOLDER_ID}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false",
        "fields": "files(id,name),nextPageToken", "pageSize": 10
    })
    files = r.json().get("files", [])
    if len(files) != 1:
        raise ImportFailure(f"Expected exactly one reel folder for {stem}; found {len(files)}")
    return files[0]["id"]

def parse_manifest(path):
    obj = json.loads(path.read_text(encoding="utf-8"))
    day = date.fromisoformat(obj["date"])
    slot = obj["slot"]
    stem = f"{day}_{slot}"
    if stem != path.stem or slot not in dict(slots_for(day)):
        raise ImportFailure("Invalid reel date/slot")
    items = obj.get("files")
    if not isinstance(items, list) or len(items) != 5:
        raise ImportFailure("Exactly five source images required")
    # Legacy GitHub blob manifests are handled by blob_import.py instead.
    if all(isinstance(f, dict) and f.get("blob_sha") for f in items):
        return stem, None
    ids = []
    for index, item in enumerate(items, 1):
        if not isinstance(item, dict):
            raise ImportFailure("Invalid image entry")
        expected = f"{index:02d}.png"
        if item.get("name") != expected or not isinstance(item.get("id"), str) or not DRIVE_ID.fullmatch(item["id"]):
            raise ImportFailure(f"Bad filename or Drive identifier at image {index}")
        ids.append(item["id"])
    if len(set(ids)) != 5:
        raise ImportFailure("Duplicate Drive image identifiers")
    return stem, items

def import_one(path, session):
    stem, items = parse_manifest(path)
    if items is None:
        return False
    if (ROOT / "docs" / "media" / (stem + ".json")).exists():
        print("SKIP already rendered", stem)
        return False
    target = INBOX / stem
    names = [f"{i:02d}.png" for i in range(1, 6)]
    if target.is_dir() and sorted(p.name for p in target.iterdir() if p.is_file()) == names:
        print("SKIP already imported", stem)
        return False
    day_str, slot = stem.split("_")
    day = date.fromisoformat(day_str)
    # For new Reels, the producer has to check whether the actual object
    # of EACH variant is visibly present, and attest the exact uploaded bytes.
    # This is content correctness, not an aesthetic or similarity rating.
    audit = load_audit(stem, load_for_render(day, slot)) if subject_audit_required(day, slot) else None
    expected_folder_id = list_one_folder(session, stem)
    with tempfile.TemporaryDirectory() as temp:
        tmp = Path(temp)
        for index, item in enumerate(items, 1):
            file_id, name = item["id"], item["name"]
            metadata = api_get(session, DRIVE_API + "/" + file_id, params={
                "fields": "id,name,mimeType,parents,size"
            }).json()
            if name != metadata.get("name") or expected_folder_id not in metadata.get("parents", []):
                raise ImportFailure(f"Image {index} is not in the expected private reel folder")
            if metadata.get("mimeType") != "image/png" or int(metadata.get("size", 0)) > MAX_BYTES:
                raise ImportFailure(f"Image {index} has incorrect type or exceeds size limit")
            response = api_get(session, DRIVE_API + "/" + file_id, params={"alt": "media"}, stream=True)
            payload = bytearray()
            try:
                for chunk in response.iter_content(128 * 1024):
                    payload.extend(chunk)
                    if len(payload) > MAX_BYTES:
                        raise ImportFailure(f"Image {index} exceeds 20 MB")
            finally:
                response.close()
            if audit is not None:
                check_payload(audit, index, bytes(payload))
            with Image.open(io.BytesIO(payload)) as image:
                image.verify()
            with Image.open(io.BytesIO(payload)) as image:
                image = ImageOps.exif_transpose(image).convert("RGB")
                if (image.width < CONFIG.get("native_source_min_width",800)
                        or image.height < CONFIG.get("native_source_min_height",1400)):
                    raise ImportFailure(f"Image {index} below true native source minimum")
                if not 0.45 <= image.width / image.height <= 0.68:
                    raise ImportFailure(f"Image {index} has incompatible portrait aspect ratio")
                image.save(tmp / name, "PNG")
        target.mkdir(parents=True, exist_ok=True)
        for name in names:
            os.replace(tmp / name, target / name)
    print("PASS: downloaded five genuine private Drive images for", stem)
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default=str(date.today()))
    parser.add_argument("--days", type=int, default=9)
    args = parser.parse_args()
    credentials_json = os.environ.get("GOOGLE_DRIVE_CREDENTIALS")
    if not credentials_json:
        raise SystemExit("Missing GOOGLE_DRIVE_CREDENTIALS secret")
    creds = Credentials.from_service_account_info(json.loads(credentials_json), scopes=[
        "https://www.googleapis.com/auth/drive.readonly"
    ])
    creds.refresh(Request())
    start = date.fromisoformat(args.start)
    permitted = {f"{start + timedelta(days=n)}_{slot}" for n in range(args.days)
                 for slot, _ in slots_for(start + timedelta(days=n))}
    manifests = sorted(p for p in MANIFESTS.glob("*.json") if p.stem in permitted)
    if not manifests:
        print("No new image manifests")
        return
    session = requests.Session()
    session.headers["Authorization"] = "Bearer " + creds.token
    for path in manifests:
        import_one(path, session)

if __name__ == "__main__":
    main()
