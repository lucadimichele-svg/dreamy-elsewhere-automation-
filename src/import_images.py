#!/usr/bin/env python3
"""Download five genuine image URLs into one Reel inbox, without publishing."""
import argparse
import io
import ipaddress
import socket
import re
from pathlib import Path
from urllib.parse import urlparse
import requests
from PIL import Image

def check_url(url):
    p = urlparse(url)
    if p.scheme != "https" or not p.hostname or p.username or p.password:
        raise ValueError("Only public HTTPS image URLs are accepted")
    for info in socket.getaddrinfo(p.hostname, 443, type=socket.SOCK_STREAM):
        ip = ipaddress.ip_address(info[4][0])
        if not ip.is_global:
            raise ValueError("Private or local addresses are not allowed")
    return url

def main():
    a = argparse.ArgumentParser()
    a.add_argument("--reel", required=True)
    for i in range(1, 6):
        a.add_argument(f"--url{i:02d}", required=True)
    args = a.parse_args()
    if not re.fullmatch(r"20\d{2}-\d{2}-\d{2}_S[1-9]\d*", args.reel):
        raise ValueError("Invalid reel ID")
    dest = Path("assets/inbox") / args.reel
    if dest.exists() and any(dest.glob("*")):
        raise ValueError("Refusing to overwrite existing Reel assets")
    images = []
    for i in range(1, 6):
        url = check_url(getattr(args, f"url{i:02d}"))
        r = requests.get(url, timeout=45, allow_redirects=False, stream=True)
        if 300 <= r.status_code < 400:
            raise ValueError("Redirects are not supported")
        r.raise_for_status()
        data = bytearray()
        for chunk in r.iter_content(65536):
            data.extend(chunk)
            if len(data) > 20 * 1024 * 1024:
                raise ValueError("Image exceeds 20 MiB")
        with Image.open(io.BytesIO(data)) as im:
            im.load()
            if im.width < 1080 or im.height < 1920:
                raise ValueError(f"Image {i}: resolution {im.width}x{im.height} below 1080x1920")
            if im.height <= im.width:
                raise ValueError(f"Image {i}: not portrait")
            out = io.BytesIO()
            im.convert("RGB").save(out, format="JPEG", quality=92, optimize=True)
            images.append(out.getvalue())
    dest.mkdir(parents=True, exist_ok=True)
    for i, data in enumerate(images, 1):
        (dest / f"{i:02d}.jpg").write_bytes(data)
        print(f"Validated {dest / f'{i:02d}.jpg'} ({len(data)} bytes)")
if __name__ == "__main__":
    main()
