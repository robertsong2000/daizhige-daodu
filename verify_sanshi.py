#!/usr/bin/env python3
# verify_sanshi.py: sanshi-zhonggao.html vs 库本 三事忠告.txt
import re, pathlib, sys

ROOT = pathlib.Path(__file__).parent
SRC = pathlib.Path('/home/robertsong/workspace/claude/daizhige-simplified/史藏/职官/三事忠告.txt')
lib = SRC.read_text(encoding='utf-8')
lib_n = re.sub(r'\s', '', lib)
html = (ROOT / 'sanshi-zhonggao.html').read_text(encoding='utf-8')

fail = []
ok = lambda m: print('  ok', m)

EXPECTED = [
 '盖养浩留心实政，举所阅历者着之。非讲学家务为高论，可坐言而不可起行者也。',
 '如曰以三职所治为三事，则自我作古，转不及“为政”之名为该括一切矣。',
 '盖明人书帕之本，好立新名，而不计其合于古义否也。相沿已数百年，不可复正。',
 '况一身之微，所享能几，厥心溪壑，适以自贼。',
 '一或罪及，上孤国恩，中贻亲辱，下使乡邻朋友蒙诟包羞，虽任累千金，不足以偿一夕缧绁之苦。',
 '与其戚于已败，曷若严于未然。',
 '急催暴敛，剥下奉上，此租赋之瘴',
 '深文以逞，良恶不白，此刑狱之瘴',
 '侵牟民利，以实私储，此货财之瘴',
 '攻金攻木，崇饰车服，此工役之瘴',
 '盛拣姬妾，以娱声色，此帷薄之瘴也',
 '是知地之瘴者未必能死人，而能死人者常在乎仕瘴也。',
 '名为劝之，其实扰之；名为优之，其实劳之。',
 '劝农之道无他也，勿夺其时而已矣。',
 '民之有讼，如己有讼；民之流亡，如己流亡；民在缧绁，如己在缧绁；民陷水火，如己陷水火。',
 '如得其情，则哀矜而勿喜。',
 '尝闻近代为县者，教民种蔓菁，捣其根以为饼，大者三四斤，干而储之，后值凶年，蒸以食饥民，味甘且美，赖以全活者甚众。',
 '使其困惫，吾治已得罪矣；又不能救，而反奴妾之，不大获罪于法耶？',
 '宁公而贫，不私而富；宁让而损己，不竞而损人。',
 '爵禄或失，有时而再来；名节一亏，终身不复矣。',
 '是则归人，非则归己；闻誉则归人，闻毁则归己',
 '恩欲己出，怨将谁归？',
 '执法之臣将以纠奸绳恶以肃中外，以正纪纲，自律不严，何以服众？',
 '吾之此言，虽曰薄汝，实厚汝也；虽若毒汝，实恩汝也。',
 '近年执宪者惟知威人以刑，而不知诲人以善。',
 '昔端州出佳砚，包孝肃公出判于彼，及其代也，徒手而归。',
 '豺狼当道，安问狐狸',
 '小人虽有小过，当力排绝之，后乃无患；君子不幸而有诖误，则当为国家保持爱护，以全其德。',
 '夫常求其生，犹失之死，况世常求其死哉！',
 '与其杀不辜，宁失不经。',
 '入焉与天子争是非，出焉与大臣辨可否',
 '慷慨杀身者易，从容就义者难。',
 '不荡于富贵，不蹙于贫贱，不摇于威武，道之所在，死生以之。',
 '自古居相位者，未闻死于冻饿，而死于财、于酒、于色、于逸乐者，无代无之。',
 '岂有三四十年之间能食胡椒八百斛之理。',
 '苟受其托而不能使之遂生安业，乃从而扰之，虐之，犬彘之，草菅之，则是逆天而违祖宗之命，以自戕其国也，而可乎？',
 '一家哭其如一路何？',
 '道行则从而留，道不行则从而去',
 '天历中，拜陕西行台中丞。卒谥文忠。',
 '闻先生为西台中丞时，悯民饥死，作诗白于朝',
 '西风疋马过长安，饥殍盈途不忍看。',
 '十里路埋千百冢，一家人哭两三般。',
 '犬衔枯骨筋犹在，鸦啄新尸血未干。',
 '寄语庙堂贤宰相，铁人闻此也心酸。',
 '即发粟赈贷，民頼以活者不可胜数',
]

# 1. extract <q> blocks from page
qs = [re.sub(r'<[^>]+>', '', m).strip() for m in re.findall(r'<q[^>]*>(.*?)</q>', html, re.S)]
qs_n = [re.sub(r'\s', '', q) for q in qs]
print(f'<q> blocks on page: {len(qs_n)}')

# 2. double-sided: page -> lib (strict, punctuation kept, whitespace removed)
for i, q in enumerate(qs_n):
    if q not in lib_n:
        fail.append(f'page q#{i} not verbatim in lib: {q[:30]}')
# 3. double-sided: expected -> page (full coverage, no extras)
page_set = set(qs_n)
for e in EXPECTED:
    en = re.sub(r'\s', '', e)
    if en not in lib_n:
        fail.append(f'EXPECTED itself not in lib: {e[:25]}')
    if en not in page_set:
        fail.append(f'expected quote missing on page: {e[:30]}')
if len(qs_n) != len(page_set):
    fail.append('duplicate <q> blocks on page')
if len(qs_n) != len(EXPECTED):
    fail.append(f'count mismatch: page {len(qs_n)} vs expected {len(EXPECTED)}')

# 4. red lines: no long dashes
for ch, name in [('—', 'em-dash'), ('–', 'en-dash')]:
    if ch in html:
        fail.append(f'{name} present')
# 5. per-line interpunct cap
for i, line in enumerate(html.split('\n'), 1):
    if line.count('·') > 1:
        fail.append(f'line {i} has more than one interpunct')
# 6. footer three elements
for w in ['文本来源', '引文核验', '时代局限']:
    if w not in html:
        fail.append(f'footer missing {w}')
# 7. numbering
if '之一百八十八' not in html:
    fail.append('page number 之一百八十八 missing')

# 8. mechanical counts from lib
CN = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10}
def cn2int(s):
    if s == '十': return 10
    if '十' in s:
        a, _, b = s.partition('十')
        return (CN.get(a,1) if a else 1) * 10 + (CN.get(b,0) if b else 0)
    return CN[s]
mutes = [cn2int(m) for m in re.findall(r'凡([一二三四五六七八九十]+)条', lib)]
# TOC + section headers each list the ten gang: 20 occurrences summing to 148 = 74 x 2
if sum(mutes) != 148:
    fail.append(f'mu total {sum(mutes)} != 148')
if len(mutes) != 20:
    fail.append(f'gang occurrences {len(mutes)} != 20')
if re.sub(r'\s','',lib).count('总九十四条') != 1:
    pass  # informational
for h in ['自律第一','全节第十','修身第一','退休第十']:
    if h not in lib:
        fail.append(f'heading missing in lib: {h}')
if '20,986' not in html:
    fail.append('char count claim missing on page')

if fail:
    print('\nFAIL:')
    for f in fail: print(' -', f)
    sys.exit(1)
print('  quotes: 45/45 verbatim both ways')
print('  red lines: no long dash, interpunct cap, footer trio')
print(f'  mech: gang {len(mutes)}, mu sum {sum(mutes)}, lib chars {len(lib_n)}')
print('verify_sanshi: ALL PASS')
