"""Translate the Dorulumon standoff and Minervamon's defense of Pukumon."""
from __future__ import annotations

import json
import textwrap

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

TEXTS = {
136: "Heh-heh! That's up to the doggy! Stop fooling around and hurry up and catch Spadamon!",
137: "D-Dorulumon...!",
138: "Don't struggle! Be a good kitty!",
139: "Don't whine! Do what I say, meow!",
140: "...Tch! Remember this, Minervamon! I won't let this end here!",
141: "Keep your mouth shut, doggy. Your breath stinks!♪",
142: "Hey, wait, Dorulumon! This has to be a joke...!",
143: "I never thought we'd have to fight you like this... But I can't abandon Cutemon!",
144: "Heh-heh... Great, just great! If this keeps up, ROG will find the Legendary Ancient Weapons and take over the world! Yee-haw!♪",
145: "Honestly, this doggy is completely useless! How will I face Lord ZD Millenniummon?",
146: "You guys aren't needed here anymore. Just leave them and go home!",
147: "Meow! We'll leave them behind, meow!",
148: "Meow! We're going home, meow!",
149: "Dorulumon!",
150: "...Cutemon!",
151: "Using your friends as hostages to make them fight... What a dirty trick!",
152: "So that's why you took Chibickmon, too! You planned to use it for something!",
153: "...Ha ha! That's a pretty nasty accusation, kid. Capturing Spadamon is my lousy job; playing with that one was the best fun! Why would I use such a cute thing for anything?",
154: "Then why did you take it away? What were you trying to do?",
155: "I was just playing with Pukumon! Kidnap, take away, use, some kind of plan... What are you even talking about?",
156: "No... Don't lie. Were you trying to steal something...? But Chibickmon doesn't have anything important... So... what else could be valuable...?",
157: "Don't insult Pukumon any further! If you look ugly, your thoughts must be ugly, too! Nothing is more precious than that little one's cuteness! But no one can ever take that away! You're filthy and unpleasant, the worst of the worst! I can't stand sharing the same air with you!",
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
                       "review_note": "Mission dialogue translated directly from Japanese. Pukumon and the other Digimon use established Western spellings."})
        review.append({"id": key, "japanese": row["source"], "english": english})
    path = ROOT / "translations/batch58.json"
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps({"description": "Translate the Dorulumon standoff and the Chibickmon misunderstanding.", "blocks": blocks}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "translations/review_batch58.json").write_text(json.dumps({"batch": 58, "translated_slots": len(blocks), "groups": review}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Batch 58 review", "", "This batch covers the Dorulumon standoff, ROG's plan, and Minervamon's defense of Pukumon. Japanese dialogue is the primary source; Digimon names use established Western spellings.", "", "| ID | Japanese | English |", "|---|---|---|"]
    for row in review:
        jp = row["japanese"].replace("<0A>", "<br>").replace("|", "\\|")
        en = row["english"].replace("\n", "<br>").replace("|", "\\|")
        lines.append(f"| `{row['id']}` | {jp} | {en} |")
    (ROOT / "translations/review_batch58.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"batch": 58, "translated_slots": len(blocks)}, ensure_ascii=False))

if __name__ == "__main__":
    main()
