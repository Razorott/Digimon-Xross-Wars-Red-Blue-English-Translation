"""Reproducible authoring for the second translation pass; output is bilingual-reviewed by build.py."""
import json
import sys
import textwrap
from xros_text import ROOT, Rom, rom_paths
from build import collect_messages

blocks=[]
def block(archive,entry,start,category,text):
    lines=text.strip('\n').split('\n')
    blocks.append(dict(archive=archive,entry=entry,start=start,category=category,english=[s.replace(' /n ','\n') for s in lines]))

block('MSG/MESPAK01.PAK',4,0,'DigiLab',"""
Choose a function.
Close the DigiLab PC?
Yes, close it
No, stay here
Use a DigiScore to create a /n new Digimon from several /n material Digimon.
Absorb other Digimon to /n power up one Digimon.
Reload your Melodies to /n give Digimon physical form.
Turn Digimon into Melodies /n or move them elsewhere.
Melody Playback
Melodies Owned
^0/^1
Total
^0/^1
Melody List
x^0
Sort Menu
Alphabetical
Species
Quantity
Close Menu
You cannot play this /n Melody yet.
Your Digimon List is full. /n Melody Playback failed.
How many ^0 will you use?
You can use up to ^1.
Use ^1 of ^0 for /n Melody Playback?
Yes, begin
No, try again
Melody Playback!
Name this Digimon /n ^0?
Yes, use this name
No, try again
Melody Playback complete! /n Sent to the DigiBank.
Jogress Up
Choose slots. The Digimon /n in the top slot is the /n main Digimon to power up.
Choose the main Digimon.
Choose a sub Digimon. /n Warning: sub Digimon are /n consumed by Jogress Up.
Selected Digimon
Candidate Digimon
Lv^0
Lv--
No candidate Digimon found.
No main Digimon selected.
No sub Digimon selected.
Perform Jogress Up with /n the selected Digimon?
Yes, please
No, choose again
The sub Digimon will be /n consumed. Is that OK?
Yes, perform Jogress Up
No, choose again
Jogress Up!
Name this Digimon /n ^0?
Yes, use this name
No, try again
Choose special moves /n to inherit.
Choose a move to discard.
Choose a move you want.
Choose a move to discard.
Choose a move to inherit.
Selected Moves
Move List
Finish
No moves inherited. /n You must inherit at least /n one move.
Inherit these moves?
Yes, these are fine
No, choose again
Your move changes will be /n undone. Is that OK?
Yes, undo changes
No, keep changes
Jogress Up complete! /n Sent to the DigiBank.
Jogress Up complete! /n Sent to the party.
DigiFusion
Requirements
Choose a DigiScore with the /n +Control Pad. Press A for /n its menu. A GOOD mark means /n DigiFusion is available.
Lv:^0
^0:^1
Befriended:^0
Owned:^0
DigiScores
^0/^1
DigiScore List
x^0 Fusion
Select DigiScore
Perform DigiFusion
View Digimon
View DigiFusion Digimon
Close Menu
Sort Menu
Alphabetical
Species
GOOD Mark
Close Menu
You cannot use this /n DigiScore yet.
Choose a Digimon with the /n +Control Pad. Press A to /n view its stats.
You have none of the /n required Digimon. /n Press B to go back.
Candidates
^0/^1
Fusion Digimon List
Sort Menu
Alphabetical
Species
Level
Location
Close Menu
Choose a Digimon with the /n +Control Pad. Press A for /n its menu.
Candidates
^0/^1
Select Digimon
Set for DigiFusion
Remove from DigiFusion
View Stats
Close Menu
Perform DigiFusion with /n the selected Digimon?
Yes, please
No, choose again
The selected Digimon will /n be consumed. Is that OK?
Yes, perform DigiFusion
No, choose again
HP             MP /n ATK            SPD /n INT            DEF
DigiFusion!
DigiFusion complete! /n Sent to the DigiBank.
DigiFusion complete! /n Sent to the party.
Digimon List
""")

