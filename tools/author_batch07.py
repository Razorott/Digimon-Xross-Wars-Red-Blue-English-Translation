"""Add the next reviewed story, mission, battle, farm, and name translation batch."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from xros_text import ROOT

DWD = 'https://raw.githubusercontent.com/joaomlsantos/Digimon-World-Dawn-Dusk-Research-Notes/master/move_name_lst.txt'
REF = 'https://digimon.net/reference_en/'
CARD = 'https://world.digimoncard.com/cards/'

# The English names below are standard forms used in Digimon releases. Keep
# unusual Xros Wars spellings visible in review notes until a direct source is
# found; do not silently pass a romanized guess off as a verified dub name.
NAMES = {
    'ルークチェスモン': ('RookChessmon', REF, ''),
    'ダイペンモン': ('DaiPenmon', 'https://digimon.net/reference_en/detail.php?directory_name=daipenmon', ''),
    'カオスドラモン': ('Chaosdramon', REF, ''),
    'グレイモン': ('Greymon', REF, 'The game may use this for a Xros Wars-era individual; the species spelling is standard.'),
    'ファイラモン': ('Flaremon', REF, ''),
    'レキスモン': ('Lekismon', REF, ''),
    'ブライモン': ('Buraimon', 'https://digimon.net/reference_en/detail.php?directory_name=buraimon', 'Use the current Reference Book spelling Buraimon.'),
    'ヴァジラモン': ('Vajramon', REF, ''),
    'アルゴモンＵＴ': ('Argomon (Ultimate)', REF, 'Stage suffix expanded for readability.'),
    'ブテンモン': ('Butenmon', REF, ''),
    'ＢＡＮレオモン': ('BanchoLeomon', REF, 'Expanded the game shorthand BAN to the established species name.'),
    'クレニアムモン': ('Craniamon', REF, ''),
    'バルバモン': ('Barbamon', REF, ''),
    'ＴＧヴェスパモン': ('TigerVespamon', REF, 'Expanded the game shorthand TG to the established species name.'),
    'デュナスモン': ('Dynasmon', REF, ''),
    'エグザモン': ('Examon', REF, ''),
    'オメガモン': ('Omnimon', REF, ''),
    'アーマゲモン': ('Armageddemon', REF, 'Use the established English Digimon name.'),
    'アポカリモン': ('Apocalymon', REF, ''),
    'ＺＤミレニアモン': ('ZeedMillenniummon', REF, 'Expanded the game shorthand ZD to the established form Zeed.'),
    'ヴァロドゥルモン': ('Valdurmon', REF, ''),
    'カオスモン': ('Chaosmon', REF, ''),
    'チンロンモン': ('Azulongmon', REF, 'Use the established English name for the Four Sovereigns Digimon.'),
    'バイフーモン': ('Baihumon', REF, ''),
    'スーツェーモン': ('Zhuqiaomon', REF, 'Use the established English name for the Four Sovereigns Digimon.'),
    'シェンウーモン': ('Ebonwumon', REF, 'Use the established English name for the Four Sovereigns Digimon.'),
    'イージスドラモン': ('Aegisdramon', REF, ''),
    'アルマモン': ('Armamon', REF, ''),
    'メタルグレイモン': ('MetalGreymon', REF, ''),
    'グレイモンＬ': ('Greymon L', REF, 'The L variant suffix is retained because its meaning is not established here.'),
    'ＤＫティラノモン': ('DarkTyrannomon', REF, 'Expanded the game shorthand DK to the established species name.'),
    'ＨＬエンジェモン': ('MagnaAngemon', CARD, 'Use the established Western name; confirm the game-specific HL variant suffix before release.'),
    'ルーチェモンＦＭ': ('Lucemon Falldown Mode', REF, ''),
    'ＥＸティラノモン': ('EXTyrannomon', REF, 'Expanded the game form prefix.'),
    'ヴァーミリモン': ('Vermillimon', REF, ''),
    'ワルシードラモン': ('WaruSeadramon', REF, ''),
    'リヴァイアモン': ('Leviamon', REF, ''),
    'ヘラクルカブテリモン': ('HerculesKabuterimon', REF, ''),
}

# These Dawn/Dusk spellings are carried across only where the Japanese title
# matches an attack in that game's extracted English move table. Other moves
# are readable working renderings and are explicitly marked for later review.
MOVES = {
    'ソードオブメテオ': ('Sword of Meteor', '', 'Working rendering; no Dawn/Dusk title match confirmed.'),
    'ラウディロッカー': ('Rowdy Rocker', '', 'Working rendering of a Xros Wars move name; cross-game match not confirmed.'),
    '∞キャノン': ('Infinity Cannon', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'スーパーノヴァ': ('Supernova', '', 'Working rendering; no Dawn/Dusk title match confirmed.'),
    'あまのはばきり': ('Ama-no-Habakiri', '', 'Retains the Japanese mythological weapon name; cross-game match not confirmed.'),
    'メガブラスター': ('Mega Blaster', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'ケティルフレア': ('Keter Flare', '', 'Working rendering of this move name; spelling needs a direct source check.'),
    'ヘヴィスピーカー': ('Heavy Speaker', '', 'Working rendering of this Xros Wars move name.'),
    'ドルルトルネード': ('Dorulu Tornado', '', 'Working rendering; preserves Dorulumon-derived move terminology.'),
    'クロスブレード': ('Cross Blade', '', 'Working rendering; no Dawn/Dusk title match confirmed.'),
    'オメガバースト': ('Omega Burst', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'ラプラスのま': ("Laplace's Demon", '', 'Standard rendering of the named concept; move localization not independently verified.'),
    'ネクロエクリプス': ('Necro Eclipse', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'イヅナ': ('Izuna', DWD, ''),
    'ガイアフォース': ('Terra Force', DWD, 'Matched to the English Dawn/Dusk attack title for the same Japanese attack.'),
    'ブリットハンマー': ('Bullet Hammer', '', 'Literal working rendering; not changed to Bullet Punch without an exact Japanese move match.'),
    'ギガデス': ('Giga Death', '', 'Working rendering; distinct from the source entry メガデス translated as Mega Death.'),
    'ゴッドフレイム': ('God Flame', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'サプライズキャノン': ('Surprise Cannon', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'テラブラスター': ('Terra Blaster', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'ギガブラスター': ('Giga Blaster', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'コキュートスブレス': ('Cocytus Breath', '', 'Working rendering of this mythological move name.'),
    'フェンリルソード': ('Fenrir Sword', DWD, ''),
    'エンド・ワルツ': ('End Waltz', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'ジュデッカプリズン': ('Judekka Prison', '', 'Working rendering; this spelling follows the Digimon move name.'),
    'ヘルズグレネード': ("Hell's Grenade", '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'ジェノサイドギア': ('Genocide Gear', DWD, ''),
    'こんごう': ('Kongo', '', 'Romanized pending a direct English localization source.'),
    'フラウカノン': ('Flau Cannon', '', 'Working rendering; spelling and source-game localization need confirmation.'),
    'ヘルマスカレード': ('Hell Masquerade', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'ししじゅうはざん': ('Shishi Juhazan', '', 'Romanized pending a direct English localization source.'),
    'シャインブレイカー': ('Shine Breaker', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'カイザーネイル': ('Kaiser Nail', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'ギガデストロイヤー': ('Giga Destroyer', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'サンダージャベリン': ('Thunder Javelin', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'ガオガトルネード': ('GaogaTornado', DWD, ''),
    'アニマルネイル': ('Animal Nail', DWD, ''),
    'パラダイスロスト': ('Paradise Lost', '', "Established Digimon attack phrase; this game's localization still needs a direct source check."),
    'ヘビィウインド': ('Heavy Wind', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'レイジトルネード': ('Rage Tornado', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'ダークネスエディ': ('Darkness Eddy', '', 'Working rendering; spelling of the final word needs a direct source check.'),
    'イビルデータボム': ('Evil Data Bomb', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'ヘビィグラビティ': ('Heavy Gravity', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'レイジデモンブレス': ('Rage Demon Breath', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'ソニックキック': ('Sonic Kick', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'メガナックルボム': ('Mega Knuckle Bomb', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'ヘビィギガアッパー': ('Heavy Giga Uppercut', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'レイジグラップル': ('Rage Grapple', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'ソードマスカレイド': ('Sword Masquerade', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'レインボゥハンド': ('Rainbow Hand', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'マルクトクリスタル': ('Malkuth Crystal', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'ヘル＆サンダー': ('Hell & Thunder', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'ヘブン＆ブレイク': ('Heaven & Break', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'アイス＆ファイア': ('Ice & Fire', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    '∞ソードレイン': ('Infinity Sword Rain', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'Ωデスブレイド': ('Omega Death Blade', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'データトゥデータ': ('Data to Data', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'トライブリザード': ('Tribe Lizard', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'シグマグラップル': ('Sigma Grapple', '', 'Working rendering of this move name; cross-game match not confirmed.'),
    'オメガクラッシャー': ('Omega Crusher', '', 'Working rendering of this move name; cross-game match not confirmed.'),
}

FARM = {
    'さいだいＨＰが　あがった！<0A>^6　→　^7': 'Max HP increased!<0A>^6 to ^7',
    'さいだいＭＰが　あがった！<0A>^6　→　^7': 'Max MP increased!<0A>^6 to ^7',
    'ちからが　あがった！<0A>^6　→　^7': 'Attack increased!<0A>^6 to ^7',
    'まもりが　あがった！<0A>^6　→　^7': 'Defense increased!<0A>^6 to ^7',
    'すばやさが　あがった！<0A>^6　→　^7': 'Speed increased!<0A>^6 to ^7',
    'ゆうじょうが　あがった！<0A>^6　→　^7': 'Friendship increased!<0A>^6 to ^7',
    'かしこさが　あがった！<0A>^6　→　^7': 'Wisdom increased!<0A>^6 to ^7',
    'ん～？　これは…': "Hmm? What's this...",
    'ん～？　これは<0A>いったい　なんなのかな…？': "Hmm? What could<0A>this possibly be...?",
    'ウォーッ　なんだこりゃーッ！？': 'Whoa! What is this?!',
    '…ん？　これは…？': '...Huh? What is this...?',
    'あら　アレは<0A>いったい　なにかしら…？': 'Oh, what could<0A>that be over there...? ',
    '…あら　なんでしょう？<0A>この　あたりから…<0A>とても　やさしくて<0A>いいニオイが　しますわ…': 'Oh, what could it be?<0A>A gentle, lovely scent<0A>is coming from around<0A>here... how curious... ',
    '…これは　タイキさんの<0A>ニオイですわね…！<0A>またタイキさんが　きたら<0A>おあいてしてもらいたいですわ！<0A>おかげで　ゆうじょうちが<0A>すこし　あがったようです…！': "This is Taiki's scent!<0A>If he comes back, I hope<0A>he'll spend time with me!<0A>My Friendship went up a bit!",
    'わたし　いつも<0A>おもってるんです…<0A>わたしたちが　シアワセに<0A>くらせているのは…<0A>ぜんぶ　タイキさんの<0A>おかげなんだって…！<0A>そうですわ　タイキさんに<0A>おれいを　いいましょう…！': "I always think about it...<0A>We're happy here because<0A>of everything Taiki has<0A>done for us! I should<0A>thank him...!",
    '…タイキさん　いつも<0A>ありがとうございます…！<0A>わたしたち　とっても<0A>カンシャしていますわ！<0A>…タイキさんに　いまの<0A>コトバ　とどいたでしょうか…？<0A>おかげで　ゆうじょうちが<0A>ずいぶん　あがったみたいです…': "Thank you as always,<0A>Taiki! We're so grateful!<0A>I wonder if he heard me...<0A>My Friendship went up<0A>quite a bit!",
    '…これは　いったい<0A>なんでしょう…？': 'What on earth<0A>could this be...? ',
    'あら　これは　デジモンの<0A>キーチェーン　ですわね…<0A>おもしろいのでしょうか？<0A>すこし　やってみますわ…': "Oh, it's a Digimon<0A>key chain... It looks<0A>interesting. I'll try it!",
}

QUEST = {
    'おねがいクエストを<0A>７コ以上クリア': 'Complete at least<0A>7 Request Quests',
    'コンデンサタワー': 'Capacitor Tower',
    'クモノスいせき西でマネージャーの<0A>レディーデビモンに　あってね': 'Meet the manager,<0A>LadyDevimon, in Spiderweb<0A>Ruins West',
    'おねがいクエストを<0A>２５コ以上クリア': 'Complete at least<0A>25 Request Quests',
    'ピエモンを　みつけだして<0A>れんぞくクイズに　クリアしよう': 'Find Piedmon and<0A>win his quiz streak',
    'フロントルームにいる<0A>ブイモンと　はなしてね': 'Talk to Veemon in<0A>the Front Room',
    'おねがいクエストを<0A>１６コ以上クリア': 'Complete at least<0A>16 Request Quests',
    'フロントルームにいる<0A>パタモンと　はなしてね': 'Talk to Patamon in<0A>the Front Room',
    'フロントルームにいる<0A>パタモンに　ほうこくしてね': 'Report to Patamon in<0A>the Front Room',
    'フロントルームにいる<0A>ブイモンに　ほうこくしてね': 'Report to Veemon in<0A>the Front Room',
    'レディーデビモンに<0A>ほうこくしよう': 'Report to LadyDevimon',
    'トコナかいがん１': 'Tokona Coast 1',
    'システムΩ': 'System Omega',
    'アイテムを　うる': 'Sell Items',
    'いいえ　やめます': 'No, cancel.',
    'フロントルームにいる<0A>トゲモンと　はなしてね': 'Talk to Togemon in<0A>the Front Room',
    'フロントルームにいる<0A>トゲモンに　わたそう': 'Give it to Togemon in<0A>the Front Room',
    'フロントルームにいる<0A>ユキダルモンと　はなしてね': 'Talk to Frigimon in<0A>the Front Room',
    'ナックルかいがん東で<0A>ニセモノを　さがしてね': 'Find the impostor at<0A>Knuckle Coast East',
    'フロントルームにいる<0A>ユキダルモンに　ほうこくしよう': 'Report to Frigimon in<0A>the Front Room',
    'ユキダルモンの<0A>ニセモノを　たおせ！': 'Defeat the fake Frigimon!',
    'ユキダルモンの　ニセモノを<0A>みつけだして　とっちめよう': 'Find and punish the<0A>fake Frigimon',
    'ドクロかいていで<0A>ＢＥヴァンデモンに　あおう': 'Meet BE Myotismon<0A>in Skull Seabed',
    'じごくの　さたも<0A>カネしだい？': 'Can money get you<0A>out of anything?',
}

STORY = {
    'う～ん　みつかったクル<0A>ゆーゲッみぃクル～▼': "Aww, you found me!<0A>You got me, Cutemon!",
    'うけたクエストは　クロスローダー<0A>がめんから　『じょうほう』の…<0A>『クエストじょうほう』を<0A>えらべば　かくにん　できるわよ<0A>１回うけた　クエストを<0A>キャンセルしたいときは…<0A>そのクエストを　もう１回<0A>えらべば　キャンセルできるわ': 'To check accepted Quests,<0A>open Information on the<0A>Xros Loader, then choose<0A>Quest Info. To cancel a<0A>Quest, select it again.<0A>You can only cancel one<0A>you have already accepted.',
    'ブッブゥーッ！　ちがーうッ！<0A>ばっきん　５０００ｂｉｔ～▼<0A>…なんてね？<0A>ホントに　やると　おもった？<0A>まあ　じょうだんヌキで<0A>やるんだけどね　ぷッぷーッ♪': "Buzzz! Wrong! That's a<0A>5,000-bit fine! Just<0A>kidding! You thought I<0A>was serious? Well, jokes<0A>aside, I really will do it!",
    '…と　おもったのに<0A>おカネ　たりないじゃない！<0A>あ～あ　つまんないのー！<0A>ぷッぷーッ♪': "...Or I would, but you<0A>don't have enough bits!<0A>Boo, how boring!",
    'ノォオーッ！　ちがーうッ！<0A>ばっきん　３０００ｂｉｔ～♪<0A>…あれ？　ぼくが　シャレで<0A>いってると　おもってる？<0A>それじゃあ　ガチで<0A>しょじきんから　ひいとくね▼<0A>ハッハーッ♪': "Nooo! Wrong! That's a<0A>3,000-bit fine! Think<0A>I'm joking? I'll really<0A>take it from your funds!",
    '…あれ？　ガチで　とろうと<0A>おもったのに　おカネ　たりないや<0A>うまいこと　にげたな～？<0A>ハッハーッ♪': "Huh? I really was going<0A>to take it, but you don't<0A>have enough bits. Lucky<0A>escape! Ha ha!",
    'こまってる　デジモンを<0A>けんさくするで　ございますっ！<0A>むむむッ…　ピコーン！<0A><0A>こまってる　デジモンを<0A>はっけんしましたぞ！<0A>クエストモニタに　あたらしい<0A>クエストが　はっせいしましたぞ！': 'Searching for Digimon<0A>who need help! Hmm...<0A>Ping! Found one! A new<0A>Quest has appeared on<0A>the Quest Monitor!',
    'クエストモニタに　あたらしい<0A>クエストが　はっせいしましたぞ！': 'A new Quest has appeared<0A>on the Quest Monitor!',
    'うまれかわった　ペンモンの<0A>アイテムショップや！<0A>あたらしゅうて　きょうりょくな<0A>しょうひんに　リニューアルしたで': "Welcome to Penguinmon's<0A>brand-new Item Shop!<0A>We've restocked with<0A>stronger, newer goods!",
    'よろしく　たのむ': 'Please, count on me.',
    'よろしく　たのむぞ！': "I'm counting on you!",
}

DESCRIPTIONS = {
    'いのちのしずくで　みかたひとりの　ＨＰをかいふくする': "Restore one ally's HP<0A>with a Life Drop.",
    'バトルちゅうに　つかって　しょうりすると<0A>チームぜんたいに　ＥＸＰが　もらえる': 'Use this in battle and win<0A>to give the whole team EXP.',
    'よび<0A>ダミーテキスト': 'Call<0A>Dummy Text',
    'ソードオブメテオ<0A>ダミーテキスト': 'Sword of Meteor<0A>Dummy Text',
    'ぜんかいかいふく<0A>ダミーテキスト': 'Full Recovery<0A>Dummy Text',
    'デジクロスで　クルモンになり　こうげきする<0A>ついかで　水のダメージを　あたえる': 'DigiXross into Calumon<0A>and attack, dealing extra<0A>water damage.',
    'デジクロスで　カブテリモンになり　こうげきする': 'DigiXross into Kabuterimon<0A>and attack.',
    'デジクロスで　レオモンになり　こうげきする': 'DigiXross into Leomon<0A>and attack.',
    'デジクロスで　ピエモンになり　こうげきする': 'DigiXross into Piedmon<0A>and attack.',
    'デジクロスで　ムゲンドラモンになり　こうげきする<0A>ついかで　デンキのダメージを　あたえる': 'DigiXross into Machinedramon<0A>and attack, dealing extra<0A>electric damage.',
    'デジクロスで　デュークモンになり　こうげきする<0A>ついかで　そくしさせる　こうかがある': 'DigiXross into Gallantmon<0A>and attack. It may cause<0A>instant death.',
    'デジクロスで　Ａボルケーモンになり　こうげきする<0A>ついかで　ホノオのダメージを　あたえる': 'DigiXross into A. Volcanomon<0A>and attack, dealing extra<0A>fire damage.',
    'ＨＰかいふく<0A>せつめいぶん': 'HP Recovery<0A>Description',
    'ＭＰかいふく<0A>せつめいぶん': 'MP Recovery<0A>Description',
    'まひかいふく<0A>せつめいぶん': 'Paralysis Recovery<0A>Description',
    'すいみんかいふく<0A>せつめいぶん': 'Sleep Recovery<0A>Description',
    'こんらんかいふく<0A>せつめいぶん': 'Confusion Recovery<0A>Description',
    'くらやみかいふく<0A>せつめいぶん': 'Blindness Recovery<0A>Description',
    'ぜんぶかいふく<0A>せつめいぶん': 'Status Recovery<0A>Description',
    'かんぜんかいふく<0A>せつめいぶん': 'Full Recovery<0A>Description',
    'そせい<0A>せつめいぶん': 'Revival<0A>Description',
    'げーとでぃすく<0A>せつめいぶん': 'Gate Disk<0A>Description',
    'でじめもり<0A>せつめいぶん': 'DigiMemory<0A>Description',
    'かりぶき<0A>せつめいぶん': 'Temporary Shelter<0A>Description',
    'かりぼうぐ<0A>せつめいぶん': 'Temporary Armor<0A>Description',
    'グッズテスト<0A>せつめいぶん': 'Goods Test<0A>Description',
    'スコアテスト０<0A>せつめいぶん': 'Score Test 0<0A>Description',
    'スコアテスト１<0A>せつめいぶん': 'Score Test 1<0A>Description',
    'スコアテスト２<0A>せつめいぶん': 'Score Test 2<0A>Description',
    'スコアテスト３<0A>せつめいぶん': 'Score Test 3<0A>Description',
    'スコアテスト４<0A>せつめいぶん': 'Score Test 4<0A>Description',
    'スコアテスト５<0A>せつめいぶん': 'Score Test 5<0A>Description',
    'スコアテスト６<0A>せつめいぶん': 'Score Test 6<0A>Description',
    'スコアテスト７<0A>せつめいぶん': 'Score Test 7<0A>Description',
    'こんらんこうかが　かけやすくなる　ヤリ<0A>こうげきが　あたりやすくなる': 'Spear that more easily<0A>causes Confusion.<0A>Attacks hit more often.',
    'カースこうかが　かけやすくなる　カタナ<0A>クリティカルが　でやすくなる': 'Katana that more easily<0A>inflicts Curse.<0A>Critical hits are likelier.',
    'よびわく<0A>せつめいぶん': 'Call Slot<0A>Description',
}


def main():
    path = ROOT / 'translations' / 'work_queue.tsv'
    rows = list(csv.DictReader(path.open(encoding='utf-8-sig'), delimiter='\t'))
    entries = {}
    for jp, (en, url, note) in NAMES.items():
        entries[('Digimon names', jp)] = (en, [url] if url else [], note)
    for jp, (en, url, note) in MOVES.items():
        entries[('Battle moves', jp)] = (en, [url] if url else [], note)
        # Battle move strings are heuristically classified as equipment in a
        # second menu table; use the same label only for those actual names.
        entries[('Items and equipment', jp)] = (en, [url] if url else [], note)
    entries[('Items and equipment', 'さくじょ')] = ('Delete', [], '')
    entries[('Items and equipment', 'いんせき？')] = ('Meteorite?', [], 'Working rendering of the item name; confirm from its in-game icon and effect.')
    for jp, en in FARM.items():
        entries[('DigiFarm reports', jp)] = (en, [], '')
    for jp, en in QUEST.items():
        entries[('Menus, quests and battle prompts', jp)] = (en, [], '')
    for jp, en in STORY.items():
        entries[('Story and dialogue', jp)] = (en, [], '')
    for jp, en in DESCRIPTIONS.items():
        entries[('Move and item descriptions', jp)] = (en, [], '')

    blocks = []
    for row in rows:
        spec = entries.get((row['category'], row['japanese']))
        if not spec:
            continue
        english, sources, note = spec
        english = english.replace('<0A>', '\n')
        for key in row['ids'].split(';'):
            archive, entry, index = key.rsplit(':', 2)
            blocks.append({
                'archive': archive, 'entry': int(entry), 'start': int(index),
                'category': row['category'], 'english': [english],
                'sources': sources, 'review_note': note,
            })

    if not blocks:
        raise SystemExit('No batch07 strings matched the current work queue.')
    out = ROOT / 'translations' / 'batch07.json'
    out.write_text(json.dumps({
        'description': 'Title logo safety-margin correction; more Digimon names, researched and review-marked battle moves, DigiFarm reports, quest/menu text, dialogue, and DigiXross descriptions.',
        'blocks': blocks,
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Wrote {len(blocks)} translated slots to {out.name}.')


if __name__ == '__main__':
    main()
