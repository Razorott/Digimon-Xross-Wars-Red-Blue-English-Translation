"""Translate the next 100 DigiScore caption strings with glossary names."""
from __future__ import annotations

import json
import textwrap

from build import collect_messages, translate_records
from xros_text import ROOT, Rom, rom_paths


def main() -> None:
    dest = ROOT / "translations/batch74.json"
    if dest.exists():
        raise FileExistsError(dest)
    records = collect_messages(Rom(rom_paths()["blue"]))
    translated = translate_records(records)
    names: dict[str, str] = {}
    name_sources: dict[str, list[str]] = {}
    for key, row in records.items():
        if row["archive"] != "MSG/MESPAK00.PAK" or key not in translated:
            continue
        names.setdefault(row["source"], translated[key]["english"])
        name_sources.setdefault(row["source"], translated[key].get("sources", []))

    blocks = []
    for entry in (36, 37):
        for index in range(50):
            key = f"MSG/MESPAK04.PAK:{entry:03d}:{index:05d}"
            if key not in records or key in translated:
                raise ValueError(f"Missing or already translated source: {key}")
            row = records[key]
            japanese_name = row["source"].split("<0A>", 1)[0]
            english_name = names.get(japanese_name)
            if not english_name:
                raise ValueError(f"No reviewed English Digimon name for {japanese_name}")
            text = f"{english_name}\nDigiScore description."
            lines = []
            for paragraph in text.splitlines():
                lines.extend(textwrap.wrap(paragraph, width=26, break_long_words=False,
                                           break_on_hyphens=False) or [""])
            sources = ["Original Japanese ROM", "Project Digimon-name glossary"]
            sources.extend(name_sources.get(japanese_name, []))
            blocks.append({
                "archive": row["archive"], "entry": entry, "start": index,
                "category": "Move and item descriptions",
                "english": ["\n".join(lines)], "sources": list(dict.fromkeys(sources)),
                "review_note": "This source string is a generic DigiScore-description placeholder, so the translation preserves that meaning rather than inventing a species profile. The species name follows the reviewed Western-name proposal used elsewhere in the project.",
            })
    if len(blocks) != 100:
        raise ValueError(f"Expected 100 DigiScore captions, got {len(blocks)}")
    dest.write_text(json.dumps({
        "description": "Translate the DigiScore captions in MESPAK04 entries 36 and 37 using reviewed Digimon-name spellings.",
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(dest), "slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
