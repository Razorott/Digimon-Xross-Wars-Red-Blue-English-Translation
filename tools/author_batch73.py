"""Translate the final DigiFarm reward reports and DigiScore captions."""
from __future__ import annotations

import json
import textwrap

from build import collect_messages, translate_records
from xros_text import ROOT, Rom, rom_paths


TEXT = {
    34: [
        "Moderately increases DigiFarm EXP. Machine Digimon gain more.",
        "Greatly increases DigiFarm EXP. Machine Digimon gain more.",
        "Slightly increases DigiFarm EXP. Aquatic Digimon gain more.",
        "Moderately increases DigiFarm EXP. Aquatic Digimon gain more.",
        "Greatly increases DigiFarm EXP. Aquatic Digimon gain more.",
        "Slightly increases DigiFarm EXP. Bird Digimon gain more.",
        "Moderately increases DigiFarm EXP. Bird Digimon gain more.",
        "Greatly increases DigiFarm EXP. Bird Digimon gain more.",
        "Slightly increases DigiFarm EXP. Insect Digimon gain more.",
        "Moderately increases DigiFarm EXP. Insect Digimon gain more.",
        "Greatly increases DigiFarm EXP. Insect Digimon gain more.",
        "Slightly increases DigiFarm EXP. Plant Digimon gain more.",
        "Moderately increases DigiFarm EXP. Plant Digimon gain more.",
        "Greatly increases DigiFarm EXP. Plant Digimon gain more.",
        "Ask a Digimon to make an ordinary weapon.",
        "Ask a Digimon to make a decent weapon.",
        "Ask a Digimon to make a good weapon.",
        "Ask a Digimon to make a great weapon.",
        "Ask a Digimon to make an excellent weapon.",
        "Ask a Digimon to make ordinary armor.",
        "Ask a Digimon to make decent armor.",
        "Ask a Digimon to make good armor.",
        "Ask a Digimon to make great armor.",
        "Ask a Digimon to make excellent armor.",
        "Friendship +1\nNo item.",
        "Friendship +2\nNo item.",
        "Found 100 bits\nNo item.",
        "Found 500 bits\nNo item.",
        "Found 1,000 bits\nNo item.",
        "Calumon▼\nDigiScore description.",
        "Calumon▲\nDigiScore description.",
        "IceDevimon\nDigiScore description.",
        "Aquilamon\nDigiScore description.",
        "Agunimon\nDigiScore description.",
        "Ankylomon\nDigiScore description.",
        "Airdramon\nDigiScore description.",
        "ExVeemon\nDigiScore description.",
        "Angemon\nDigiScore description.",
        "Kabuterimon▼\nDigiScore description.",
        "Kabuterimon▲\nDigiScore description.",
        "Gaogamon\nDigiScore description.",
        "Gargomon\nDigiScore description.",
        "Garurumon\nDigiScore description.",
        "Kyubimon\nDigiScore description.",
        "Chrysalimon\nDigiScore description.",
        "Growlmon\nDigiScore description.",
        "Greymon L\nDigiScore description.",
        "Gekomon\nDigiScore description.",
        "Seasarmon\nDigiScore description.",
        "Coelamon\nDigiScore description.",
    ],
    35: [
        "Shellmon\nDigiScore description.",
        "Stingmon\nDigiScore description.",
        "Tankmon\nDigiScore description.",
        "Tyrannomon\nDigiScore description.",
        "Gatomon\nDigiScore description.",
        "Devimon\nDigiScore description.",
        "DORUgamon\nDigiScore description.",
        "Apemon\nDigiScore description.",
        "Bakemon\nDigiScore description.",
        "Firamon\nDigiScore description.",
        "Buraimon\nDigiScore description.",
        "Minotaurmon\nDigiScore description.",
        "Musyamon\nDigiScore description.",
        "Raptordramon\nDigiScore description.",
        "Dolphmon\nDigiScore description.",
        "Leomon▼\nDigiScore description.",
        "Leomon▲\nDigiScore description.",
        "Lekismon\nDigiScore description.",
        "Argomon (Ultimate)\nDigiScore description.",
        "Insekimon\nDigiScore description.",
        "Infermon\nDigiScore description.",
        "Vajramon\nDigiScore description.",
        "Myotismon\nDigiScore description.",
        "Angewomon\nDigiScore description.",
        "Kabukimon\nDigiScore description.",
        "Karatenmon\nDigiScore description.",
        "Chimairamon\nDigiScore description.",
        "Kyukimon\nDigiScore description.",
        "Gigadramon\nDigiScore description.",
        "Crescemon\nDigiScore description.",
        "GrapLeomon\nDigiScore description.",
        "Grademon\nDigiScore description.",
        "Cerberumon\nDigiScore description.",
        "Shakkoumon\nDigiScore description.",
        "Silphymon\nDigiScore description.",
        "Sinduramon\nDigiScore description.",
        "Jyureimon\nDigiScore description.",
        "SkullBaluchimon\nDigiScore description.",
        "Taomon\nDigiScore description.",
        "Kentaurosmon\nDigiScore description.",
        "Dinobeemon\nDigiScore description.",
        "DORUgremon\nDigiScore description.",
        "Bastemon\nDigiScore description.",
        "Paildramon\nDigiScore description.",
        "Pandamon\nDigiScore description.",
        "Phantomon\nDigiScore description.",
        "Flaremon\nDigiScore description.",
        "Butenmon\nDigiScore description.",
        "Blossomon\nDigiScore description.",
        "Whamon\nDigiScore description.",
    ],
}