block('MSG/MESPAK01.PAK',3,0,'DigiFarm',"""
Go to the DigiFarm?
Return to the entrance?
Name ^0 /n ^1?
Set this Terrain Board? /n "^0"
Set this BGM Board? /n "^0"
Yes, go there
Yes, return
Yes, that's fine
Yes, set it
Yes, set it
No, stay here
No, stay here
No, change it
No, cancel
No, cancel
Configure your Farm Islands.
Move Digimon between groups.
Choose a Farm Island.
Choose a menu option.
Choose a Digimon to talk to.
Choose a Training Pen.
Choose a training partner.
Choose a Job Pen.
Choose a Digimon /n for the job.
Choose a Digimon to feed /n a DigiNoir.
Digimon living on this /n Farm Island.
Farm goods placed on /n this Farm Island.
Stats for Terrain Board /n "^0".
Stats for BGM Board /n "^0".
Total EXP gained per day /n on this Farm Island.
Return to Island Selection
Leave DigiFarm
Talk
Train
Jobs
DigiNoir
EXP Gained Per Day
Manage Goods
Change Terrain Board
Change BGM Board
No farm goods suitable /n for training are placed.
Not enough stamina /n to train.
No farm goods suitable /n for jobs are placed.
Digimon involved in a /n request quest cannot work.
Digimon undergoing training /n cannot work.
Weapon crafting started.
Armor crafting started.
You already fed a DigiNoir /n to that Digimon.
You have no farm goods.
Placed farm goods: /n "^0"
All of these farm goods /n are placed on other islands.
Removed farm goods: /n "^0"
Those farm goods are /n already placed here.
Changed Terrain Board: /n "^0"
That Terrain Board is /n already set.
Changed BGM Board: /n "^0"
That BGM Board is /n already set.
Those farm goods are /n already placed here.
Digimon on this island: ^0/8
Digimon on this island: ^0/8 /n Press L/R to switch islands.
Removing these farm goods /n also cancels the job. /n Is that OK?
Yes, that's fine
No, cancel
Swap Farm Goods
Remove Farm Goods
Close Menu
Place Farm Goods
Digimon
Goods
Terrain Board
BGM Board
Recommended
Training Pen
Success Rate
Job Pen
Board Level
ATK
DEF
SPD
Max Level
Friendship
Rank
Live Event Effect
MAX Points
Remaining
Owned
Level
Recommended
Farm 1
Farm 2
Farm 3
Farm 4
Farm 5
Farm 6
Farm 7
Farm 8
^0 EXP
SS
S
A
B
C
D
E
Max HP
Max MP
ATK
DEF
SPD
Friendship
EXP
None
^0/^1
^0/^1
Digimon
Farm Goods
Terrain Board
BGM Board
Board Level
MAX
""")

block('MSG/MESPAK01.PAK',14,0,'growth notifications',"""
Learned a new special move!
New DigiXross move learned!
Learned a new trait!
Close the DigiReport?
Yes, close it
No, keep reading
""")

