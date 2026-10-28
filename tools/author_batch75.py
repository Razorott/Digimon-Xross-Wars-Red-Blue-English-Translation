"""Translate Mega DigiScores and the Sky Fort travel items."""
from __future__ import annotations

import json
import textwrap

from build import collect_messages, translate_records
from xros_text import ROOT, Rom, rom_paths


ITEMS = {
    48: "A portable tent where you can rest. Use it at a Tent Point.",
    49: "A pass from Biyomon. Carry it to ride the Digimon Air Corps.",
}


def main() -> None:
    dest = ROOT / "translations/batch75.json"
    if dest.exists():
        raise FileExistsError(dest)
    records = collect_messages(Rom(rom_paths()["blue"]))
    translated = translate_records(records)
    names, sources = {}, {}
    for key, row in records.items():
        if row["archive"] == "MSG/MESPAK00.PAK" and key in translated:
            names.setdefault(row["source"], translated[key]["english"])
            sources.setdefault(row["source"], translated[key].get("sources", []))
    blocks = []
    for index in range(50):
        key = f"MSG/MESPAK04.PAK:038:{index:05d}"
        if key not in records or key in translated:
            raise ValueError(f"Missing or already translated source: {key}")
        row = records[key]
        if index < 48:
            japanese_name = row["source"].split("<0A>", 1)[0]
            english_name = names.get(japanese_name)
            if not english_name:
                raise ValueError(f"No reviewed English Digimon name for {japanese_name}")
            text = f"{english_name}\nDigiScore description."
            extra_sources = sources.get(japanese_name, [])
            note = "Generic DigiScore placeholder translated without inventing a profile; name follows the reviewed project glossary."
        else:
            text = ITEMS[index]
            extra_sources = []
            note = "Direct item-description translation from the Japanese ROM; route and item terminology follow the established project glossary."
        lines = []
        for paragraph in text.splitlines():
            lines.extend(textwrap.wrap(paragraph, width=26, break_long_words=False,
                                       break_on_hyphens=False) or [""])
        blocks.append({
            "archive": row["archive"], "entry": 38, "start": index,
            "category": "Move and item descriptions", "english": ["\n".join(lines)],
            "sources": list(dict.fromkeys(["Original Japanese ROM", "Project Digimon-name glossary", *extra_sources])),
            "review_note": note,
        })
    dest.write_text(json.dumps({
        "description": "Translate the remaining Mega-level DigiScore captions and two travel items in MESPAK04 entry 38.",
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(dest), "slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
