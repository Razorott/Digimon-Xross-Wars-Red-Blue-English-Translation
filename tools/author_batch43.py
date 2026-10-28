"""Translate the first 100 Digimon Encyclopedia profile blurbs."""
from __future__ import annotations

import json
import textwrap

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

LOCAL = "Original Japanese ROM (local primary source)"
CARD_LIST = "https://world.digimoncard.com/cards/"
PROFILE: dict[int, str] = {
    0: "Dummy Data\n123456789012345678901234567\n123456789012345678901234567\n123456789012345678901234567\n123456789012345678901234567\n123456789012345678901234567",
    1: "Its fuzzy down fell\noff, and it grew a\nsize larger. Small,\nbut full of the spirit\nof a dragon!",
    2: "A mysterious Digimon\nthat suddenly appeared\non a computer network.\nIt is said to have been\nborn from a Digi-Egg\nfilled with humanity's\ndestructive instincts.\nIt multiplies like\nbacteria and ruins\nnetworks.",
    3: "A being called\nDigi-Entelecheia,\nwhich governs evolution,\nbecame a Digimon. It\nis said to help other\nDigimon evolve.",
    4: "A small Digimon\nthat loves to fight.\nIts motto is, \"Bring\non the fight!\" It\nfears no foe and\nfights with a powerful\nfist. Full of energy,\nit has a deep-purple\nbody and a dragon's\nform.",
    5: "A reptilian Digimon\nthat has grown to walk\non two legs. It faces\nany foe with its hard\nclaws and Baby Flame,\nwhich it spits from\nits mouth. A reliable\npartner in a fight.",
    6: "Descended from a\ntribe that flourished\nin the early Digital\nWorld. It may be able\nto Armor Digivolve\nusing a Digi-Egg. This\nenergetic dragon has\na pure, honest heart.",
    7: "A Rookie dragon\nDigimon with the\npotential to fight.\nThe mark on its belly\nis the Digital Hazard,\nplaced on data that\nmay threaten computer\nsystems. But if used\nfor peace, its power\ncan protect the world.",
    8: "It has an old-style\n\"Interface\" on its\nforehead, so it may be\na Prototype Digimon\nfrom before Digimon\nwere discovered. It\nloves to bite and has\na strong fighting\ninstinct, but grows\nfond of what it bites.\nIt may become mighty.",
    9: "A four-legged\namphibian Digimon.\nUsually gentle and\nquiet, but when angered\nit shocks everything\naround it without\ndiscrimination.",
    10: "It gathers data left\nby Garurumon and wears\nit as a pelt to protect\nitself. Shy by nature,\nit becomes bold while\nwearing the fur.",
    11: "A mammal Digimon\nwith huge, wing-shaped\nears. It can fly, but\nonly at 1 km per hour,\nso walking is faster.\nIt can Armor Digivolve\nwith a Digi-Egg.",
    12: "A chick Digimon\nwith wings developed\nlike arms. It lives on\nthe ground and flies\naway when danger comes.\nIt flies as slowly as\nPatamon, but dreams\nof soaring freely\nthrough the sky.",
    13: "A Digimon with a\ntropical flower growing\non its head. The flower's\nscent changes with its\nmood: sweet when happy,\nbut so pungent when\nangry that even large\nDigimon run away.",
    14: "A Digimon from which\ninsect Digimon descend.\nIt loves nature and\nlives at an easy pace.\nThough many insect\nDigimon are aggressive,\nthis one is gentle. It\nhas a hard shell and\nsharp claws.",
    15: "A mineral-type\nDigimon that wears\nmineral data as armor\nand has powerful\ndefenses. Its data\nchanges depending on\nwhere and how it forms.",
    16: "It swims by using\nits large tail as a\npropeller and lives\nunderwater. Its skin\nhas not fully hardened\nafter so long in the\nwater. Sometimes it\nclimbs onto rocks to\npractice walking.",
    17: "A seal-like Digimon\nthat can now live on\nland. Warm fur covers\nits body. Its coat grows\nlonger as it matures,\nand its color may turn\nfrom white to brown.",
    18: "A small, bat-like\nDigimon said to have\nled Devimon, once an\nangel, down the path\nof evil. It avoids the\nfront lines, but its\ncunning mind keeps it\ncausing trouble\neverywhere.",
    19: "Said to have been\ncreated by a child\ncopying Agumon while\nplaying online. It is\ntimid, but has a strong\nsense of justice and\ncan't ignore wrongdoing.\nIt loves chatting with\nchildren online. When\nstartled, its body\nblocks fall apart.",
    20: "A Digimon shaped\nlike a huge gear. More\ngears fill its body;\nif even one is missing,\nit stops moving. It can\nsend a computer virus\nto control the machine\nit infects.",
    21: "An experimental new\nDigimon created by a\nDigimon researcher.\nIt does not yet know\nits purpose, so how it\nis raised can lead it\ntoward good or evil.",
    22: "A timid, gentle\nlarval Digimon. It is\nweak and can't match\nlarger Digimon, but\nArmor Digivolution\nwith a Digi-Egg can\ngive it tremendous\npower.",
    23: "A bird Digimon\ndescended from an\nancient tribe. It can\nArmor Digivolve with\na Digi-Egg. Polite,\ncalm, and collected.",
    24: "A mammal Digimon\ncovered in a hard\nshell. It is descended\nfrom an ancient tribe\nand can Armor Digivolve\nwith a Digi-Egg.",
    25: "One of a pair of\ntwin Digimon, with a\nsingle horn on its head.\nBright and energetic,\nit hardly seems like\na fighter, but it can\nrelease tremendous\npower when battle\ncomes.",
    26: "One of a pair of\ntwin Digimon, with\nthree horns. A crybaby\nand the opposite of\ncheerful Terriermon,\nit is shy and lonely.\nLike its twin, it can\nshow its true strength\nwhen needed.",
    27: "A Digimon whose\ngrowth reflects its\nbond with its Tamer.\nCare from its early\nstages can help it\nbecome a particularly\nwise Renamon. It\nfavors speed over\nstrength in battle.",
    28: "A mischievous\nDigimon with a little\ndemon-like appearance.\nProud and unable to\nstand losing, it never\nflatters or follows the\nstrong. Deep down,\nit is very lonely.",
    29: "A Digimon that\nevolved from Tsumemon.\nIts huge mouth can\ndestroy over 100 MB\nof data in a second.\nWhen it enters a\ncomputer, it destroys\nall its data. It thinks\ndestroying data is fun.",
    30: "A bird Digimon\nwith a ninja-like form.\nIt uses its wings\nskillfully to move\nquickly and confuse\nits opponent.",
    31: "A bird Digimon\ndiscovered in a base\nin Antarctica. Its\nwings have atrophied,\nso it walks slowly,\nbut it swims skillfully\nwith its small wings.",
    32: "A mischievous little\ngoblin Digimon that\nnever picks a fight\nwith someone stronger.\nIt carefully tends its\nmohawk every day. Its\nspecial move is Gobli\nStrike.",
    33: "A bivalve Digimon\ncovered by a hard shell.\nIt lures foes with its\ncute face, then attacks.\nThe shell is so tough\nthat small attacks\ncan't harm it. Its body\ninside is like slime.",
    34: "A cold-loving\nvariant of Agumon\nthat lives in chilly\nplaces. Its color acts\nas camouflage when\nit fights in the snow.",
    35: "A crab-like Digimon\nthat wears metal data\nfrom the \"Net Ocean\"\nto strengthen its\nbattle ability. Its\nhuge pincers and hard\nshell are its pride,\nbut its joints and\nbelly are weak spots.",
    36: "A Digimon whose\nface is shaped like a\nflower. It usually\nwears its petal-like\nshell as a helmet,\nbut opens the petals\nwide when in a good\nmood.",
    37: "A bud-shaped plant\nDigimon. It spins the\nleaves on its head to\nfloat through the air.\nThough expressionless,\nit has a charming face.\nA gentle, caring soul,\nit always thinks of\nits friends.",
    38: "A beast Digimon\nwith sharp claws. It\nwears gloves to protect\nits paws until the\nclaws grow. It excels\nat swift hit-and-run\nattacks.",
    39: "A Digimon wearing\na holy shell. It is\nsaid to store holy\npower in the earring\non its left ear. The\nmore power it stores,\nthe more it may affect\nits next evolution.",
    40: "A turtle Digimon\nwith a shell shaped\nlike a computer mouse.\nIt can hide its whole\nbody inside, except\nfor the helmet on\nits head.",
    41: "A vampire Digimon\nthat loves pranks. It\nwill even forget to\ndrink blood or take\ndangerous risks if\nthat helps a prank\nsucceed.",
    42: "A puppet Digimon\nborn from data leaked\nfrom a computer chess\ngame. It is still weak,\nbut may rise to the\nstrength of an Ultimate\nDigimon if it climbs\nthe ranks.",
    43: "A poisonous\nmushroom-shaped\nDigimon. Tiny mushrooms\ngrow all over its body;\ntheir attacks cause\nvarious symptoms. It\nloves bullying the weak,\nbut is actually very\nshy.",
    44: "A stag-beetle\nDigimon with a head\nand arms like stun\nguns. When it senses\ndanger, it releases\none million volts. It\nrecharges when hungry,\nbut is usually calm.",
    45: "A Digimon that\nevolved from Sunmon.\nEnergetic and curious,\nit holds solar-like\nfire within its body.\nIt fights by striking\nfoes with fiery fists.",
    46: "A Digimon that\nevolved from Moonmon.\nA little shy and\nreserved, it holds the\npower of pure water.\nIt attacks with claws\nimbued with darkness,\ndespite its cute look.",
    47: "A chick-like baby\nbird Digimon that has\njust begun sword\ntraining. Confident\nand proud, it still\nhasn't noticed its\neggshell is stuck on.",
    48: "A child-shaped\nangel Digimon said to\nhave brought peace to\nthe Digital World in\nancient times. Though\nit looks like a child,\nit has the wisdom and\npower to surpass even\nPerfect Digimon.",
    49: "A Digimon that\nsmall Digimon can ride.\nIt has no will of its\nown and cannot move\nwithout a rider. But\nit reflects the rider's\npower, so never\nunderestimate it.",
    50: "A yellow, dinosaur-\nlike Digimon. Its\nhardened forehead\nskin forms a shell\nthat protects it. With\nsharp claws and a huge\nhorn, it is powerful\nand intelligent, and\nworks well with allies.",
    51: "An ancient, dinosaur-\nlike Digimon. It looks\nfrightening, but is\nactually calm and\nintelligent, so it is\nfairly easy to tame.\nIn battle, it charges\nwith its two developed\narms and huge tail,\nknocking foes aside.",
    52: "A fallen angel\nDigimon with tattered\nwings and black robes.\nOnce an angel, it was\ncorrupted by evil. A\nlarge mark of evil\nrests on its chest.\nCruel by nature, it\nfaithfully serves the\nmaster it has sworn\nto obey.",
    53: "A Digimon that\nsoars through the\nDigital World's skies\non giant wings. So\nrare it is called a\nphantom Digimon, it\nis said to be close\nto a god. It can\nsummon storms and\ntornadoes.",
    54: "A long, snake-like\nDigimon that lives\nnear water. It is\nsurprisingly gentle\nand usually swims\nslowly underwater,\nbut becomes fierce\nwhen it must fight.",
    55: "A slug-like Digimon\nthat prefers dark,\ndamp places. It has\nlittle strength or\nwill to fight and just\nlives freely. When\nattacked, it throws\npoop to protect itself,\nstartling its foes.",
    56: "A blue, beetle-like\nDigimon. Its huge body\nis full of strength,\nand its hard shell\ngives it strong\ndefenses. Its head is\nreinforced with metal\nand especially tough.",
    57: "A wolf-like Digimon\nwith fur as tough as\nthe legendary rare\nmetal Mithril. The\nblades on its shoulders\ncan slice anything.\nHighly intelligent,\nit faithfully follows\nits master.",
    58: "An angelic Digimon\nwith six wings and\npure-white robes. A\nperfectly good being,\nit is said to guide all\nDigimon to happiness.\nIt is merciless toward\nevil and attacks\nwithout hesitation.",
    59: "A carnivorous plant\nDigimon with long,\nvine-like arms and a\nwide-open mouth. Its\nsweet scent lures\nsmall Digimon, which\nit catches with its\nvines. As it grows,\nit is said to flower\nand bear fruit.",
    60: "An ogre-like Digimon\nwith a short temper\nthat loves to fight.\nIt challenges foes\nstronger than itself,\nso it is called a\n\"Digimon Hunter.\" Its\nbone club is a trophy\nfrom defeating\nSkullGreymon.",
    61: "A ghost Digimon\nformed from a cursed\nvirus program. It can\ndestroy a possessed\ncomputer in an instant.\nWhat lies beneath its\nwhite cloth is unknown;\nits shadow is said to\nlead to a black hole.",
    62: "A golden-poop-shaped\nDigimon said to have\nbeen born when data\nscraps suddenly\nmutated. Chuumon clings\nto it and acts as its\nbrains, using cunning\ntricks to lead it into\ntrouble.",
    63: "A chicken-like\nDigimon that lived on\nland so long it can no\nlonger fly. Its two\nlegs grew powerful,\nbut it is a brawler\nthat dislikes battles\nthat use too much\nenergy.",
    64: "Called the \"Lion\nKing of Beasts\" and\n\"Noble Hero,\" this\nDigimon has a strong\nsense of justice and\na firm will. It trains\nits body every day and\nfights evil with its\nsword, Shishioumaru.",
    65: "A stag-beetle\nDigimon with huge\npincers on its head.\nIts hard shell protects\na body with tremendous\npower, but it is\ndangerous and driven\nonly by instinct. It\nis hostile to\nKabuterimon.",
    66: "A frog Digimon with\na pleasant singing\nvoice no one would\nexpect from its looks.\nThree holes in its\ntongue shape the notes,\nwhile the horn around\nits neck carries its\nsong.",
    67: "A small, cat-like\nDigimon. The Holy Ring\non its tail marks it as\na holy Digimon; without\nit, it cannot use its\ntrue power. Its claws\ncopy SaberLeomon's\ndata to protect it.\nIt can Armor Digivolve\nwith a Digi-Egg.",
    68: "A wizard Digimon\nfrom another Digital\nWorld. It came here\nto train and become\na great mage. Very\nshy, it never shows\nits true face.",
    69: "A giant cactus\nDigimon that stores\nnutrient data in its\nbody, letting it live\nfor a while even in\nbarren places. It moves\nat its own pace and\nlooks relaxed, but\ncan be hardworking.",
    70: "A machine Digimon\nwith excellent\ndefenses. An evil\nvirus infected it,\nerasing its emotions\nand leaving only its\ndefense program. Virus\nDigimon exploit its\npower for their own\nends.",
    71: "An original dragon\nDigimon with immense\npower. Its muscular\narms and legs can\ndestroy huge rocks\nwithout a trace, but\nits strong sense of\njustice keeps it from\nusing that power\ncarelessly.",
    72: "A humanoid insect\nDigimon covered by\na hard shell. Cool\nand highly skilled\nat assassination, it\nuses speed and sharp\njudgment to strike\nits foes' weak points.",
    73: "A giant bird\nDigimon wreathed in\nblazing flames. It is\nsaid to have been born\nfrom the Firewall that\nprotects the Internet.\nIt flies through the\nnetwork on huge wings.",
    74: "An armored dragon\nDigimon covered in\nhard skin. Tough spikes\ngrow from its head and\nbody, letting it deal\nheavy damage when it\ncharges. Gentle, but\nbrave at heart.",
    75: "A hunter Digimon\nskilled at tracking\nits prey. Despite its\nappearance, it moves\nquickly and catches\nfoes precisely. It can\njump high and fly. Its\nfavorite jeans are\ncustom-made.",
    76: "A crimson dragon\nDigimon with a white\nmane. It has the\nviolent nature common\nto Virus Digimon, but\ncan grow into a hero\nthat fights for justice\ndepending on how it\nis raised.",
    77: "A fox-like Digimon\nwith nine tails tipped\nwith blue flames. It is\nsaid to evolve from an\nexperienced Renamon.\nWith strong willpower,\nit excels at many\nmagical techniques.",
    78: "A Digimon that\nturned into a cocoon\nto store energy and\ngrow stronger than\nKeramon. It cannot\nmove, but its hard\nskin withstands\nattacks. It strikes\nfoes with the tentacles\non its back.",
    79: "A Digimon shaped\nlike the legendary\nholy beast Shisa. It\ncan ward off disaster\nand unleash immense\npower against evil. It\nrisks its life to guard\nthe kind-hearted, but\nusually relaxes in\nthe sunlight.",
    80: "A little-demon\nDigimon said to be the\nancestor of dark\nDigimon. Mischievous\nand a bit twisted, it\nis close friends with\nDemiDevimon, and they\noften go around\ncausing trouble.",
    81: "A bird Digimon with\na hawk-like form and\na huge horn on its\nhead. It flies at\nMach speed, spots\neven tiny prey, then\ndives to attack with\nits horn and beak.",
    82: "A mutant Digimon\nthat looks like a\npirate captain. It\nsearches the Net Ocean\nfor the phantom \"White\nWhamon.\" A warrior\nof the sea, it faces\nrough waves with a\nclaw and cannon for\narms.",
    83: "A massive dragon\nDigimon so heavy that\nmost Digimon flee at\nthe sight of its shadow.\nA terrifying beast in\nbattle, it also has\na dragon's wisdom and\nis normally very\ncalm.",
    84: "A cyborg Digimon\nmodified from a wild\nDigimon. Its athletic\nability is so high\nthat heavy Chrome\nDigizoid armor\nrestrains its power.",
    85: "A legendary Digimon\nwith golden fur, said\nto defeat evil computer\nviruses. It rides a\ncloud-like object at\nhigh speed through the\nnetwork, so it is\nrarely seen.",
    86: "A mutant space\nwarrior equipped with\na star-shaped armor\nsuit, gloves, and boots.\nIts eyes burn with\nfighting spirit, and\nit can communicate its\nwill without speaking.\nIt admires the hero\nLeomon.",
    87: "An Invade-type\nDigimon related to\nNanimon. Its whole\nbody is a bomb, and\nthe hair on its head\nworks like a fuse.\nA super-dangerous\nbomb old man with\nMAXIMUM threat level!",
    88: "A mythical beast\nDigimon with a unicorn's\nhorn and Pegasus wings.\nIt flies through the\nnetwork and pierces\nfoes with its horn.\nWild Unimon are\nextremely violent, so\napproach with care.",
    89: "A black dinosaur\nDigimon said to have\nformed when Tyranomon\nwas corrupted by a\nmalicious computer\nvirus. Now violent,\nit attacks everything\nit sees.",
    90: "A unicorn-like\nDigimon covered in\npure-white fur. Its\nskin is as tough as\nMithril and withstands\nany cold. It emits\nintense heat from its\nhooves and can melt\nice as it walks.",
    91: "A bull-like Digimon\nwith powerful dark\nenergy. Its tough skin\nwithstands ordinary\nattacks. A mighty\nweapon, the Demon Arm,\nis fused with its\nleft arm.",
    92: "A mysterious dragon\nDigimon thought to be\na Greymon subspecies.\nIts horns, body, and\nforelimbs have grown\nmore powerful, giving\nit a more aggressive\nappearance.",
    93: "A Digimon evolved\nfrom Gaomon. Its build\ngrew larger, and the\nclaws once protected\nby gloves matured. It\nusually walks on four\nlegs, but can rise\nlike a bear to attack\nother Digimon.",
    94: "A living fossil: an\nancient giant dragon\nDigimon. Its wings\naren't suited for\nflying, but powerful\nlegs let it run at\n200 km/h. Extremely\nviolent, it attacks\nanything that moves.\nMetal in its wings\nadds to its defense.",
    95: "A sickle-weasel-like\nDigimon with a blade\nfor a tail. Its tail\nblade lets it defend\nagainst surprise\nattacks from behind,\nbut it sometimes\nfights with its own\ntail.",
    96: "A sunflower-like\nplant Digimon. Sunlight\nmakes it energetic\nand raises its attack\npower. On clear days,\nit may flap the leaves\non its back and fly.",
    97: "A Digimon formed\nfrom the data of a\nmusic player and a\nlegendary kappa. It is\nalways cheerful and\nlistens to its favorite\nmusic. It cries if\nits head disk is\nscratched.",
    98: "A sacred vampire\nwolf Digimon said to\nhave existed since the\nDigital World's dawn.\nDigimon drained by\nSangloupmon lose all\ndata in their Digicore\nand die. It can break\nits body into data\nto move.",
    99: "A bird Digimon that\ncan fly, but runs\nfaster on its powerful\nlegs. Several steel\nfeathers are hidden\nunder its wings. It\nfavors speed in battle.",
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
        key = f"MSG/MESPAK03.PAK:000:{index:05d}"
        if key in prior:
            raise ValueError(f"Already translated: {key}")
        row = records.get(key)
        if not row or not row["source"].strip():
            raise ValueError(f"Missing profile source: {key}")
        english = fit(raw)
        note = ("Translated from the original Japanese profile. Western species and move spellings follow the project's official English Digimon reference list where named; general terminology uses Digi-Egg, Armor Digivolution, Digital Hazard, and Digicore.")
        blocks.append({"archive": row["archive"], "entry": 0, "start": index,
            "category": "Digimon profiles", "english": [english],
            "sources": [CARD_LIST], "review_note": note})
        review.append({"id": key, "japanese": row["source"], "english": english,
            "evidence_url": LOCAL, "terminology_reference": CARD_LIST,
            "review_note": note})
    if len(blocks) != 100:
        raise ValueError(f"Expected 100 profiles, authored {len(blocks)}")
    path = ROOT / "translations/batch43.json"
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps({"description": "Translate Digimon profile blurbs 1-100 from the original Japanese data, including the reserved dummy profile slot.", "blocks": blocks}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "translations/review_batch43.json").write_text(json.dumps({"batch": 43, "translated_slots": len(blocks), "groups": review}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Batch 43 review", "", "Batch 43 translates the first 100 Digimon profile records, including a clearly labeled dummy-data slot. Each entry is checked against its original Japanese record; official English naming references are linked for Digimon proper nouns. Text is wrapped to the measured 15-character story line width.", "", "| ID | Japanese | English |", "|---|---|---|"]
    for row in review:
        jp = row["japanese"].replace("<0A>", "<br>").replace("|", "\\|")
        en = row["english"].replace("\n", "<br>").replace("|", "\\|")
        lines.append(f"| `{row['id']}` | {jp} | {en} |")
    (ROOT / "translations/review_batch43.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"batch": 43, "translated_slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
