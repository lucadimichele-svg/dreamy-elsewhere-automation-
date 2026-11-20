"""Guarded cleanup of Dreamy Elsewhere ORIGINAL source folders in private Drive.

- Never touches audio, rendered media, demo or unknown folders.
- Uses public, exact-handle Buffer SENT receipts produced by the credential bridge.
- Moves a complete five-PNG source folder incoming -> used after publication.
- Deletes ONLY that folder and the identified five source PNGs >=24h AFTER move.
- Dry-run by default. All REST edits require --apply and exact verification.
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit

import requests
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials

from schedule import ROOT, marker, slots_for
from datetime import date

INCOMING = "1c_nwLIkqHANFUtCCQhT6waEj57q4XA7m"
USED = "1z_kF31owkUnu8Fx_fIbAkkPv0zG6_vw3"
DRIVE = "https://www.googleapis.com/drive/v3/files"
RECEIPT_BASE = ("https://raw.githubusercontent.com/lucadimichele-svg/"
                "blinkpuzz-automation/main/docs/dreamy-published")
FOLDER_TAG = "DREAMY_SOURCE_CLEANUP_V1:"
MOVED_DIR = ROOT / "docs" / "source-moved"
AGE = timedelta(hours=24)
STEM = re.compile(r"^\d{4}-\d{2}-\d{2}_S[1-4]$")
MIME_FOLDER = "application/vnd.google-apps.folder"


def parse_time(s):
    if not isinstance(s, str):
        raise ValueError("Missing timestamp")
    dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("Timezone missing")
    return dt.astimezone(timezone.utc)


def utc_now():
    return datetime.now(timezone.utc)


def validate_manifest(path):
    stem = path.stem
    if not STEM.fullmatch(stem):
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        day = date.fromisoformat(data["date"])
        slot = data["slot"]
        if stem != f"{day}_{slot}" or slot not in dict(slots_for(day)):
            return None
        ident = data["drive_folder_id"]
        if not isinstance(ident, str) or not re.fullmatch(r"[A-Za-z0-9_-]{12,160}", ident):
            return None
        files = data["files"]
        if not isinstance(files, list) or len(files) != 5:
            return None
        ids = []
        for i, f in enumerate(files, 1):
            if f["name"] != f"{i:02d}.png" or not re.fullmatch(r"[A-Za-z0-9_-]{12,160}", f["id"]):
                return None
            ids.append(f["id"])
        if len(set(ids)) != 5:
            return None
        media_meta = ROOT / "docs/media" / (stem+".json")
        video = ROOT / "docs/media" / (stem+".mp4")
        if not media_meta.exists() or not video.exists():
            return None
        meta = json.loads(media_meta.read_text(encoding="utf-8"))
        if (meta.get("marker") != marker(day, slot)
                or meta.get("video") != stem+".mp4"
                or meta.get("audio_status") != "EMBEDDED_AUDIO"
                or meta.get("image_count") != 5 or meta.get("duration_seconds") != 15):
            return None
        return data
    except (ValueError, KeyError, TypeError, OSError):
        return None


def validate_receipt(data, manifest):
    if not isinstance(data, dict):
        return False
    stem = f"{manifest['date']}_{manifest['slot']}"
    key = "DE" + manifest["date"].replace("-", "") + manifest["slot"]
    if (data.get("schema") != 1 or data.get("account") != "dreamy_elsewhere"
            or data.get("source") != "verified_buffer_sent_instagram_reel"
            or data.get("status") != "sent" or data.get("marker") != key
            or data.get("stem") != stem
            or not isinstance(data.get("buffer_post_id"), str)):
        return False
    url = data.get("instagram_url")
    if not isinstance(url, str):
        return False
    parts = urlsplit(url)
    if (parts.scheme != "https" or parts.hostname != "www.instagram.com"
            or not re.fullmatch(r"/reel/[A-Za-z0-9_-]+/", parts.path)):
        return False
    try:
        sent = parse_time(data["sent_at"])
        if sent > utc_now() or sent < datetime(2026,11,17,tzinfo=timezone.utc):
            return False
    except ValueError:
        return False
    return True


class Drive:
    def __init__(self):
        raw = os.environ.get("GOOGLE_DRIVE_CREDENTIALS")
        if not raw:
            raise RuntimeError("Missing GOOGLE_DRIVE_CREDENTIALS")
        credentials = Credentials.from_service_account_info(
            json.loads(raw), scopes=["https://www.googleapis.com/auth/drive"])
        credentials.refresh(Request())
        self.session = requests.Session()
        self.session.headers.update({"Authorization": "Bearer " + credentials.token})
        self.apply = False

    def call(self, method, url, **kw):
        result = self.session.request(method, url, timeout=45, **kw)
        result.raise_for_status()
        if result.status_code == 204 or not result.content:
            return {}
        return result.json()

    def get(self, fid):
        return self.call("GET", DRIVE+"/"+fid, params={
            "fields":"id,name,mimeType,parents,description,trashed,capabilities(canEdit,canDelete,canTrash,canMoveItemWithinDrive,canAddChildren,canDeleteChildren)"})

    def children(self, folder):
        items=[]
        page=None
        while True:
            params={"q":f"'{folder}' in parents and trashed = false",
                    "fields":"nextPageToken,files(id,name,mimeType,parents,capabilities(canDelete))",
                    "pageSize":100}
            if page:
                params["pageToken"]=page
            result=self.call("GET", DRIVE, params=params)
            items.extend(result.get("files",[]))
            page=result.get("nextPageToken")
            if not page:
                break
        return items

    def move(self, fid, source, destination, description):
        return self.call("PATCH",DRIVE+"/"+fid,
                         params={"addParents":destination,"removeParents":source,
                                 "fields":"id,parents,description"},
                         json={"description":description})


def exact_files(files, manifest, allow_subset=False):
    expected={x["id"]:(x["name"], "image/png") for x in manifest["files"]}
    found=set()
    for f in files:
        fid=f["id"]
        if fid not in expected or fid in found:
            return False
        if (f.get("name"),f.get("mimeType")) != expected[fid]:
            return False
        found.add(fid)
    return found.issubset(expected.keys()) if allow_subset else found == set(expected.keys())


def remember_move(stem, manifest, receipt, record, apply):
    """Write a durable, public but NON-SENSITIVE move time for owner-side deletion."""
    obj = {
        "schema": 1, "account": "dreamy_elsewhere", "stem": stem,
        "source": "confirmed_drive_incoming_to_used",
        "marker": receipt["marker"],
        "buffer_post_id": receipt["buffer_post_id"],
        "sent_at": receipt["sent_at"], "moved_at": record["moved_at"],
        "instagram_url": receipt["instagram_url"],
        "drive_folder_id": manifest["drive_folder_id"],
        "files": manifest["files"],
    }
    path = MOVED_DIR / (stem+".json")
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            raise RuntimeError("Corrupt existing archive receipt; refusing overwrite")
        if existing != obj:
            raise RuntimeError("Archive receipt conflict; refusing overwrite")
    elif apply:
        MOVED_DIR.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")


def run(apply=False):
    driveway = Drive()
    root_in=driveway.get(INCOMING)
    root_used=driveway.get(USED)
    if root_in.get("mimeType") != MIME_FOLDER or root_used.get("mimeType") != MIME_FOLDER:
        raise RuntimeError("Wrong Drive directory; refuse all cleanup")
    print("ROOT PERMISSIONS incoming:",root_in.get("capabilities"),
          "used:",root_used.get("capabilities"))
    print("MODE:", "APPLY" if apply else "DRY_RUN")
    # Safe permission probe only: never modify this file.
    probe_path = ROOT / "assets/drive_manifests/2026-11-17_S1.json"
    probe = validate_manifest(probe_path) if probe_path.exists() else None
    if probe:
        sample_file = driveway.get(probe["files"][0]["id"])
        sample_folder = driveway.get(probe["drive_folder_id"])
        print("ORIGINAL FILE CAPABILITIES:", sample_file.get("capabilities"))
        print("ORIGINAL FOLDER CAPABILITIES:", sample_folder.get("capabilities"))
    receipts_seen=0
    moved=0
    deleted=0
    held=0
    for path in sorted((ROOT/"assets/drive_manifests").glob("????-??-??_S?.json")):
        manifest=validate_manifest(path)
        if not manifest:
            continue
        stem=path.stem
        try:
            response=requests.get(RECEIPT_BASE+"/"+stem+".json", timeout=25)
        except requests.RequestException as exc:
            print("HOLD",stem,"Could not verify Buffer receipt",str(exc)[:120])
            held+=1
            continue
        if response.status_code == 404:
            print("HOLD",stem,"No confirmed Instagram SENT receipt")
            held+=1
            continue
        response.raise_for_status()
        try:
            receipt=response.json()
        except ValueError:
            print("HOLD",stem,"Invalid delivery receipt")
            held+=1
            continue
        if not validate_receipt(receipt,manifest):
            print("HOLD",stem,"Untrusted/incomplete Instagram delivery receipt")
            held+=1
            continue
        receipts_seen+=1
        folder_id=manifest["drive_folder_id"]
        try:
            folder=driveway.get(folder_id)
            children=driveway.children(folder_id)
        except requests.HTTPError as exc:
            print("HOLD",stem,"Drive item cannot be read:",str(exc)[:150])
            held+=1
            continue
        if folder.get("name") != stem or folder.get("mimeType") != MIME_FOLDER or folder.get("trashed"):
            print("HOLD",stem,"Folder identity does not match")
            held+=1
            continue
        parents=set(folder.get("parents",[]))
        if parents == {INCOMING}:
            if not exact_files(children,manifest):
                print("HOLD",stem,"Incoming folder is not EXACTLY five expected PNG originals")
                held+=1
                continue
            if folder.get("description","").startswith(FOLDER_TAG):
                print("HOLD",stem,"Unexpected cleanup marker on incoming folder")
                held+=1
                continue
            # Move only AFTER confirmed SENT publication and complete on-Drive
            # source file identity; description and move in one transaction.
            record={"marker":receipt["marker"],"buffer_post_id":receipt["buffer_post_id"],
                    "sent_at":receipt["sent_at"],
                    "moved_at":utc_now().isoformat().replace("+00:00","Z")}
            description=FOLDER_TAG+json.dumps(record,sort_keys=True,separators=(",",":"))
            if apply:
                try:
                    result=driveway.move(folder_id,INCOMING,USED,description)
                    if set(result.get("parents",[])) != {USED}:
                        raise RuntimeError("Drive returned unexpected parent after moving")
                except (requests.RequestException,RuntimeError) as exc:
                    print("HOLD",stem,"Move failed:",str(exc)[:160])
                    held+=1
                    continue
            if apply:
                try:
                    remember_move(stem, manifest, receipt, record, apply)
                except RuntimeError as exc:
                    print("ARCHIVE_RECEIPT_ERROR", stem, str(exc))
                    held += 1
                    # Moving was still successful; next run may recover from
                    # the durable Drive folder description.
            print("MOVE" if apply else "WOULD MOVE",stem,
                  "incoming -> used (Instagram status SENT confirmed)")
            moved+=1
        elif parents == {USED}:
            raw_description=folder.get("description","")
            if not raw_description.startswith(FOLDER_TAG):
                print("HOLD",stem,"Used folder lacks our cleanup provenance")
                held+=1
                continue
            try:
                record=json.loads(raw_description[len(FOLDER_TAG):])
                moved_at=parse_time(record["moved_at"])
            except (ValueError,KeyError,TypeError):
                print("HOLD",stem,"Malformed move record")
                held+=1
                continue
            if (record.get("marker") != receipt["marker"]
                    or record.get("buffer_post_id") != receipt["buffer_post_id"]
                    or record.get("sent_at") != receipt["sent_at"]
                    or moved_at < parse_time(receipt["sent_at"])
                    or moved_at > utc_now()):
                print("HOLD",stem,"Move record conflicts with Buffer receipt")
                held+=1
                continue
            try:
                remember_move(stem, manifest, receipt, record, apply)
            except RuntimeError as exc:
                print("HOLD",stem,"Move receipt conflict:",str(exc))
                held+=1
                continue
            if utc_now() - moved_at < AGE:
                print("RETAIN",stem,"Not yet 24h since moving to used")
                continue
            # Permit prior partial deletion to resume, but NEVER unknown extras.
            if not exact_files(children,manifest,allow_subset=True):
                print("HOLD",stem,"Unknown extra file or renamed original in used")
                held+=1
                continue
            # GitHub service account has canDelete=false for user-owned files.
            # Never try to delete using insufficient rights; separate owner
            # connector cleanup must verify the moved receipt before deletion.
            print("OWNER_DELETE_REQUIRED",stem,
                  "24h elapsed; owner-connected cleaner may delete originals")
            held+=1
        else:
            print("HOLD",stem,"Folder outside authorized incoming/used parents")
            held+=1
    print("SUMMARY",json.dumps({"apply":apply,"receipts":receipts_seen,
                                "moved":moved,"deleted":deleted,"held":held}))
    return 0


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--apply",action="store_true",
                   help="Perform guarded folder moves and after-24h source deletion")
    a=p.parse_args()
    sys.exit(run(apply=a.apply))


if __name__=="__main__":
    main()
