"""Translate the next 30 Sky Fortress story messages."""
from __future__ import annotations

import json
import textwrap

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

TEXTS = {
33: "Taiki, Ballistamon!",
34: "He’s okay! He’s only unconscious. We made it in time!",
35: "Hey, Ballistamon! Hang in there!",
36: "How dare you do whatever you want with us! I’ll pay you back a million times over!",
37: "Wake up, Ballistamon! We came to save you!",
38: "Ballistamon!!",
39: "...Taiki. I knew you’d come.",
40: "Of course I came! There’s no way I’d leave you behind!",
41: "...Yeah, you’re right. Thanks. You saved me.",
42: "Oh, thank goodness! Is everyone all right?",
43: "Yeah, we managed. But unless we defeat their boss, ROG will occupy this place again in no time.",
44: "Ballistamon, where’s their boss?",
45: "In the room ahead.",
46: "Everyone, be careful! Their boss, Minotaurmon... is on a whole different level from anyone we’ve fought so far!",
47: "No matter what kind of enemy they are, we won’t lose!",
48: "Hmm... If only the DigiLab and DigiFarm were working, they could help us. They’re completely shut down, so I can’t get them running right away. But that’s also why your friends stayed safe.",
49: "What are the DigiLab and DigiFarm?",
50: "The DigiLab is where you gather and raise your allies.",
51: "The DigiFarm is where Digimon train to get stronger.",
52: "If you use these two systems well, Digimon can greatly increase their strength. While you all go defeat the Digimon in the Commander Room, I’ll check the systems here.",
53: "...I still don’t really get it, but right now we have to protect this Sky Fortress from the enemy! Come on, everyone!",
54: "Ballistamon joined the team!",
55: "Hey, you there! Are you the ROG boss?",
56: "...Hmm? Who are you? I won’t forgive anyone who barges into my Sky Fortress!",
57: "You’re the ones who barged in here!",
58: "You kicked out the Digimon who live here by force! That’s awful! I’m Zenjiro, Koto Ward’s strongest swordsman, and these are my friends!",
59: "You don’t get it... I’m Minotaurmon, ROG’s powerful leader, Lord Minotaurmon the Quake! Get lost before I crush you!",
60: "Y-you’re the ones who are leaving! Give our Sky Fortress back!",
61: "Y-you... Spadamon! I heard you got away... Hahaha! You came right to me! If I capture you, Lord ZD Millenniummon’s ambition will be fulfilled: conquering the world with the Legendary Ancient Weapons!",
62: "ROG’s biggest boss... ZD Millenniummon?",
}

def fit(s: str) -> str:
    return "\n".join("\n".join(textwrap.wrap(line, width=15, break_long_words=True, break_on_hyphens=False)) if line else "" for line in s.split("\n"))

def main() -> None:
    records = collect_messages(Rom(rom_paths()["blue"]))
    done = translate_records(records)
    blocks, review = [], []
    for index, raw in TEXTS.items():
        key = f"MSG/MESPAK02.PAK:003:{index:05d}"
        if key in done:
            raise ValueError(f"Already translated: {key}")
        row = records.get(key)
        if not row or not row["source"].strip():
            raise ValueError(f"Missing story source: {key}")
        english = fit(raw)
        blocks.append({"archive": row["archive"], "entry": 3, "start": index,
                       "category": "Story and dialogue", "english": [english],
                       "sources": ["Original Japanese ROM (local primary source)"],
                       "review_note": "Story dialogue translated from the Japanese scene. DigiLab, DigiFarm, and DigiXross use the established project terminology."})
        review.append({"id": key, "japanese": row["source"], "english": english})
    path = ROOT / "translations/batch48.json"
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps({"description": "Translate the Sky Fortress rescue and ROG confrontation scene.", "blocks": blocks}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "translations/review_batch48.json").write_text(json.dumps({"batch": 48, "translated_slots": len(blocks), "groups": review}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Batch 48 review", "", "This batch continues the Sky Fortress rescue and introduces ROG leader Minotaurmon. Japanese dialogue is the primary source; names and feature terms follow the project glossary.", "", "| ID | Japanese | English |", "|---|---|---|"]
    for row in review:
        jp = row["japanese"].replace("<0A>", "<br>").replace("|", "\\|")
        en = row["english"].replace("\n", "<br>").replace("|", "\\|")
        lines.append(f"| `{row['id']}` | {jp} | {en} |")
    (ROOT / "translations/review_batch48.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"batch": 48, "translated_slots": len(blocks)}, ensure_ascii=False))

if __name__ == "__main__":
    main()
