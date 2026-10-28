"""Translate the next continuous story scene in MESPAK02 entry 7."""
from __future__ import annotations

import json

from build import collect_messages, translate_records
from translation_queue import category
from xros_text import ROOT, Rom, rom_paths


DIALOGUE = {
    0: "Pukuku! We meet again~!",
    1: "You! You're the one from Knuckle Coast!",
    2: "I, Pukumon the Prickle, ROG's Splash Leader, will show you the difference in our strength~!",
    3: "Pukumon! Stop this! The black shadow will absorb you too if you keep this up!",
    4: "You people are hilarious~! Did you think a clever Digimon like me wouldn't notice that shadow? Pukuku!",
    5: "Then why...?",
    6: "That shadow will absorb all of ROG! That's why you people are in our way!",
    7: "...Pukuku! That one stung a little.",
    8: "Give up already!",
    9: "You don't understand why I'm here, do you? Did you think I was fighting at random? I've reported everything about how you fight...",
    10: "Pukumon, well done...",
    11: "Now hand over your 'wisdom' to me...",
    12: "As you command, our Dark Emperor! Pukuku!",
    13: "What is ROG...? Aren't you afraid you'll disappear?",
    14: "A boss who sacrifices allies is no good at all!",
    15: "Minotaurmon is 'Power,' and Pukumon is 'Wisdom'...? What did that shadow mean?",
    16: "Maybe they are the keys to the seal.",
    17: "They said they were reporting on how we fight, too... They must be sending stronger foes after us!",
    18: "No matter who we face, we won't lose! Let's move on!",
    19: "Hey, you guys~! We meet again~!",
    20: "You're the one who kidnapped Chibickmon! And you took Dorulumon and Cutemon hostage, too!",
    21: "Kidnap? Such a rude word for an ugly bunch~!",
    22: "Who are you calling ugly, you... Grr! Now I'm mad!",
    23: "Minervamon... tell me something.",
    24: "If you like cute things, couldn't everyone live together in peace without invading zones? Why take over zones in a way that makes everyone suffer?",
    25: "Minervamon... if you like cute things... Maybe you and Akari would get along! Chibickmon likes you, too. I just can't believe you're a bad guy.",
    26: "You guys may be ugly, but you say the sweetest things~! A dreamy goof like you isn't so bad~!",
    27: "...What did you say?!",
    28: "Everyone has things they have to do. You can't just do whatever you want, can you? I don't know how sweet your real life is, but mine is bitter and heavy, dirty and dark! That's why I can appreciate cute things. You get it?",
    29: "Minervamon!!",
    30: "If you won't come over here, then I'll come to you~!",
    31: "Ouch... Good job, you guys! My Lil' Bits got beaten~! Hehe... hehehehe~!",
    32: "How can you laugh like that?! There's something wrong with you! You're completely crazy!",
    33: "Ha-ha! That's right! Of course I'm crazy~! And? What's it to you? Ah-ha~?",
    34: "Taiki! Minervamon can't be a good guy! She's just making fun of us and playing around!",
    35: "The rule of TEAM CUTE!",
    36: "When we're down, we laugh! When things get tough, we laugh them off! That's what we all promised, together with the precious friends we lost in battle. Looking at you guys reminds me of those days...",
    37: "Minervamon, have you grown fond of this boy...? Still, I'll take your Agility data.",
    38: "...Well, it was our first promise, right? Guess I have to give it to you.",
    39: "Don't worry. All your friends, with you at their center, will be absorbed into one.",
    40: "The 'Legendary Ancient Weapon'...? ROG is crazier than me for gathering data for that! Someday these ugly guys will beat you!",
    41: "Yeeeeah! Yahoooo~!",
    42: "...What was with her?",
    43: "She called us ugly right to the end... Damn, Taiki! I'm so frustrated!",
    44: "Yeah, Shoutmon. I'm frustrated, too. I won't let her do whatever she wants anymore!",
    46: "That's the boss of Skull Glacier! Watch out, he's a lying crook! He tried to use Sparrowmon as a hostage even though he hadn't captured her!",
    47: "I see... So that's the trick... Ha-ha-ha! You fools don't know, do you? ROG has Sparrowmon! If you want her back, admit defeat now!",
    48: "...Hey, you're the one who doesn't know! We already rescued Sparrowmon, and she's doing just fine!",
    49: "W-what?! So that's what happened?!",
}


def main() -> None:
    destination = ROOT / "translations/batch68.json"
    if destination.exists():
        raise FileExistsError(destination)
    records = collect_messages(Rom(rom_paths()["blue"]))
    existing = translate_records(records)
    blocks = []
    for index, english in DIALOGUE.items():
        key = f"MSG/MESPAK02.PAK:007:{index:05d}"
        if key not in records or key in existing:
            raise ValueError(f"Missing or already translated source: {key}")
        row = records[key]
        if category(row) != "Story and dialogue":
            raise ValueError(f"Unexpected category for {key}")
        blocks.append({
            "archive": row["archive"], "entry": row["entry"],
            "start": row["index"], "category": "Story and dialogue",
            "english": [english], "sources": ["Original Japanese ROM"],
            "review_note": "Direct dialogue translation with continuous scene context. Original character names and established western Digimon spellings are retained; the term Pukumon is confirmed by Bandai's English Digimon Encyclopedia.",
        })
    destination.write_text(json.dumps({
        "description": "Translate the Pukumon and Minervamon story scene in MESPAK02 entry 7, including the ROG reveal and Nene's rescue arc.",
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(destination), "slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