block('MSG/MESPAK01.PAK',16,0,'inventory and information',"""
Farm goods placed: ^0/6
Press L/R to switch /n Farm Islands.
Terrain
BGM
Recommended
Goods
Digimon
Selected ^0 Board stats
EXP Gained Per Day
Remaining
Digimon Befriended:
Digimon Owned:
x^0 Fusion
Choose a consumable item /n to use.
View equipment that is /n currently unused.
View your DigiScores.
View your Melodies.
View farm goods that are /n not placed on a Farm Island.
View your key items.
You cannot use this /n item here!
Use a Gate Disk?
Yes, use it
No, cancel
Play Time
Location
Digimon
Farms
DigiScores
Quests
DigiDex
General
Taiki Kudo
Play Log
Melody
Jogress
Fusions
Battles
Defeated
Melodize
Training
Wireless
No quests /n active.
View information about /n your current quest.
Max
Cond.
Mood
Effect
Species
EP
DigiXross
Habitat
Unknown
You have not befriended /n this Digimon. Detailed /n information is unavailable.
Save
Last Save
Date/Time
Location
You have no tickets for /n summoning Digimon.
Choose a Digimon ticket /n to use.
Summon /n ^0?
Yes, summon it
No, choose again
Stop summoning Digimon?
Yes, stop
No, continue
Summon Tickets
Choose the information /n you want to view.
Choose a Digimon whose /n equipment you want /n to change.
Current Equipment
Choose equipment to use.
Range
Equipment
ATK
INT
SPD
DEF
FRND
Money
LV
Level
Learned
^0/^1
^0/^1/^2
^0: ^1
^0:^1:^2
Sort Menu
Alphabetical
Species
Digimon Number
Level
Location
Close Menu
Digimon
Total
^0 times
^0 Digimon
ATK
DEF
INT
Default Order
Healthy
Paralysis
Sleep
Confusion
Blindness
Sealed
None
Paralysis Resist
Sleep Resist
Confusion Resist
Blindness Resist
All Status Resist
Paralysis Immunity
Sleep Immunity
Confusion Immunity
Blindness Immunity
KO Immunity
HP Drain Resist
MP Drain Resist
Shuffle Resist
Poison Resist
Curse Resist
All Special Resist
HP Drain Immunity
MP Drain Immunity
Shuffle Immunity
Poison Immunity
Curse Immunity
All Special Immunity
MP Cost
Effect Duration
HP Recovery
Evasion
Accuracy
Critical Rate
Escape Rate
Melodize Rate
Drop Rate
Expedition Success
Job Success
Bit Gain
EXP Gain
Party Paralysis Resist
Party Sleep Resist
Party Confusion Resist
Party Blindness Resist
Party All Status Resist
Party HP Drain Resist
Party MP Drain Resist
Party Shuffle Resist
Party Poison Resist
Party Curse Resist
Party All Special Resist
Paralysis Rate
Sleep Rate
Confusion Rate
Blindness Rate
HP Drain Rate
MP Drain Rate
Shuffle Rate
Poison Rate
Curse Rate
HP Drain Damage
MP Drain Damage
Poison Damage
Damage
Damage
Damage
Damage
Damage
Damage
ATK
INT
SPD
DEF
Paralysis
Sleep
Confusion
Blindness
HP Drain
MP Drain
Shuffle
Poison
Curse
HP Recovery
MP Recovery
Cure Paralysis
Cure Sleep
Cure Confusion
Cure Blindness
KO Recovery
Revive
Melody Effect
^0/^1 Digimon
Family
Type
Species
Class
Strong Against
Weak Against
Equipment
Trait 1
Trait 2
Trait 3
Trait 4
Trait 5
Trait 6
Field Skill
Drop Item 1
Drop Item 2
Drop Item 3
Drop Item 4
^0 left
""")

block('MSG/MESPAK01.PAK',19,0,'move management',"""
Finish changing /n special moves?
Yes, finish
No, continue
Known Special Moves
Unlearned Special Moves
Change Moves
""")

block('MSG/MESPAK01.PAK',20,0,'Reload Challenge',"""
Digimon Challenge
Point your DS microphone /n toward the DigiMelody! /n The mark on the Touch Screen /n moves while it reads the /n DigiMelody. Something will /n happen if you succeed at /n the Reload Challenge!
Got the key item /n "^0"! /n Visit the service counter!
You already received /n the key item "^0".
In a quiet place, hold the /n microphone near the speaker /n and play the sound again. /n If it still will not work, /n read the instruction /n booklet.
That password seems wrong. /n Try entering it again!
Complete!
""")

