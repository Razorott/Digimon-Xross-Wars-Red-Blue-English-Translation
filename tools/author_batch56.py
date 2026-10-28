"""Translate Minervamon's playful misunderstanding and the rock-monster encounter."""
from __future__ import annotations

import json
import textwrap

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

TEXTS = {
66: "Yay, Shoutmon! Pukumon's okay!♪",
67: "After all the trouble we went through, and now this...",
68: "You won't get away this time! Give up already!",
69: "...Grr! You're so persistent! Then I'll make a quick escape!",
70: "This rock is in my way! I'll split it wide open with the Rock Break skill!",
71: "If only I had the Rock Break skill... I can't smash it with spirit alone! My knuckle's what hurts! Oww, oww... Go away, pain!",
72: "...What a weird one. Is this one with ROG, too?",
73: "Who knows...? It doesn't look that bad, though.",
74: "Hey, Taiki, Shoutmon... That rock it was trying to break... Isn't it moving?!",
75: "Grrrr...",
76: "...Meow!!",
77: "What is that thing?! We're surrounded! We can't move forward or back... This might be a serious pinch!",
78: "With one interruption after another, I have no choice... This is goodbye, squishy you.",
79: "Hey! Who are you?! Why did you kidnap Chibickmon?",
80: "You call me 'someone' and ask who I am? Who are you? And what do you mean, kidnapped?",
81: "We were just playing! Big sis, this is fun!",
82: "Did this Digimon do anything mean to you, Chibickmon?",
83: "Nothing mean, Pukumon! I like big sis!♪",
84: "Minerva-me had lots of fun, too! But playtime is almost over. You should go home now!",
85: "I not go home! I wanna play more!",
86: "You've been such a good kid this whole time, right? So don't be so selfish at the very end.",
87: "Big sis... We'll play again...",
88: "If fate brings us together, we'll meet again. Then we'll play some more. You understand?",
89: "Y-yes... meow!",
90: "I knew it... You're so, so cute!",
91: "Being cute is nice, but... what are we going to do about that thing?",
92: "Grrrr!",
93: "Oof?!",
94: "N-no! It's so fluffy! I wanna go home!",
95: "You didn't notice until now...?",
96: "Maybe if we explain, it'll understand... No, probably not...",
98: "Doesn't look like it... We'll have to fight!",
100: "Grr... Grrrr... Grr...",
}

def fit(s: str) -> str:
    return "\n".join("\n".join(textwrap.wrap(line, width=15, break_long_words=True, break_on_hyphens=False)) if line else "" for line in s.split("\n"))

def main() -> None:
    records = collect_messages(Rom(rom_paths()["blue"]))
    done = translate_records(records)
    blocks, review = [], []
    for index, raw in TEXTS.items():
        key = f"MSG/MESPAK02.PAK:004:{index:05d}"
        if key in done:
            raise ValueError(f"Already translated: {key}")
        row = records.get(key)
        if not row or not row["source"].strip():
            raise ValueError(f"Missing story source: {key}")
        english = fit(raw)
        blocks.append({"archive": row["archive"], "entry": 4, "start": index,
                       "category": "Story and dialogue", "english": [english],
                       "sources": ["Original Japanese ROM (local primary source)"],
                       "review_note": "Mission dialogue translated directly from Japanese. Minervamon and other character names follow the project naming style."})
        review.append({"id": key, "japanese": row["source"], "english": english})
    path = ROOT / "translations/batch56.json"
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps({"description": "Translate the Minervamon and Chibickmon misunderstanding and the rock-monster encounter.", "blocks": blocks}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "translations/review_batch56.json").write_text(json.dumps({"batch": 56, "translated_slots": len(blocks), "groups": review}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Batch 56 review", "", "This batch covers Minervamon's game with Chibickmon and the sudden rock-monster encounter. Japanese dialogue is the primary source; character names follow the project naming style.", "", "| ID | Japanese | English |", "|---|---|---|"]
    for row in review:
        jp = row["japanese"].replace("<0A>", "<br>").replace("|", "\\|")
        en = row["english"].replace("\n", "<br>").replace("|", "\\|")
        lines.append(f"| `{row['id']}` | {jp} | {en} |")
    (ROOT / "translations/review_batch56.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"batch": 56, "translated_slots": len(blocks)}, ensure_ascii=False))

if __name__ == "__main__":
    main()
