#!/usr/bin/env python3
# verify_mideng.py: mideng-yinhua.html vs 库本 觅灯因话.txt
import re, pathlib

ROOT = pathlib.Path(__file__).parent
SRC = pathlib.Path('/home/robertsong/workspace/claude/daizhige-simplified/佛藏/藏外/觅灯因话.txt')
lib = SRC.read_text(encoding='utf-8')
lib_n = re.sub(r'\s', '', lib)
PUNCT = re.compile(r'[，。、；：？！「」『』《》〈〉（）…·　\s,.:;!?()""\'\'""''—]')
lib_np = PUNCT.sub('', lib)

html = (ROOT / 'mideng-yinhua.html').read_text(encoding='utf-8')

fail = []
loose = []

def norm(s):
    return re.sub(r'\s', '', s)

def norm_p(s):
    return PUNCT.sub('', s)

# 页面自报的三十组引文（先对库本，再对页面）
QUOTES = [
"自好子深有动于其衷，呼童举火，与客择而录之，凡二卷",
"盖灯已灭而复举，阅《新话》而因及，皆一时之高兴，志其实也，而何嫌乎不文",
"非幽冥果报之事，则至道名理之谈；怪而不欺，正而不腐",
"谛视之，皆成犬形，反自顾，亦无少异",
"夫负人之与负于人，一也。今日之梦，是天以象告，非其实也，犹可得而悔悟",
"今生已矣，俟来世为犬马以报德也",
"其冀食乞哀之情，怨悔颠连之状，宛若曩时梦中故态",
"千年田土八百翁，何须苦苦较雌雄。古今富贵知谁在，唐宋山河总是空。去时却似来时易，无他还与有他同。若人笑我亡先业，我笑他人在梦中。",
"群少年乃镂版刷印，备载由语及图籍年月，后附七言八句诗一首",
"每日晨出，先印数十本，临时则填注数目而已",
"乃断发剺面，自毁其容，杂处乞儿中，以故得免",
"波中偶有断木，附之，其行如飞，若有神运者。顷之，入芦渚中。渚有莲实，孙氏取以啖儿",
"吾宁与儿俱死矣!",
"水势冲涌不得近，以木为桥，木皆中折，而死者危坐如故",
"于怀中得一纸，具述李本官之逼与夫之冤，虽不成章，达意而已",
"粲粲梅花树，盈盈似玉人。甘心对冰雪，不爱艳阳春",
"与其嫁而导淫于人，宁自守而独居以死耳!",
"烧夜香非寻佳偶，披鹤氅星月下礼拜茅君；登春台不望远人，驾鸾车云霄上衹寻萧史",
"冬青花，不可折，南风吹凉积香雪。遥遥翠盖万年枝，上有凤巢下龙穴。君不见，犬之年，羊之月，霹雳一声天地裂!",
"昼则乞食，夜则往收其骨。或假寐树下，人以为丐者，不疑也",
"乃自杭抵越，涂遇暴骨，不论牛马，即以夹拾箩中，竟投陵上",
"夫天下不知几千万人，古往今来，生死代嬗，不知几千万世",
"盖天非他，理而已矣。福善祸淫，理之可信者也。栽培倾覆，人之自取者也",
"此所谓弥近理而大乱真者也",
"然有大限，无小限",
"子独不见风之送落英乎",
"或拂于帘栊之上，或堕于粪溷之中，其清浊大较然也，而风无心",
"乃若鬼神之灵，卜算之智，不过能前知其当然，非能预定其已然也",
"闭目则暗里成形，饮酒则杯中现影，顷刻顾盼，随处与俱",
"尔慎毋一念亏心，三尺之上，盖可畏哉",
]
assert len(QUOTES) == 30, len(QUOTES)

# 0. 引文清单对库本
lib_hits = {}
for i, q in enumerate(QUOTES):
    t = norm(q)
    if t in lib_n:
        lib_hits[i] = 'strict'
    elif norm_p(q) and norm_p(q) in lib_np:
        lib_hits[i] = 'loose'
        loose.append(('清单对库本', t[:24]))
    else:
        fail.append(f'清单[{i}] not in lib: {t[:30]}')
strict_n = sum(1 for v in lib_hits.values() if v == 'strict')
print(f'引文对库本: {strict_n} strict / {len(QUOTES)-strict_n} loose / {len(fail)} fail')