block('MSG/MESPAK02.PAK',2,0,'opening story',"""
I have no allies. Whoever you are... leave quietly, unless you want to get hurt.
Come with me quietly. I would rather not use force.
I don't know who you are, but stop ordering me around! I'm escaping with my friends! I'm not going with anyone!
Wh-what is this...?!
A-are you all right?! Hey, hang in there!
Did that do it?
All right! Round them all up!
We'll show you what happens to anyone who defies ROG!
Hmph... I expected more of a fight. Even with a surprise attack, that was almost too easy.
...Honestly, why now? I'll have to withdraw for the moment.
We'll get caught at this rate! S-sorry!!
One got away! Is that all right?
You expect me to do everything? We had to take down the strong ones first, or we'd be in trouble! Spadamon can wait. We've caught all his friends. He'll come back to rescue them soon enough.
Carry them inside Sky Fort!
Is everyone all right?!
Doesn't look like anyone's hurt or in trouble.
Great! Then all's well that ends well!
I have to save them... I... I have to save everyone...
You're awake, Taiki.
That voice just now...
A voice? I didn't hear anything.
More importantly, Taiki, take a look. We've definitely reached another Zone, but we've never been thrown around like that before.
Another Zone...?
Hey, where's Akari? Zenjiro's missing too!
That's right! We've all been split up. I sure hope this Zone is safe...
No other Digimon or humans detected nearby. We should hurry and find Akari and the others.
Right. Standing here thinking won't help. Let's go, Taiki!
You lot! Never seen you before! Come with us to Sky Fort. You wouldn't dare defy ROG, would you? ROG rules Elestou Zone!
ROG? As in "rogue"? Doesn't that mean a villain or a thief? You're practically calling yourselves crooks! Besides, we didn't come here by choice! Everyone kept making jokes, and I was dragged here before I could even talk back! I'm the one who should be asking: what's going on?!
What's going on?!
What's going on?
What's goin' ooon!
Enough! Be quiet! Stop babbling nonsense, all of you!
Hey, Zenjiro! Starmon! Pickmons!
Taiki Kudo! Everyone!
Whoa, brothers! We're saved!
Hooray! We're saved!
That's our Taiki! So cool!
Taiki-cool!
So you did have allies. No matter... I'll crush the lot of you!
Taiki!
All right... let's go, everyone!
Whoo! Thanks, everyone!
I knew you'd come to save us!
We knew it!
Did we know it?
We moo-knew it!
Who were those Digimon? They called themselves ROG...?
Apparently they're a group of Digimon that's taken over this Zone. ROG... rogue... Going by that name, I'm guessing they're bad news!
That's right, brother! Definitely bad news!
Rooogue! Sounds villainous!
We'll worry about ROG later. Hey, Zenjiro, have you seen Akari?
Huh?! I've only found the Pickmons since arriving here... Isn't she with you?
That's worrying... I was thrown here without a clue what was happening. Until I met the Pickmons falling from the sky, I thought I was done for! Alone again, no weapon, and this place is full of vicious Digimon!
Vicious Digimon?
Yeah, more of them attack you here than in other Zones. We can't leave a girl alone in a place like this!
You're right. Come on, everyone! Let's find Akari and the others!
Zenjiro, Starmon, and the Pickmons joined you!
Surrender quietly...? Is that a joke? Who waves a white flag because a mushroom blocks the road?
H-hey, Dorulumon! Isn't that enough? Let's just run away without fighting. Please? Please?!
Fine by me, but they seem eager to fight. Stand back, Cutemon. I'll finish this quickly.
Hand over all the items you've collected! To think anyone still dares defy ROG, rulers of Elestou Zone!
He's obviously bluffing! He'll turn tail and run soon enough... if he still has a tail by then!
R-right! ROG's Mushroomon squad could smash these guys to pieces in no time!
Hey, you lot! Stop it, it's dangerous! Don't make Dorulumon angry!
...Hold on a moment. You're making me sound like the villain here.
Hey, Akari! Dorulumon! Cutemon!
Everyone!! Perfect timing! Hurry and do something about these guys!
What's wrong, Akari? There's no danger worth getting so worked up over.
You don't get it, Dorulumon. YOU are the danger!
So you've got a whole gang! No wonder you looked so confident! But no matter how many enemies gather, ROG's Mushroomon squad will never lose!
We'll squash the lot of you!
All right, everyone! Let's help Akari and the others!
Are you all right, Akari?
Ha... hahaha... I'm perfectly fine! Of course!
You're smiling, but your cheeks are twitching, kyu...
I've been dragged into so much trouble all at once... I can't decide whether to laugh or get mad! Oh, right, I almost forgot. Here, Taiki.
Got consumable items! Bandage x3
Got consumable items! Energy Source x3
These items restore Digimon's HP and MP. At least, that's what those guys said.
That'll help a lot! Nice work, Akari!
Huh? Those guys...? Oh, ROG! Those crooks! So where did you get the items?
The Digimon around here dropped them when they were defeated. Dorulumon took down every one that attacked us! Well, they dropped them... or he made them drop them... sent them flying, really! Enemies kept swarming us, and Dorulumon went on a rampage! I honestly thought we wouldn't make it!
Use those when your Digimon are running low. Press START or X to open the Xros Loader menu, then choose Items. You can also use them from the Command Ring during battle.
Got it. I'll remember.
Huh? You're just going to ignore everything I went through?!
I have to save them... I have to save everyone in Elestou Zone... Whatever it takes... I have to...
That was... the voice from before!
...Hey, Taiki. What's wrong all of a sudden?
I heard it much more clearly this time! They must be close!
Close...? Who are you talking about?
I... don't know. But I heard them just now. They sounded desperate! It's definitely the same voice!
It must be whoever brought us here from the jungle. They keep saying they have to save someone. They need our help! I can't just leave them like that!
We finally found everyone after getting split up, and Taiki's already saying his usual line again...
Please, everyone! I want to help them!
Of course I'm coming, Taiki! I'm always with you!
I don't understand what you're talking about... but fine. I'll help. Lead the way, Taiki.
I'll come along too, then. Just don't do anything too reckless, all right?
Th-thanks, everyone!
Akari, Cutemon, and Dorulumon joined you!
""")

