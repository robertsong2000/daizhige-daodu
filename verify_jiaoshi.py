#!/usr/bin/env python3
# 焦氏易林 页面核验：引文逐字对库 + 条目归属 + 引文全覆盖 + 排版红线
import re, unicodedata

PAGE = 'jiaoshi-yilin.html'
LIB = '../daizhige-simplified/易藏/术数/焦氏易林.txt'

VAR = {"旡": "无"}
PUNCT = re.compile(r"[\s，。、；：？！「」『』（）()《》〈〉·…—–\-,.:;?!'\"“”‘’【】●■　\t]")

def norm(s):
    s = unicodedata.normalize("NFKC", s)
    s = "".join(VAR.get(c, c) for c in s)
    return PUNCT.sub("", s)

GUAXU = ['乾','坤','屯','蒙','需','讼','师','比','小畜','履','泰','否','同人','大有','谦','豫','随','蛊',
         '临','观','噬嗑','贲','剥','复','无妄','大畜','颐','大过','坎','离','咸','恒','遁','大壮','晋',
         '明夷','家人','睽','蹇','解','损','益','夬','姤','萃','升','困','井','革','鼎','震','艮','渐',
         '归妹','丰','旅','巽','兑','涣','节','中孚','小过','既济','未济']
GXMAP = {'干': '乾', '旡妄': '无妄', '遯': '遁'}
def gx(s): return GXMAP.get(s, s)
NAMES = set(GUAXU) | set(GXMAP)

raw = open(LIB, encoding='utf-8').read()
entries = {}

# ---------- A. marker 区（此起为X卦 ... X卦终）：标题行与繇辞行分离 ----------
head = raw
zone_end = 0
pos = 0
while True:
    m = re.search(r'■+此起为(.+?)卦■+', raw[pos:])
    if not m:
        break
    ben = m.group(1)
    start = pos + m.end()
    e = re.search(r'■+' + ben + r'卦终■+', raw[start:])
    if not e:
        raise AssertionError(f'{ben} 卦终缺失')
    zone = raw[start:start + e.start()]
    pending = None
    for ln in zone.splitlines():
        t = ln.strip()
        if not t:
            continue
        mt = re.fullmatch(r'(\S{1,6})之(\S{1,6})', t)
        if mt and gx(mt.group(1)) == ben:
            pending = gx(mt.group(2))
            continue
        if pending:
            entries[(ben, pending)] = t
            pending = None
    pos = start + e.end()
    zone_end = pos
print(f'marker 区条目: {len(entries)}')

# ---------- B. 缩进区：蛊卦终后，行首之卦名，每 64 行一循环，环序校验 ----------
j = re.search(r'■+蛊卦终■+', raw).start()
assert j > 0
ben_start = GUAXU.index('临')
rows = []
for ln in raw[j:].splitlines()[1:]:
    m = re.match(r'^[\s.。]{0,3}(\S+?)　+(.+)$', ln)
    if m and m.group(1) in NAMES:
        rows.append((m.group(1), m.group(2).strip()))
for k, (name, txt) in enumerate(rows):
    cyc, k2 = divmod(k, 64)
    bi = ben_start + cyc
    assert bi < 64, f'循环数超出: {k}'
    ben = GUAXU[bi]
    exp = ben if k2 == 0 else (GUAXU[k2-1] if k2-1 < bi else GUAXU[k2])
    nm = gx(name)
    assert nm == exp, f'缩进区第{k}行卦序错位: 得{name} 应{exp}'
    entries.setdefault((ben, nm), txt)
print(f'缩进区条目: {len(rows)} 行, 环序全部对齐, 合计 {len(entries)} 条')
assert len(entries) >= 3900, f'条目数异常: {len(entries)}'

