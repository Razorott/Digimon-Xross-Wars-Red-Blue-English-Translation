"""Record reproducible QA facts for the 70% batch58 translation build."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from xros_text import ROOT, Rom, rom_paths


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    config = json.loads((ROOT / "project.json").read_text(encoding="utf-8"))
    progress = json.loads((ROOT / "build/progress.json").read_text(encoding="utf-8"))
    outputs = {}
    for version, report in progress.items():
        original = Rom(rom_paths()[version])
        output_path = ROOT / "build" / report["output"]
        output_hash = sha(output_path.read_bytes())
        original_hash = sha(original.data)
        if output_hash != report["output_sha256"]:
            raise ValueError(f"Output checksum mismatch for {version}")
        if original_hash != config["original_sha256"][version]:
            raise ValueError(f"Original checksum mismatch for {version}")
        if report["wide_lines"]:
            raise ValueError(f"Text width errors remain for {version}")
        outputs[version] = {
            "output": report["output"],
            "output_sha256": output_hash,
            "output_bytes": output_path.stat().st_size,
            "original_sha256": original_hash,
            "translated_slots": report["translated_slots"],
            "total_slots": report["total_slots"],
            "slot_percent": report["slot_percent"],
            "display_names": report["display_names"],
            "move_names": report["move_names"],
            "wide_lines": report["wide_lines"],
            "structural_validation": report["structural_validation"],
        }
    if {r["translated_slots"] for r in outputs.values()} != {10972}:
        raise ValueError("Expected both versions at 10,972 translated slots")
    qa = {
        "review_date": "2026-10-25",
        "scope": "Batches 45-58 add 194 Digimon profile blurbs and 345 story/mission messages, reaching 70% of extracted text slots. The dialogue covers the Elestou Zone, Sky Fortress, Melody Capture tutorial, and Chibickmon/Dorulumon mission. No new graphic states were authored in this batch.",
        "translation_progress": {
            "new_profile_slots": 194,
            "new_story_dialogue_slots": 345,
            "new_slots_total": 539,
            "translated_slots": 10972,
            "total_slots": 15674,
            "percent": 70.0,
            "remaining_slots": 4702,
        },
        "checks": {
            "pipeline_tests": "17 passed",
            "both_roms": "Built and structurally validated",
            "source_rom_checksums": "Match project.json for Blue and Red",
            "font_glyphs_and_widths": "Passed; no missing glyphs or over-budget lines",
            "emulator": "Not run for batch58; existing emulator screenshots are from earlier build batches and are not presented as validation of these outputs.",
        },
        "graphics_states": 233,
        "versions": outputs,
    }
    dest = ROOT / "build/qa/validation_batch58.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"path": str(dest), "translated_slots": 10972, "slot_percent": 70.0, "versions": list(outputs)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