block('MSG/MESPAK00.PAK',0,73,'Digimon families and types',"""
Dragon
Beast
Holy
Dark
Aquatic
Machine
Bird
Insect
Plant
Dragon
Animal
Angel
Devil
Aqua
Machine
Wing
Insect
Plant
Sky Dragon
Sea Dragon
Dark Dragon
Beast Dragon
Dragonkin
Holy Dragon
Ice/Water
Metal Beast
Holy Beast
Ancient
Dark Beast
Darkness
Mutant Machine
Aurora Bird
Dark Bird
Holy Bird
Fire Insect
Tree
Light
Fire
Metal
Dark
Slime
Egg
""")

block('MSG/MESPAK01.PAK',0,0,'early quest objectives',"""
Talk to Biyomon in /n the Front Room.
Find the flight squad /n in Canyon Yard.
Report to Biyomon in /n the Front Room.
Find the Digimon /n Flight Squad!
Find the flight squad's /n leader and restore the /n Digimon Flight Squad.
No requirements to /n accept this quest.
Talk to Biyomon in /n the Front Room.
Find the flight squad /n in Grass Yard.
Report to Biyomon in /n the Front Room.
Find the Digimon /n Flight Squad!
Find the flight squad's /n leader and restore the /n Digimon Flight Squad.
No requirements to /n accept this quest.
Talk to Agumon in /n the Front Room.
Find the Ultimate DigiNoir /n in West Guruguru Amazon.
Give it to Agumon in /n the Front Room.
Find the /n Ultimate DigiNoir!
Find the /n Ultimate DigiNoir.
A Lively Shoutmon /n is in your party.
""")

