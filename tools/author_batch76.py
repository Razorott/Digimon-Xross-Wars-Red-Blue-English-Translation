"""Translate item descriptions and unused labels in MESPAK04 entry 39."""
from __future__ import annotations

import json
import textwrap

from build import collect_messages, translate_records
from xros_text import ROOT, Rom, rom_paths


DESCRIPTIONS = {
    0: "Elestou Zone's Code Crown. Proof that you are the owner of a legendary Weapon Digimon.",
    13: "Sunburn lotion from Wendigomon. Even a pale Digimon will get a deep tan.",
    14: "A gift from a devoted TerriLop fan, wrapped in a pretty ribbon.",
    15: "An autograph from TerriLop. Something is written on it very badly.",
    16: "A TerriLop key chain. The two dolls are holding hands.",
    17: "A photo of Numemon with a tiny flower resting on its tongue.",
    18: "A Sukamon postcard. It strikes a pose with its arms crossed.",
    19: "A live portrait of Numemon and Sukamon. A must-have for Numesuka fans.",
    20: "An autograph from Numesuka. It has a truly awful smell.",
    21: "A hair tie from Angewomon with a red strawberry charm.",
    22: "A hair tie from Angewomon with an unassuming marimo charm.",
    23: "Treasure reclaimed from the East Pirate Gang: a rod of pure silver.",
    24: "Treasure reclaimed from the South Pirate Gang: a pearl about as big as Koromon.",
    25: "Treasure reclaimed from the West Pirate Gang: a sapphire shaped like a shining blue heart.",
    26: "Treasure reclaimed from the North Pirate Gang: a large golden crown.",
    27: "A special razor from Zudomon. It gives even the coarsest hair a clean shave.",
    28: "A miracle razor from Drimogemon. It gives even the coarsest hair a clean shave.",
    29: "A thick book from Wisemon, filled with writing no one has ever seen.",
    30: "A large feather from Diatrymon. Handy for dusting.",
    31: "Bits Devimon forced on you. They might not even be real.",
    32: "Bits Evilmon forced on you. They might not even be real.",
    33: "A fist-sized, suspicious-smelling meteorite. It glows an ominous black.",
    34: "A head-sized, dubious meteorite. It glows an ominous black.",
    35: "A bean-sized, fishy meteorite. It glows an ominous black.",
    36: "A bean-sized meteorite with a very nice appraisal from Vademon.",
    37: "A voice recorder for interviews with your favorite Digimon.",
    38: "Dinobeemon voice data. An interview is recorded on it.",
    39: "Paildramon voice data. An interview is recorded on it.",
    40: "A system notebook dropped by LadyDevimon, filled with idol schedules.",
    41: "A signed TerriLop CD. The lettering is a little pretentious.",
    42: "A giant bronze statue, given to thank you for saving TerriLop.",
    43: "An autograph from TerriLop, written in cute, picture-like letters.",
    44: "A crown like a roaring flame. They say it brings good luck.",
    45: "A crown like falling snow. They say it brings good luck.",
    46: "A crown like shining light. They say it brings good luck.",
    47: "A crown like rising darkness. They say it brings good luck.",
    48: "A bone from a bony Digimon, honed to a brilliant, razor-sharp edge.",
    49: "The legendary food everyone loves. Penguinmon's shop doesn't sell it.",
}


def main() -> None:
    dest = ROOT / "translations/batch76.json"
    if dest.exists():
        raise FileExistsError(dest)
    records = collect_messages(Rom(rom_paths()["blue"]))
    translated = translate_records(records)
    blocks = []
    for index in range(50):
        key = f"MSG/MESPAK04.PAK:039:{index:05d}"
        if key not in records or key in translated:
            raise ValueError(f"Missing or already translated source: {key}")
        row = records[key]
        if index in DESCRIPTIONS:
            text = DESCRIPTIONS[index]
        else:
            # Unused data rows are deliberately explicit in the ROM. Keep them
            # identifiable instead of inventing a real item for the slot.
            japanese = row["source"].split("<0A>", 1)[0]
            slot = int(''.join(c for c in japanese if c.isdigit()) or "0")
            text = f"Unused slot {slot:03d}\nDescription text."
        lines = []
        for paragraph in text.splitlines():
            lines.extend(textwrap.wrap(paragraph, width=26, break_long_words=False,
                                       break_on_hyphens=False) or [""])
        blocks.append({
            "archive": row["archive"], "entry": 39, "start": index,
            "category": "Move and item descriptions", "english": ["\n".join(lines)],
            "sources": ["Original Japanese ROM", "Project item glossary"],
            "review_note": "Direct item-description translation. Existing item names and character spellings are kept consistent; explicit unused slots remain labeled as unused.",
        })
    dest.write_text(json.dumps({
        "description": "Translate the Code Crown, quest rewards, gifts, and explicit unused item slots in MESPAK04 entry 39.",
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(dest), "slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
