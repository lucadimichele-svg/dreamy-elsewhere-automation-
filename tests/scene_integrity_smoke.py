"""Test exact-theme auditable-source contract; does not claim visual model competence."""
import hashlib
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import scene_integrity as integrity
from creative_plan import validate_plan, CreativePlanError

stem="2026-11-20_S2"
plan={
    "date":"2026-11-20",
    "slot":"S2",
    "topic":"Which extraordinary bridge would you cross?",
    "theme_category":"architecture/bridges",
    "core_subject":"bridge",
    "variants":[
        {
            "label":f"BRIDGE {i:02d}",
            "brief":f"An unmistakable scenic engineered bridge spanning a distinct gorge scene {i}",
            "must_show":f"A large visible bridge spans the canyon in image {i}",
            "image_prompt":f"Bridge! A large visible bridge spans the center of a canyon in image {i}. The bridge itself is the dominant main subject, photograph in 9:16."
        }
        for i in range(1,6)
    ]
}
assert validate_plan(plan,stem)["core_subject"]=="bridge"
no_subject={**plan,"core_subject":""}
try:
    validate_plan(no_subject,stem)
except integrity.SubjectMismatch:
    pass
else:
    raise AssertionError("Plan without shared main subject was wrongly accepted")

with tempfile.TemporaryDirectory() as td:
    integrity.AUDITS=Path(td)
    payloads=[("unique raw source "+str(i)).encode() for i in range(1,6)]
    files=[]
    for i,(v,payload) in enumerate(zip(plan["variants"],payloads),1):
        files.append({
            "name":f"{i:02d}.png",
            "label":v["label"],
            "must_show":v["must_show"],
            "sha256":hashlib.sha256(payload).hexdigest(),
            "subject_visible":True,
            "subject_dominant":True,
            "observed_subject":f"Test reviewer attests a large bridge spanning the canyon in scene {i}."
        })
    audit={"date":plan["date"],"slot":plan["slot"],"topic":plan["topic"],
           "core_subject":plan["core_subject"],"files":files}
    path=integrity.AUDITS/(stem+".json")
    path.write_text(json.dumps(audit),encoding="utf-8")
    verified=integrity.load_audit(stem,plan)
    for i,payload in enumerate(payloads,1):
        assert integrity.check_payload(verified,i,payload)==files[i-1]["sha256"]
    print("PASS: exact five labeled source identities match audit and raw Drive bytes")

    try:
        integrity.check_payload(verified,2,b"wrong theme image")
    except integrity.SubjectMismatch:
        pass
    else:
        raise AssertionError("Mismatched source file did not fail")

    audit["files"][1]["subject_dominant"]=False
    path.write_text(json.dumps(audit),encoding="utf-8")
    try:
        integrity.load_audit(stem,plan)
    except integrity.SubjectMismatch:
        pass
    else:
        raise AssertionError("Wrong-object attestation did not fail")
    print("PASS: wrong source hash and unconfirmed theme object are rejected")
print("PASS: legacy slots not retroactively blocked:",not integrity.required(__import__("datetime").date(2026,11,19),"S4"))
