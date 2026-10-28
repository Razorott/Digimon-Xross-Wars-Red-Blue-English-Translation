"""Translate the Sky Fortress systems briefing and first tower lead."""
from __future__ import annotations

import json
import textwrap

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

TEXTS = {
123: "Hey, Taiki... If your Digimon are low on HP or MP, use a Tent or the healing bed on the Sky Fortress. A nap there will get everyone back on their feet!",
124: "There should be a request to find the Digimon Flight Team. First, accept it from the Quest Monitor.",
125: "The Quest Monitor...?",
126: "It's the big digital screen in the Commander Room. Ask Palmon beside it how to use it.",
127: "Taiki can do anything perfectly! And that thing you called it? Leave it to me, too!",
128: "Woo! Brother! So cool!",
129: "I-I want to come, too! When I'm with you, Taiki... I feel like I might get back the memories I lost...",
130: "...Taiki, I know this is a lot, but please look after Spadamon! I'll keep repairing the system and gathering data. If you need anything, I'll be right here.",
131: "All right, let's go!",
132: "Mmm...",
133: "Mmmph!",
134: "Grrrr...",
135: "Why is everyone standing here grunting?",
136: "Oh, Taiki! You came at the perfect time!",
137: "We've been waiting for you, Taiki Kudo!",
138: "Oh? What's wrong? Is there trouble, Akari? I can lend a hand, my head, or my strength! Whatever you need, I'll do it right now!",
139: "What's going on, Zenjiro? Patamon, what happened?",
140: "...Starmon, Shoutmon. Calm down.",
141: "What's wrong, Patamon?",
142: "I was checking the Sky Fortress systems... but there's not enough energy. The DigiLab and DigiFarm can't run any of their important functions. Worse, unless we get the Capacitor Towers working soon, we'll run out of energy and the systems will shut down.",
143: "The Capacitor Towers?",
144: "They generate this Zone's energy. There are six towers, but it looks like all of them have stopped. They were working fine before ROG took the Sky Fortress... Did Minotaurmon mess with something?",
145: "They cut the Sky Fortress's power so they could steal it! This must be part of ROG's plan! What a dirty trick!",
146: "But each Capacitor Tower has a huge door, with the Capacitor System behind it. Only the tower's administrator should be able to start it. That's why ROG has the area around every tower locked down.",
147: "Who is the administrator of the Capacitor Towers?",
148: "I don't know... The towers have been locked for ages. Patamon and I once tried to sneak in, but the door wouldn't budge. We had to go back in tears... I mean, that was a long time ago! I wouldn't cry now! Really!",
149: "But the system behind those doors shut down, so the energy stopped flowing and the towers stopped working, right? We have to investigate the Capacitor Towers...",
150: "Yeah, something may have happened there. Let's investigate. Where are the Capacitor Towers?",
151: "The closest one is... let's see... on the edge of the Energy Continent, at Knuckle Coast.",
152: "Ooh! That sounds like a tough place! I can't wait to get going!",
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
                       "review_note": "Story, request, and system dialogue translated directly from Japanese; named features follow the project glossary."})
        review.append({"id": key, "japanese": row["source"], "english": english})
    path = ROOT / "translations/batch51.json"
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps({"description": "Translate the Sky Fortress energy crisis and Knuckle Coast lead-in.", "blocks": blocks}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "translations/review_batch51.json").write_text(json.dumps({"batch": 51, "translated_slots": len(blocks), "groups": review}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Batch 51 review", "", "This batch explains the Sky Fortress's power crisis, the Capacitor Towers, and the lead to Knuckle Coast. Japanese text is the primary source; system names follow the project glossary.", "", "| ID | Japanese | English |", "|---|---|---|"]
    for row in review:
        jp = row["japanese"].replace("<0A>", "<br>").replace("|", "\\|")
        en = row["english"].replace("\n", "<br>").replace("|", "\\|")
        lines.append(f"| `{row['id']}` | {jp} | {en} |")
    (ROOT / "translations/review_batch51.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"batch": 51, "translated_slots": len(blocks)}, ensure_ascii=False))

if __name__ == "__main__":
    main()
