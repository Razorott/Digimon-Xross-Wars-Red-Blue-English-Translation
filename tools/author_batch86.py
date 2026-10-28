"""Translate Spadamon's farewell/return and the new alliance, entry 11."""
from __future__ import annotations

import json

from build import collect_messages, translate_records
from translation_queue import category
from xros_text import ROOT, Rom, rom_paths


DIALOGUE = {
    100: "I understand what Armamon wanted... I'm a Weapon Digimon, so I can't just abandon him. Are you both ready?",
    101: "W-wait! I haven't finished talking...!",
    102: "It's okay! I'll stop Armamon's rampage and come right back! Bye!",
    103: "...It's all right. Everything will be okay. Taiki, Shoutmon... Dynasmon... Everyone made me strong. I'm sure it'll work out. Thank you, everyone... Now it's my turn to save you!",
    104: "Taiki! Shoutmon!",
    105: "...Huh? Akari... Wait, what was I doing...?",
    106: "Hey, Shoutmon! Are you all right?!",
    107: "He is only unconscious. His injuries are minor.",
    108: "What a lightweight! Get up, brother!",
    109: "...Huh?! What's going on? Why is everyone here? Did something happen?!",
    110: "Ballistamon reports: no damage at all.",
    111: "That's one tough hide, bro!",
    112: "By the way, Taiki, what happened? There was a huge tremor and a loud noise... It sounded like a massive explosion. Then you two suddenly appeared!",
    113: "That wasn't a normal teleport. It looked like you were blasted here from somewhere.",
    114: "Blasted... here...?",
    115: "Taiki... Did something happen to Spadamon?!",
    116: "Everyone, it's a miracle! The data disturbance in Lost Space has disappeared! If it had kept spreading, it would've been a disaster. It vanished right after you came back... Could it be thanks to you?",
    117: "...It was thanks to Spadamon.",
    118: "...Huh?",
    119: "Hey, where's Spadamon?",
    120: "Right... Where is Spadamon? Only you two appeared here.",
    121: "Spadamon probably won't be coming back...",
    122: "He stayed behind in Lost Space to stop that huge Weapon Digimon's rampage...",
    123: "That idiot... Spadamon...!",
    124: "Phew! That was close! I barely made it out!",
    125: "Spadaaaamon!",
    126: "What?",
    127: "...No way.",
    128: "Spadamon! Thank goodness you're safe! You had us worried!",
    129: "Shoutmon was already bawling his eyes out...",
    130: "Sh-shut up, Ballistamon! Don't say stuff like that!",
    131: "Spadamon! You made it out all right?",
    132: "Yeah. It was close, but I escaped just in time.",
    133: "Everyone, it's okay now! Armamon disappeared along with the black hole! I think he went back to the same place as Dynasmon.",
    134: "What happened to Lost Space?",
    135: "Lost Space itself should now be open to travel, just like the other areas. I completely sealed off every dangerous part. But there's still a lot we don't know, so let's keep watch and think it over for a while.",
    136: "Spadamon, you've changed a little. You're suddenly so dependable!",
    137: "W-well! That's thanks to my excellent training! You were a crybaby when we first met. A guy can't cry anymore, okay?!",
    138: "Yeah, thanks, Shoutmon. ...So wipe those tears, okay?",
    139: "Spadamon, you did such a wonderful job. While you were away, everyone told me you were one of the last Weapon Digimon. I knew there was something special about you!♪",
    140: "By the way, Spadamon, what will you do now? Armamon and Dynasmon are both gone...",
    141: "I've decided! As the last Weapon Digimon, I'll protect Elestou Zone from now on! So, Taiki... Will you become my warrior?",
    142: "Your warrior...?",
    143: "When a Weapon Digimon finds someone it can entrust with all its power, it asks them to become its warrior! I'll become your sword. This is the proof of our bond.",
    144: "...Whoa! Taiki, is that...?",
    145: "A Code Crown?!",
    146: "That's right. The Code Crown is given by Elestou Zone's ruler to the person I should serve.",
    147: "All right! I got a Code Crown!",
    148: "Key item acquired! Code Crown",
    149: "Equipment acquired! Elestou Sword",
    150: "Equipment acquired! Elestou Shield",
    151: "...Oh no. I gave it to him...",
    152: "Huh? Was that a bad idea?",
    153: "It's not bad... but are you really sure, Taiki?",
    154: "Sure about what?!",
    155: "Hey, Spadamon! Explain properly!",
    156: "Hehe! I was so happy, I skipped a step.",
    157: "Wait... What does that mean?",
    158: "Whoever receives this Zone's Code Crown has a duty to train a Weapon Digimon until it's strong enough to protect the Zone. So you can't leave until that's done, okay?",
    159: "Whaaaaaat?!",
    160: "It's okay! I've gotten pretty strong, so it shouldn't take too long! Everyone, let's keep working together!♪",
    161: "...I don't mind. I like Sky Fort, so I could stay for a while! There are probably areas I haven't seen yet, too!",
    162: "Oh! Then I want to go to Earth Fort! A secret base inside a giant machine... That's a guy's dream!",
    163: "Well, that sounds nice. It'll be fun... Let's support the Digimon here for a while!♪",
    164: "All right, Spadamon! I'm going to train you hard, so get ready!",
    165: "Enter Lost Space?",
    166: "Yes, enter.",
    167: "No, stay here.",
    168: "Return to Sky Garden?",
    173: "I... I saw lightning strike right in front of me... Then everything went dark, and I passed out... What happened to Barbamon and Kiriha after that?",
    174: "...Barbamon sent Kiriha to another Zone. Damn it! I couldn't do anything...!",
    178: "Parrotmon... Thank goodness the aerial squad is safe!",
    185: "You're safe... Team Xros Heart.",
    186: "Kiriha was sent away...?",
    187: "MailBirdramon?! And Greymon... You're safe, too?",
    188: "Kiriha reloaded us when he saw an opening. He told us to help you if anything happened to him.",
    189: "We'd been tracking ROG's movements from the start. We were close to solving this Zone's mystery... I never thought Barbamon was secretly controlling ROG.",
    190: "What will you do now?",
    191: "I already told you: we'll help you. Barbamon's Shadow Guard took the Capacitor Towers. We'll need more strength from now on... So we'll lend you ours.",
    192: "...I appreciate that, but...",
    193: "Are you two sure about this?",
    194: "Don't misunderstand. We only follow Kiriha.",
    195: "Hmph... That's a pretty irritating way to put it!",
    196: "We'll help you until Kiriha returns to this Zone.",
    197: "Thank you, both of you... Kiriha will be all right. Knowing him, he won't go down easily.",
    198: "Kiriha thinks highly of you.",
    199: "Don't do anything that will disappoint him.",
}


def main() -> None:
    destination = ROOT / "translations/batch86.json"
    if destination.exists():
        raise FileExistsError(destination)
    records = collect_messages(Rom(rom_paths()["blue"]))
    existing = translate_records(records)
    blocks = []
    for index, english in DIALOGUE.items():
        key = f"MSG/MESPAK02.PAK:011:{index:05d}"
        if key not in records or key in existing:
            raise ValueError(f"Missing or already translated source: {key}")
        row = records[key]
        if category(row) != "Story and dialogue":
            raise ValueError(f"Unexpected translation category for {key}")
        blocks.append({
            "archive": row["archive"], "entry": row["entry"],
            "start": row["index"], "category": "Story and dialogue",
            "english": [english], "sources": ["Original Japanese ROM"],
            "review_note": "Armamon's defeat, Spadamon's return and Code Crown choice, followed by the Graymon/MailBirdramon alliance scene.",
        })
    if len(blocks) != 87:
        raise ValueError(f"Expected 87 dialogue strings, got {len(blocks)}")
    destination.write_text(json.dumps({
        "description": "Translate the aftermath of Armamon's defeat and Kiriha's allies, MESPAK02 entry 11.",
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(destination), "slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
