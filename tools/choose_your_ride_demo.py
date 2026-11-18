"""Render a standalone 15-second Reel PREVIEW: no publishing and no changes to production slots."""
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

import requests
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "demos"
OUT.mkdir(parents=True, exist_ok=True)
W, H = 1080, 1920
AUDIO_ID = "1epXkgSoT41uTYpFUB0bC4r_ADrViBuOP"
TRAIN_ID = "1GHysgZsF0poB7NNXaUWk7OJYYfxBLWAX"
SCENE_URLS = json.loads("[\"https://dnznrvs05pmza.cloudfront.net/gemini/gemini-3.1-flash-image/images/9f80f909-3b4b-4b8f-b1a3-ec472e3d3ed6/317c9deb-8b94-49eb-905f-88f53bf26cfa/ONE_SINGLE_continuous_photorealistic_cinematic_portrait_imag.png?_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXlIYXNoIjoiZDk2MThmYmYyOWU1MGM5YiIsImJ1Y2tldCI6InJ1bndheS10YXNrLWFydGlmYWN0cyIsInN0YWdlIjoicHJvZCIsImV4cCI6MTc5NTE1MjA2M30.infG6qAWYzknwEWsFseHKHjp41pB_bBAyoA91IcV57E\",\"https://dnznrvs05pmza.cloudfront.net/gemini/gemini-3.1-flash-image/images/ff474edc-d15b-4d52-b1f2-8fd28da8e79b/a04172d6-f548-4114-a2b2-5c8ba7867f32/ONE_SINGLE_continuous_photorealistic_cinematic_portrait_imag.png?_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXlIYXNoIjoiMzJjOGNmMjhiNWY5NDQ2NSIsImJ1Y2tldCI6InJ1bndheS10YXNrLWFydGlmYWN0cyIsInN0YWdlIjoicHJvZCIsImV4cCI6MTc5NTE2MzQzMn0.qk4wlo7heRA8WmXulSdm62EC6S2zniv58iCrPJetg8k\",\"https://dnznrvs05pmza.cloudfront.net/gemini/gemini-3.1-flash-image/images/569cba37-0ad2-44d5-acb9-bff71d5ee5f2/92b9d9a6-4e6b-4b9d-b93e-7aaa4eb2a094/ONE_SINGLE_continuous_photorealistic_vertical_9_16_cinematic.png?_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXlIYXNoIjoiYzIyZmE2NzAyODZjYjRjNCIsImJ1Y2tldCI6InJ1bndheS10YXNrLWFydGlmYWN0cyIsInN0YWdlIjoicHJvZCIsImV4cCI6MTc5NTE1MDcwNH0.KKJIVHYtRRo1tj2iajU5X3wskUSPsj7pHHA9xUOBaws\",\"https://dnznrvs05pmza.cloudfront.net/gemini/gemini-3.1-flash-image/images/1ce1f121-252d-43cf-acb5-6bb581cadaa6/09543e05-cf21-43b1-b9ab-265b57800027/ONE_SINGLE_continuous_hyper_detailed_photorealistic_9_16_por.png?_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXlIYXNoIjoiZDgyOTBjMTg1YWVhMmMzZCIsImJ1Y2tldCI6InJ1bndheS10YXNrLWFydGlmYWN0cyIsInN0YWdlIjoicHJvZCIsImV4cCI6MTc5NTE0NzkyOH0.P4FWdD-rfhSges_Q2Y1mnccfyhEWBUZWybNwjXmIVq0\"]")
NAMES = [
    "BELLE ÉPOQUE TRAIN", "FLYING PIRATE SHIP",
    "LUXURY AIRSHIP", "ENCHANTED CARRIAGE", "STARLIGHT CRUISER"
]
FONT = "/usr/share/fonts/truetype/ebgaramond/EBGaramond12-Regular.ttf"
BOLD = "/usr/share/fonts/truetype/ebgaramond/EBGaramond12-Bold.ttf"
FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"

def font(size, bold=False):
    p = BOLD if bold else FONT
    return ImageFont.truetype(p if Path(p).exists() else FALLBACK, size)

def fetch_bytes(url, headers=None):
    last = None
    for tries in range(3):
        try:
            with requests.get(url, headers=headers, timeout=90, stream=True) as res:
                res.raise_for_status()
                chunks = bytearray()
                for chunk in res.iter_content(131072):
                    chunks.extend(chunk)
                    if len(chunks) > 25000000:
                        raise RuntimeError("Source file exceeds 25 MB")
                if len(chunks) < 40000:
                    raise RuntimeError("Source image/audio appears empty")
                return bytes(chunks)
        except (requests.RequestException, RuntimeError) as e:
            last = e
    raise RuntimeError(f"Failed to retrieve source: {last}")

def shade_gradient(img):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay, "RGBA")
    for y in range(255, 615):
        v = max(0, 1 - abs((y - 410)/205))
        d.line([(0,y),(W,y)], fill=(4,7,17,round(135*v)))
    for y in range(1295, 1635):
        v = max(0, 1 - abs((y - 1470)/190))
        d.line([(0,y),(W,y)], fill=(4,7,17,round(150*v)))
    return Image.alpha_composite(img.convert("RGBA"), overlay)

