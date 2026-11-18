"""End-to-end technical smoke for new free-theme plan -> real 15s Reel (NEVER published)."""
import json
import os
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from schedule import ROOT, CONFIG
from creative_plan import validate_plan, load_for_render, recent_history, CreativePlanError
import render

assert CONFIG["account"] == "dreamy_elsewhere"
assert CONFIG["creative_mode"] == "open_theme_five_variants"
assert "topics" not in CONFIG, "Fixed topic list must not be active"
assert CONFIG["legacy_topics"], "Old posts must stay compatible"
assert load_for_render(date(2026,11,17),"S4")["mode"] == "legacy"

day = date(2099, 1, 5)  # Will NEVER match Buffer's current publishing window.
stem = f"{day}_S1"
plan_path = ROOT / "assets/creative_plans" / f"{stem}.json"
images = ROOT / "assets/inbox" / stem
outputs = [ROOT / "docs/media" / f"{stem}.{ext}" for ext in ("mp4","jpg","json")]
plan = {
  "date":str(day), "slot":"S1", "topic":"Which fantastic breakfast would you choose?",
  "theme_category":"culinary/history/sci-fi",
  "variants":[
    {"label":"MEDIEVAL BANQUET","brief":"A crowded candlelit medieval breakfast table in a stone hall"},
    {"label":"ROMAN VILLA","brief":"Breakfast in a marble Roman villa with food in terra cotta bowls"},
    {"label":"PHARAOH'S FEAST","brief":"Ancient Egyptian breakfast in a palace beside a lotus pond"},
    {"label":"JAPANESE RYOKAN","brief":"Traditional Japanese breakfast in a wooden ryokan garden room"},
    {"label":"ORBITAL BREAKFAST","brief":"Futuristic space station breakfast floating above Earth"}
  ]
}
with tempfile.TemporaryDirectory() as td:
    temporary = Path(td)
    audio = temporary / "test_audio.mp3"
    try:
        assert not plan_path.exists(), "Smoke plan must use an unused stem"
        assert not any(path.exists() for path in outputs), "Smoke media must not preexist"
        plan_path.parent.mkdir(parents=True,exist_ok=True)
        plan_path.write_text(json.dumps(plan,ensure_ascii=False)+"\n",encoding="utf-8")
        assert validate_plan(plan,stem)["topic"] == plan["topic"]
        assert load_for_render(day,"S1")["variants"][2]["label"] == "PHARAOH'S FEAST"
        assert recent_history()[0]["id"] == stem

        images.mkdir(parents=True,exist_ok=True)
        for i in range(5):
            source = Image.new("RGB", (1200, 2100), [(60,88,148),(117,82,60),(170,116,48),(45,123,95),(42,54,122)][i])
            d = ImageDraw.Draw(source)
            d.rectangle([150,670,900,1260],fill=(190,150+i*12,100+i*11))
            source.save(images/f"{i+1:02d}.png")
        subprocess.run(["ffmpeg","-loglevel","error","-y","-f","lavfi",
          "-i","sine=frequency=280:sample_rate=44100","-t","15",
          "-c:a","libmp3lame",str(audio)],check=True)
        os.environ["DREAMY_AUDIO_PATH"]=str(audio)
        assert render.make_one(day,"S1")
        assert outputs[0].is_file() and outputs[0].stat().st_size > 100000
        with Image.open(outputs[1]) as cover:
            assert cover.format=="JPEG", cover.format
            assert cover.size == (1080,1920), cover.size
        meta=json.loads(outputs[2].read_text(encoding="utf-8"))
        assert meta["topic"]==plan["topic"]
        assert meta["theme_category"]==plan["theme_category"]
        assert meta["creative_source"]=="open_theme_five_variants"
        assert meta["variants"]==[v["label"] for v in plan["variants"]]
        assert "5. Orbital Breakfast" in meta["caption"]
        assert "\\n" not in meta["caption"],"Caption contains literal slash-n"
        info=subprocess.check_output(["ffprobe","-v","error",
            "-show_entries","stream=codec_type,width,height,r_frame_rate",
            "-of","json",str(outputs[0])],text=True)
        streams=json.loads(info)["streams"]
        assert any(s.get("codec_type")=="video" and s.get("width")==1080 and
                   s.get("height")==1920 and s.get("r_frame_rate")=="30/1" for s in streams)
        assert any(s.get("codec_type")=="audio" for s in streams)
        print("PASS: open creative plan + five labeled scenes -> 1080x1920 H264/AAC 15s MP4")
        print("PASS: poster cover JPEG; caption with all variant labels; no publishing")
    finally:
        for file in outputs:
            file.unlink(missing_ok=True)
        plan_path.unlink(missing_ok=True)
        if images.exists():
            for file in images.glob("*.png"):
                file.unlink()
            images.rmdir()
