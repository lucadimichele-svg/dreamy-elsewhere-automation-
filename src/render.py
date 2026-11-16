"""Convert five high-resolution Cozy & Dreamy still images into one Reel.

No subjective aesthetic judgement. Does not generate images or silently embed
commercial music. Input: assets/inbox/YYYY-MM-DD_S1/01.jpg through 05.jpg.
"""
import argparse
import json
import os
import subprocess
import tempfile
from datetime import date, timedelta
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
from schedule import ROOT, CONFIG, slots_for, reel_key, marker

INBOX = ROOT / "assets" / "inbox"
OUT = ROOT / "docs" / "media"
W, H = CONFIG["output_width"], CONFIG["output_height"]
FONT_PATHS = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
)
OUT.mkdir(parents=True, exist_ok=True)

def font(size):
    for path in FONT_PATHS:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def find_images(folder):
    if not folder.is_dir():
        return []
    pics = sorted(p for p in folder.iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"))
    if len(pics) != 5:
        print("SKIP:", folder.name, "requires exactly five images; found", len(pics))
        return []
    for pic in pics:
        with Image.open(pic) as im:
            if im.width < W or im.height < H:
                print("SKIP:", pic.name, "too small", im.size, "need", (W, H))
                return []
    return pics

def draw_frame(source, index, hook, destination):
    with Image.open(source) as img:
        img = ImageOps.exif_transpose(img).convert("RGB")
        img = ImageOps.fit(img, (W, H), method=Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rounded_rectangle((40, 120, W-40, 342), radius=28, fill=(11, 19, 31, 148))
    label = hook[:90]
    chosen_font = font(54 if len(label) < 38 else 44)
    if draw.textbbox((0, 0), label, font=chosen_font)[2] > W - 150:
        words = label.split()
        middle = len(words) // 2
        label = " ".join(words[:middle]) + "\n" + " ".join(words[middle:])
    draw.multiline_text((W/2, 228), label, font=chosen_font, anchor="mm",
                        align="center", spacing=7, fill=(255, 249, 236, 255))
    draw.ellipse((60, 370, 186, 496), fill=(12, 23, 39, 190),
                 outline=(243, 223, 186, 240), width=3)
    draw.text((123, 433), str(index), font=font(64), anchor="mm",
              fill=(255, 249, 236, 255))
    draw.rounded_rectangle((W-296, H-163, W-48, H-98), radius=21,
                           fill=(11, 22, 39, 155))
    draw.text((W-172, H-131), "Dreamy Elsewhere", font=font(23), anchor="mm",
              fill=(245, 232, 213, 255))
    img.save(destination, quality=93, subsampling=0)

def run(cmd):
    subprocess.run(cmd, check=True)

def make_one(day, slot):
    stem = reel_key(day, slot)
    pics = find_images(INBOX / stem)
    if not pics:
        return False
    target, cover, manifest = (OUT / f"{stem}.{ext}" for ext in ("mp4", "jpg", "json"))
    if target.exists() and manifest.exists():
        return False

    # Never mark a silent Reel as finished when music is mandatory.
    optional_path = os.environ.get("DREAMY_AUDIO_PATH")
    candidates = ([Path(optional_path)] if optional_path else []) + [
        ROOT / "assets/audio/background.mp3",
        ROOT / "assets/audio/background.m4a",
        ROOT / "assets/audio/background.wav",
    ]
    audio = next((p for p in candidates if p.is_file()), None)
    if audio is None:
        raise RuntimeError("Licensed soundtrack missing: no silent Dreamy Elsewhere Reel will be rendered.")

    offset = (day - date.fromisoformat(CONFIG["launch_date"])).days
    topic = CONFIG["topics"][(offset * 4 + int(slot[1:]) - 1) % len(CONFIG["topics"])]
    with tempfile.TemporaryDirectory() as temporary:
        temp = Path(temporary)
        segments = []
        for index, pic in enumerate(pics, 1):
            frame = temp / f"{index:02}.jpg"
            segment = temp / f"{index:02}.mp4"
            draw_frame(pic, index, topic, frame)
            if index == 1:
                cover.write_bytes(frame.read_bytes())
            run(["ffmpeg", "-loglevel", "error", "-y", "-loop", "1",
                 "-i", str(frame), "-t", "3", "-r", "25", "-c:v", "libx264",
                 "-preset", "fast", "-pix_fmt", "yuv420p", "-vf", "setsar=1",
                 "-an", str(segment)])
            segments.append(segment)
        playlist = temp / "concat.txt"
        playlist.write_text("".join(f"file '{p}'\n" for p in segments))
        silent = temp / "silent.mp4"
        run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
             "-i", str(playlist), "-c", "copy", str(silent)])
        run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(silent),
             "-stream_loop", "-1", "-i", str(audio), "-t", "15",
             "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a",
             "aac", "-b:a", "160k", "-filter:a",
             "volume=0.35,afade=t=out:st=13.8:d=1.2", "-movflags",
             "+faststart", str(target)])
    meta = {
        "date": str(day), "slot": slot, "marker": marker(day, slot),
        "video": target.name, "cover": cover.name, "topic": topic,
        "caption": f"{topic} 🌙✨\n\n1, 2, 3, 4 or 5? Tell us below!\n\n#DreamyElsewhere #CozyAesthetic #DreamyPlaces",
        "audio_status": "EMBEDDED_AUDIO",
        "image_count": 5, "duration_seconds": 15,
    }
    manifest.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
    print("RENDERED", stem)
    return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default=str(date.today()))
    ap.add_argument("--days", type=int, default=9)
    args = ap.parse_args()
    start = date.fromisoformat(args.start)
    count = sum(bool(make_one(start + timedelta(days=d), slot))
                for d in range(args.days)
                for slot, _ in slots_for(start + timedelta(days=d)))
    print("Rendered", count, "new Reels; no missing images synthesized.")

if __name__ == "__main__":
    main()
