"""Fetch the licensed soundtrack privately for rendering, never commit the source MP3.

Required GitHub Actions secrets:
  DREAMY_DRIVE_AUDIO_ID: ID of the private audio file on Google Drive.
  DREAMY_DRIVE_SA_JSON: Google service-account JSON with access to that file.
"""
import hashlib
import io
import json
import os
import subprocess
from pathlib import Path

import requests
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "assets/audio/background.mp3"
EXPECTED_SHA256 = "3ffae7ccd5ea6f612f75efdf9a8318ccce79a5e4f355b26e233631330a57660f"
MAX_BYTES = 20 * 1024 * 1024

def main():
    file_id = os.environ.get("DREAMY_DRIVE_AUDIO_ID")
    service_info = os.environ.get("DREAMY_DRIVE_SA_JSON")
    if not file_id or not service_info:
        raise SystemExit("Private music connection not configured: set DREAMY_DRIVE_AUDIO_ID and DREAMY_DRIVE_SA_JSON.")
    try:
        credentials = Credentials.from_service_account_info(
            json.loads(service_info),
            scopes=["https://www.googleapis.com/auth/drive.readonly"],
        )
        credentials.refresh(Request())
    except Exception as exc:
        raise SystemExit("Unable to authenticate service account for private audio transfer") from exc
    if not credentials.token:
        raise SystemExit("No Google Drive access token was issued")
    response = requests.get(
        f"https://www.googleapis.com/drive/v3/files/{file_id}",
        params={"alt": "media"},
        headers={"Authorization": f"Bearer {credentials.token}"},
        timeout=90,
        stream=True,
    )
    try:
        response.raise_for_status()
        output = io.BytesIO()
        digest = hashlib.sha256()
        size = 0
        for chunk in response.iter_content(chunk_size=65536):
            if not chunk:
                continue
            size += len(chunk)
            if size > MAX_BYTES:
                raise RuntimeError("Audio file exceeds maximum allowed size")
            digest.update(chunk)
            output.write(chunk)
    finally:
        response.close()
    if digest.hexdigest() != EXPECTED_SHA256:
        raise RuntimeError("Audio SHA-256 does not match the approved Vastness MP3")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_bytes(output.getvalue())
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a:0",
         "-show_entries", "stream=codec_name", "-of", "csv=p=0", str(TARGET)],
        check=True, capture_output=True, text=True,
    )
    if "mp3" not in probe.stdout:
        TARGET.unlink(missing_ok=True)
        raise RuntimeError("Approved audio is not a valid MP3")
    print("PASS: approved licensed audio downloaded privately and verified")
    print("The source audio remains on the temporary runner and is not committed.")

if __name__ == "__main__":
    main()
