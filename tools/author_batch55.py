"""Translate the underground chase and Melody capture tutorial."""
from __future__ import annotations

import json
import textwrap

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

TEXTS = {
31: "Meow! Time to skedaddle, meow!",
32: "Well, you're so cute, I'll make a special exception! I'll take you on an underground expedition with my special technique!",
33: "Underground expedition! Here we go!♪",
34: "Whoa, what the heck just happened?!",
35: "That was the Digging skill! To chase them, we need a Digimon with Digging. Use Melody Capture to obtain one, materialize it in the DigiLab, add it to your party, and go together.",
36: "Melody Capture? Materialize it in the DigiLab? I know I've heard that somewhere... What does it mean again?",
37: "If you defeat an uninjured Digimon in one hit, or finish it with a Melody-effect attack, the defeated Digimon becomes a Melody! If you use a move that hits its weakness, it's more likely to become a Melody. If you use an attribute it's strong against, it's less likely. You can turn a Melody you obtain into a Digimon in the DigiLab! Um... what else...? I can't... I'm tired... Ask Guilmon or Veemon at the Sky Fortress for the details...",
38: "Either way, we need more allies. Which Digimon know the Digging skill?",
39: "Guilmon at Knuckle Coast and Dorulumon in the mountains near the Sky Fortress can dig. The Tyrannomon around here should be able to, too.",
40: "Then let's head back for now, Shoutmon.",
41: "All right...",
42: "Oh! There's a Digimon in our party with the Digging skill!",
43: "Great! Let's chase them!",
44: "We finally escaped Ring Wandering by digging... Why is there still nothing but darkness ahead?!",
45: "Aaah... so dark... I'm dizzy from all this darkness...",
46: "M-my gosh! It appeared! A ghost?! A spirit?! A monster?!",
47: "D-Digimon... meow?!",
48: "Yeah! It's a terrifying monster that will capture and restrain us! The only thing to do is escape! You understand?",
49: "Meow! Yes, meow?!",
50: "All right! Let's run!",
51: "Darn it! We were so close to catching it!",
52: "Aah! I hate this dark place! Taiki, Shoutmon... hurry up and chase them so we can get out!",
53: "What a coward, Spadamon! Anyway, let's chase them!",
54: "Even past the darkness, there's more darkness... It's just like my life! Yee-haw!♪",
55: "What's wrong? You're trembling. Are you scared of the dark?",
56: "N-no... I'm n-not scared!",
57: "A-a-aah...",
58: "Hey! Team Cute's rule is: when you're in trouble, laugh! Even when things get tough or you're in a pinch, laugh it off! You understand?",
59: "...... I... Meow! I'll laugh, meow!",
60: "Ah... You're so very cute!",
61: "Team Cute, full speed ahead! Let's charge!♪",
62: "Meow! Charge forward, meow!",
63: "Ugh... We were so close to catching it...",
64: "Hee-hee! Good for you, squishy! You're alive in a beautiful flower garden!",
65: "Hey, Chibickmon! Are you okay?!",
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
                       "review_note": "Mission dialogue and the Melody capture tutorial translated directly from Japanese. Character, feature, and skill terms follow the project style."})
        review.append({"id": key, "japanese": row["source"], "english": english})
    path = ROOT / "translations/batch55.json"
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps({"description": "Translate the underground chase and Melody capture tutorial.", "blocks": blocks}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "translations/review_batch55.json").write_text(json.dumps({"batch": 55, "translated_slots": len(blocks), "groups": review}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Batch 55 review", "", "This batch covers the underground chase, Team Cute dialogue, and the game's Melody capture/materialization tutorial. Japanese text is the primary source; mechanics terms should be reviewed in play after the build.", "", "| ID | Japanese | English |", "|---|---|---|"]
    for row in review:
        jp = row["japanese"].replace("<0A>", "<br>").replace("|", "\\|")
        en = row["english"].replace("\n", "<br>").replace("|", "\\|")
        lines.append(f"| `{row['id']}` | {jp} | {en} |")
    (ROOT / "translations/review_batch55.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"batch": 55, "translated_slots": len(blocks)}, ensure_ascii=False))

if __name__ == "__main__":
    main()
