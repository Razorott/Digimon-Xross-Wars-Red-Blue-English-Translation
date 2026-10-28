"""Translate remaining Digimon profile blurbs from MESPAK03 entry 3."""
from __future__ import annotations

import json
import textwrap

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

LOCAL = "Original Japanese ROM (local primary source)"
CARD_LIST = "https://world.digimoncard.com/cards/"
PROFILE = {
0: "A female demon Digimon cloaked in jet-black armor, feared as the Dark Goddess. Its mysterious beauty ensnares foes and leads them to their deaths.",
1: "Flaremon's Mega form surrounds itself with a fiery aura and awe-inspiring presence. It gathers power in the flame orb on its back and fires a scorching sun-shaped sphere: Sol Blaster.",
2: "Crescemon's Mega form has a mystical, moonlike aura that captivates anyone who sees it. It cuts foes with its weapon and uses the moon's power to create illusions. Its signature move is Crescent Harken.",
3: "A lotus-like fairy Digimon said to be a flower blooming in heaven. Quiet and refined, it brings happy dreams, but punishes anyone who defies its will.",
4: "Argomon's Mega form has amplified combat abilities and a gigantic body. It fires a destructive beam from the eye-like parts of its body, powerful enough to distort space.",
5: "A courageous female warrior Digimon reminiscent of the Amazons of Greek myth. Called the Snake Princess, it wears snakeskin and can easily wield the greatsword Olympia, as tall as Minervamon.",
6: "One of the 13 Royal Knights, a brilliant strategist and commander who is also a master swordsman. It can transform into a beast form called Leopard Mode.",
7: "A jungle-dwelling dinosaur Digimon. The blades on its back provide both strong defense and offense, badly wounding anyone who attacks it.",
8: "An Olympus Twelve Digimon said to be the fastest in the Digital World. It moves too quickly to see with the naked eye; every recorded image is only an afterimage.",
9: "A dragon-man Digimon from a Greymon subspecies, discovered in an Eastern computer. Much about its power remains unknown. Its sword Kikurin is said to cut anything it touches.",
10: "A beast Digimon considered the king of vampire Digimon. Its voice can bewitch others and has even caused many angel Digimon to fall. It is said to be immortal.",
11: "An Ancient Digimon with the attribute of wind, one of the legendary Ten Warriors who saved the ancient Digital World. It was the first Mega in ancient times, with golden wings and a radiant form.",
12: "An Ancient Digimon with the attribute of light, one of the legendary Ten Warriors who saved the ancient Digital World. It was the first Mega in ancient times and was called the radiant beast of supreme wisdom.",
13: "An Ancient Digimon with the attribute of ice, one of the legendary Ten Warriors who saved the ancient Digital World. As the first ancient Mega, it was strong and brave enough to survive the coldest frozen lands.",
14: "An Ancient Digimon with the attribute of fire, one of the legendary Ten Warriors who saved the ancient Digital World. It was the first ancient Mega, said to surpass even today's Mega Digimon.",
15: "An Ancient Digimon with the attribute of water, one of the legendary Ten Warriors who saved the ancient Digital World. As the first ancient Mega, it ruled the Net Ocean and controlled sea dragons, tsunamis, and all water.",
16: "An Ancient Digimon with the attribute of steel, one of the legendary Ten Warriors who saved the ancient Digital World. As the first ancient Mega, it is said to know everything there is to know.",
17: "An Ancient Digimon with the attribute of darkness, one of the legendary Ten Warriors who saved the ancient Digital World. As the first ancient Mega, it governs destruction and extinction, born from darkness.",
18: "An Ancient Digimon with the attribute of wood, one of the legendary Ten Warriors who saved the ancient Digital World. It is the largest of the Ancient Digimon and has many hidden mechanisms inside its body.",
19: "An Ancient Digimon with the attribute of thunder, one of the legendary Ten Warriors who saved the ancient Digital World. This first ancient Mega resembles a fusion of many insects, including beetles and stag beetles.",
20: "An Ancient Digimon with the attribute of earth, one of the legendary Ten Warriors who saved the ancient Digital World. It was the first ancient Mega and is said to have the greatest power of all the Ancient Digimon.",
21: "A legendary Holy Knight Digimon appearing only in an ancient prophecy. Weapons and a shield unfold from the V-Bracelets on its arms.",
22: "The most courteous of the Royal Knights. It insists on one-on-one battles, and the stronger its opponent, the more it savors the fight.",
23: "A Demon Lord Digimon in the form of an old man with a long beard. One of the Seven Great Demon Lords, it is obsessed with every treasure in the network and will kill to possess it.",
24: "A cyborg Digimon guarding the mysterious Royal Base. It has incredible stamina and never stops moving during battle.",
25: "A Holy Knight and Royal Knight with the power of a flying dragon. Its mighty strength and high-purity Chrome Digizoid dragon armor make it nearly invincible.",
26: "A Holy Knight Digimon and Royal Knight. It can be cold when carrying out its mission and shows no mercy to the weak.",
27: "A Holy Dragon Knight and Royal Knight with so much data that older digital devices cannot even render it.",
28: "An ice Digimon that inherited the powers of all Ten Warriors and surpassed their legend. It flaps the ice masses Kaki-Kaki-kun and Kochi-Kochi-kun to briefly take flight.",
29: "A Royal Knight born from the fusion of WarGreymon and MetalGarurumon. It combines both Digimon's traits and can use its abilities in any situation.",
30: "Imperialdramon Dragon Mode's humanoid mode change, which lets it control its full power more easily. This ancient dragon-man Digimon equips a Positron Laser on its right arm.",
31: "Imperialdramon Fighter Mode's final form, powered up with Omnimon's strength. It is said to have saved the ancient Digital World from great destruction and carries the ultimate sword, Omega Blade.",
32: "A Holy Knight Digimon with the Digital Hazard sealed in its DigiCore. It has ten pure-white wings and crimson armor, and wields the sacred lance Gungnir and sword Blutgang.",
33: "A gigantic special Digimon filled with malice, born from a huge Digi-Egg formed by countless Kuramon, the Rookie form of Diaboromon.",
34: "A high-level Demon Lord born by controlling overflowing power with an evil heart. This is Vamdemon's final form, which retained its intelligence while surpassing VenomVamdemon.",
35: "A dark being born from the negative feelings of humans and Digimon. Said to bring great destruction, it controls endless darkness and reshapes its many tentacles to use the power it gathers.",
36: "A wicked god Digimon said to be the resurrected form of defeated Millenniumon, reborn with a dark soul. It is the final form of the Millenniumon line and wields immense dark power.",
37: "Dukemon's other form, awakened to its Virus instincts. Its heart is wholly consumed by darkness, making it the Digital Hazard itself. It wears demonic Chrome Digizoid armor and wields the spear Balmung and shield Gorgon.",
38: "A legendary Digimon born after uniting all the Spirits. Worshipped as a god of war, it governs life and death and is said to wield power that shakes heaven and earth.",
39: "A spirit Digimon born from the darkness within Millenniumon's mind. It has no fixed shape and may change form with its anger or hatred. It can directly attack an enemy's mind.",
40: "A legendary bird Digimon living in the stratosphere, 40,000 meters above the ground. Its six huge wings span 30 meters. It is said to be an ancient species from the dawn of the Digital World.",
41: "ShineGreymon's Burst Mode, a special form that briefly releases its full potential and surrounds it with a high-energy flame aura as powerful as the sun.",
42: "ShineGreymon Ruin Mode, driven berserk by dark power during Burst Evolution. It fires the darkness surrounding its body from its fingertips in indiscriminate attacks. Its signature move is Trid Vice.",
43: "MirageGaogamon's Burst Mode, a special form that briefly releases its full potential. It wields a planetary-scale high-energy weapon and is wrapped in an aura with energy comparable to a planet.",
44: "Ravemon's Burst Mode, a special form that briefly releases its full potential and surrounds it with all the energy it stores while airborne.",
45: "Rosemon's Burst Mode, a special form that briefly releases its full potential and surrounds it with an aura of love and beauty.",
46: "A Digimon born in an incomplete state with two DigiCores, one from each of the Digimon before its Jogress. The Digital World treats it as a bug. Chaosmon is a codename for a Digimon that should not exist.",
47: "One of the Four Great Holy Beasts who protect the Digital World. It guards the east and unleashes powerful thunder. Like the others, it is a legendary being.",
48: "One of the Four Great Holy Beasts who protect the Digital World. It guards the west and has the attribute of steel. Like the others, it is a legendary being.",
49: "One of the Four Great Holy Beasts who protect the Digital World. It guards the south and controls blazing fire. Like the others, it is a legendary being.",
50: "One of the Four Great Holy Beasts who protect the Digital World. It guards the north and controls water in countless forms. Like the others, it is a legendary being.",
51: "A variant born when Plesiomon fused with Seadramon data. Its shining form, clad in golden armor, is said to drive away all evil.",
52: "Chaosdramon is an improved, stronger version of Mugendramon with a crimson metal body. The program installed in its DigiCore has also been enhanced to be even more destructive.",
53: "A Digimon with an extremely aggressive nature. Its passion fuels its attacks, and it will never give up while that passion burns, even if its body is damaged. That is why Shoutmon is known for its fighting spirit.",
54: "A heavy-class Digimon with metal armor and overwhelming strength. It prefers peace, but becomes a powerful warrior who sweeps foes aside with its mighty arms when battle begins.",
55: "A beast Digimon that often acts alone. The drill on its head is hardened hair; spun at high speed and fired as Drill Buster, it boasts perfect accuracy.",
56: "A Digimon specialized for aerial combat. It is highly maneuverable and can make sharp turns with ease. Its flight style changes with its mood, making its condition easy to read.",
57: "A cheerful show-off with an extremely positive outlook. It rarely feels down, so other Digimon may take it lightly, but it does not care at all.",
58: "Dorulumon's Artillery Mode condenses all its energy into a maximum-power finishing attack. Another Digimon must help aim it, so this mighty shot depends on trust between partners.",
59: "Ballistamon's Reinforced Armor Mode houses one other Digimon, multiplying its strength and defense. Their latent abilities combine to produce several powerful finishing moves.",
60: "The sword-fusion form of Starmon and Pickmon. Its saw-like blade grinds through foes, leaving ragged wounds that take a long time to heal.",
61: "Sparrowmon's Supersonic Cruise Mode has incredible thrust and can carry other Digimon. Most are blown away by its wind speed unless they have exceptional resolve.",
62: "A miraculous Victory Mode born from four Digimon's determination to win. Its power is tremendous, making it unquestionably one of the strongest Digimon.",
63: "A Tyrannosaurus-type dinosaur Digimon focused on offense. It has a fierce fighting instinct and will not stop until its enemy is annihilated. Its aura is so intimidating that ordinary Digimon cannot approach.",
64: "A bird-of-prey Digimon skilled at scouting from high above and delivering precise support attacks. Cool-headed and calculating, it has excellent judgment.",
65: "Tactical Upgrade Mode combines Greymon's power with MailBirdramon's armor, boosting Greymon's combat ability without diminishing its strength.",
66: "DeadlyAxemon's older brother, a knight skilled in underhanded schemes who values victory above all. He will use any dirty trick to achieve it.",
67: "SkullKnightmon's younger brother, a mighty warrior with quick movement and endless stamina. He follows SkullKnightmon loyally and fights with faith in his brother. At top speed, he is as fast as lightning, leaving afterimages.",
68: "DarkKnightmon is the fusion of SkullKnightmon and DeadlyAxemon. The elder brother's cunning and the younger's physical prowess unite in an elite warrior who will use dirty tricks to achieve its goal.",
69: "A lively, mischievous fairy Digimon that lives in cold regions. It can heal wounds and may secretly approach an injured Digimon to help.",
70: "A Pickmon that serves as a key member of the Starmon army. It left its group to prove itself, and can become a Starmon after making its major-league debut.",
71: "A ninja Digimon found everywhere, always watching someone for fun. If you spot one, assume there are 30. Through information sharing, anything a Monitamon sees spreads faster than light.",
72: "A festival-loving Digimon that appears from nowhere when trouble starts and gets everyone moving to a hot rhythm. Its beat can rile listeners up; if it appears during a fight, a huge brawl may erupt.",
73: "A short-tempered Digimon that snaps over little things. The angrier it gets, the shorter its topknot becomes; when it disappears into its head, its rage explodes. The blast is only as strong as a firecracker, so it is often a party act.",
74: "A solitary warrior with terrible destructive power. Though quiet and indifferent to others, it loves fighting more than anyone. Few but fools would challenge Beelzemon.",
75: "A powered-up Finalist Mode born when five Digimon join hearts. Victory Mode excels on the ground; this form gains flight and becomes even stronger.",
76: "Beelzemon grants even more power to Victory Mode, creating a new form. Every technique's power rises several times over.",
77: "A warrior born from three Digimon's fighting spirit in Physical Mode. It is agile and acrobatic, outmaneuvering foes; its flexible joints also resist impact attacks.",
78: "One of the last Weapon Digimon, said to save the world in an angel's hands and destroy it in a demon's. It is earnest and hardworking but overthinks, struggles under pressure and improvisation, and loves sweets.",
79: "A fierce, aggressive small dragon Digimon often seen at night. It sings lullabies in a rock style and reportedly performs nightly for Digimon who cannot sleep.",
80: "A Tyrannosaurus-type dinosaur Digimon focused on offense. Its fierce fighting instinct keeps it battling until every foe is defeated. Its striking color shows its absolute confidence in battle.",
81: "DeadlyAxemon's older brother, a knight skilled in underhanded schemes who values victory above all. Its blood-red body bears witness to thousands of battles won.",
82: "A berserk warrior whose intelligence has been lost and fighting instinct heightened. Once a lion-like Digimon, it was repeatedly modified; its sharp claws carry a deadly poison that corrodes anything.",
83: "A warrior Digimon wielding the sword Jatetsufujinmaru. Its true strength lies not in brute force but in strategy. Victory is assured when Tactimon leads the army.",
84: "A heavyweight mineral Digimon with a crystal armor that regenerates when broken and powerful attacks. Its shining body and strength make it call itself the most beautiful and noble being.",
85: "A female Demon Lord Digimon whose mysterious beauty bewitches others. When leading an army, it ruthlessly cuts down any subordinate who fails.",
86: "A Digimon born when Greymon and MailBirdramon join the Physical Mode of three Digimon. It excels at high-speed aerial combat, and its blazing form can be felt from miles away.",
87: "A Digimon born when SkullKnightmon and DeadlyAxemon join the Physical Mode of three Digimon. It swings a gigantic Victory Spear and ruthlessly sweeps foes aside, feared as the Halberd God of War.",
88: "Armed Warrior Mode adds Weapon Digimon Spadamon as a powerful weapon to the four-Digimon Victory Mode. It wields two weapons freely, charging through battle to seize victory.",
89: "A Digimon born from Greymon, MailBirdramon, SkullKnightmon, and DeadlyAxemon. It wields a gigantic Drill Lance and carries two enormous cannons, overwhelming every Digimon with its size.",
90: "A small Digimon that barks loudly and is quick to run away. It is built for running on land and hates water, unable to swim; sometimes it is found unconscious after falling into a puddle.",
91: "Space Warrior Mode adds Weapon Digimon Spadamon to five-Digimon Finalist Mode, granting even more power. It can fly into space and absorb cosmic energy directly.",
92: "An artificial Digimon made by packing other Digimon's energy into a special rubber body. It acts like a machine, only following orders and never acting on its own.",
93: "A Digimon that hides underwater or among rocks and rarely moves. It will not attack unless approached, but reproduces abnormally when the temperature exceeds 30 degrees.",
94: "A knight Digimon fully clad in Chrome Digizoid armor. It moves so fast it appears like a mirage to its opponents and can use many different techniques.",
95: "A huge cyborg Digimon fitted with beam cannons across its body, sacrificing the strength of its metal shell. Its powerful weapons make 'the best defense is a good offense' an apt description.",
96: "A stealthy ninja Digimon once called the Silver Crow, serving another Digimon at the dawn of the Digital World. Legend says the gods' anger turned one of its wings black.",
97: "The strongest Chessmon, with extreme range and attack power. It is a reliable protector for the timid KingChessmon.",
98: "The king Chessmon scheming to build a Chessmon Empire. No other Chessmon knows what that empire would be, and no one around him is interested. He is timid and runs very fast.",
99: "A legendary Digimon born with Chrono Data through the YMIR Project. It can enter Holy Mode only when it undergoes super evolution with sacred light.",
}

