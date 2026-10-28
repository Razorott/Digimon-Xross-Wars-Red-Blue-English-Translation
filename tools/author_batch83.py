"""Translate Dynasmon's memory reveal and farewell in MESPAK02 entry 10."""
from __future__ import annotations

import json

from build import collect_messages, translate_records
from translation_queue import category
from xros_text import ROOT, Rom, rom_paths


DIALOGUE = {
    0: "Spadamon, let me give you your final memory... The one I kept safe for you.",
    1: "Wait, Spadamon! Can we really trust him...?",
    2: "Spadamon's full power has been restored!",
    3: "Spadamon, are you all right?",
    4: "Dynasmon...! I finally remember!",
    5: "It's been a long time, Spadamon. Now show me the strength of the friends you chose.",
    6: "Y-yes! With Xros Heart, I'm sure we can protect Elestou Zone!",
    7: "Hey! Spadamon, what's going on?!",
    8: "The final test... I'll do my best!",
    9: "A test? What kind of test is that?!",
    10: "Team Xros Heart! I won't go easy on you... Give it everything you've got!",
    11: "Damn! I don't know what's going on, but we'll give this everything we've got!",
    12: "Spadamon, you passed. You've grown so strong... Truly strong.",
    13: "What was that for?!",
    14: "Explain yourself! What did we pass?!",
    15: "...How much do you know about the Weapon Digimon?",
    16: "They have enough power to destroy the world, and they're sealed in Lost Space for some reason... Barbamon called one Armamon. That's all we know.",
    17: "You're not wrong, but there's a misunderstanding. Armamon isn't the only Weapon Digimon in this Zone. Spadamon is one of the few who survived.",
    18: "Spadamon is a Weapon Digimon?!",
    19: "Long ago, many Weapon Digimon lived in this Zone. They chose warriors they trusted as partners and fought alongside them to protect the Zone. Spadamon was the youngest among them, so I sealed his memories to protect him from the invaders.",
    20: "I see... So that's why Spadamon could activate the towers...",
    21: "Maybe Dynasmon...",
    22: "No, I doubt it. Only the administrator could open the towers, right? Maybe Dynasmon locked them so only Spadamon could open the doors...",
    23: "As expected of the boy Spadamon chose. The only way to protect young Spadamon from the invaders was to make him stronger. I set the doors to open as he grew... Everything was meant to train him.",
    24: "Hey, Dynasmon! Weren't you the warrior who was supposed to protect this Zone? Didn't you have an incredibly powerful Weapon Digimon partner?! Why didn't you fight?!",
    25: "Calm down, Shoutmon! There must be a reason.",
    26: "Right, Dynasmon? I sensed the warmth in your heart, how you wanted to protect Spadamon. There's no way someone like you would hide here alone without a reason!",
    27: "Th-that's right, Taiki... Dynasmon...",
    28: "...During the long war to protect this Zone, I once had the strongest Weapon Digimon as my partner. But it became consumed by its own power and forgot its mission to protect the Zone... That Digimon was Armamon.",
    29: "I sealed the rampaging Armamon, but my Digicore was badly damaged. Now I can only keep my data intact by using energy from the Capacitor System... If I leave here, my data will disappear...",
    30: "I see... I'm sorry, Dynasmon.",
    31: "It's all right, Shoutmon. Because you trained Spadamon, hope has returned to Elestou Zone. Please stop Barbamon before he revives Armamon... I beg you.",
    32: "I want to ask you again, too... I want to save this Zone and everyone in it! Please, fight alongside me!",
    33: "Of course! You didn't even have to ask, Spadamon!",
    34: "What are you talking about, Spadamon?! You've been our friend for ages!",
    35: "Th-thank you... Both of you!",
    36: "I can't just leave Elestou Zone in danger! I'll stop Barbamon, no matter what!",
    37: "Leave it to us! We'll bring peace back to this Zone!",
    38: "Thank you, everyone. I truly appreciate it... Spadamon, restore this Capacitor System so we can deactivate Sky Fort's protective field.",
    39: "...Yes.",
    40: "The protective field has been deactivated!",
    41: "Now we can go help everyone in Sky Fort!",
    42: "You did it, Taiki! Let's head back right away!",
    43: "Also, a Digimon was looking for you, so I called them here to Elestou Zone.",
    44: "Could it be...?",
    45: "...Beelzemon!",
    46: "Taiki! Shoutmon! You're safe!",
    47: "...Who is that? A friend of yours, Taiki?",
    48: "This Digimon is your friend, isn't he? I found him searching for you in another Zone, so I pulled him here.",
    49: "...Hey, Taiki? I just realized... Maybe we were brought here, too...",
    50: "Yeah, probably. Dynasmon brought us here to help Spadamon... Well, that's all right, I guess.",
    51: "R-right! And we got to meet Spadamon because of it!",
    52: "Beelzemon! We're fighting some bad guys in this Zone. Help us protect its Digimon!",
    53: "Heh. Still helping people, as always. If you're asking, I'll gladly lend a hand.",
    54: "Thanks, Beelzemon!",
    55: "Thank you, Dynasmon... And thank you, Taiki and Shoutmon...",
    56: "It's all right, Dynasmon. I just couldn't leave you in trouble.",
    57: "That's our Taiki! The best General!",
    58: "Until ROG is defeated and this Zone is reclaimed, no one can travel to another Zone. That means you can't go home, either.",
    59: "What?! You dragged me here without asking, and now you say I can't leave? What am I supposed to do here?!",
    60: "Beelzemon, wait for us at Earth Fort, east of Crystal Volcano. We'll be there soon.",
    61: "...Understood. I'll wait there.",
    62: "Beelzemon, if you can... Would you fight alongside us?",
    63: "I don't have anything else to do, so I can help. Call if you need me... See you.",
    64: "We don't have much time... If you need other allies, I can bring them here, too.",
    65: "You make it sound like a mail-order service...",
    66: "What about Nene? Can you find her? Barbamon sent her somewhere...",
    67: "...I see. Wait a moment while I check.",
    68: "It seems she's outside the range of my power.",
    69: "What does that mean?! Is she just missing, or could she already be...?",
    70: "I checked the data from when she was sent away... There was no corruption, loss, or damage. She is probably safe. But I'll have to investigate to learn where she went...",
    71: "That's all right, Dynasmon. Thank you. Knowing she's safe is enough for now.",
    72: "...I see.",
    73: "Dynasmon?!",
    74: "Wh-what's wrong?!",
    75: "...At last... It seems... the time... has come... for me... to go...",
    76: "Go...? What do you mean?",
    77: "D-Dynasmon! Your data...!",
    78: "When you say 'go'... Do you mean you're disappearing?!",
    79: "Why are you disappearing now?! We still need you!",
    80: "...Dynasmon was keeping his data alive with this system's energy. Now that the system is running again, he'll disappear...!",
    81: "You... You knew that, and still...",
    82: "Spada...mon... Xros...Heart... I... entrust... them... to you...",
    83: "Thank you, Dynasmon...",
    84: "...Taiki, let's return to Earth Fort. Things have probably changed by now.",
    85: "Yeah...",
}


