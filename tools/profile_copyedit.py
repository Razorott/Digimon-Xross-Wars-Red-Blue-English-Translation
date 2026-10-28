"""Contextual wording for punctuation the DigiDex profile printer skips.

The printer leaves ASCII apostrophes blank. Keep Japanese and the authored
English intact in the batch files; apply these explicit English paraphrases
when preparing profile text for the ROM. Every source phrase is checked, and
any new unhandled apostrophe fails the build rather than becoming a blank.
"""

REWRITES = (
    ("can't", "cannot"),
    ("hasn't", "has not"),
    ("aren't", "are not"),
    ("you'll", "you will"),
    ("a dragon's form", "the form of a dragon"),
    ("The flower's scent", "The scent of the flower"),
    ("the rider's power", "the power of its rider"),
    ("the Digital World's skies", "the skies of the Digital World"),
    ("the Digital World's dawn", "the dawn of the Digital World"),
    ("the Digital World's order", "the order of the Digital World"),
    ("the Digital World's heaven", "the heaven of the Digital World"),
    ("the Digital World's creation", "the creation of the Digital World"),
    ("all the Digital World's evil", "all the evil of the Digital World"),
    ("SaberLeomon's data", "data from SaberLeomon"),
    ("its foes' weak points", "the weak points of its foes"),
    ("a dragon's wisdom", "the wisdom of a dragon"),
    ("a unicorn's horn", "the horn of a unicorn"),
    ("its foe's life", "the life of its foe"),
    ("a beast's strength", "the strength of a beast"),
    ("foes' abilities", "enemy abilities"),
    ("a lab's data bank", "a laboratory data bank"),
    ("a ship's computer", "a shipboard computer"),
    ("its master's orders", "the orders of its master"),
    ("Monochromon's", "that of Monochromon"),
    ("Monzaemon's", "those of Monzaemon"),
    ("Leomon's Ultimate form", "The Ultimate form of Leomon"),
    ("Lekismon's Ultimate form", "The Ultimate form of Lekismon"),
    ("the Egg's fire attribute", "the fire attribute of the Digi-Egg"),
    ("the Egg's holy attribute", "the holy attribute of the Digi-Egg"),
    ("Veemon's Armor Digivolution", "an Armor Digivolution of Veemon"),
    ("Patamon's Armor Digivolution", "An Armor Digivolution of Patamon"),
    ("Wormmon's Armor Digivolution", "An Armor Digivolution of Wormmon"),
    ("Hawkmon's Armor Digivolution", "An Armor Digivolution of Hawkmon"),
    ("Armadillomon's Armor Digivolution", "An Armor Digivolution of Armadillomon"),
    ("Tailmon's Armor Digivolution", "An Armor Digivolution of Tailmon"),
    ("another Digimon's data", "data from another Digimon"),
    ("Its tail's venomous stinger", "Its venomous tail stinger"),
    ("the assassin's presence", "the presence of the assassin"),
    ("both species' weaknesses", "the weaknesses of both species"),
    ("Etemon's Mega form", "The Mega form of Etemon"),
    ("Digitamamon's dark evolution", "a dark evolution of Digitamamon"),
    ("a Pandora's box", "the box of Pandora"),
    ("a hacker's computer virus", "a computer virus created by a hacker"),
    ("the Musyamon army's charge", "the charge of the Musyamon army"),
    ("its host's full abilities", "the full abilities of its host"),
    ("the D-Brigade's final battle weapon", "the final battle weapon of the D-Brigade"),
    ("the Dark Area's depths", "the depths of the Dark Area"),
    ("WarGreymon's", "those of WarGreymon"),
    ("HerakleKabut erimon's eternal rival", "an eternal rival of HerculesKabuterimon"),
    ("Megalogrowmon's mistaken evolution", "a mistaken evolution of Megalogrowmon"),
    ("'the best defense is a good offense'", '"the best defense is a good offense"'),
    ("the gods' anger", "the anger of the gods"),
    ("Flaremon's Mega form", "The Mega form of Flaremon"),
    ("Crescemon's Mega form", "The Mega form of Crescemon"),
    ("Argomon's Mega form", "The Mega form of Argomon"),
    ("the moon's power", "the power of the moon"),
    ("today's Mega Digimon", "modern Mega Digimon"),
    ("both Digimon's traits", "the traits of both Digimon"),
    ("Imperialdramon Dragon Mode's humanoid mode change", "The humanoid mode change of Imperialdramon Dragon Mode"),
    ("Imperialdramon Fighter Mode's final form", "The final form of Imperialdramon Fighter Mode"),
    ("Omnimon's strength", "the strength of Omnimon"),
    ("Vamdemon's final form", "the final form of Myotismon"),
    ("VenomVamdemon", "VenomMyotismon"),
    ("Dukemon's other form", "Another form of Gallantmon"),
    ("Millenniumon's mind", "the mind of Millenniumon"),
    ("an enemy's mind", "the mind of an enemy"),
    ("ShineGreymon's Burst Mode", "The Burst Mode of ShineGreymon"),
    ("MirageGaogamon's Burst Mode", "The Burst Mode of MirageGaogamon"),
    ("Ravemon's Burst Mode", "The Burst Mode of Ravemon"),
    ("Rosemon's Burst Mode", "The Burst Mode of Rosemon"),
    ("Dorulumon's Artillery Mode", "The Artillery Mode of Dorulumon"),
    ("Ballistamon's Reinforced Armor Mode", "The Reinforced Armor Mode of Ballistamon"),
    ("Sparrowmon's Supersonic Cruise Mode", "The Supersonic Cruise Mode of Sparrowmon"),
    ("four Digimon's determination", "the determination of four Digimon"),
    ("Greymon's power", "the power of Greymon"),
    ("Greymon's combat ability", "its combat ability"),
    ("MailBirdramon's armor", "the armor of MailBirdramon"),
    ("DeadlyAxemon's older brother", "The older brother of DeadlyAxemon"),
    ("SkullKnightmon's younger brother", "The younger brother of SkullKnightmon"),
    ("The elder brother's cunning", "The cunning of the elder brother"),
    ("the younger's physical prowess", "the physical prowess of the younger brother"),
    ("Every technique's power", "The power of every technique"),
    ("three Digimon's fighting spirit", "the fighting spirit of three Digimon"),
    ("an angel's hands", "the hands of an angel"),
    ("a demon's", "the hands of a demon"),
    ("other Digimon's energy", "energy from other Digimon"),
    ("Sea's Destroying Weed", "Sea Destroying Weed"),
    # Official Western species spellings in Bandai's English card list:
    # https://world.digimoncard.com/products/goods/pdf/products_BT01-03_ver1.0_list.pdf
    # https://world.digimoncard.com/cards/?card_no=BT21-076&search=true
    # https://world.digimoncard.com/cards/?card_no=BT18-015&search=true
    ("Tailmon", "Gatomon"),
    ("Vamdemon", "Myotismon"),
    ("Megalogrowmon", "WarGrowlmon"),
    ("Mugendramon", "Machinedramon"),
    ("Chimairamon", "Kimeramon"),
)


def copyedit_profile(text, record_id):
    for before, after in REWRITES:
        text = text.replace(before, after)
    if "'" in text:
        raise ValueError(f'DigiDex profile still has an invisible apostrophe: {record_id}: {text}')
    return text