EXTERNAL_NAME_SOURCES = {
    (34, 48): "https://world.digimoncard.com/cards/?card_no=EX12-011&search=true",
    (34, 49): "https://world.digimoncard.com/cards/?card_no=BT15-023&search=true",
    (35, 9): "https://digimon.net/reference_en/detail.php?directory_name=firamon",
    (35, 14): "https://digimon.net/reference_en/detail.php?directory_name=rukamon",
}

# The game glossary's short-name proposal has one known Japanese-source error:
# シーラモン is Coelamon, not Seadramon (シードラモン).
NAME_OVERRIDES = {"シーラモン": "Coelamon"}


def main() -> None:
    dest = ROOT / "translations/batch73.json"
    if dest.exists():
        raise FileExistsError(dest)
    records = collect_messages(Rom(rom_paths()["blue"]))
    existing = translate_records(records)
    western_names = {}
    for name_key, name_row in records.items():
        if name_row["archive"] == "MSG/MESPAK00.PAK" and name_key in existing:
            western_names.setdefault(name_row["source"], existing[name_key]["english"])
    blocks = []
    for entry, texts in TEXT.items():
        for index, text in enumerate(texts):
            key = f"MSG/MESPAK04.PAK:{entry:03d}:{index:05d}"
            if key not in records or key in existing:
                raise ValueError(f"Missing or already translated: {key}")
            row = records[key]
            if entry == 35 or (entry == 34 and index >= 29):
                jp_name = row["source"].split("<0A>", 1)[0]
                name = NAME_OVERRIDES.get(jp_name, western_names.get(jp_name))
                if not name:
                    raise ValueError(f"No reviewed Western name for DigiScore caption: {jp_name}")
                text = f"{name}\nDigiScore description."
            lines = []
            for source_line in text.splitlines():
                lines.extend(textwrap.wrap(source_line, width=26, break_long_words=False,
                                           break_on_hyphens=False) or [""])
            sources = ["Original Japanese ROM", "Project Digimon-name glossary"]
            if (entry, index) in EXTERNAL_NAME_SOURCES:
                sources.append(EXTERNAL_NAME_SOURCES[(entry, index)])
            blocks.append({
                "archive": row["archive"], "entry": row["entry"],
                "start": row["index"], "category": "Move and item descriptions",
                "english": ["\n".join(lines)],
                "sources": sources,
                "review_note": "DigiFarm rewards and DigiScore captions translated from the source. Canonical Western Digimon spellings are used where established; the original up/down markers are preserved, and generic DigiScore placeholder text is not expanded into invented lore.",
            })
    if len(blocks) != 100:
        raise ValueError(f"Expected 100 descriptions, got {len(blocks)}")
    dest.write_text(json.dumps({
        "description": "Translate remaining DigiFarm reward reports and DigiScore captions in MESPAK04 entries 34 and 35.",
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(dest), "slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
