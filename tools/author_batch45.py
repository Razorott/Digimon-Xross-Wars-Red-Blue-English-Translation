"""Translate 100 Digimon profile blurbs from MESPAK03 entry 2."""
from __future__ import annotations

import json
import textwrap

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

LOCAL = "Original Japanese ROM (local primary source)"
CARD_LIST = "https://world.digimoncard.com/cards/"
PROFILE = {
0: "An armored dragon Digimon with a tough body and a horn as hard as diamond. It charges foes with its horn and can breathe huge fireballs.",
1: "A reaper-like ghost Digimon carrying a huge chain sickle. The cloth covering it connects to another dimension. It is said that no one possessed by Phantomon can be saved.",
2: "A black, bull-like sacred beast Digimon clad in red armor. This mighty warrior wields two swords said to be powerful enough to split a mountain.",
3: "A legendary holy dragon Digimon evolved from Veedramon after many victories. It has grown wings and gained greatly improved offense and defense.",
4: "Leomon's Ultimate form is a beast-man Digimon wearing rapidly spinning armor on its arms and legs. A master warrior, it battles evil with swift, powerful attacks like a whirlwind.",
5: "A warrior Digimon clad in heavy Chrome Digizoid armor and wielding its favorite greatsword with ease. The armor restrains its dangerous power. It serves its master faithfully, whether good or evil.",
6: "A gentle, long-necked dragon Digimon resembling a dinosaur from ancient times. Despite its huge body, it is mild-mannered and spends its days at a leisurely pace.",
7: "A kappa-like demon Digimon said to have been banished from the Digital World's heaven. Its necklace seals its DigiCore; if even one charm is lost, it may revert to a terrifying creature.",
8: "A three-legged crow Digimon. The sacred jewels on its wings generate holy energy. Legend says it guides the chosen to the Golden Land of the Digital World.",
9: "A puppet Digimon skilled with artillery. Its attacks cover a long, wide range, allowing it to strike enemies from afar.",
10: "A fortress-like Digimon with impenetrable defense. It blocks enemy attacks, then counterattacks with speed unexpected from a giant.",
11: "A form evolved from Fairymon for hand-to-hand combat. It stands on two legs and channels the power of fire and lions into its fighting spirit. Its signature fist attack is Crimson Beast King Wave.",
12: "Lekismon's Ultimate form moves at incredible speed. Wielding two crescent-marked weapons called Noire Luna, it dances through battle and slices foes apart with its signature move, Lunatic Dance.",
13: "An Armor Digivolution of Veemon using the Digi-Egg of Courage. It draws out the Egg's fire attribute completely and launches fierce attacks like blazing flames.",
14: "A Royal Knight and Veemon's Armor Digivolution with the Digi-Egg of Miracles. Its Chrome Digizoid armor is exceptionally tough, and its miraculous power can overcome any crisis.",
15: "Patamon's Armor Digivolution with the Digi-Egg of Kindness. It excels at digging through the ground and, when frightened, may quickly burrow away to escape.",
16: "Wormmon's Armor Digivolution with the Digi-Egg of Miracles. This heavyweight fighter has a golden metal body and wields the sacred Vajra, said to make miracles happen.",
17: "Hawkmon's Armor Digivolution with the Digi-Egg of Purity. It blends into nature and attacks like a ninja, extending its springlike arms and legs to great length.",
18: "Armadillomon's Armor Digivolution with the Digi-Egg of Friendship. Its right arm is a forklift and its left a power shovel, making it useful for any construction job.",
19: "A Digimon born from an algorithm bug. It uses countless vines like tentacles to dominate a wide area, transforming into a parasitic form called Worm Phase.",
20: "A Jogress of Angemon and Ankylomon with high defense. Its appearance suggests it may be an angel Digimon descended from the ancient Digital World. Its neck and torso rotate 360 degrees, letting it attack in any direction.",
21: "An evil evolution of the Seadramon species. It controls dark power with the blade-like horn on its head and is even more cunning and relentless in hunting prey than Megaseadramon.",
22: "An undead Digimon revived from fossil data. The black chill pouring from its DigiCore fills any Digimon with mortal terror. Its signature move is Grave Bone.",
23: "A dual-sword warrior Digimon known as the Golden Meteor. Its swordsmanship is said to surpass even the Royal Knight LordKnightmon. Its royal-blue cape honors its many victories.",
24: "A Tyrannomon that evolved after surviving fierce battles. It trains its younger Tyrannomon followers to become full-fledged warriors, like a master to its students.",
25: "A mysterious Digimon that can appear anywhere in time and space through a book. Researchers believe it is a demon Digimon from the same lineage as Piedmon.",
26: "A mermaid-like Digimon with a captivating singing voice. Its greed for treasure is so strong that it will even steal another Digimon's data.",
27: "A warrior Digimon evolved from Bryweludramon. It swings a huge greatsword that can fell a mountain with one blow. Though nearing the peak of strength, it has begun to question battles that destroy everything.",
28: "A beast-man Digimon called the Cat Goddess. Flashy and cunning, it uses its jewels and bewitching eyes to control others. Its graceful movements hide great strength, and its claws can cut stone.",
29: "A hellhound Digimon protected by tough biological armor. It repairs damage over time. The armor on its shoulders is sentient, detecting attacks from every direction and warning its true body, Cerberumon.",
30: "A flame Digimon burning even hotter than Meramon. Its signature Ice Phantom fires dry-ice-cold ice at foes, leaving them with burns.",
31: "An insect Digimon known as the Desert Assassin. Its tail's venomous stinger kills before its victim notices the wound, so the assassin's presence is never discovered.",
32: "Tailmon's Armor Digivolution with the Digi-Egg of Light. It draws out the Egg's holy attribute to its fullest, gaining power that can drive away darkness.",
33: "The ultimate insect Digimon, evolved from combined Kabuterimon and Kuwagamon data. Its huge horn and pincers compensate for both species' weaknesses, and it flies at supersonic speed.",
34: "An ancient lion Digimon believed to be an ancestor of Leomon. Its origins are a mystery; some say it is Leomon in a beast form. It moves at the speed of Mach.",
35: "Etemon's Mega form, upgraded into a full-metal cyborg for combat. It rebuilt its damaged body with Chrome Digizoid, using data gathered from countless battles.",
36: "A cute fairy Digimon living in the Net Ocean, rarely seen by others. Its Holy Ring suggests a connection to holy Digimon, and it prefers to avoid fighting.",
37: "A cyborg Digimon nicknamed the giant amphibious assault carrier. It is longer than Whamon and can carry several Digimon inside. Its attack power matches its enormous size.",
38: "A demon Digimon in the form of a clown. It appears without warning and is shrouded in mystery. If you meet it, you can only curse your fate.",
39: "A Demon Lord who commands demons and fallen angels. It was once a high-ranking angel, but was cast into the Dark Area for defying the forces of good and now bears a grudge against them.",
40: "The ultimate form of a golden bird Digimon with four wings. It leads all bird Digimon and is also said to unite holy Digimon.",
41: "A puppet Digimon made from the body of the cursed Cherrymon. Though it looks like a marionette, it has a will of its own. Many computer errors are said to be its doing.",
42: "A rose-like fairy Digimon known as the Queen of Flowers. The gem on its chest, Tifaret, is said to promise eternal beauty and strength. It always strives to remain beautiful.",
43: "The Mega form of the Greymon species, clad in Chrome Digizoid armor with Dramon Killers on its arms and a Brave Shield on its back. This veteran dragon warrior has greatly increased speed and power.",
44: "The Mega form of the Garurumon species, upgraded without sacrificing speed. Its cyborg body hides many weapons; it locks on with a laser sight and can fly at extreme speed on beam wings.",
45: "A full-metal cyborg assembled from parts of many cyborg Digimon. It has immense power and intelligence but no will of its own. An unknown being implanted an evil program in its DigiCore, feeding it endless malice.",
46: "A beast Digimon with an armored upper body and animal-like lower half. It is Vamdemon after releasing its true power, but loses itself to rampaging and dislikes this form.",
47: "An ancient, ultimate dragon Digimon. Its immense power is difficult to control, so it may become either good or evil. It is said to have another form that can use all its power.",
48: "A Demon Lord once a high-ranking angel, cast into the Dark Area. Unlike other fallen angels, it stays neutral between good and evil, but is said to become a god of destruction in the final battle.",
49: "A Seraph Digimon clad in sacred armor and bearing ten golden wings. It ranks above all other angel Digimon and is one of the Three Great Angels, alongside Ophanimon and Cherubimon (Virtue).",
50: "A cyborg Digimon perfected by upgrading the incomplete Andromon and adding Chrome Digizoid parts to its body. It can think for itself and launch precise, powerful attacks against Virus Digimon.",
51: "A mutant Digimon said to be Digitamamon's dark evolution, like a Pandora's box. It contains all the Digital World's evil and uses lost ancient programming languages as magic to destroy everything.",
52: "A beast-like Cherub Digimon that wields powerful lightning like divine punishment. It is one of the Three Great Angels, alongside Seraphimon and Ophanimon.",
53: "The Virus-corrupted form of Cherubimon (Virtue), one of the Three Great Angels. It can wield powerful lightning that falls like divine punishment.",
54: "A Royal Knight, one of the highest-ranking network security guardians. Though a Virus type, it protects the Net; if balance is lost, it can become dangerous. It bears sacred Chrome Digizoid armor, the lance Gram, and the shield Aegis.",
55: "A gigantic machine Digimon made entirely of weapons. It is slow because it channels its energy into power, giving it astonishing destructive force and the ability to counterattack from any direction.",
56: "A Digimon that serves as a shrine maiden and conveys divine will. It can assume a priestess form for rituals. Four fox spirits hide in the tubes at its waist, aiding it in battle and gathering information. Its Onmyodo arts create barriers that repel evil.",
57: "A destructive Digimon bearing the name of a demon. It absorbs network data, repeatedly evolves and grows, and rampages. It plans to seize a military computer and attack the human world with nuclear missiles.",
58: "A sea-king Digimon who rules all aquatic Digimon. Its scale armor is made of light, strong Blue Digizoid, granting high mobility. Its massive spear also gives it formidable attack power.",
59: "A Digimon born when a hacker's computer virus suddenly mutated. Small but fiercely proud, it cannot resist picking a fight with anyone. Its metal head is made of Chrome Digizoid.",
60: "A beast Digimon born from parts of bird-like and animal-like Digimon. It hides in caves in deserts and mountains. Fast and powerful, it guards data on the Internet.",
61: "A mysterious long-necked dragon Digimon discovered by researchers studying unidentified creatures. It appears on misty days but is rarely seen; its cry makes listeners feel sad.",
62: "A cyborg Digimon created around the same time as Andromon, with a human-based body. It has emotions and great strength, but could not be controlled; records of its existence were erased after an accident.",
63: "A mutant Digimon born from royal data, called the Prince of the Mamemon Kingdom. Its crown and cape are based on royal records, it is quite luxurious, and it always wears a smile.",
64: "An Ophanim Digimon embodying divine love and standing at the summit of female angel Digimon. It is one of the Three Great Angels, alongside Seraphimon and Cherubimon (Virtue).",
65: "A brave demon Digimon who leads the Musyamon army's charge. Its lower body is a horse, giving it balance in battle as it swings its katana. The huge blade in its right hand is called Ryuzanmaru.",
66: "An ancient Digimon in the form of an old man, said to have existed since the Digital World's creation. This sage knows everything and is said to have guided chosen humans when the world was in danger.",
67: "An ancient Digimon in the form of an old woman. Some whisper that an evil being cursed Rosemon into this shape, though no one knows the truth. One sweep of her magic broom can erase evil Virus data.",
68: "A god Digimon called the judge of Digimon, guardian of the Dark Area. It can rebirth incoming data as Digi-Eggs or imprison evil data in darkness, and can summon the beasts of hell.",
69: "A parasite Digimon that possesses others and controls them at will. It resembles a one-eyed spider and can draw out its host's full abilities, but makes the victim ferocious.",
70: "A metal, four-legged dragon Digimon equipped with a long-range cannon. Its powerful cannon shot and sturdy armor make it a formidable fighter, and its tail is dangerous at close range.",
71: "An angel Digimon who leads the angel army into battle. Its whole body is like a sharp blade, letting it slash foes to pieces. It is among the angels most specialized for offense.",
72: "A giant bird Digimon clad in golden armor made of Chrome Digizoid, which repels every attack. It is said to remove intruders who enter the Digital World.",
73: "A fictional Digimon born from the imagined DigiCore: an avatar of immense destruction and the ultimate enemy. Its power is too great for an ordinary Tamer to control.",
74: "A solitary Demon Lord Digimon who prefers to act alone. Proud and fiercely independent, it dislikes ganging up on the weak. Its two favorite shotguns are called Beerenhena.",
75: "A proud beast-man Digimon who lives by its own sense of justice. It fights anyone who opposes that justice, and only a Digimon that keeps winning against powerful foes can earn the title of Bancho.",
76: "A cyborg Digimon believed to be the D-Brigade's final battle weapon. It wanders in search of a target codenamed BAN-TYO and carries a hidden Gigastick Lance in its right arm.",
77: "A cyborg Digimon artificially created by studying captured Vademon data. It is said to have been built with alien technology at Area 51.",
78: "A dark beast Digimon from the deepest part of the Dark Area. Its body is as large as a mountain, and its lower jaw is said to open into the Dark Area's depths. Anything swallowed has its DigiCore crushed.",
79: "A golden holy dragon Digimon with a dragon hidden in each hand. It can release divine energy and attack foes anywhere with its tree-shattering move, God Flame.",
80: "The Mega form of the Seadramon species, entirely covered in Chrome Digizoid armor. Its metal body deflects attacks, and it is by far the fastest aquatic Digimon in the water.",
81: "A pure-white warrior Digimon that moves too quickly for the eye to follow. Its magic sword Fenrir Sword freezes anything it cuts. The golden bird Freyja at its side warns it of danger.",
82: "A righteous cyborg Digimon who appears in a flash, trailing a red scarf. It is a hero admired by Rookie Digimon and never tolerates evil. It evolves from Cyberdramon.",
83: "A beast-man Digimon who commands Ikkakumon and Zudomon and rules the frozen land. Its fur is as hard as Chrome Digizoid. It is merciless to foes but caring toward its followers, and carries Mjolnir on its back.",
84: "The black Virus form of WarGreymon. Its beliefs oppose WarGreymon's, but it has its own sense of justice. A proud warrior, it hates cowardice and does not consider deceitful Virus Digimon its allies.",
85: "A SkullMammothmon created when Mammothmon, long a fighter against Virus Digimon, was infected and reduced to bones. It has lost its emotions but still remembers its mission to defeat Virus types.",
86: "The final form of the Kuwagamon species. It lives deep in the forest and is active only at night. Called the Demon of the Deep Forest, it is HerakleKabuterimon's eternal rival.",
87: "A Digimon said to have evolved from a mummy type and ruled many areas of the ancient Digital World. Legends say it used many Digimon to complete mysterious ancient ruins, showing its great authority.",
88: "A Royal Knight said to restrain the others, though it never appears. It is also called the master of the Empty Seat.",
89: "The ultimate form of the holy beast Digimon, a holy dragon that carries the energy of justice and light to erase evil. Few have seen it, and its home is unknown; it is said to appear when evil energy arises.",
90: "A composite Digimon born from the fusion of powerful Mugendramon and Chimairamon data. The cause of the fusion remains a mystery; it is said to freely control space and dimensions.",
91: "A wicked dragon Digimon formed by Megalogrowmon's mistaken evolution. It spreads hatred and seeks to destroy everything it sees, embodying the dangerous power of the Digital Hazard.",
92: "A Royal Knight beast Digimon with six legs and high-speed movement, clad in Red Digizoid armor. It carries the sacred bow Muspelheim and the sacred shield Niflheim.",
93: "A holy dragon Digimon that stores blazing solar energy for battle. Its shining wings overflow with light, and it can summon the GeoGrey Sword, condensed from the power of the earth.",
94: "A heavy knight Digimon fully covered in Chrome Digizoid armor. It moves at incredible speed, appearing like a mirage to its opponents, and can use a wide range of techniques.",
95: "A gigantic cyborg Digimon that sacrificed some shell strength to cover its body with beam cannons. Its powerful all-over weapons make the saying 'the best defense is a good offense' suit it perfectly.",
96: "A stealthy ninja Digimon once called the Silver Crow, serving another Digimon at the dawn of the Digital World. Legend says the gods' anger turned one of its wings black.",
97: "The strongest Chessmon, with extreme range and attack power. It is a reliable protector for the timid KingChessmon.",
98: "The king Chessmon who schemes to build a Chessmon empire. The other Chessmon do not know what this empire would be, and no one around him is interested. He is timid and runs very fast.",
99: "A legendary Digimon born alongside Chrono Data through the YMIR Project. It can assume Holy Mode only when it undergoes super evolution with the power of sacred light.",
}

