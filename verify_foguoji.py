#!/usr/bin/env python3
# 核验 foguoji.html：引文逐字比对库内文件 + 排版红线
import re, sys, unicodedata

PAGE = 'foguoji.html'
SRC = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/地理/佛国记.txt'

QUOTES = [
 '法显昔在长安，慨律藏残缺，于是遂以弘始二年岁在已亥，与慧景、道整、慧应、慧嵬等同契，至天竺寻求戒律。',
 '沙河中多有恶鬼、热风，遇则皆死，无一全者。上无飞鸟，下无走兽。遍望极目，欲求度处，则莫知所拟，唯以死人枯骨为标帜耳。',
 '入食堂时，威仪齐肃，次第而坐，一切寂然，器钵无声。',
 '离城三四里，作四轮像车，高三丈余，状如行殿，七宝庄校，悬缯幡盖。',
 '像入城时，门楼上夫人、采女摇散众华，纷纷而下。',
 '般遮越师，汉言“五年大会”也。',
 '葱岭冬夏有雪，又有毒龙，若失其意，则吐毒风、雨雪、飞沙、砾石。遇此难者，万无一全。',
 '昔人有凿石通路施傍梯者，凡度七百，度梯已，蹑悬縆过河',
 '其道艰阻，崖岸险绝，其山唯石，壁立千仞，临之目眩，欲进则投足无所。',
 '慧景一人不堪复进，口出白沫，语法显云：“我亦不复活，便可时去，勿得俱死。”于是遂终。法显抚之悲号：“本图不果，命也，奈何！”',
 '尽作中天竺语，中天竺所谓中国。',
 '从是以南，名为中国。中国寒暑调和，无霜、雪。',
 '凡诸中国，唯此国城邑为大。',
 '如何边地人，能知出家为道，远求佛法？',
 '贫人以少华投中便满，有大富者，欲以多华而供养，正复百千万斛，终不能满。',
 '城中都无王民，甚如丘荒，只有众僧、民户数十家而已。',
 '汝从何国来？','从汉地来。','奇哉！边地之人，乃能求法至此！',
 '自伤生在边地',
 '共诸同志游历诸国，而或有还者，或有无常者，今曰乃见佛空处，怆然心悲。',
 '法显生不值佛，但见遗迹处所而已。',
 '法显本求戒律，而北天竺诸国皆师师口传，无本可写，是以远步，乃至中天竺。',
 '故法显住此三年，学梵书、梵语，写律。',
 '自今已去至得佛，愿不生边地。',
 '故遂停不归。法显本心欲令戒律流通汉地，于是独还。',
 '法显去汉地积年，所与交接悉异域人，山川草木，举目无旧，又同行分析，或留或亡，顾影唯已，心常怀悲。忽于此玉像边，见商人以晋地一白绢扇供养，不觉凄然，泪下满目。',
 '泥洹已来一千四百九十七年，世间眼灭，众生长悲。',
 '若千百年，当复来到汉地。',
 '即斫绳断',
 '法显亦以军持及澡灌并余物弃掷海中，但恐商人掷去经像，唯一心念观世音及归命汉地众僧',
 '大海弥漫无边，不识东西，唯望曰、月、星宿而进。',
 '但见大浪相搏，晃然火色',
 '坐载此沙门，使我不利，遭此大苦。当下比丘置海岛边，不可为一人令我等危验。',
 '汝若下此比丘，亦并下我！不尔，便当杀我！',
 '见藜藿菜依然，知是汉地。',
 '此青州长广郡界，统属刘家。',
 '法显发长安，六年到中国，停六年还，三年达青州。凡所游历，减三十国。',
 '故竹帛疏所经历，欲令贤者同其闻见。',
 '顾寻所经，不觉心动汗流。所以乘危履险，不惜此形者，盖是志有所存，专其愚直，故投命于不必全之地，以达万一之冀。',
 '自大教东流，未有忘身求法如显之比。',
 '慧应在佛钵寺无常。',
 '慧达、宝云、僧景遂还秦土。',
 '智严、慧简、慧嵬遂返向高昌，欲求行资。',
 '僧绍一人，随胡道人向罽宾。',
 '衣服粗与汉地同',
]

def norm(s):
    return ''.join(ch for ch in s if '一' <= ch <= '鿿')

fails = []
html = open(PAGE, encoding='utf-8').read()
src = open(SRC, encoding='utf-8').read()
nsrc = norm(src)

# 1. 页面所有 .q 引文块（blockquote.q 与 span.q，含嵌套）逐段比对
raw = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html, flags=re.S)
spans = re.findall(r'<span class="q">(.*?)</span>', raw, flags=re.S)
bqs = re.findall(r'<blockquote class="q">(.*?)</blockquote>', raw, flags=re.S)
qtexts = []
for t in spans:
    qtexts.append(norm(re.sub(r'<[^>]+>', '', t)))
for t in bqs:
    t = t.split('<span', 1)[0]
    qtexts.append(norm(re.sub(r'<[^>]+>', '', t)))
print(f'页面引文块（.q）共 {len(qtexts)} 段')
miss_src = [q for q in QUOTES if norm(q) not in nsrc]
if miss_src:
    fails.append('以下引文在库内文件中不存在: ' + ' | '.join(miss_src[:5]))
for i, qt in enumerate(qtexts):
    if len(qt) < 3:
        continue
    if qt not in nsrc:
        fails.append(f'页面引文块 #{i+1} 与库内文件不符: {qt[:40]}...')
unused = [q for q in QUOTES if norm(q) not in set(qtexts)]
if unused:
    print(f'清单中未出现在页面 .q 里的引文 {len(unused)} 条: ' + ' / '.join(u[:16] for u in unused))
    fails.append('QUOTES 清单有引文未用于页面（需全部上页或从清单移除）')

# 2. 红线：禁长划线
for ch, name in [('—', 'EM DASH —'), ('–', 'EN DASH –'), ('‒', 'FIGURE DASH'), ('⸺','TWO-EM DASH'), ('⸻','THREE-EM DASH')]:
    if ch in html:
        fails.append(f'发现禁用字符 {name}')

# 3. 红线：每行 · ≤1（按渲染文本行近似：按标签间文本行检查）
plain = re.sub(r'<[^>]+>', '', raw)
for ln in plain.splitlines():
    if ln.count('·') > 1:
        fails.append(f'一行内出现 {ln.count("·")} 个 ·: {ln.strip()[:50]}')

# 4. 结构断言
if html.count('<div class="tk">') != 7:
    fails.append(f'行程票头应为 7 个，实际 {html.count(chr(60)+"div class=\"tk\">")}')
if html.count('<div class="lrow">') != 7:
    fails.append('同行者账应为 7 行')
if '四十三' not in html:
    fails.append('页内缺少篇号「四十三」')
if len(norm(html)) < 3000:
    fails.append('页面正文疑似过短')

if fails:
    print('\nFAIL')
    for f in fails:
        print(' ×', f)
    sys.exit(1)
print('\n全部通过：引文逐字命中库内文件；无长划线；每行 · ≤1；结构断言通过')