block('MSG/MESPAK02.PAK',0,55,'opening story',"""
All right, let's go, Taiki! We'll knock those guys flat!
I've heard something is hidden in this Zone... Just what have you hidden here?! Tell me already!
I-I told you, I don't know! A low-ranking guy like me wouldn't know anything!
Then you're no use to us anymore! I'll throw you out of here and see whether you can fly!
Stop!
I-I won't let you hurt my friends!
...Hmph. Your voice is cracking. So you're the coward who got away?
I hear you ran away while your friends were being beaten. Are you going to let these ones take the fall for you now?
I don't want anyone to take my place, and I don't want to run away alone! I want to beat you and save everyone! Please, Taiki! Shoutmon! Fight with me!
Leave it to us, Spadamon! We've got Taiki! He's a General who can bring out the best in his Digimon! Right, Taiki?!
Your Digimon's fate is in their General's hands! Give orders to your Digimon on the Touch Screen!
Give orders using the Command Ring! Press Left or Right on the +Control Pad to rotate it, then press A to choose a command!
Choose Fight for attacks that use no MP! Pick it when you want to save MP in battle.
0000000000 /n 0000000000
Choose DigiXross to combine Digimon! To use this command, you must know a DigiXross move and have all its required Digimon in your party.
Choose Items to use consumables! They can cure paralysis, sleep, or confusion, restore HP or MP, and even revive fallen Digimon!
Choose Tactics for automatic battle orders! Full Power uses your strongest moves and targets enemies you can defeat. Conserve MP chooses moves with low MP costs. Guard focuses on defense. Escape tries to flee. If even one Digimon escapes, you can get out of battle!
The Formation command swaps the Digimon giving the order with another Digimon in your party!
One last thing to remember! Press B to change your orders. When you're ready, press X to begin the turn!
Hear the explanation again?
Explain again
Go to battle
All right, everyone! Here we go again! DigiXross!!
""")

block('MSG/MESPAK02.PAK',0,85,'opening story',"""
Think about your formation to gain an advantage! The Digimon attacking in the middle are your vanguard. Their Fight attacks deal heavy damage, and they can use DigiXross moves!
The Digimon supporting them from below are your rearguard. Their Fight attacks only deal half damage, and they cannot use DigiXross moves. In return, enemy attacks cannot hit them! Be careful: you cannot place Digimon in the rearguard without a vanguard!
Move the cursor with the +Control Pad. Select the Digimon you want to command, then press A to open the Command Ring!
If your Digimon do not need new orders, press X! Each Digimon will carry out its assigned command!
Hear the explanation again?
Explain again
Go to battle
All right, everyone! Here we go again! DigiXross!!
""")

block('MSG/MESPAK02.PAK',0,121,'opening story',"""
Hey, Taiki, do you know how to set up a tent?
See that tent mark over there?
Press A while standing on a tent mark to set up a tent and go inside. Inside, you can restore HP and MP or save your adventure so far.
I see... But I don't have a tent.
Once we take back Fort Island, I'll give you all the tents you want! For now, though, it's probably better not to use one, even if you have it. Apparently tents make it surprisingly easy for enemies to find you.
You can check the DigiFarm here.
DigiFarm? What's that?
It's a place where the Digimon you've befriended can grow stronger, faster!
You can have up to six DigiFarms. Each can hold eight Digimon, and you can befriend up to forty Digimon in all! Try letting your farm Digimon talk, train, work, or join expeditions. They can improve their stats, make items, and do all sorts of useful things! You can also move Digimon freely between your party, DigiFarms, expeditions, and DigiBank.
How do I get more DigiFarms?
This world has six power stations called Capacitor Towers that send energy to Sky Fort. Turn on a tower's generator to restore Sky Fort and add a DigiFarm. So if you find a Capacitor Tower, switch it on!
Have I already told you what a DigiFarm is?
A place where Digimon grow stronger, faster, right?
That's right! Using the DigiFarm well is important if you want your Digimon to become stronger!
Digimon gain EXP and levels on the DigiFarm, but that's not all! Talk and Train can raise stats. Jobs let you make rare items, and expeditions collect items from the Zones.
The DigiFarm sounds amazing...!
You need the DigiFarm to draw out a Digimon's full potential. And to get the DigiFarm running at full capacity, you have to switch on the Capacitor Tower generators!
You can check the DigiLab here.
DigiLab? What's that?
The DigiLab is where we research Digimon!
You can turn Melodies collected in battle into Digimon, use Melodies to complete DigiScores, or fuse Digimon together to create new ones!
Melodies?
A Melody is a Digimon in data form. Defeat a Digimon with a single hit, or finish it off with a move that has a Melody effect, and it becomes a Melody collected by your Xros Loader.
What about DigiScores?
A DigiScore is required for fusion. It tells you which Digimon you can create by fusing certain Digimon together. You can't read an incomplete DigiScore, so fill its missing parts with Melodies to complete it!
By the way, Spadamon, what's fusion?
It's a special kind of combination you can only perform at Sky Fort.
Collect Melodies in battle and complete a DigiScore, and you can create the Digimon it describes! But each DigiScore has requirements. Simply creating a Digimon from Melodies isn't enough. You may need to raise friendship, level, ATK, INT, or other stats first.
DigiCoding? What was that again?
DigiCoding means gathering the Melodies you get in battle and combining them into a Digimon! Defeat a Digimon in one hit, or finish it off with a move that has a Melody effect, and it becomes a Melody collected by your Xros Loader.
I see... Thanks for explaining, Spadamon!
The DigiLab is where you research Digimon, right?
Yes! DigiCompose creates incomplete DigiScores. DigiCoding turns Melodies into Digimon. Fusion combines Digimon to create another one. In the Digimon List, you can view their information or move them around!
""")

