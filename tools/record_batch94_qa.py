"""Record checksum-bound structural and Digidex smoke QA for batch 94."""
from __future__ import annotations

import hashlib
import json
from collections import Counter

from PIL import Image

from xros_text import ROOT, Rom, rom_paths


EXPECTED_SAVE_SHA256 = "ada13c046d762f81631ed5b98d4dee2f1f2ea8010f9897649ca10cd63f3d037d"
EXPECTED_TRANSLATED = 14107
EXPECTED_PROPOSALS = 14579
EXPECTED_PRESERVED = 472
TOTAL_SLOTS = 15674


def sha(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    config = json.loads((ROOT / "project.json").read_text(encoding="utf-8"))
    progress = json.loads((ROOT / "build/progress.json").read_text(encoding="utf-8"))
    source_save = ROOT / "build/qa/digidex_repro/Digimon_Super_Xros_Wars_Blue_English_batch60.dsv"
    test_save = ROOT / "build/qa/digidex_batch94/Digimon_Super_Xros_Wars_Blue_English_batch94.dsv"
    screenshot = ROOT / "build/qa/digidex_batch94/digidex_fixed.png"
    versions = {}
    for version, report in progress.items():
        output = ROOT / "build" / report["output"]
        original = Rom(rom_paths()[version])
        output_hash = sha(output)
        original_hash = hashlib.sha256(original.data).hexdigest()
        if output_hash != report["output_sha256"]:
            raise ValueError(f"Output checksum mismatch for {version}")
        if original_hash != config["original_sha256"][version]:
            raise ValueError(f"Original ROM checksum mismatch for {version}")
        if (report["translated_slots"] != EXPECTED_TRANSLATED
                or report["translation_proposals"] != EXPECTED_PROPOSALS
                or report["runtime_preserved_slots"] != EXPECTED_PRESERVED
                or report["total_slots"] != TOTAL_SLOTS
                or report["wide_lines"]):
            raise ValueError(f"Unexpected translation count or line-width result for {version}")
        if not report["structural_validation"].startswith("passed:"):
            raise ValueError(f"Structural validation did not pass for {version}")
        versions[version] = {
            "output": report["output"],
            "output_sha256": output_hash,
            "output_bytes": output.stat().st_size,
            "original_sha256": original_hash,
            "translated_slots": report["translated_slots"],
            "translation_proposals": report["translation_proposals"],
            "runtime_preserved_slots": report["runtime_preserved_slots"],
            "total_slots": report["total_slots"],
            "slot_percent": report["slot_percent"],
            "proposal_percent": report["proposal_percent"],
            "wide_lines": report["wide_lines"],
            "graphics_translation": report["graphics_translation"],
            "structural_validation": report["structural_validation"],
        }

    if set(versions) != {"blue", "red"}:
        raise ValueError(f"Expected both versions, got {sorted(versions)}")
    if sha(source_save) != EXPECTED_SAVE_SHA256:
        raise ValueError("The supplied source save changed")
    if sha(test_save) != EXPECTED_SAVE_SHA256:
        raise ValueError("The QA save copy changed during the emulator smoke test")

    with Image.open(screenshot) as image:
        pixels = image.convert("RGB").tobytes()
        nonblack = sum(1 for i in range(0, len(pixels), 3)
                       if max(pixels[i:i + 3]) > 8)
        dimensions = list(image.size)
    if dimensions != [256, 384] or nonblack < 1000:
        raise ValueError("The Digidex screenshot is missing or appears black")

    batch_counts = {}
    for number in (93, 94):
        batch = json.loads((ROOT / f"translations/batch{number}.json").read_text(encoding="utf-8"))
        batch_counts[str(number)] = len(batch["blocks"])
    if batch_counts != {"93": 171, "94": 97}:
        raise ValueError(f"Unexpected author batch sizes: {batch_counts}")

    qa = {
        "review_date": "2026-10-26",
        "scope": "Batch 93 adds battle help and Sky Fort NPC dialogue; batch 94 adds tower, rescue, and DWM tournament reactions.",
        "translation_progress": {
            "new_effective_slots": 268,
            "translated_slots": EXPECTED_TRANSLATED,
            "translation_proposals": EXPECTED_PROPOSALS,
            "runtime_preserved_name_slots": EXPECTED_PRESERVED,
            "total_slots": TOTAL_SLOTS,
            "applied_percent": 90.0,
            "proposal_percent": 93.01,
        },
        "checks": {
            "pipeline_tests": "19 passed",
            "both_roms": "Built and structurally validated",
            "line_widths": "Passed; no over-width text lines",
            "digidex_freeze": "Passed on Blue: the profile and list were visible after 4,496 emulator frames; screenshot is not black.",
            "save_handling": "The supplied save and its separate QA copy both retain the previously recorded SHA-256; the original was untouched.",
            "digidex_display_names": "472 proposed name slots remain runtime-preserved in Japanese because writing the shared Digidex name table reproducibly caused a freeze.",
            "graphics": "233 previously localized graphic states remain included; batches 93 and 94 add no new graphic states.",
            "red_emulator_test": "Not run; Red passed structural validation.",
        },
        "batch_sizes": batch_counts,
        "digidex_screenshot": {
            "path": str(screenshot.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha(screenshot),
            "dimensions": dimensions,
            "nonblack_pixels": nonblack,
            "frames": 4496,
        },
        "save_copy": {
            "source": str(source_save.relative_to(ROOT)).replace("\\", "/"),
            "test_copy": str(test_save.relative_to(ROOT)).replace("\\", "/"),
            "sha256_before_and_after": EXPECTED_SAVE_SHA256,
        },
        "versions": versions,
    }
    destination = ROOT / "build/qa/validation_batch94.json"
    destination.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"path": str(destination), "digidex": "passed",
                      "translated_slots": EXPECTED_TRANSLATED,
                      "applied_percent": 90.0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
