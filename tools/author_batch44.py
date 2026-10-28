"""Translate the next 100 Digimon profile blurbs."""
from __future__ import annotations

import json
import textwrap

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

LOCAL = "Original Japanese ROM (local primary source)"
CARD_LIST = "https://world.digimoncard.com/cards/"
PROFILE: dict[int, str] = {
    0: "A mole-like Digimon\nthat lives deep\nunderground. It digs\nthrough the earth at\nhigh speed with the\nhuge drill on its\nnose. Usually gentle,\nit can be mischievous\nand sometimes steals\nthe bones Garurumon\nhid underground.",
    1: "A ferocious beast\nDigimon covered in\ndark-brown fur. It can\nmanipulate time and\nspace, warp through\nother dimensions, and\ncreate special spaces.\nIt can also unleash\na shock wave powerful\nenough to shatter rock.",
    2: "A mutant Digimon\nmade of earth that\nlooks much like\nFrigimon. It seems\nheavy, but can move\nwith surprising speed.",
    3: "It looks like a\nlobster, but is really\nan aquatic dragon\nDigimon. It has a hard\nshell and huge claws.\nFierce by nature, it\nis dangerous to\napproach. It lives in\nthe deep Net Ocean.",
    4: "An octopus Digimon\nthat gathers anything\nlying in the Net Ocean\nand wears it. The claws\non its hands came from\nDevimon data. A Shellmon\nlives in the pot on its\nhead and warns it of\ndanger.",
    5: "A squid Digimon\nthat looks vicious,\nbut is intelligent and\navoids pointless\nfights. Enter its\nterritory without leave,\nthough, and it attacks\nin a rage. It spits\npoisonous ink that\nparalyzes the whole\nbody.",
    6: "A Digimon whose\nbody structure recalls\nan ancient fish. Its\nfins developed like\nlimbs, and its hard\nhead gives it strong\noffense and defense.\nIt is said to be an\nancestor of many\nDigimon.",
    7: "An aquatic Digimon\nthat resembles a hermit\ncrab. Its shell is hard,\nbut its body is soft.\nIt settles in anything\nit can fit inside, then\nchanges homes as it\ngrows. Some Shellmon\ngrow as large as\na small mountain.",
    8: "An ice Digimon\nwhose body is made of\nsnow and ice crystals.\nThough cold to the\ntouch, it has a warm\nheart. It avoids\nfighting and lives\npeacefully at its\nown pace.",
    9: "A fallen-angel\nDigimon with a cold\nbody and heart. It\nshows no mercy or\nemotion, and attacks\nin ways that make its\nfoes suffer. It uses\nmany ice techniques.",
    10: "A dolphin-like\naquatic mammal\nDigimon, apparently\nborn from software\nthat studies language.\nVery intelligent, it\ndislikes fighting but\nshows no restraint\nwhen attacked.",
    11: "A plant Digimon\nthat resembles a dead\ntree. Fierce and\nviolent, it disguises\nitself as an ordinary\ntree and attacks\nDigimon passing by.\nIts thick trunk gives\nit excellent defense,\nbut it keeps its\ndistance from fire\nDigimon.",
    12: "An insect Digimon\nthat looks like a\npraying mantis. It is\nsaid to have been\ncreated in a lab to\neliminate Virus\nDigimon. Cold and\nprecise, it finishes\nits target with the\nsharp scythes on\nboth arms.",
    13: "A bee-like insect\nDigimon that flies at\nextreme speed. The\nsound of its wings is\nso powerful it can\nparalyze the sense of\nhearing. Its poisonous\nstinger is dangerous,\nbut can regenerate\nagain and again.",
    14: "A dragonfly-like\ninsect Digimon that\nflies through the\nnetwork and dives at\nfoes with its sharp\nfangs. It can also\nfire lightning from\nits tail.",
    15: "A Digimon dressed\nlike a ninja, known\nfor its red mask. It\nuses the ninjutsu of\nthe Iga school. It\nhides in forests and\nwater, traveling\nquietly from place\nto place as it trains.",
    16: "A machine Digimon\nmarked by a huge\nclock. It manages\nspace-time in the\nnetwork and can freely\ncontrol time. Neutral\nby nature, it shows\nno mercy to anyone\nwho attacks it.",
    17: "A mutant Digimon\nthought to be related\nto Mamemon. Its body\nis a magnet that\nconstantly emits\nelectricity. Small as\nit is, it fights back\nwith shocks, punches,\nand kicks when\nattacked.",
    18: "A tank-like Digimon\nthat loves conflict\nand sides with any\nfaction that benefits\nit. It has terrifying\npower and sprays foes\nwith weapons mounted\nall over its body.",
    19: "A mineral Digimon\nwhose body is 90%\nrock. Its limbs hold\nit together and keep\nit alive, but it cannot\nmove unless ordered.\nThis clay doll has an\nancient spell carved\ninto its back.",
    20: "A mutant Digimon\nshaped like a gun\nbarrel and dressed\nas a gunslinger. Its\nstrong sense of justice\nboils over when it\nsees evil. It loves\ngambling, though, and\nmay let a villain go\nif it wins at Russian\nroulette.",
    21: "A Digimon with a\nstarfish-like upper\nbody and beast-like\nlegs. Its trained right\narm is fused with a\nweapon. The blue\nsubstance on its body\nworks as armor, and\na fan on its back lets\nit move at incredible\nspeed.",
    22: "A wicked dragon\nDigimon summoned to\nthe Dark Area by\nDevimon. It flies\nthrough darkness on\neerie wings. In battle,\nit glares with red eyes\nto freeze its foe, then\nrips it apart with\nblade-like claws.",
    23: "A spider-like insect\nDigimon whose whole\nbody is infected by\na computer virus. It\ncorrupts anything it\ntouches. Once it picks\na target, its eight\nlegs let it catch up\nand kill even a foe\nthat runs at full speed.",
    24: "A phantom original\ndragon Digimon that\nis rarely seen. Though\nit is a dragon, people\nsometimes mistake it\nfor a dog. It has a\nV-shaped mark on its\nchest and immense\npower; in a crisis,\nit may reach Ultimate\nand beyond.",
    25: "A demon-like\nDigimon resembling\na foreign-game virus\ninfected samurai. Its\narmor is battered from\nsurviving endless\nbattles. Its beloved\nsword, Shiratamaru,\nhas a spell that\ndrains its foe's life.",
    26: "A white puppet\nDigimon shaped like\na horse and carrying\na huge dart. It avoids\nclose combat, relying\non the strength of a\nthoroughbred and\nleaping past foes to\nconfuse them.",
    27: "A Digimon that\nevolved from Coronamon.\nIt moves on four legs\nwith a beast's strength\nand agility. It flies\nwith the wings on its\nback, then charges\nfoes while wreathed in\nflame. Its special\nmove is Flame Dive.",
    28: "A Digimon that\nevolved from Lunamon.\nIt can leap to great\nheights and darts\nabout nimbly. It throws\nsleep-inducing bubbles\nmade by its Moon\nGloves. Its special\nmove is Moon Night\nBomb.",
    29: "A command dragon\nthat aims to become\na Virus Buster. It\nwears metal plates in\nCommander Mode. Kind\nat heart, it fights\nVirus Digimon until\nthe enemy is reduced\nto dust.",
    30: "A Digimon that\nevolved from Hyokomon.\nIt became a rogue while\nfollowing the way of\nthe sword, and now\nworks as a bodyguard.\nIt takes any job for\npayment, but still has\na kind side toward\nthe weak.",
    31: "A fire Digimon\nthat carries the power\nof the Legendary Ten\nWarriors. Its Digicore\nis wrapped in holy\nflames called Spiritual\nFire, letting it control\nfire at will. It is an\nincarnation and guardian\ngod of the Firewall.",
    32: "A powerful, bulky\ncyborg Digimon and\na worthy rival to\nEtemon. When furious\nor pushed past MAX\nenergy, the volcano\non its back erupts.\nIt excels at deep-\nvoiced microphone\nperformances.",
    33: "A cyborg Digimon\nevolved from Greymon,\nwith over half its body\nmechanized. Its attack\npower is said to equal\na nuclear blast. It\nlaunches courage-type\nmissiles from the hatch\non its chest.",
    34: "A very lovely\npuppet Digimon that\nlooks like a giant\nteddy bear. A zipper\non its back has led to\nrumors that someone\nis inside. Its Lovely\nAttack makes foes feel\nso happy that they\nlose their fighting\nspirit.",
    35: "An undead Digimon\nthat kept living even\nafter its body rotted\nfrom being consumed\nby battle. Now only\nbones remain. It has\nlost its emotions and\nknows only how to\nfight, so other\nDigimon fear it.",
    36: "A cyborg Digimon\nthat evolved into a\nstronger form of\nMamemon. It is about\nthe same size, but\nlooks can be deceiving: \n90% of its body is\nmechanical, including\na powerful Psycho\nBlaster gun in its\nleft arm.",
    37: "A humanoid cyborg\nDigimon built as an\nexperiment to complete\ncyborg Digimon. Every\naction is programmed.\nIt can defeat a Digimon\nbelow Ultimate level\nwith one blow.",
    38: "A mysterious puppet\nDigimon that calls\nitself the \"King of\nDigimon.\" It wears a\nreinforced monkey suit\nthat withstands any\nattack and travels the\nworld to battle. Some\nsay it secretly\ncontrols Monzaemon.",
    39: "A cyborg Digimon\nmodified by humans.\nIt contains a terrifying\nprogram that can\ndestroy anything, yet\nhas powerful security\nmeasures. It can even\nenter protected\ncomputer networks and\nfire missiles from\nboth arms.",
    40: "A tiny fairy\nDigimon that casts\nspells by chanting in\na language from another\ndimension. It seals\nfoes' abilities, then\nknocks them out with\na mighty blow. It loves\npranks and can make\ncomputers go haywire\nwith its wand, Fairy\nTale.",
    41: "A Perfect-level\nDigimon shaped like\na Digi-Egg, said to\nbe the beginning and\nend of all Digimon.\nIts shell is as hard\nas an eggshell and\nit can unleash attacks\nso powerful its foes\nmay never stand again.",
    42: "An ancient giant\nDigimon that looks\nlike a mammoth. It has\namazing power but\nis weak to heat. The\nemblem on its face\nholds ancient wisdom,\ngiving it far-sight\nand extraordinary\nhearing.",
    43: "An evolved form of\nKuwagamon with stronger\ndefenses. Aggressive\nand driven to destroy,\nit can track foes with\nits antennae. Its claws\nare even better at\ncutting through\nanything.",
    44: "An amphibian\nDigimon evolved from\nGekomon, with a\ntopknot-like feeler.\nIt is rumored to have\nbeen born from karaoke\nscoring software. It\nplays melodies on the\nhorns from its shoulders\nand sings in a deep,\ncommanding voice.",
    45: "A beautiful, female\nArchangel Digimon.\nUsually gentle, it\nnever forgives evil\nor injustice and keeps\nattacking until its foe\nrepents. Its spirit\nand power have earned\nit worship as a goddess\nof the Digital World.",
    46: "A Digimon that\nTailmon Armor\nDigivolved into with\nthe Digi-Egg of\nSincerity. It moves\nthrough water like a\njet and can smell\nunderwater scents from\na kilometer away,\nletting it chase prey\nwithout end.",
    47: "An ancient\ncrustacean Digimon\nborn when a computer\nvirus infected a lab's\ndata bank. It catches\nfoes with its head\ntentacles and attacks\nwith the blade on its\ntail. In a pinch, it\nhides and uses its\nradar eye to strike\nback.",
    48: "An aquatic Digimon\nthat evolved from\nSeadramon to survive\nharsh environments.\nA lightning-shaped\nblade grows from its\nhead, its shell is\nharder, and its body\nis larger. It tracks\nfoes like a torpedo\nand finishes them off.",
    49: "An aquatic beast-\nman Digimon evolved\nfrom a virus that\ninfected a ship's\ncomputer and scrambled\nits navigation. Its\ntentacles form a\nhumanoid shape, but\nits true form is said\nto be hideous. It is\ncalled the \"Sea's\nDestroying Weed.\"",
    50: "A Digimon that\nevolved from Garurumon\nand can now walk on\ntwo legs. It has\nexcellent all-around\ncombat ability, a\nstrong sense of justice,\nand always follows\nthe right path and\nits master's orders.",
    51: "The king of undead\nDigimon, revived by\ndark magic. It can\nrestore data destroyed\nby computer viruses\nwith evil viruses. Very\ncunning and hard to\nbanish, it is said to\nlose power in daylight.",
    52: "A high-ranking\nfemale fallen-angel\nDigimon. Its powerful\ndark energy makes it\nrare outside of\nindividual computers\nwhere it is raised.\nIt uses terrifying\nattacks that incinerate\nits foes.",
    53: "A heroic Digimon\nthat loves justice\nand nature, protecting\nthe earth and wind.\nWhen the Digital\nWorld's order is lost,\nit appears from nowhere\nto guide things back\nto the right path. It\nis a close friend of\nLeomon and shares\nhis ideals.",
    54: "A plant Digimon\nshaped like a giant\nflower, with many\ntentacles growing from\nits body. Quiet and\ngentle, it lives out\nof sight near water.\nEach season, its petals\nfall and new ones\ngrow.",
    55: "A fairy Digimon\nborn from a flower.\nA refreshing breeze\nis said to blow when\nit flies. Capricious\nand lively, it is kind\nto the small and weak,\nand opens its heart\nto girls of a similar\ntemperament.",
    56: "An insect Digimon\nfrom a MegaKabuterimon\nsubspecies discovered\nin a tropical network\narea. It seems to fly\nbetter than Blue\nMegaKabuterimon.\nHard to read, it has\nbeen seen protecting\nthe weak like a knight.",
    57: "A tiny machine\nDigimon developed for\nmedical treatment. It\nwas originally built\nto repair broken\ncomputers, but a virus\nattack damaged its\nlogic circuits. Now it\ncauses healthy systems\nto malfunction.",
    58: "A dragon-humanoid\ncyborg Digimon wearing\narmor made of special\nrubber. The armor\nprovides excellent\ndefense and increases\nits attack power. It\nappears to eliminate\nVirus Digimon from\ncomputer networks.",
    59: "An Archangel\nDigimon who oversees\nmany angel Digimon.\nUsually a priest, it\nchanges to Battle Mode\nwhen darkness appears\nand fights evil with\nthe holy sword\nExcalibur. It has\neight shining silver\nwings.",
    60: "A dragon-humanoid\nDigimon formed when\nXV-mon and Stingmon\nJogress-Digivolved.\nA dragon-insect hybrid,\nit has more dragon\ntraits. It carries a\ndragon's power and\nan insect's shell, and\nfights to the death\nto protect its master.",
    61: "A mutant Digimon\nformed when Stingmon\nand XV-mon Jogress-\nDigivolved. This\ndragon-insect hybrid\nhas stronger insect\ntraits. It flies swiftly\non four wings and\ntracks foes precisely\nwith its compound eyes.",
    62: "A holy beast\nDigimon shaped like\nthe rabbit from an\nEastern legend. It\ncontrols the \"qi\"\nflowing through its\nbody, letting it move\nwith grace or unleash\na powerful strike.",
    63: "A cunning beast\nDigimon shaped like\nthe \"Spider Queen\"\nof Greek myth. It\ncommands all Dokugumon\nand is skilled at\ntransforming into a\nhuman. Get too close\nand you'll become\nits prey in an instant.",
    64: "An undead Digimon\nwrapped like a mummy.\nIt is called a\n\"Necromancer\" because\nit summons and controls\nDigimon spirits. When\ncornered, it fires its\nbeloved gun, Obelisk,\nin every direction.",
    65: "A crimson, Virus\ncyborg Digimon called\n\"Giant Growlmon.\" Its\nupper body is covered\nin Chrome Digizoid.\nThrusters on both\nshoulders let it fly,\nand it can attack\ntargets in the air\nor on the ground.",
    66: "A cyborg Digimon\nevolved from Gargomon,\ncalled the \"Swift\nHound.\" It defeats\nfoes with near-sonic\nspeed. Its large ear\nradar detects distant\ntargets, and its\nmissiles home in.",
    67: "A wizard Digimon\nevolved from Kyubimon.\nIt masters Onmyodo\nand uses many spells\nand weapons. Living\nin darkness, it excels\nat sorcery, talisman\nattacks, and hiding\nweapons in its long\nsleeves.",
    68: "A giant parrot\nDigimon that wandered\nthrough a rift in\nspace-time into the\nDigital World. When it\nspots an enemy, it\nattacks with its feet\nand can also call\ndown lightning.",
    69: "A spider-like\nDigimon that can enter\nany computer network.\nIt has a normal form\nwith its head and limbs\nextended, and a cocoon\nform that folds its\nlimbs into its body\nfor defense. In its\ncocoon, it can only\nmove straight ahead.",
    70: "A rare panda\npuppet Digimon. Blunt\nand not very cute, it\nthinks of itself as a\nlone wolf, but secretly\nenvies the popular\nMonzaemon. It is\nsurprisingly skilled\nin battle.",
    71: "A deep-sea Digimon\nrelated to Devimon.\nLiving alone in the\nabyss, it lost every\nemotion but hatred.\nIt keeps attacking\neven when its foe\nloses the will to fight.\nEach tentacle on its\nback seems to have\na will of its own.",
    72: "A wizard Digimon\nthat trains in the\nmountains, shaped like\nthe tengu of Japanese\nfolklore. It studies\nShugendo and freely\nuses mysterious powers.\nIts two swords, the\nIrataka Swords, hold\na powerful curse.",
    73: "A fox-like Digimon\nwith sharp blades all\nover its body. It\nslices anything nearby\nwithout distinction.\nSo fast that when a\nwhirlwind appears,\nits foes are already\ncut to pieces.",
    74: "A sacred bird\nDigimon shaped like\na rooster. It wears\nimpenetrable steel\narmor and carries\nPaotzu, a mallet that\ncreates lightning. It\ncontrols electricity\nand may drain power\nfrom the area, causing\na blackout.",
    75: "A colossal beast\ndragon Digimon called\nthe \"Final Enemy,\"\nits hidden Digicore\ndata released. Its\noverwhelming size\ncrushes foes, and a\nsingle flap of its\nwings deflects attacks.",
    76: "An aquatic beast-\nman Digimon wearing\na wetsuit as it swims\nthrough the Net Ocean.\nCheerful and friendly,\nit is built for life\nunderwater and excels\nin aquatic combat. It\nattacks with its\nfavorite spear,\nTrent.",
    77: "A composite Digimon\nassembled from many\nothers, with fearsome\nfighting instincts and\ndestructive power. Its\nparts are organic. It\nis said to be a\nprototype for\nMachinedramon, or to\nhave been made to\nfight it.",
    78: "A two-legged,\nhorned dragon Digimon\nshaped like a\nTriceratops. Its skin\nand two long forehead\nhorns are extremely\nhard; the horns are\nsaid to be tougher\nthan Monochromon's.\nGentle, yet powerful.",
    79: "A beast-man Digimon\nformed when Aquilamon\nand Tailmon Jogress-\nDigivolved. It leaps\nhigh, spreads its arms\nlike a glider, and\nflies. Its ear radar\ntracks enemies and\ndisplays them on the\nhead-mounted screen.",
    80: "A mutant Digimon\nthat evolved from\nspace warrior Starmon.\nEven more self-satisfied,\nit wears flashy clothes\nand sunglasses and\nfights with confidence.\nIt can summon countless\nmeteorites.",
    81: "A Digimon evolved\nfrom Ikkakumon that\ncan walk on two legs.\nIts trained muscles\nare protected by hide\nand shell armor. It\nmodified its regrown\nhead horn into a saw\nand carries the ancient\nice-carved Thor Hammer.",
    82: "A whale Digimon\nliving deep in the Net\nOcean. It has so much\ndata that ordinary\ncomputers cannot\nprocess it. It can\ncreate enormous\ntsunamis.",
    83: "A tiny bean-like\nmutant Digimon. It\nsuddenly mutated while\nliving in harsh\nconditions, becoming\nfar smaller than an\nUltimate should be.\nYet its power is so\ngreat that other\nUltimates fear it.",
    84: "A mineral Digimon\nthat is the Ultimate\nform of Gotsumon,\nwearing mineral data.\nIt looks just like\nGotsumon, but its\npower is immeasurable.\nIt can wield immense\ncosmic energy.",
    85: "A cyborg Digimon\nrebuilt from Megadramon\ninto a complete combat\nweapon for aerial\ninterception. It fires\ncountless missiles in\na flash from both arms.\nIts special move is\nGenocide Gear.",
    86: "A cyborg Digimon\nwith more than half\nits body mechanized.\nDespite its huge frame,\nit can fly high into\nthe sky. It fires\npowerful shots from\nthe Chrome Digizoid\nrevolver in its left\narm.",
    87: "A cyborg Digimon\nwith a rocket engine\nstrapped to its back,\ngiving it tremendous\nthrust. It cannot stay\nairborne long, so it\nuses short bursts of\nmaximum power for\nhit-and-run attacks.",
    88: "A holy beast\nDigimon said to have\nbeen born at the dawn\nof the Digital World.\nLegends say its power\nas a Perfect equals\nan Ultimate. Peaceful\nand compassionate, it\nseverely punishes\nthose who start wars.",
    89: "A beautiful fairy\nDigimon resembling\nthe beloved lilac\nflower. Pure and\ninnocent, it is also\nsaid to govern\n\"life\" and \"death.\"",
    90: "A vampire dancer\nDigimon that performs\na graceful dance. It\nwas born from a folk\ndance database in a\nmuseum and perfected\nthe dance \"Bulldog.\"\nIts flowing costume\ndistracts foes before\nit cuts them with a\nrapier hidden in its\narm.",
    91: "A Digimon that\nTailmon Armor\nDigivolved into with\nthe Digi-Egg of\nPurity. Huge flowers\nbloom on its head and\nhands. It loves showy\nplaces and strikes a\npose even in battle.",
    92: "A plant Digimon\nevolved from Woodmon,\nwith great wisdom and\npower. Called the lord\nof the forest, it lures\nthose who wander in\ndeeper and traps them.\nIt releases hallucinatory\nfog and absorbs foes\nwith vines and\ntentacles.",
    93: "A mutant Digimon\nborn when a desktop\ntrash can came to life.\nThe can is like a\nblack hole: anything\nsucked inside vanishes\nfrom the Digital World.\nIt fires poop from a\nbazooka made of cans.",
    94: "The ultimate Demon\nLord Digimon, combining\nholy and evil. It is\nLucemon after its\nFall Down from an\nangelic form. It aims\nto destroy this world\nand create a new one.",
    95: "A small mutant\nDigimon shaped like\na dragon wearing a\nhelmet. Tiny but\naggressive, it attacks\nwithout hesitation\nanyone who enters its\nterritory. It is\nsometimes called the\n\"Little Tyrant.\"",
    96: "A machine Digimon\nthat patrols computer\nnetworks. Its job is\nto drive away Digimon\nthat force their way in.\nIt attacks intruders\nwith all its strength,\nand self-destructs to\ndefeat them when\ncornered.",
    97: "A mysterious\nDigimon with an alien-\nlike appearance. Some\nsay it was born from\na plant fruit. Its huge\nhead and octopus-like\nlower body hide\nterrifying attack\npower.",
    98: "A cyborg Digimon\nmodified for ground\nassault. Its reinforced\nbody repels any attack,\nand its powerful jaws\ncan crush anything. It\nfires missiles from its\nright arm and lasers\nfrom its left.",
    99: "A puppet Digimon\nhiding inside a cute\nTyranomon plush. It\nhas power and defense\nclose to Monzaemon's,\nbut like Monzaemon,\nit is only a doll\nwithout someone to\ncontrol it.",
}