for index,english in {
0:'And now even Nene is acting strangely, too.',
1:'Nene Amano is a mysterious girl with plenty of secrets. Just when we thought she had opened up and become our friend, she disappeared. Ever since she returned, something has been wrong.',
2:'Zenjiro was acting strangely too, though.',
3:'He was like that from the start!',
4:'Hear that, Zenjiro? They are talking about you!',
5:'Now, enjoy your adventure with us in the mysterious world of Elestou Zone!',
81:'You lot! Never seen you before! Come with us to Sky Fort. You would not dare defy ROG, would you? ROG rules Elestou Zone!',
82:'ROG? As in "rogue"? Does that not mean a villain or a thief? You are practically calling yourselves crooks! Besides, we did not choose to come here! Everyone kept making jokes, and I got dragged here before I could even talk back! I should be asking what is going on!',
93:'So you did have allies. No matter... No one gets away with defying ROG! We will crush the lot of you!',
99:'Choose Special for special moves that use MP! Some hit groups of enemies, while others deal elemental damage. Hit an enemy with an element it is weak against to deal double damage!',
102:'Choose Tactics for automatic battle orders! Full Power selects your strongest moves and enemies you can defeat. Conserve MP uses only Fight attacks, saving MP. Guard focuses on defense. Escape tries to flee. If even one Digimon escapes, you can get out of battle!',
104:'One last thing to remember! Press B to change your orders. When you are ready, press X to begin the turn!',
109:'Whoo! Thanks, everyone!',
125:'Surrender quietly...? Is that a joke? Who waves a white flag every time they trip over a pebble?',
130:'R-right! ROG\'s Gotsumon squad could smash these guys to pieces in no time!',
137:'So you have got a whole gang! No wonder you looked so confident! But no matter how many enemies gather, ROG\'s Gotsumon squad will never lose!',
141:'If your Digimon do not need new orders, press X! Each Digimon will carry out its assigned command!',
152:'These items restore Digimon\'s HP and MP. At least, that is what those guys said.',
166:'We still have not found Nene or Sparrowmon, and Taiki is already saying his usual line again...',
173:'It is no use, Spadamon! Do you think you can escape? ROG already controls Elestou Zone! Our commander Minotaurmon has taken over Sky Fort! There is nothing you can do! Your only choice is to obey ROG!',
174:'S-stop it! Just leave me alone! I do not know anything about what you ROG invaders are looking for! Please, go away!',
175:'That is him!! Everyone, help that Digimon! He was the one asking me for help! We cannot leave him!',
176:'Huh...? Who are you?',
177:'He still had allies?',
178:'No, we should have captured all his allies already...',
179:'Then who are they?! Some of them do not even look like Digimon!',
180:'Whoever they are, it does not matter! We will show them how foolish it is to defy ROG!',
181:'Um... Taiki? Sorry to interrupt, but you are going to help someone you do not even know?',
182:'How could I ignore someone in trouble right in front of me?!',
183:'...Of course. Silly question. They really do look cornered. Let us hurry and help!',
184:'If you want to hurt him, you will have to face us!',
185:'Think about your formation to gain an advantage! The Digimon attacking in the middle are your vanguard. Their Fight attacks deal heavy damage, and they can use powerful DigiXross moves!',
186:'The Digimon below the vanguard are your rearguard. They support you without being hit by enemy attacks. But they cannot use DigiXross moves, and their Fight attacks only deal half the vanguard\'s damage. You cannot place Digimon in the rearguard unless there is a vanguard!',
191:'Whew... That was scary... Thank you for saving me... Um... Who are you? A-are you another enemy coming after me?!',
192:'Huh...? Did you not call us here...?',
193:'Take one more step toward him and I will blast you away!',
194:'You will hand that Digimon over to me. I will not let anyone else have the hidden power of Elestou Zone.',
195:'N-Nene! You are all right!',
196:'Thank goodness! We were worried. Is Sparrowmon with you?',
197:'...Who are you people? Do not talk to me as if we are friends.',
198:'Huh? What do you mean? It is us! We are your friends!',
199:'H-hey... Something is wrong. She does not seem to recognize us...',
}.items():
    blocks.append(dict(archive='MSG/MESPAK02.PAK',entry=1,start=index,category='opening story',english=[english]))