def main() -> None:
    destination = ROOT / "translations/batch83.json"
    if destination.exists():
        raise FileExistsError(destination)
    records = collect_messages(Rom(rom_paths()["blue"]))
    existing = translate_records(records)
    blocks = []
    for index, english in DIALOGUE.items():
        key = f"MSG/MESPAK02.PAK:010:{index:05d}"
        if key not in records or key in existing:
            raise ValueError(f"Missing or already translated source: {key}")
        row = records[key]
        if category(row) != "Story and dialogue":
            raise ValueError(f"Unexpected translation category for {key}")
        blocks.append({
            "archive": row["archive"], "entry": row["entry"],
            "start": row["index"], "category": "Story and dialogue",
            "english": [english], "sources": ["Original Japanese ROM"],
            "review_note": "Continuous Dynasmon memory-reveal scene. The Weapon Digimon origin, Spadamon's sealed memory, tower access, Beelzemon's arrival, and Dynasmon's data dependence are kept consistent with the preceding scene.",
        })
    if len(blocks) != 86:
        raise ValueError(f"Expected 86 dialogue strings, got {len(blocks)}")
    destination.write_text(json.dumps({
        "description": "Translate Dynasmon's restoration of Spadamon's memories, the Armamon reveal, and Dynasmon's farewell in MESPAK02 entry 10.",
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(destination), "slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
