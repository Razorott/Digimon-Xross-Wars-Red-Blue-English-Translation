"""Translate the Megidramon, TigerVespamon, and MarineDevimon tower scenes."""
from __future__ import annotations

import json

from build import collect_messages, translate_records
from translation_queue import category
from xros_text import ROOT, Rom, rom_paths


DIALOGUE = {
    0: "W-wait! Where are you going to disappear to?",
    1: "Where else? I'm going to be absorbed by Lord Barbamon♪ The more Shadow Guard you defeat, the stronger he gets! Isn't that wonderful?♪",
    2: "Bye-bye~♪",
    3: "What's with that casual 'bye-bye'?! Everyone keeps vanishing so easily...!",
    6: "...I'm getting warmer and warmer... A little sleepy, maybe?",
    7: "...Anyway, I'll switch the tower back to Normal Mode.",
    9: "Now this tower's energy won't be used for the protective field anymore.",
    10: "Great! Let's move on!",
    11: "Careful. I'm sure that's a Shadow Guard.",
    12: "Hahahaha! You've made it this far, chosen heroes! I am the Digital Hazard Dragon from ancient legend! I'm Megidramon, the Blast Elite in Lord Barbamon's Shadow Guard, sent to protect this Capacitor Tower!",
    13: "Uh... Doesn't he look a little different than that?",
    14: "Y-yeah... I was a little surprised, that's all.",
    15: "Hey, what do you mean by 'chosen heroes'?",
    16: "Is it because he's a dragon? You know, like in games...",
    17: "Barbamon...! What do you mean, a game?! Quit messing around! Let's go, Taiki! Send him flying!",
    18: "Come on, attack me!",
    19: "Hahahaha! To defeat this Megidramon... You truly are the ancient Hazard Hero chosen by the dragon!",
    20: "That doesn't make any sense!",
    21: "You fell before your quest was complete... But Megidramon sought even greater strength, so the Dark Emperor, Lord Barbamon, absorbed him! Hahahaha!",
    22: "...Damn. What's wrong with these guys?",
    23: "They're enjoying watching us fight... Fine! I'll go straight to their boss!",
    24: "Spadamon, switch the tower to Normal Mode.",
    28: "I want something sweet...",
    29: "Where did that come from?!",
    30: "Spadamon, are you all right? Did activating the tower drain your strength?",
    31: "...Yeah. I'm getting a little dazed... But I'm fine. Let's keep going.",
    32: "Hah-hah? You're here, the boys everyone's been talking about♪ That's right! Come on over!",
    34: "...What is that? Is it a Shadow Guard?",
    35: "Why would Barbamon send someone so weird...?",
    36: "He's completely toying with us...",
    37: "Damn... Is this all a game to him?!",
    38: "I'm TigerVespamon, the Speedy Elite in Lord Barbamon's Shadow Guard, sent to protect this Capacitor Tower! Call me TG Vespamon! Or just Tigress♪",
    41: "Ugh... That guy's creepy...",
    42: "Hmm? What's that? You're shy boys♪ All right, special treat! You can call me Tiggy♪",
    44: "As if!",
    45: "Absolutely not!!",
    47: "No way I'm losing to such a ridiculous opponent! I'm counting on you, Taiki!",
    48: "Oh, impatient, are we? All right! I'll hit you until your hate turns to love♪",
    49: "...That was a rough fight.",
    50: "...Are they calm now?",
    51: "Hey, TG Vespamon! Tell Barbamon he'll regret messing around!",
    52: "Yeah! We're never going to lose!",
    53: "Why... Why does everyone hate me so much...? Barbamon is the only one who accepts and understands me... Wait for me, my lord! Let's become one!",
    54: "He definitely doesn't care about you.",
    56: "Shoutmon...",
    57: "Yeah... That was a little too blunt...",
    58: "That's fine! You have to be clear with people like that!",
    59: "I'll switch the tower's mode now.",
    61: "Spadamon, are you all right? You look tired.",
    62: "Uh... Yeah... I feel kind of hot...",
    63: "Did you catch a cold or something?",
    64: "Don't work so hard that you collapse. Don't push yourself!",
    65: "Didn't think I'd hear that from you... Come on, let's go!",
    66: "...Urrp.",
    68: "S-sorry, everyone... Just... give me a minute... That Shadow Guard... Urrp...",
    69: "Hey, what happened?! Did it attack you?!",
    70: "No... That's not it... I'm... I'm fine... Blech!",
    71: "That 'blech' doesn't sound like you're fine. What's wrong, Spadamon?",
    72: "...It's hard to say, but... I can't handle squid-like things...",
    73: "Now that you mention it... I heard cats shouldn't eat squid.",
    74: "...I'm not a cat.",
    75: "All right, Spadamon, hold your nose! Let's go, Taiki! We'll finish this quickly!",
    76: "I heard someone whispering insults... It was you?!",
    77: "I'm MarineDevimon, the Wetty Elite in Lord Barbamon's Shadow Guard, sent to protect this Capacitor Tower!",
    78: "Phew... Ugh! That's disgusting! I can't do this... It's slimy and shiny, and it smells so fishy... This is breaking my spirit!",
    79: "Are you all right? I told you to hold your nose!",
    80: "So Lord Barbamon expected this! But... even if it gives us an advantage, I feel awful!",
    81: "B-Barbamon won't get his way! ...Ugh!",
    82: "Why are you telling him that to his face?!",
    83: "I'll crush you until that nose stops working!",
    84: "Yeah... I think that already happened...",
    85: "Couldn't agree more...",
    86: "You...! I'll use my last strength to cover you all in slime!",
    87: "Eww! Stop it! We already won!",
    88: "Shut up! Lord Barbamon must have expected this. I'll at least make sure Spadamon can't recover!",
    89: "No thanks! If that thing wraps around me, my nose is done for!",
}


def main() -> None:
    destination = ROOT / "translations/batch80.json"
    if destination.exists():
        raise FileExistsError(destination)
    records = collect_messages(Rom(rom_paths()["blue"]))
    existing = translate_records(records)
    blocks = []
    for index, english in DIALOGUE.items():
        key = f"MSG/MESPAK02.PAK:009:{index:05d}"
        if key not in records or key in existing:
            raise ValueError(f"Missing or already translated source: {key}")
        row = records[key]
        if category(row) != "Story and dialogue":
            raise ValueError(f"Unexpected translation category for {key}")
        blocks.append({
            "archive": row["archive"], "entry": row["entry"],
            "start": row["index"], "category": "Story and dialogue",
            "english": [english], "sources": ["Original Japanese ROM"],
            "review_note": "Continuous tower scene translation. The Shadow Guard's exaggerated self-introductions and deliberate jokes are kept as jokes, while tower mechanics and Spadamon's weakness remain clear.",
        })
    destination.write_text(json.dumps({
        "description": "Translate the Megidramon, TigerVespamon, and MarineDevimon tower scenes in MESPAK02 entry 9.",
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(destination), "slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