def main():
    records=collect_messages(Rom(rom_paths()['blue']))
    # Identical lines in the two route scripts share the reviewed translation.
    source_english={}
    for path in [ROOT/'translations/batch01.json']:
        for b in json.loads(path.read_text(encoding='utf-8'))['blocks']:
            for index,en in enumerate(b['english'],b['start']):
                key=f"{b['archive']}:{b['entry']:03d}:{index:05d}"
                source_english[records[key]['source']]=en
    already=set()
    for path in [ROOT/'translations/batch01.json']:
        for b in json.loads(path.read_text(encoding='utf-8'))['blocks']:
            already.update(f"{b['archive']}:{b['entry']:03d}:{i:05d}" for i in range(b['start'],b['start']+len(b['english'])))
    for b in blocks:
        for index,en in enumerate(b['english'],b['start']):
            key=f"{b['archive']}:{b['entry']:03d}:{index:05d}"
            if key not in records:raise ValueError(key)
            source_english[records[key]['source']]=en
    # Common UI elsewhere uses exactly the same source wording; route variants
    # are only reused on byte-identical Japanese, never fuzzy matched.
    authored=[]
    for b in blocks:
        for index,en in enumerate(b['english'],b['start']):
            key=f"{b['archive']}:{b['entry']:03d}:{index:05d}"
            if key in already:raise ValueError(f'Duplicate {key}')
            authored.append(dict(archive=b['archive'],entry=b['entry'],start=index,category=b['category'],english=[en]));already.add(key)
    for key,r in records.items():
        if key in already or r['source'] not in source_english:continue
        if r['archive']=='MSG/MESPAK02.PAK':category='opening story'
        elif r['archive']=='MSG/MESPAK01.PAK':category='shared menu wording'
        else:continue
        en=source_english[r['source']]
        authored.append(dict(archive=r['archive'],entry=r['entry'],start=r['index'],category=category,english=[en]));already.add(key)
    out=ROOT/'translations/batch02.json'
    out.write_text(json.dumps({'description':'Title and intro graphics, DigiLab and Xros Loader UI, reunion dialogue; originals retained by stable IDs.','blocks':authored},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(len(authored),'new text slots')

if __name__=='__main__':main()