# 1. 每组引文出现在页面全文
body = re.sub(r'<script.*?</script>', '', html, flags=re.S)
body = re.sub(r'<style.*?</style>', '', body, flags=re.S)
page_n = norm(re.sub(r'<[^>]+>', '', body))
for i, q in enumerate(QUOTES):
    t = norm(q)
    if t in page_n:
        continue
    if norm_p(q) and norm_p(q) in norm_p(re.sub(r'<[^>]+>', '', body)):
        loose.append(('清单对页面', t[:24]))
    else:
        fail.append(f'清单[{i}] not on page: {t[:30]}')

# 2. 页面引用区反扫（blockquote 去 who 签 + <q> 元素），每个必须能锚回清单或库本
def strip_who(m):
    return re.sub(r'<span class="who">.*?</span>', '', m.group(0), flags=re.S)

spans = []
for m in re.finditer(r'<blockquote>(.*?)</blockquote>', html, re.S):
    spans.append(('blockquote', re.sub(r'<[^>]+>', '', strip_who(m))))
for m in re.finditer(r'<q>(.*?)</q>', html, re.S):
    spans.append(('q', re.sub(r'<[^>]+>', '', m.group(1))))
for k, (tag, s) in enumerate(spans):
    t = norm(s)
    if not t:
        continue
    ok = any(t in norm(q) or norm(q) in t for q in QUOTES)
    if not ok:
        tp = norm_p(s)
        ok = any(tp and (tp in norm_p(q) or norm_p(q) in tp) for q in QUOTES)
    if not ok:
        fail.append(f'{tag}#{k} 不属于任何清单引文: {t[:36]}')
print(f'引用区反扫: {len(spans)} 处')

# 3. 「」反扫：每个「」片段必须是清单引文子串或库本子串（异体归一退化为恒等，库本已简体）
corner_fail = 0
for m in re.finditer(r'「(.*?)」', re.sub(r'<[^>]+>', '', body), flags=re.S):
    c = norm(m.group(1))
    if not c:
        continue
    ok = any(c in norm(q) for q in QUOTES) or c in lib_n or norm_p(c) in lib_np
    if not ok:
        corner_fail += 1
        fail.append(f'「」无锚: {c[:30]}')
print('「」反扫 完成')

# 4. 排版红线
if '—' in html or '–' in html:
    fail.append('出现长划线/短划线')
for ln, line in enumerate(html.splitlines(), 1):
    if line.count('·') > 1:
        fail.append(f'第{ln}行 · 超限')
# 正文区（去 script/style/引文区/URL）半角标点白名单
core = re.sub(r'<blockquote>.*?</blockquote>', '', body, flags=re.S)
core = re.sub(r'<q>.*?</q>', '', core, flags=re.S)
core = re.sub(r'<script.*?</script>', '', core, flags=re.S)
core = re.sub(r'<style.*?</style>', '', core, flags=re.S)
core = re.sub(r'github\.com\S*', '', core)
core_txt = re.sub(r'<[^>]+>', '', core)
bad_hw = re.findall(r'[!?.,;:()\'"]', core_txt)
if bad_hw:
    fail.append(f'正文区半角标点越界 {len(bad_hw)} 处: {"".join(bad_hw)[:30]}')
# 零外部依赖
for pat in [r'\ssrc\s*=', r'<link', r'@import', r'url\((?!#)', r'https?://(?!github)']:
    hits = re.findall(pat, html)
    if hits:
        fail.append(f'外部依赖 {pat}: {len(hits)} 处')

# 5. 机数：库本去空白 15805，页面自述一致
nw = len(lib_n)
assert nw == 15805, nw
if '一万五千八百零五' not in page_n:
    fail.append('页面缺库本字数自述')
print(f'库本去空白: {nw}')

# 6. 校字记自我申报
for kw in ['句读补', '半角标点照录', '时代局限' ]:
    if kw not in html:
        fail.append(f'校字记/页脚缺: {kw}')

print(f'loose {len(loose)} 条: {[x[0]+":"+x[1] for x in loose]}')
if fail:
    print('FAIL')
    for f in fail:
        print(' -', f)
    raise SystemExit(1)
print('PASS')
