"""Translate the next 30 Sky Fortress and travel story messages."""
from __future__ import annotations

import json
import textwrap

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

TEXTS = {
93: "It's okay. The shaking is real. The Sky Fortress is flying toward a place called the Energy Continent.",
94: "Huh? This island moves? That scared me... So, what's the Energy Continent like?",
95: "It's the largest landmass, right in the middle of this Zone. Digimon from other Zones seem to think the Energy Continent is the Elestou Zone. Most of ROG's main forces have gone there, too. There should be lots of our allies there, but we don't know if they're safe or where they are now.",
96: "I see... So there are allies there. We should find them soon. How long until we reach the Energy Continent?",
97: "Well...",
98: "Patamon will explain in the Central Room next door. He's been waiting for you to wake up.",
99: "Ha ha... Sorry. Looks like I did it again.",
100: "It's fine, Taiki. I need you to stay healthy. And it seems there's not much to do while the island is flying, so I wanted to make sure you were in top shape first. That's all... I'm counting on you, you know!",
101: "Yeah, leave it to me! Thanks as always, Akari!",
102: "Hmm... Taiki and Akari, huh...? ...Never mind. I'll go tell Patamon. Come on, everyone!",
103: "All right, let's get going!",
104: "Wait, Taiki! What are you doing? The ROG boss isn't this way! Ballistamon said he's in the back of the room we were just in. Let's hurry in there and beat him!",
105: "Good morning, Taiki. Sorry to ask so soon, but there's something I really need you all to do.",
106: "Yeah, I heard. Leave it to us! We'll land on the Energy Continent and find our allies. If most of ROG is there, too, we can't just leave them alone. We'll head out right away!",
107: "Don't get so worked up that you collapse again. You always say you can't leave people in trouble, but you're the one I worry about most!",
108: "I'll be careful. Thanks, Akari.",
109: "So... how do we get to the Energy Continent?",
110: "We're heading there now, right? Can't we just land when we get there?",
111: "The Sky Fortress can fly close to the continent, but it can't land directly on the ground. We've never tried, but we'd probably crash and break it.",
112: "Then how have you been getting there until now?",
113: "I've got it, brother! We fly way up high, then jump down from there...",
114: "...Only Starmon and Pickmon can do that.",
115: "Darn it! If Sparrowmon were here, we could fly with DigiXross! Where did it go?!",
116: "Um, in our Elestou Zone, we travel to other islands by having a flying Digimon Flight Team carry us!",
117: "But they hid somewhere when ROG attacked. Can you find out where they are?",
118: "Got it, Patamon. So... do you have any clues?",
119: "All I know is they're somewhere on the Sky Fortress. For now, I'll give you a detailed map of it. You can view it by opening Map on your Cross Loader.",
120: "Key item obtained!\nMap 01",
121: "Key item obtained!\nMap 02",
122: "We should stay here on the Sky Fortress and help Patamon and the others. If it's machine repairs, leave it to the swordsman Zenjiro!",
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
                       "review_note": "Story dialogue and key-item notifications translated directly from Japanese; zone and feature names follow the project glossary."})
        review.append({"id": key, "japanese": row["source"], "english": english})
    path = ROOT / "translations/batch50.json"
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps({"description": "Translate the Sky Fortress briefing and search for the Digimon Flight Team.", "blocks": blocks}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "translations/review_batch50.json").write_text(json.dumps({"batch": 50, "translated_slots": len(blocks), "groups": review}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Batch 50 review", "", "This batch covers the Energy Continent briefing, the Sky Fortress travel plan, and two key-item notices. Japanese dialogue is the primary source; Elestou Zone follows the project's glossary.", "", "| ID | Japanese | English |", "|---|---|---|"]
    for row in review:
        jp = row["japanese"].replace("<0A>", "<br>").replace("|", "\\|")
        en = row["english"].replace("\n", "<br>").replace("|", "\\|")
        lines.append(f"| `{row['id']}` | {jp} | {en} |")
    (ROOT / "translations/review_batch50.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"batch": 50, "translated_slots": len(blocks)}, ensure_ascii=False))

if __name__ == "__main__":
    main()
