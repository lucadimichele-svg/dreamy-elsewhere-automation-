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

def wrap_heading(text, chosen_font, max_width):
    """Wrap to at most two centered lines without cutting off any words."""
    words = text.strip().split()
    if not words:
        return ""
    draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    lines = [words[0]]
    for word in words[1:]:
        proposal = lines[-1] + " " + word
        if draw.textbbox((0, 0), proposal, font=chosen_font)[2] <= max_width:
            lines[-1] = proposal
        else:
            lines.append(word)
    if len(lines) <= 2:
        return "\n".join(lines)
    # Exact text is retained: reduce the font size in draw_frame if needed.
    return None


def draw_frame(source, index, hook, destination):
    """Full-bleed 9:16 frame with unobtrusive text below Instagram's top UI."""
    with Image.open(source) as img:
        img = ImageOps.exif_transpose(img).convert("RGB")
        # ImageOps.fit crops instead of adding side bars or stretching pixels.
        img = ImageOps.fit(img, (W, H), method=Image.Resampling.LANCZOS,
                           centering=(0.5, 0.5))
        # Subtle sharpening after resize; no artificial detail is invented.
        from PIL import ImageFilter
        img = img.filter(ImageFilter.UnsharpMask(radius=1.05, percent=115,
                                                threshold=3))

    # A very soft full-width shade avoids the opaque grey rounded rectangle.
    # The top 320px and bottom UI area remain free of captions.
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shade_pixels = ImageDraw.Draw(shade, "RGBA")
    for y in range(340, 640):
        p = (y - 340) / 300
        opacity = round(59 * (1.0 - abs(2.0 * p - 1.0)))
        if opacity:
            shade_pixels.line([(0, y), (W, y)], fill=(9, 16, 25, opacity))
    img = Image.alpha_composite(img.convert("RGBA"), shade)
    draw = ImageDraw.Draw(img)

    # Restrained elegant white title, in the safe center-upper area.
    label = hook.strip()
    for size in range(46, 29, -2):
        chosen_font = font(size)
        wrapped = wrap_heading(label, chosen_font, W - 148)
        if wrapped is not None:
            break
    if wrapped is None:
        raise ValueError("Cannot fit title into two lines")
    draw.multiline_text((W // 2 + 2, 456 + 3), wrapped,
                        font=chosen_font, anchor="mm", align="center",
                        spacing=11, fill=(0, 0, 0, 155),
                        stroke_width=2, stroke_fill=(0, 0, 0, 105))
    draw.multiline_text((W // 2, 456), wrapped, font=chosen_font,
                        anchor="mm", align="center", spacing=11,
                        fill=(249, 248, 246, 255),
                        stroke_width=1, stroke_fill=(21, 27, 32, 100))

    # The number is necessary for "1–5?" comments, but not a side badge.
    # No left border, bar, circle, or extra branding panel.
    numeral = f"{index:02d}  /  05"
    draw.text((W // 2 + 1, 572 + 2), numeral, font=font(28), anchor="mm",
              fill=(0, 0, 0, 155))
    draw.text((W // 2, 572), numeral, font=font(28), anchor="mm",
              fill=(253, 247, 235, 235))
    img.convert("RGB").save(destination, format="PNG", optimize=True)


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
            frame = temp / f"{index:02}.png"
            segment = temp / f"{index:02}.mp4"
            draw_frame(pic, index, topic, frame)
            if index == 1:
                cover.write_bytes(frame.read_bytes())
            run(["ffmpeg", "-loglevel", "error", "-y", "-loop", "1",
                 "-framerate", "30", "-i", str(frame), "-t", "3", "-r", "30",
                 "-c:v", "libx264", "-preset", "slow", "-crf", "17",
                 "-pix_fmt", "yuv420p", "-vf", "setsar=1,format=yuv420p",
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