def center_text(draw, xy, text, ft, fill, stroke=0):
    draw.text((xy[0]+2,xy[1]+3),text,font=ft,anchor="mm",fill=(0,0,0,170),
              stroke_width=3,stroke_fill=(0,0,0,125))
    draw.text(xy,text,font=ft,anchor="mm",fill=fill,
              stroke_width=stroke,stroke_fill=(18,12,8,145))

def draw_frame(src, n, output):
    with Image.open(src) as original:
        image = ImageOps.exif_transpose(original).convert("RGB")
        # Exactly one quality resample to 1080x1920; no montage-panel sources.
        image = ImageOps.fit(image, (W,H), method=Image.Resampling.LANCZOS)
    image = shade_gradient(image)
    d=ImageDraw.Draw(image, "RGBA")
    cream=(255,244,221,255)
    gold=(240,200,139,255)
    center_text(d,(W//2,335),"D R E A M Y   E L S E W H E R E",font(24),gold)
    center_text(d,(W//2,425),"Choose Your Ride",font(76),cream)
    d.line([(340,504),(508,504)],fill=(227,182,114,190),width=2)
    d.line([(572,504),(740,504)],fill=(227,182,114,190),width=2)
    d.polygon([(540,494),(549,504),(540,514),(531,504)],fill=(239,208,152,225))
    # Subtle bottom ribbon; inside IG safe area and clear of control rails.
    d.rounded_rectangle([125,1398,955,1543],radius=28,fill=(13,15,21,185),
                        outline=(220,181,119,235),width=3)
    d.ellipse([156,1425,260,1529],fill=(32,31,31,220),
              outline=(238,199,133,255),width=3)
    center_text(d,(208,1478),f"{n:02d}",font(49),cream)
    name=NAMES[n-1]
    sz=49
    while sz>31 and d.textbbox((0,0),name,font=font(sz,True))[2]>625:
        sz-=2
    center_text(d,(606,1473),name,font(sz,True),cream)
    image.convert("RGB").save(output, "PNG", optimize=True)

def run(*args):
    subprocess.run([str(x) for x in args],check=True)

def main():
    credential_json=os.environ["GOOGLE_DRIVE_CREDENTIALS"]
    creds=Credentials.from_service_account_info(json.loads(credential_json),
           scopes=["https://www.googleapis.com/auth/drive.readonly"])
    creds.refresh(Request())
    hdr={"Authorization":"Bearer "+creds.token}
    with tempfile.TemporaryDirectory() as tempdir:
        temp=Path(tempdir)
        audio=temp/"audio.mp3"
        audio.write_bytes(fetch_bytes("https://www.googleapis.com/drive/v3/files/"+AUDIO_ID+"?alt=media",hdr))
        metadata=[]
        segments=[]
        for i in range(1,6):
            src=temp/f"source_{i:02d}.png"
            if i==1:
                payload=fetch_bytes("https://www.googleapis.com/drive/v3/files/"+TRAIN_ID+"?alt=media",hdr)
            else:
                payload=fetch_bytes(SCENE_URLS[i-2])
            src.write_bytes(payload)
            with Image.open(src) as im:
                im.verify()
            with Image.open(src) as im:
                width,height=im.size
            if width<800 or height<1400:
                raise RuntimeError(f"Scene {i} source too small: {width}x{height}; no upscaled collage panels")
            metadata.append({"scene":i,"variant":NAMES[i-1],
                             "native_source_width":width,"native_source_height":height,
                             "source_sha256":hashlib.sha256(payload).hexdigest()})
            frame=temp/f"frame_{i:02d}.png"
            draw_frame(src,i,frame)
            if i==1:
                with Image.open(frame) as cover:
                    cover.save(OUT/"choose_your_ride_cover.jpg",quality=93,subsampling=0)
            segment=temp/f"clip_{i:02d}.mp4"
            run("ffmpeg","-hide_banner","-loglevel","error","-y","-loop","1",
                "-framerate","30","-i",frame,"-t","3","-r","30",
                "-c:v","libx264","-preset","medium","-crf","17",
                "-pix_fmt","yuv420p","-vf","setsar=1,format=yuv420p","-an",segment)
            segments.append(segment)
            print(f"SCENE_{i} {NAMES[i-1]} SOURCE {width}x{height} RENDER 1080x1920",flush=True)
        playlist=temp/"concat.txt"
        playlist.write_text("".join("file '" + str(p) + "'" + chr(10) for p in segments))
        silent=temp/"silent.mp4"
        run("ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0",
            "-i",playlist,"-c","copy",silent)
        target=OUT/"choose_your_ride_15s.mp4"
        run("ffmpeg","-hide_banner","-loglevel","error","-y","-i",silent,
            "-stream_loop","-1","-i",audio,"-t","15",
            "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac",
            "-b:a","160k","-af","volume=0.35,afade=t=out:st=13.8:d=1.2",
            "-movflags","+faststart",target)
        info={"title":"Choose Your Ride","status":"TEST ONLY; NOT PUBLISHED",
              "video":target.name,"width":1080,"height":1920,"fps":30,
              "seconds":15,"scene_count":5,"seconds_per_scene":3,
              "audio":"Licensed music embedded","source_details":metadata}
        (OUT/"choose_your_ride_details.json").write_text(json.dumps(info,indent=2,ensure_ascii=False)+"\n")
        print("PASS TEST VIDEO:",target,target.stat().st_size,"bytes; no Buffer publishing",flush=True)

if __name__ == "__main__":
    main()
