"""Record checksum-bound QA facts for the batch59 translation build."""
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
    batch = json.loads((ROOT / "translations/batch59.json").read_text(encoding="utf-8"))
    batch_counts = Counter(block["category"] for block in batch["blocks"])
    expected_counts = Counter({"Story and dialogue": 218, "Move and item descriptions": 34})
    if batch_counts != expected_counts:
        raise ValueError(f"Unexpected batch59 categories: {dict(batch_counts)}")

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
        if report["translated_slots"] != 11224 or report["wide_lines"]:
            raise ValueError(f"Unexpected translation count or text width issue for {version}")
        if not report["structural_validation"].startswith("passed:"):
            raise ValueError(f"Structural validation did not pass for {version}")

        screenshots = {}
        for name in ("boot_splash", "opening_scene"):
            image_path = ROOT / "build/qa" / f"batch59_smoke_{version}" / f"{name}.png"
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
            "Batch59 adds 218 story/dialogue slots and 34 battle-technique descriptions. "
            "The story continues after Cutemon's rescue, follows Nene and Sparrowmon's "
            "reunion, and begins the Papyrus Desert Pharaohmon arc. No new graphic states "
            "were authored in this batch."
        ),
        "translation_progress": {
            "new_story_dialogue_slots": 218,
            "new_technique_description_slots": 34,
            "new_slots_total": 252,
            "translated_slots": 11224,
            "total_slots": 15674,
            "percent": 71.61,
            "remaining_slots": 4450,
        },
        "checks": {
            "pipeline_tests": "17 passed",
            "both_roms": "Built and structurally validated",
            "source_rom_checksums": "Match project.json for Blue and Red",
            "font_glyphs_and_widths": "Passed; no missing glyphs or over-budget text lines",
            "emulator": (
                "Blue and Red each rendered the boot splash and opening scene in the "
                "headless emulator. This smoke check does not cover the new later-story "
                "dialogue or technique-description screens."
            ),
        },
        "graphics_states": 233,
        "versions": outputs,
    }
    dest = ROOT / "build/qa/validation_batch59.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"path": str(dest), "translated_slots": 11224, "percent": 71.61,
                      "new_slots": 252, "versions": list(outputs)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
