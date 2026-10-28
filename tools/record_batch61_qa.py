"""Record checksum-bound QA facts for the batch61 translation build."""
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
    batch = json.loads((ROOT / "translations/batch61.json").read_text(encoding="utf-8"))
    counts = Counter(block["category"] for block in batch["blocks"])
    expected = Counter({"Move and item descriptions": 121, "Story and dialogue": 14})
    if counts != expected:
        raise ValueError(f"Unexpected batch61 categories: {dict(counts)}")

    outputs = {}
    for version, report in progress.items():
        original = Rom(rom_paths()[version])
        output = ROOT / "build" / report["output"]
        output_hash = sha(output.read_bytes())
        original_hash = sha(original.data)
        if output_hash != report["output_sha256"]:
            raise ValueError(f"Output checksum mismatch for {version}")
        if original_hash != config["original_sha256"][version]:
            raise ValueError(f"Original checksum mismatch for {version}")
        if report["translated_slots"] != 11591 or report["wide_lines"]:
            raise ValueError(f"Unexpected translation count or width issue for {version}")
        if not report["structural_validation"].startswith("passed:"):
            raise ValueError(f"Structural validation did not pass for {version}")

        screenshots = {}
        for name in ("boot_splash", "opening_scene"):
            image = ROOT / "build/qa" / f"batch61_smoke_{version}" / f"{name}.png"
            if not image.is_file():
                raise FileNotFoundError(image)
            screenshots[name] = {
                "path": str(image.relative_to(ROOT)).replace("\\", "/"),
                "png_sha256": sha(image.read_bytes()),
            }

        outputs[version] = {
            "output": report["output"],
            "output_sha256": output_hash,
            "output_bytes": output.stat().st_size,
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
            "Batch 61 adds 100 battle-technique descriptions, 21 gift-ticket "
            "descriptions, and 14 story/NPC dialogue slots. No new graphic states "
            "were authored. Digidex profile blurbs continue to use the 28-column "
            "reflow introduced in batch 60."
        ),
        "translation_progress": {
            "new_technique_description_slots": 100,
            "new_ticket_description_slots": 21,
            "new_story_dialogue_slots": 14,
            "new_slots_total": 135,
            "translated_slots": 11591,
            "total_slots": 15674,
            "percent": 73.95,
            "remaining_slots": 4083,
        },
        "checks": {
            "pipeline_tests": "18 passed",
            "both_roms": "Built and structurally validated",
            "source_rom_checksums": "Match project.json for Blue and Red",
            "font_glyphs_and_widths": "Passed; no missing glyphs or over-width text lines",
            "digidex_profile_layout": (
                "All 394 profile blurbs remain within 28 characters and 10 lines."
            ),
            "digidex_freeze": (
                "The black-screen report was not reproduced. Startup smoke testing "
                "does not enter the Digidex; a copy of the user's save or savestate "
                "is still needed to reproduce the freeze in-game."
            ),
            "emulator": (
                "Blue and Red each rendered the boot splash and opening scene. "
                "This does not exercise the Digidex or new technique descriptions."
            ),
            "item_name_audit": (
                "Digimon-only inventory labels were cross-checked against their "
                "paired DigiMemory or gift-ticket descriptions; Kudamon's item is "
                "translated as Kudamon Earring."
            ),
        },
        "graphics_states": 233,
        "versions": outputs,
    }
    destination = ROOT / "build/qa/validation_batch61.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "path": str(destination), "translated_slots": 11591,
        "percent": 73.95, "new_slots": 135, "versions": list(outputs),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
