"""Translate the first restored tower, farm tutorial, and allies, entry 13."""
from __future__ import annotations

import json

from build import collect_messages, translate_records
from translation_queue import category
from xros_text import ROOT, Rom, rom_paths


DIALOGUE = {
    5: "This door protects the Capacitor System. ...It's still firmly shut. ROG hasn't been here, so why does something feel different from last time...?",
    6: "What?! How did that happen?! Taiki, did you do something?!",
    7: "N-no... Spadamon, did you do something?",
    8: "I only touched it! Then it suddenly lit up! How? Only the administrator should be able to open it...",
    9: "So... does that mean Spadamon is the administrator?",
    10: "N-no way! When I came here before, it wouldn't open at all!",
    11: "But...",
    12: "What are you standing around talking for?! Let's get the tower running! Sky Fort will crash with everyone still inside!",
    13: "...Right. Restoring the energy supply comes first.",
    14: "Spadamon, try activating the tower.",
    15: "O-okay...",
    16: "Will getting this running make Sky Fort move again? We can use the DigiLab and DigiFarm, too? This is gonna be great!♪",
    19: "It worked!",
    20: "Nice work, Spadamon! But what's a Farm Island? Is that different from the DigiFarm Patamon mentioned?",
    21: "Farm Islands are the growing areas inside the DigiFarm. Each one can raise up to eight Digimon. They help you make your Digimon stronger! The Terrain Board and BGM Board affect how different types grow, so try different combinations on each island! Now, give your first Farm Island a name!",
    22: "Nice! I like it. That's the perfect name for our first DigiFarm!",
    23: "Did that restore Sky Fort's systems, too?",
    24: "Only one of the six Capacitor Towers is running, so... maybe about 16% of Sky Fort's systems are back?",
    25: "That's all?!",
    26: "Hey, don't rush it. We'll get there one tower at a time. At least the energy problem is fixed!",
    27: "And now that Sky Fort has power again, I can access the Data Library folder!",
    31: "A DigiScore? What's this?",
    32: "You need DigiScores for DigiFusion. You can use DigiFusion at the DigiLab.",
    33: "DigiFusion? What's that?",
    34: "DigiFusion is a special kind of DigiXross. It fuses two Digimon to create a new one!",
    35: "A fusion?! A special DigiXross? You can do that?! That's amazing!",
    36: "This system was developed specially for this Zone. Sky Fort used to have every DigiScore, but the energy stopped and the backup was damaged... Only a few DigiScores remain. Still, don't worry! You can collect more by defeating wild Digimon! Check the DigiLab PC and DigiFarm PC at Sky Fort.",
    37: "...Taiki! Did you hear that? Someone's over there!",
    38: "C-could it be ROG?!",
    39: "No way. They couldn't have shown up this soon... right?",
    40: "We can talk later! Let's go check it out! Spadamon, come on,and keep up!",
    41: "Huh? Oh,whoa! Wait! I'm not mentally ready yet!",
    42: "Spadamon! And you must be... Hmm, how unusual. There's even a human with you.",
    43: "...Who are you?",
    44: "I'm Ganimon. I live around here. The Capacitor Tower suddenly started running, so I hurried over. I'm not a threat.",
    45: "You startled us! We're here to get the Capacitor Towers running. That's one down, only five left!",
    46: "You got the Capacitor Tower running?! I was worried ROG had taken it, too. So you stopped them... Thank you! If you could activate the tower, does that mean Spadamon's memories have returned?",
    47: "Huh?! Well... I... Not yet... I don't even know why the door opened.",
    48: "...I see. Don't force it. Your memories are important, but they'll come back when the time is right. Until then, fight your enemies and grow stronger. You can't keep running away, all right?",
    80: "That's incredible! You seem like someone we can count on.",
    81: "You're amazing, too! You defeated Pukumon from ROG! We'll protect this place from now on. I'll be right here, so come talk to me if you need anything!",
    82: "Great! Let's head to the next one!",
    83: "Then put us in your Xros Loader for now!♪",
    85: "Once we get this one running, our Digimon friends will come back, right? I can't wait!♪",
    88: "Can you give this Farm Island a good name, too?",
    89: "...Yeah, I like it. Oh, I can access the Data Library folder again!",
    94: "...All right! This tower is running now! We got a new Farm Island and more DigiScores, too!",
    95: "The more Capacitor Towers we get running, the more of Sky Fort's systems should come back.",
    96: "And our Digimon friends will return, too! Someone might already be here. Let's go check!",
    97: "...Huh? Kuwagamon? Did you live around here?",
    98: "Nope! I was a free-spirited drifter! But I got lost, hit a rough patch, and somehow washed up here... I don't really know how it happened, but if you'll let me stay, I'll put down roots here and do my best!",
    99: "Is this guy okay? He seems kind of... mellow.",
    100: "He's fine! Kuwagamon's jaws are incredibly strong! Kids love him, too!",
    101: "Well, he is a stag beetle. They're pretty cool.",
    102: "Aw, you're making me blush!♪ Now I'm fired up! Count on me!♪",
    103: "All right! Let's hurry to the next one!",
    104: "Taiki, we'll hop into the Xros Loader now!♪",
    105: "All right, let's open this door, too...!",
    106: "All these Capacitor Towers look the same... I'd probably take a wrong turn and end up at the wrong one!",
    109: "Will you name the new Farm Island?",
    110: "Hmm... 72 points! ...I guess? But maybe it's even better... Hmm... 98 points! Yes, that's more like it! Oh! I can access the Data Library again!",
    115: "Hey, Spadamon. I still don't really understand the Farm Goods you can put on Farm Islands... What should I choose?",
    116: "Farm Goods can raise stats like strength or speed, give you lots of EXP, or help you make equipment. Choose whatever suits what you want to do, Taiki!",
    117: "I see... But they're kind of expensive. Can't they be a little cheaper?",
    118: "B-but they're worth the price! Strong enemies might show up later! For our sake, don't be too stingy... Buy us strong equipment and Farm Goods! You will, right?!",
    119: "Don't worry! Taiki will buy them for you. More importantly, let's go see if any friends have returned!",
    120: "...Mammothmon! And Zudomon, too!",
    121: "You finally took the tower back from them! Thank you so much, Spadamon!",
    122: "You went to all the trouble of taking the Capacitor Tower back... Now it's our turn to guard it with everything we've got!",
    123: "Yeah! I'm counting on you!",
    124: "We'll leave the rest to them. Let's move on.",
    125: "Let's hop into the Xros Loader for a while.",
    126: "Right! Then we're counting on you, Taiki!",
    127: "I'll open it now, so wait a moment.",
    128: "Taiki, think of a name for the next Farm Island!♪",
    131: "Taiki, will you name the new Farm Island?",
    132: "...Yeah, that's a clear, easy-to-remember name. Oh! I can access the Data Library folder again!",
    138: "...By the way, Taiki, I've been wondering for a while... Why did you come to Elestou Zone?",
    139: "Why? Spadamon called us, didn't he? Taiki heard your voice.",
    140: "We were standing in front of a Weapon Digimon buried in the jungle when a strange ball of light swallowed us and brought us here. I thought you had called us.",
    141: "Whaaat?! I called Taiki? I have no idea what you're talking about!",
    142: "...Really? Then who brought us to this Zone...? Well, never mind the details. Let's head into the city!",
    143: "Devitamamon! And Pinocchimon, too!",
    144: "I heard the rumors and couldn't stay away! Spadamon and Xros Heart! Everyone is grateful to you!",
    145: "Well, I'm tired of running away. With you guys, we might actually take the Zone back!",
    146: "Leave it to us! Let's work together from now on!",
    147: "Spadamon, you've got a lot of great friends.",
    148: "...Yeah. We were all able to come back because of Taiki and the others. Thank you both!",
    149: "No problem! Now let's hurry and take the rest back!",
    150: "I'll open the door now. Wait a little...",
    151: "Taiki, what setup should we use for the next Farm Island? Let's think about it now!♪",
    154: "Will you name the new Farm Island?",
    155: "Thanks, Taiki. That's a good name! I knew you'd think of one! Oh! I can access the Data Library again!",
    162: "Hey, you two! Do you like sweets?",
    163: "Why do you ask all of a sudden, Spadamon?",
    164: "When we take the Zone back from ROG, I want to have a huge cake ready at Sky Fort... Then we can all celebrate together!",
    165: "Oh, great idea! We should have fireworks, too! Since Sky Fort is in the sky, we could launch them from there... Everyone in the Zone would see!",
    166: "Fireworks? That sounds like something delicious!",
    167: "I don't think they're food...",
    168: "I hear someone's voice outside! Let's go see!",
    169: "CannonBeemon!",
    170: "Sorry we left everything to you. From now on, we'll help with whatever you need!",
    171: "Thanks. I'm counting on you!",
    172: "We'll be right here. Come talk to us if you need anything.",
    173: "Everyone here is so nice.",
    174: "Yeah. They really are.",
    175: "All right, on to the next one! Let's keep moving!",
    176: "Wait a moment.",
    177: "Huh...? That's strange... I don't think I have enough power. My abilities will return when we defeat ROG's leaders... Maybe we have to defeat the leader Digimon first?",
    178: "Yes, recruit this Digimon.",
    179: "Not yet. Don't recruit this Digimon.",
    180: "You can't recruit any more Digimon. Release some and come back.",
    181: "Understood. I'll wait here...",
    183: "Want me to join you?",
    185: "Would you like me to join you?",
    186: "Make me your ally...?",
    187: "You want me on your team?!",
    189: "Talk to me whenever you're ready.",
    190: "Recruit me if you want to beat up the bad guys!",
    191: "I'm always ready to fight.",
    192: "Stop pretending you don't need me and recruit me.",
    193: "Make me your ally.",
    194: "Put me on your team!",
    195: "If you need help, recruit me.",
    196: "Dorumon joined your team.",
    197: "Sparrowmon joined your team.",
    198: "Beelzemon joined your team.",
    199: "SkullKnightmon joined your team.",
}


def main() -> None:
    destination = ROOT / "translations/batch88.json"
    if destination.exists():
        raise FileExistsError(destination)
    records = collect_messages(Rom(rom_paths()["blue"]))
    existing = translate_records(records)
    blocks = []
    for index, english in DIALOGUE.items():
        key = f"MSG/MESPAK02.PAK:013:{index:05d}"
        if key not in records or key in existing:
            raise ValueError(f"Missing or already translated source: {key}")
        row = records[key]
        if category(row) != "Story and dialogue":
            raise ValueError(f"Unexpected translation category for {key}")
        blocks.append({
            "archive": row["archive"], "entry": row["entry"],
            "start": row["index"], "category": "Story and dialogue",
            "english": [english], "sources": ["Original Japanese ROM"],
            "review_note": "Restored Capacitor Tower tutorial, Farm Island and DigiFusion explanations, returning allies, and recruitment prompts. Key game terms follow the project glossary.",
        })
    if len(blocks) != 128:
        raise ValueError(f"Expected 128 dialogue strings, got {len(blocks)}")
    destination.write_text(json.dumps({
        "description": "Translate the next Capacitor Tower, DigiFarm/Farm Island tutorials, and returning allies in MESPAK02 entry 13.",
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(destination), "slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