def fit(s: str) -> str:
    return "\n".join(textwrap.wrap(s, width=15, break_long_words=True, break_on_hyphens=False))

def main() -> None:
    records = collect_messages(Rom(rom_paths()["blue"]))
    done = translate_records(records)
    blocks, review = [], []
    for index, raw in PROFILE.items():
        key = f"MSG/MESPAK03.PAK:002:{index:05d}"
        if key in done:
            raise ValueError(f"Already translated: {key}")
        row = records.get(key)
        if not row or not row["source"].strip():
            raise ValueError(f"Missing profile source: {key}")
        english = fit(raw)
        note = "Translated from the original Japanese profile. Official Digimon names and franchise terminology are used where identifiable; see the linked English card list for nomenclature reference."
        blocks.append({"archive": row["archive"], "entry": 2, "start": index,
                       "category": "Digimon profiles", "english": [english],
                       "sources": [CARD_LIST], "review_note": note})
        review.append({"id": key, "japanese": row["source"], "english": english,
                       "evidence_url": LOCAL, "terminology_reference": CARD_LIST,
                       "review_note": note})
    if len(blocks) != 100:
        raise ValueError(f"Expected 100 profiles, authored {len(blocks)}")
    path = ROOT / "translations/batch45.json"
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps({"description": "Translate the third 100 Digimon profile records directly from Japanese.", "blocks": blocks}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "translations/review_batch45.json").write_text(json.dumps({"batch": 45, "translated_slots": len(blocks), "groups": review}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Batch 45 review", "", "Batch 45 translates the third 100 profile records from MESPAK03 entry 2. Japanese ROM strings remain the primary source; English proper nouns and terminology follow established Western usage where identifiable.", "", "| ID | Japanese | English |", "|---|---|---|"]
    for row in review:
        jp = row["japanese"].replace("<0A>", "<br>").replace("|", "\\|")
        en = row["english"].replace("\n", "<br>").replace("|", "\\|")
        lines.append(f"| `{row['id']}` | {jp} | {en} |")
    (ROOT / "translations/review_batch45.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"batch": 45, "translated_slots": len(blocks)}, ensure_ascii=False))

if __name__ == "__main__":
    main()