def fit(s: str) -> str:
    return "\n".join(textwrap.wrap(s, width=15, break_long_words=True, break_on_hyphens=False))

def main() -> None:
    records = collect_messages(Rom(rom_paths()["blue"]))
    done = translate_records(records)
    blocks, review = [], []
    for index, raw in PROFILE.items():
        key = f"MSG/MESPAK03.PAK:003:{index:05d}"
        row = records.get(key)
        if not row or not row["source"].strip() or key in done:
            continue
        english = fit(raw)
        note = "Translated from the original Japanese profile. Official Digimon names and franchise terminology use established Western usage where identifiable; see the linked English card list for nomenclature reference."
        blocks.append({"archive": row["archive"], "entry": 3, "start": index,
                       "category": "Digimon profiles", "english": [english],
                       "sources": [CARD_LIST], "review_note": note})
        review.append({"id": key, "japanese": row["source"], "english": english,
                       "evidence_url": LOCAL, "terminology_reference": CARD_LIST,
                       "review_note": note})
    if len(blocks) != 94:
        raise ValueError(f"Expected 94 remaining profiles, authored {len(blocks)}")
    path = ROOT / "translations/batch46.json"
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps({"description": "Translate the remaining Digimon profile records directly from Japanese.", "blocks": blocks}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "translations/review_batch46.json").write_text(json.dumps({"batch": 46, "translated_slots": len(blocks), "groups": review}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Batch 46 review", "", "Batch 46 translates the remaining 94 profile records from MESPAK03 entry 3. Japanese ROM strings remain the primary source; established Western names and terms are used where identifiable.", "", "| ID | Japanese | English |", "|---|---|---|"]
    for row in review:
        jp = row["japanese"].replace("<0A>", "<br>").replace("|", "\\|")
        en = row["english"].replace("\n", "<br>").replace("|", "\\|")
        lines.append(f"| `{row['id']}` | {jp} | {en} |")
    (ROOT / "translations/review_batch46.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"batch": 46, "translated_slots": len(blocks)}, ensure_ascii=False))

if __name__ == "__main__":
    main()
