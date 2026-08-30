#!/usr/bin/env python3
# verify_shuxue.py — 数学九章页核验：引文逐字对库 + 库本计数 + 数学复核 + 排版红线
import re, sys, math

PAGE = 'shuxue-jiuzhang.html'
LIB = '../daizhige-simplified/子藏/算法/数学九章.txt'
GUIXIN = '../daizhige-simplified/史藏/志存记录/癸辛杂识.txt'

html = open(PAGE, encoding='utf-8').read()
lib = open(LIB, encoding='utf-8').read()
gx = open(GUIXIN, encoding='utf-8').read()

PUNCT = set('，。、；：？！「」『』（）【】〔〕·,.:;?!()<>「」""''…—・/')
def norm(s, strip_html=True):
    if strip_html:
        s = re.sub(r'<[^>]+>', '', s)
    out = []
    for ch in s:
        if ch.isspace() or ch in PUNCT:
            continue
        out.append(ch)
    return ''.join(out)

fails = []
def chk(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond:
        fails.append(msg)

# ---------- 1. 收集页面 .q 引文（标签平衡扫描） ----------
def collect_q(html):
    out = []
    for m in re.finditer(r'<(\w+)([^>]*\bclass="[^"]*\bq\b[^"]*"[^>]*)>', html):
        tag = m.group(1)
        depth = 1
        i = m.end()
        while depth > 0:
            nm = re.search(r'<(/?)%s\b[^>]*>' % tag, html[i:])
            if not nm:
                break
            depth += -1 if nm.group(1) else 1
            i += nm.end()
        out.append(html[m.end():i - len('</%s>' % tag) if depth == 0 else i])
    return out

qs = collect_q(html)
print(f'页面 .q 引文块：{len(qs)}')

# ---------- 2. 引文逐字对库 ----------
QUOTES = [
 ('hero·数与道', 'lib', '要其归，则数与道非二本也'),
 ('问一·访学', 'lib', '早岁侍亲中都，因得访习于太史，又尝从隐君子受数学'),
 ('问一·兵难', 'lib', '时际兵难，歴岁遥塞，不自意全于矢石之间，更险离忧，荏苒十禩'),
 ('问一·成书', 'lib', '积多而惜其弃，因取八十一题，厘为九类，立术具草，间以图发之'),
 ('问一·落款', 'lib', '时淳祐七年九月，鲁郡秦九韶叙'),
 ('问三·案情', 'lib', '有米铺诉被盗去米一般三箩，皆适满，不记细数。今左壁箩剰一合，中间箩剰一升四合，右壁箩剰一合'),
 ('问三·三器', 'lib', '索到三器：马杓满容一升九合，木履容一升七合，漆椀容一升二合'),
 ('问三·天元草', 'lib', '立天元一于左上空其左下'),
 ('问三·求一术', 'lib', '大衍求一术云：以竒于右上，定母于右下，立天元一于左上。先以右行上下两位，以少除多，所得商数，乃递互乘归左行，使右上得一而止，左上为乘率'),
 ('问三·荅', 'lib', '共失米九石五斗六升三合'),
 ('问四·三斜术', 'lib', '以小斜幂并大斜幂，减中斜幂，余半之，自乘于上；以小斜幂乘大斜幂，减上，余四约之为实，一为从隅，开平方得积'),
 ('问五·天池问', 'lib', '今州郡多有天池盆以测雨水。但知以盆中之水为得雨之数，不知器形不同，则受雨多少亦异，未可以所测便为平地得雨之数'),
 ('问五·荅防字', 'lib', '平地雨防三寸'),
 ('问六·张九韶卷头', 'lib', '数学九章卷三上　宋　张九韶　撰田域'),
 ('问六·营廷卷头', 'lib', '数学九章卷七下　宋　秦九韶　撰营廷'),
 ('问六·拟题注', 'lib', '【按旧本此问无题今増】'),
 ('问七·提要谜', 'lib', '九韶始末未详。惟据原序自称其籍曰鲁郡，然序题淳祐七年，鲁郡已久入于元，九韶葢述其祖贯，未详实为何许人也'),
 ('问七·虚谈', 'lib', '宋代诸儒尚虚谈而薄实用'),
 ('问七·沈括', 'lib', '数百年中惟沈括究心是事，而自梦溪笔谈以外未有成书'),
 ('问七·崛起', 'lib', '九韶当宋末造，独崛起而明绝学'),
 ('问七·机巧', 'gx', '性极机巧，星象、音律、算术，以至营造等事，无不精究'),
 ('问七·殂梅', 'gx', '窜之梅州。在梅治政不辍，竟殂于梅'),
 ('问八·借根方', 'lib', '后元郭守敬用之于弧矢，李冶用之于勾股方圆，欧逻巴新法易其名曰借根方'),
 ('问八·源开', 'lib', '其源实开自九韶，亦可云有功于算术者矣'),
 ('coda·源开', 'lib', '其源实开自九韶'),
]
nlib, ngx = norm(lib, strip_html=False), norm(gx, strip_html=False)
srcs = {'lib': nlib, 'gx': ngx}
for name, src, text in QUOTES:
    n = norm(text)
    chk(n in srcs[src], f'引文[{name}] ⊂ {src}')
    chk(n in norm(html), f'引文[{name}] 在页内')

# 页面 .q 总数与清单一致（含 <q class="q">）
chk(len(qs) == len(QUOTES) + 1, f'.q 块数 {len(qs)} == 清单 26（+1 立天元一短语）')
chk('立天元一' in qs, '短语引文[立天元一] 被 .q 收集')

# ---------- 3. 库本计数 ----------
chk(len(lib) == 121740, f'全帙 {len(lib)} 字符')
chk(len(re.sub(r'\s', '', lib)) == 115611, '去空白 115,611')
wen = len(re.findall(r'\n　　问[^\n]{6,}', lib))
chk(wen == 81, f'问起句 {wen} == 81（序自报八十一题）')
chk(len(re.findall(r'答曰', lib)) == 67, '答曰 67 见')
chk(len(re.findall(r'荅曰', lib)) == 14, '荅曰 14 见（67+14=81）')
chk(len(re.findall(r'术曰', lib)) == 84, '术曰 84 见')
chk(len(re.findall(r'草曰', lib)) == 83, '草曰 83 见')
chk(len(re.findall(r'\n　　按', lib)) == 109, '四库馆臣按语 109 处')
chk(lib.count('防') == 203, '讹块「防」203 见')
chk(len(re.findall(r'数学九章卷[一二三四五六七八九十]+[上下][ 　]+宋　张九韶　撰', lib)) == 1, '张九韶署名恰 1 见')
chk(len(re.findall(r'数学九章卷[一二三四五六七八九十]+[上下][ 　]+宋　秦九韶　撰', lib)) == 16, '秦九韶卷头 16 见（卷八上缺卷头）')
chk('数学九章卷八上　' not in lib, '卷八上无卷头行')
chk(len(re.findall(r'撰营廷', lib)) == 1, '营廷讹 1 见')
chk(len(re.findall(r'【按[^】]*无题[^】]*】', lib)) == 7, '馆臣代拟题名 7 处')

# ---------- 4. 数学复核 ----------
chk(19 * 17 * 12 == 3876, '三定母相乘 = 衍母 3876')
chk(3060 + 1140 * 14 + 3553 == 22573, '剩米乘用数并之 = 22573')
chk(22573 % 3876 == 3193, '满衍母去之 = 3193 合（三石一斗九升三合）')
s = (13 + 14 + 15) / 2
chk(math.isqrt(round(s * (s-13) * (s-14) * (s-15))) == 84, '三斜求积：开方 7056 得 84 方里')
chk(84 * 300 * 300 // 240 // 100 == 315, '84 方里 = 315 顷')
chk('数学九章' in html and '秦九韶' in html, '书名作者在页')

# ---------- 5. 页面申报数字 ----------
ptext = norm(html, strip_html=False)
for token, msg in [('八十一', '页内申报 81'), ('六十七', '页内申报 67'), ('八十四', '页内申报 84'),
                   ('八十三', '页内申报 83'), ('一百零九', '页内申报 109'), ('二百零三', '页内申报 203'),
                   ('之七十四', '页内篇号 74'), ('有七问原本无题', '页内申报 7 拟题')]:
    chk(token in ptext, msg)

# ---------- 6. 排版红线 ----------
chk('—' not in html, '无长划线 —')
chk('–' not in html, '无短划线 –')
body = re.sub(r'<style[\s\S]*?</style>', '', html)
body = re.sub(r'<script[\s\S]*?</script>', '', body)
bad_dots = []
for ln in body.split('\n'):
    txt = re.sub(r'<[^>]+>', '', ln)
    if txt.count('·') > 1:
        bad_dots.append(ln.strip()[:40])
chk(not bad_dots, f'每行·≤1（违例：{bad_dots}）' if bad_dots else '每行·≤1')
for need in ['殆知阁古代文献简体库', '逐字核验', '时代局限']:
    chk(need in html, f'页脚要素：{need}')

print()
if fails:
    print(f'共 {len(fails)} 项未过')
    sys.exit(1)
print('全部通过')