def fit(value: str) -> str:
    return "\n".join("\n".join(textwrap.wrap(line, width=15,
        break_long_words=True, break_on_hyphens=False)) if line else ""
        for line in value.split("\n"))


def main() -> None:
    records = collect_messages(Rom(rom_paths()["blue"]))
    prior = translate_records(records)
    blocks, review = [], []
    for index, raw in PROFILE.items():
        key = f"MSG/MESPAK03.PAK:001:{index:05d}"
        if key in prior:
            raise ValueError(f"Already translated: {key}")
        row = records.get(key)
        if not row or not row["source"].strip():
            raise ValueError(f"Missing profile source: {key}")
        english = fit(raw)
        note = "Original Japanese profile translated directly; Western Digimon spellings and established terms are checked against linked English references where used."
        blocks.append({"archive": row["archive"], "entry": 1, "start": index,
            "category": "Digimon profiles", "english": [english],
            "sources": [CARD_LIST], "review_note": note})
        review.append({"id": key, "japanese": row["source"], "english": english,
            "evidence_url": LOCAL, "terminology_reference": CARD_LIST,
            "review_note": note})
    if len(blocks) != 100:
        raise ValueError(f"Expected 100 profiles, authored {len(blocks)}")
    path = ROOT / "translations/batch44.json"
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps({"description": "Translate the second 100 Digimon profile records directly from the original Japanese.", "blocks": blocks}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "translations/review_batch44.json").write_text(json.dumps({"batch": 44, "translated_slots": len(blocks), "groups": review}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Batch 44 review", "", "Batch 44 translates profile records 101-200. Digimon proper nouns and franchise terms use established English spellings where identifiable; every translation retains its source string and stable message ID. Lines are wrapped to the measured 15-character story line width.", "", "| ID | Japanese | English |", "|---|---|---|"]
    for row in review:
        jp = row["japanese"].replace("<0A>", "<br>").replace("|", "\\|")
        en = row["english"].replace("\n", "<br>").replace("|", "\\|")
        lines.append(f"| `{row['id']}` | {jp} | {en} |")
    (ROOT / "translations/review_batch44.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"batch": 44, "translated_slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
