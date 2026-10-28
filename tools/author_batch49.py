"""Translate the next 27 Elestou Zone story messages."""
from __future__ import annotations

import json
import textwrap

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

TEXTS = {
63: "The Legendary Ancient Weapons...?",
64: "That's enough talk! Spadamon, prepare yourself!",
65: "Hah! You're on! Leave him to me, Taiki!",
66: "Now do you understand the power of Xros Heart?",
67: "Guh... I didn't expect Spadamon to have allies like this... But before Lord ZD Millenniummon, you're just kids! Enjoy your friendship with that weakling Spadamon while you can...!",
70: "What a pain... He lost to that 'weakling Spadamon'?",
71: "Huh? Spadamon, what's wrong?",
73: "W-what happened? What was that just now?",
74: "Are you okay, Spadamon?",
75: "I remember! The Legendary Ancient Weapons... That's the secret sealed in the Elestou Zone! I must never tell anyone... I think someone told me that... Who was it...?",
76: "...Hm? What's wrong?",
77: "I can't remember what came after that. But it's a huge secret! The Legendary Ancient Weapons are hidden in this Zone. It has to stay a secret! ...Oh no! I just told everyone! W-what do I do?!",
78: "It's okay, Spadamon. We're all your friends. Still, what a strange guy. We were fighting him just a moment ago... Wait! Maybe Spadamon's memory came back because he fought... because he got stronger!",
79: "...I got stronger?",
80: "Wow! You really beat him! He looked so scary. It must have been hard to take him down!",
81: "Heh... It wasn't that hard.",
82: "Zenjiro didn't do anything, though.",
83: "We got this room back. Who used it before?",
84: "This is the Commander Room, where the commander works. Taiki, you can use it if you'd like. You're the commander of the Elestou Zone now, after all!",
85: "You can also accept requests from the monitor over there.",
86: "If you use the healing bed at the back of the room, you can restore your allies' HP and MP.",
87: "Huh? Taiki seems more tired than the Digimon. I can explain everything later... Why don't you rest in the healing bed for a while?",
88: "That's right! Taiki always pushes himself too hard. Go rest in bed first! We can talk after.",
89: "I guess... Come to think of it, all of a sudden... I feel sleepy...",
90: "Good morning, Taiki.",
91: "Huh? What's with that puzzled look?",
92: "...Hmm? Hey, Akari... I feel kind of dizzy. Did I sleep too long?",
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
                       "review_note": "Story dialogue translated from the Japanese scene. Elestou Zone and other proper nouns follow the project glossary."})
        review.append({"id": key, "japanese": row["source"], "english": english})
    path = ROOT / "translations/batch49.json"
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps({"description": "Translate the end of the Elestou Zone and Commander Room story scene.", "blocks": blocks}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "translations/review_batch49.json").write_text(json.dumps({"batch": 49, "translated_slots": len(blocks), "groups": review}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Batch 49 review", "", "This batch completes the 27 remaining messages in the Elestou Zone boss scene and the Commander Room introduction. Japanese dialogue is the primary source; zone naming follows the project glossary.", "", "| ID | Japanese | English |", "|---|---|---|"]
    for row in review:
        jp = row["japanese"].replace("<0A>", "<br>").replace("|", "\\|")
        en = row["english"].replace("\n", "<br>").replace("|", "\\|")
        lines.append(f"| `{row['id']}` | {jp} | {en} |")
    (ROOT / "translations/review_batch49.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"batch": 49, "translated_slots": len(blocks)}, ensure_ascii=False))

if __name__ == "__main__":
    main()
