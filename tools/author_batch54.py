"""Translate the opening Team Cute scene of the Chibickmon mission."""
from __future__ import annotations

import json
import textwrap

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

TEXTS = {
0: "Big sis? Do you mean Akari?",
1: "No, I don't think I've ever called Akari that. Besides, she's in the Commander Room right now. It must be someone they met in this Zone.",
2: "We asked around to see if anyone had spotted Chibickmon. Someone said they saw it near East Knuckle City, but it disappeared soon after, so we don't know where it went.",
3: "East Knuckle City...? You mean near East Knuckle Coast? That's close to where we fought Pukumon.",
4: "All right, brother! Let's go find Chibickmon!",
5: "You left it to me?!",
6: "L-left it to... me?! Huh?! Hey, wasn't I supposed to go first?!",
7: "Without that little one, the Pickmons are a mess... Leave it to us! We'll find it right away!",
8: "Come on, Taiki! We have to save Chibickmon!",
9: "Wait a minute, Taiki! If you're going to East Knuckle Coast, take this!",
10: "What... What kind of key is this?",
11: "It's the key to the gate near East Knuckle City. Past that gate is Twisting Amazon. If you can't find Chibickmon at East Knuckle Coast, will you search the neighboring Twisting Amazon, too?",
12: "Twisting Amazon, huh? Got it. We'll look there, too.",
13: "What the heck?! We just came through here! We're going round and round in the same place!",
14: "Big sis, round and round!♪",
15: "That's why you should call me Lady Minervamon! And since you've joined Team Cute, you have to... add 'meow' before and after you speak! You understand?",
16: "Meow! Yes, meow!",
17: "Aaaah! There they are! Chibickmon... and who are those guys? What are they doing?",
18: "Um... don't ask me... But they look like they're having fun. Maybe they're not bad Digimon?",
19: "Hey, you! Dangerous bad boys are coming! Hurry up and run!",
20: "D-danger... meow? Bad boy...?",
21: "Shut up! Stand up! And hurry up!!",
22: "M-meow! Yes, meow!",
23: "Ah! They got away...",
24: "Let's chase them, Taiki! We'll catch up in no time!",
26: "The whirlpools here are one-way. Once you enter one, you can't return through the whirlpool you came from. Be careful!",
27: "We can hide here for a little while...",
28: "...We can hide here!",
29: "Round and round... round and round... meow?",
30: "If there's a hole, I have to hop in! Let's skedaddle, meow! You understand?",
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
                       "review_note": "Mission dialogue translated directly from Japanese. Character names, zone names, and Team Cute follow the project style."})
        review.append({"id": key, "japanese": row["source"], "english": english})
    path = ROOT / "translations/batch54.json"
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps({"description": "Translate the opening Team Cute scene and directions for the Chibickmon search.", "blocks": blocks}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "translations/review_batch54.json").write_text(json.dumps({"batch": 54, "translated_slots": len(blocks), "groups": review}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Batch 54 review", "", "This batch introduces the Chibickmon search request, East Knuckle Coast, Twisting Amazon, and Minervamon's Team Cute gag. Japanese dialogue is the primary source; proper nouns follow the project glossary where established.", "", "| ID | Japanese | English |", "|---|---|---|"]
    for row in review:
        jp = row["japanese"].replace("<0A>", "<br>").replace("|", "\\|")
        en = row["english"].replace("\n", "<br>").replace("|", "\\|")
        lines.append(f"| `{row['id']}` | {jp} | {en} |")
    (ROOT / "translations/review_batch54.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"batch": 54, "translated_slots": len(blocks)}, ensure_ascii=False))

if __name__ == "__main__":
    main()
