"""Record checksum-bound build and save-based Digidex QA for batch 63."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from PIL import Image
from xros_text import ROOT, Rom, rom_paths


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    config = json.loads((ROOT / "project.json").read_text(encoding="utf-8"))
    progress = json.loads((ROOT / "build/progress.json").read_text(encoding="utf-8"))
    batch = json.loads((ROOT / "translations/batch63.json").read_text(encoding="utf-8"))
    counts = Counter(block["category"] for block in batch["blocks"])
    if counts != Counter({"Story and dialogue": 87}):
        raise ValueError(f"Unexpected batch63 categories: {dict(counts)}")

    versions = {}
    for version, report in progress.items():
        output = ROOT / "build" / report["output"]
        original = Rom(rom_paths()[version])
        output_hash = sha(output.read_bytes())
        original_hash = sha(original.data)
        if output_hash != report["output_sha256"]:
            raise ValueError(f"Output checksum mismatch for {version}")
        if original_hash != config["original_sha256"][version]:
            raise ValueError(f"Original checksum mismatch for {version}")
        if report["translated_slots"] != 11480 or report["translation_proposals"] != 11952:
            raise ValueError(f"Unexpected translation totals for {version}")
        if report["runtime_preserved_slots"] != 472 or report["wide_lines"]:
            raise ValueError(f"Unexpected preserved-name count or width issue for {version}")
        if not report["structural_validation"].startswith("passed:"):
            raise ValueError(f"Structural validation did not pass for {version}")
        versions[version] = {
            "output": report["output"], "output_sha256": output_hash,
            "output_bytes": output.stat().st_size,
            "original_sha256": original_hash,
            "translated_slots": report["translated_slots"],
            "translation_proposals": report["translation_proposals"],
            "runtime_preserved_slots": report["runtime_preserved_slots"],
            "slot_percent": report["slot_percent"],
            "proposal_percent": report["proposal_percent"],
            "wide_lines": report["wide_lines"],
            "structural_validation": report["structural_validation"],
        }

    if set(versions) != {"blue", "red"}:
        raise ValueError(f"Expected Blue and Red builds, got {sorted(versions)}")

    source_save = ROOT / "build/qa/digidex_repro/Digimon_Super_Xros_Wars_Blue_English_batch60.dsv"
    test_save = ROOT / "build/qa/digidex_batch63/Digimon_Super_Xros_Wars_Blue_English_batch63.dsv"
    expected_save_hash = "ada13c046d762f81631ed5b98d4dee2f1f2ea8010f9897649ca10cd63f3d037d"
    source_save_hash = sha(source_save.read_bytes())
    test_save_hash = sha(test_save.read_bytes())
    if source_save_hash != expected_save_hash or test_save_hash != expected_save_hash:
        raise ValueError("The supplied save copy changed during Digidex testing")

    screenshot = ROOT / "build/qa/digidex_batch63/digidex_fixed.png"
    with Image.open(screenshot) as image:
        rgb = image.convert("RGB")
        pixels = rgb.tobytes()
        nonblack = sum(1 for offset in range(0, len(pixels), 3)
                       if max(pixels[offset:offset + 3]) > 8)
        if nonblack < 1000:
            raise ValueError("DigiDex screenshot appears black")
        dimensions = list(image.size)

    qa = {
        "review_date": "2026-10-26",
        "scope": (
            "Batch 63 adds 87 Farm Island, field-skill, attribute-tip, and character-quiz dialogue slots. "
            "The Blue Digidex was opened from a separate copy of the supplied save."
        ),
        "translation_progress": {
            "new_dialogue_slots": 87,
            "translated_slots": 11480,
            "translation_proposals": 11952,
            "runtime_preserved_name_slots": 472,
            "total_slots": 15674,
            "applied_percent": 73.24,
            "proposal_percent": 76.25,
        },
        "checks": {
            "pipeline_tests": "19 passed",
            "both_roms": "Built and structurally validated",
            "source_rom_checksums": "Match project.json for Blue and Red",
            "line_widths": "Passed; no over-width text lines",
            "digidex_freeze": (
                "Passed on Blue: after 4,496 frames, the Digidex profile and list were visible; "
                "the screenshot is not black. The 472 short-name labels remain Japanese in the ROM "
                "because translating the shared lookup table reproducibly caused the freeze."
            ),
            "save_handling": (
                "The user-provided save copy was cloned into the QA output folder. Its SHA-256 "
                "remained unchanged; the user's source copy was not modified."
            ),
            "digidex_display_names": (
                "English name proposals remain in the layout manifest for review, marked applied=false "
                "and runtime_preserved=true."
            ),
            "graphics": "233 existing localized graphic states; no new graphic states in batch 63",
            "red_emulator_test": "Not run in this batch; Red passed structural validation.",
        },
        "digidex_screenshot": {
            "path": str(screenshot.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha(screenshot.read_bytes()),
            "dimensions": dimensions,
            "nonblack_pixels": nonblack,
            "frames": 4496,
        },
        "save_copy": {
            "source": str(source_save.relative_to(ROOT)).replace("\\", "/"),
            "test_copy": str(test_save.relative_to(ROOT)).replace("\\", "/"),
            "sha256_before_and_after": source_save_hash,
        },
        "versions": versions,
    }
    destination = ROOT / "build/qa/validation_batch63.json"
    destination.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"path": str(destination), "blue_digidex": "passed",
                      "translated_slots": 11480, "applied_percent": 73.24,
                      "proposal_percent": 76.25}, ensure_ascii=False))


if __name__ == "__main__":
    main()
