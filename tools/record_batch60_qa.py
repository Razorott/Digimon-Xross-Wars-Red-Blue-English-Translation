"""Record checksum-bound QA facts for the batch60 translation build."""
from __future__ import annotations

import hashlib
import json
from collections import Counter

from xros_text import ROOT, Rom, rom_paths


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    config = json.loads((ROOT / "project.json").read_text(encoding="utf-8"))
    progress = json.loads((ROOT / "build/progress.json").read_text(encoding="utf-8"))
    batch = json.loads((ROOT / "translations/batch60.json").read_text(encoding="utf-8"))
    batch_counts = Counter(block["category"] for block in batch["blocks"])
    expected_counts = Counter({
        "Story and dialogue": 163,
        "Move and item descriptions": 66,
        "DigiFarm reports": 3,
    })
    if batch_counts != expected_counts:
        raise ValueError(f"Unexpected batch60 categories: {dict(batch_counts)}")

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
        if report["translated_slots"] != 11456 or report["wide_lines"]:
            raise ValueError(f"Unexpected translation count or text width issue for {version}")
        if not report["structural_validation"].startswith("passed:"):
            raise ValueError(f"Structural validation did not pass for {version}")

        screenshots = {}
        for name in ("boot_splash", "opening_scene"):
            image_path = ROOT / "build/qa" / f"batch60_smoke_{version}" / f"{name}.png"
            if not image_path.is_file():
                raise FileNotFoundError(image_path)
            screenshots[name] = {
                "path": str(image_path.relative_to(ROOT)).replace("\\", "/"),
                "png_sha256": sha(image_path.read_bytes()),
            }

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
            "emulator_screenshots": screenshots,
        }

    if set(outputs) != {"blue", "red"}:
        raise ValueError(f"Expected Blue and Red builds, got {sorted(outputs)}")

    qa = {
        "review_date": "2026-10-25",
        "scope": (
            "Batch60 adds 163 Pharaohmon/Crystal Volcano story slots, 66 battle "
            "technique descriptions, and the final 3 tree-sap DigiFarm reports. "
            "The 394 Digidex profile blurbs now reflow at 28 columns instead of "
            "the portrait-dialogue width. No new graphic states were authored."
        ),
        "translation_progress": {
            "new_story_dialogue_slots": 163,
            "new_technique_description_slots": 66,
            "new_digifarm_report_slots": 3,
            "new_slots_total": 232,
            "translated_slots": 11456,
            "total_slots": 15674,
            "percent": 73.09,
            "remaining_slots": 4218,
        },
        "checks": {
            "pipeline_tests": "18 passed",
            "both_roms": "Built and structurally validated",
            "source_rom_checksums": "Match project.json for Blue and Red",
            "font_glyphs_and_widths": "Passed; no missing glyphs or over-budget text lines",
            "digidex_profile_layout": (
                "Automated regression confirms all 394 blurbs are at most 28 "
                "characters wide and 10 lines long."
            ),
            "digidex_freeze": (
                "The reported black screen was not reproduced in startup smoke "
                "testing. In-game confirmation still needs the user's Digidex save "
                "or savestate."
            ),
            "emulator": (
                "Blue and Red each rendered the boot splash and opening scene. "
                "This does not exercise the later story, the Digidex, or the new "
                "battle-technique screens."
            ),
        },
        "graphics_states": 233,
        "versions": outputs,
    }
    dest = ROOT / "build/qa/validation_batch60.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "path": str(dest), "translated_slots": 11456,
        "percent": 73.09, "new_slots": 232,
        "versions": list(outputs),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
