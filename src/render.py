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
from creative_plan import load_for_render

INBOX = ROOT / "assets" / "inbox"
OUT = ROOT / "docs" / "media"
W, H = CONFIG["output_width"], CONFIG["output_height"]
FONT_PATHS = (
    "/usr/share/fonts/truetype/ebgaramond/EBGaramond12-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
)
BOLD_FONT_PATHS = (
    "/usr/share/fonts/truetype/ebgaramond/EBGaramond12-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
)
MIN_SOURCE_W = CONFIG.get("native_source_min_width", 800)
MIN_SOURCE_H = CONFIG.get("native_source_min_height", 1400)
OUT.mkdir(parents=True, exist_ok=True)

def font(size, bold=False):
    for path in (BOLD_FONT_PATHS if bold else FONT_PATHS):
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
            if im.width < MIN_SOURCE_W or im.height < MIN_SOURCE_H:
                print("SKIP:", pic.name, "native source too small", im.size,
                      "need at least", (MIN_SOURCE_W, MIN_SOURCE_H))
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


def draw_frame(source, index, hook, destination, variant_label=None):
    """Gold serif layout from the approved Choose Your Ride demonstration."""
    with Image.open(source) as img:
        img = ImageOps.exif_transpose(img).convert("RGB")
        img = ImageOps.fit(img, (W, H), method=Image.Resampling.LANCZOS)
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shade_draw = ImageDraw.Draw(shade, "RGBA")
    for y in range(265, 615):
        v = max(0.0, 1.0 - abs(y - 425) / 175)
        shade_draw.line([(0, y), (W, y)], fill=(8, 11, 19, int(130*v)))
    for y in range(1305, 1635):
        v = max(0.0, 1.0 - abs(y - 1460) / 180)
        shade_draw.line([(0, y), (W, y)], fill=(8, 11, 19, int(140*v)))
    img = Image.alpha_composite(img.convert("RGBA"), shade)
    draw = ImageDraw.Draw(img, "RGBA")
    cream = (255, 247, 227, 255)
    gold = (240, 203, 144, 255)

    def centered(text, center, f, color):
        draw.text((center[0]+2, center[1]+3), text, font=f, anchor="mm",
                  align="center", spacing=8, fill=(0,0,0,175),
                  stroke_width=2, stroke_fill=(4,6,9,145))
        draw.text(center, text, font=f, anchor="mm", align="center",
                  spacing=8, fill=color, stroke_width=1,
                  stroke_fill=(20,14,10,130))

    centered("D R E A M Y   E L S E W H E R E", (W//2, 329), font(26), gold)
    title = hook.strip()
    for size in range(72, 25, -2):
        chosen = font(size)
        wrapped = wrap_heading(title, chosen, W-150)
        if wrapped is not None:
            break
    else:
        raise ValueError("Title cannot fit in two lines")
    centered(wrapped, (W//2, 437), chosen, cream)
    draw.line([(340,521),(510,521)], fill=(230,185,121,205), width=2)
    draw.line([(570,521),(740,521)], fill=(230,185,121,205), width=2)
    draw.polygon([(540,509),(551,521),(540,533),(529,521)],
                 fill=(250,216,159,230))

    # Decorative number + variant plaque, clear of Instagram bottom controls.
    draw.rounded_rectangle([125,1398,955,1543], radius=29,
                           fill=(13,15,20,191),
                           outline=(229,190,131,238), width=3)
    draw.ellipse([156,1423,260,1527], fill=(28,27,27,230),
                 outline=(245,207,146,248), width=3)
    centered(f"{index:02d}", (208,1475), font(49), cream)
    label = " ".join((variant_label or f"CHOICE {index:02d}").upper().split())
    for size in range(49, 23, -1):
        label_font = font(size, bold=True)
        if draw.textbbox((0,0), label, font=label_font)[2] <= 620:
            break
    else:
        raise ValueError("Variant label is too long for the plaque")
    centered(label, (608,1473), label_font, cream)
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

    plan = load_for_render(day, slot)
    topic = plan["topic"]
    labels = [v["label"] for v in plan["variants"]]
    with tempfile.TemporaryDirectory() as temporary:
        temp = Path(temporary)
        segments = []
        for index, pic in enumerate(pics, 1):
            frame = temp / f"{index:02}.png"
            segment = temp / f"{index:02}.mp4"
            draw_frame(pic, index, topic, frame, labels[index-1])
            if index == 1:
                with Image.open(frame) as cover_frame:
                    cover_frame.convert("RGB").save(cover, format="JPEG",
                                                    quality=94, subsampling=0)
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
        "theme_category": plan["theme_category"], "variants": labels,
        "creative_source": ("legacy" if plan.get("mode") == "legacy"
                            else "open_theme_five_variants"),
        "caption": (f"{topic} 🌙✨\\n\\n"
                    + "\\n".join(f"{i}. {name.title()}" for i, name in enumerate(labels, 1))
                    + "\\n\\nWhich one would you choose? Comment your number! 🌙"
                    + "\\n\\n#DreamyElsewhere #ChooseYourFavorite #DreamWorlds"),
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
