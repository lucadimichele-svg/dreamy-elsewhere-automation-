"""Objective scene-subject integrity contract for future Dreamy Elsewhere Reels.

This is NOT an aesthetic scorer: a theme requires its named subject to be visible.
The creative agent must visually check each REAL generated source after creation
and write a per-image attestation. Importer enforces its slot/label/file hash.
It cannot independently determine semantics from pixels; do not claim it can.
"""
import hashlib
import json
import re
from datetime import date
from pathlib import Path

from schedule import ROOT

AUDITS = ROOT / "assets" / "scene_audits"
ENFORCE_DATE = date(2026, 11, 20)
ENFORCE_FIRST_SLOT = 2
HEX_SHA256 = re.compile(r"^[a-f0-9]{64}$")


class SubjectMismatch(RuntimeError):
    pass


def required(day, slot):
    return day > ENFORCE_DATE or (day == ENFORCE_DATE and int(slot[1:]) >= ENFORCE_FIRST_SLOT)


def check_new_plan_fields(plan, stem):
    d, slot = stem.split("_")
    if not required(date.fromisoformat(d), slot):
        return
    subject = plan.get("core_subject")
    if not isinstance(subject, str) or not 3 <= len(subject.strip()) <= 80:
        raise SubjectMismatch("core_subject missing: what must visibly connect all five scenes?")
    for i, variant in enumerate(plan.get("variants", []), 1):
        anchor = variant.get("must_show")
        prompt = variant.get("image_prompt")
        if not isinstance(anchor, str) or not 5 <= len(anchor.strip()) <= 180:
            raise SubjectMismatch(f"Scene {i}: must_show visibly described subject missing")
        if not isinstance(prompt, str) or len(prompt) < 50:
            raise SubjectMismatch(f"Scene {i}: standalone prompt must describe the object")
        if not any(word in prompt.casefold() for word in anchor.casefold().split() if len(word) >= 5):
            raise SubjectMismatch(f"Scene {i}: must_show object must be mentioned in prompt")


def load_audit(stem, plan):
    path = AUDITS / (stem + ".json")
    if not path.is_file():
        raise SubjectMismatch(f"Missing per-image topic-presence audit: {path}")
    try:
        audit = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        raise SubjectMismatch(f"Unreadable scene audit: {stem}") from exc
    if audit.get("date") != plan["date"] or audit.get("slot") != plan["slot"]:
        raise SubjectMismatch("Audit date or slot mismatch")
    if audit.get("topic") != plan["topic"] or audit.get("core_subject") != plan["core_subject"]:
        raise SubjectMismatch("Audit subject or theme does not match creative plan")
    scenes = audit.get("files")
    if not isinstance(scenes,list) or len(scenes)!=5:
        raise SubjectMismatch("Exactly five independently reviewed image records required")
    hashes = []
    for i, (record, variant) in enumerate(zip(scenes, plan["variants"]), 1):
        if not isinstance(record, dict) or record.get("name") != f"{i:02d}.png":
            raise SubjectMismatch(f"Audit scene {i} file missing/out of order")
        if record.get("label") != variant["label"] or record.get("must_show") != variant["must_show"]:
            raise SubjectMismatch(f"Audit scene {i} label / required subject does not match plan")
        h = record.get("sha256")
        if not isinstance(h,str) or not HEX_SHA256.fullmatch(h):
            raise SubjectMismatch(f"Audit scene {i} needs sha256 of the ACTUAL PNG bytes")
        if record.get("subject_visible") is not True or record.get("subject_dominant") is not True:
            raise SubjectMismatch(f"Audit scene {i} does NOT depict its required main subject")
        observation = record.get("observed_subject")
        if not isinstance(observation, str) or not 12 <= len(observation.strip()) <= 300:
            raise SubjectMismatch(f"Audit scene {i} must explain visible object, not aesthetics")
        hashes.append(h)
    if len(set(hashes)) != 5:
        raise SubjectMismatch("Audit has repeated file hashes; five original scenes required")
    return audit


def check_payload(audit, index, payload):
    expected = audit["files"][index - 1]["sha256"]
    observed = hashlib.sha256(payload).hexdigest()
    if observed != expected:
        raise SubjectMismatch(
            f"Scene {index} Drive bytes differ from checked original; refuse unrelated upload")
    return observed