# ---------- C. 页面引文逐字核对归属 ----------
html = open(PAGE, encoding='utf-8').read()
QUOTES = [
    ("乾之干",   "道徙多阪，胡言连蹇。译喑且聋，莫使道通。请遏不行，求事无功。"),
    ("乾之泰",   "不风不雨，白日皎皎，宜出驱驰，通理大道。"),
    ("乾之比",   "中夜犬吠，盗在墙外。神明佑助，消散皆去。"),
    ("乾之讼",   "龙马上山，绝无水泉，喉焦唇干，舌不能言。"),
    ("乾之无妄", "传言相误，非干径路。鸣鼓逐狐，不知迹处。"),
    ("乾之贲",   "室如悬磬，既危且殆。早见之士，依山谷处。"),
    ("乾之小畜", "据斗运枢，顺天无忧。所行造德，与乐并居。"),
    ("乾之随",   "乘龙上天，两蛇为辅，踊跃云中，游观沧海，民乐安处。"),
    ("临之临",   "弱水之西，有西王母。生不知老，与天相保。行者危殆，利居善喜。"),
    ("临之大有", "三十无室，长女独宿。心劳未得，忧在胸臆。"),
    ("未济之艮",   "鹿求其子，虎庐之西。唐伯李耳，贪不我许。"),
    ("临之师",   "六人俱行，各遗其囊。鸿鹄失珠，无以为明。"),
    ("临之履",   "驾龙骑虎，周遍天下。为神人使，西见王母。不忧危殆。"),
    ("临之同人", "管鲍相知，至德不离。三言于桓，齐国以安。"),
]
RX = '(乾|坤|屯|蒙|需|讼|师|比|小畜|履|泰|否|同人|大有|谦|豫|随|蛊|临|观|噬嗑|贲|剥|复|无妄|大畜|颐|大过|坎|离|咸|恒|遁|大壮|晋|明夷|家人|睽|蹇|解|损|益|夬|姤|萃|升|困|井|革|鼎|震|艮|渐|归妹|丰|旅|巽|兑|涣|节|中孚|小过|既济|未济)'
for label, txt in QUOTES:
    m = re.fullmatch(RX + r'之(.+)', label)
    assert m, f'标签异常: {label}'
    key = (m.group(1), gx(m.group(2)))
    assert key in entries, f'{label} 不在库本解析结果中'
    nq, ne = norm(txt), norm(entries[key])
    assert nq == ne or nq in ne, f'{label} 引文与库本不符:\n  页面: {nq}\n  库本: {ne}'
print(f'{len(QUOTES)} 条引文逐字命中对应条目（乾之X 8 + 临之X 6）')

# ---------- D. 页面引文载体全覆盖 ----------
quoted = set(norm(t) for _, t in QUOTES)
carriers = []
carriers += re.findall(r'id="q-txt">([^<]+)<', html)
carriers += re.findall(r'class="ci">([^<]+)<', html)
carriers += re.findall(r'class="t">([^<]+)<', html)
for s in re.findall(r'class="shici">([^<]+)', html):
    carriers.append(s.strip())
carriers += re.findall(r'txt:"([^"]+)"', html)
bad = [c for c in carriers if norm(c) and norm(c) not in quoted]
assert not bad, '未核验的引文载体: ' + ' | '.join(c[:40] for c in bad)
print('页面所有引文载体均已核验（签纸初始签、六签卡、两段 shici、结尾签、抽签池）')

# ---------- E. 排版红线 ----------
assert '—' not in html and '–' not in html, '出现长划线'
body = html.split('</head>')[1]
body = re.sub(r'<script.*?</script>', '', body, flags=re.S)
for i, ln in enumerate(re.sub(r'<[^>]+>', '\n', body).splitlines(), 1):
    assert ln.count('·') <= 1, f'渲染行{i}出现{ln.count("·")}个·: {ln.strip()[:40]}'
ext = re.findall(r'(?:src|href)="(http[^"]+)"', html)
assert not ext, f'外部依赖: {ext}'
assert re.search(r'殆知阁简体库', html) and re.search(r'引文核验', html) and re.search(r'阅读提醒', html), '页脚三件套缺失'
print('排版红线通过: 无长划线, 每行至多1个·, 无外部依赖, 页脚三件套齐全')
print('ALL PASS')
