#!/usr/bin/env python3
# 核验 shunzong-shilu.html（顺宗实录导读）：引文双侧、「」反扫、红线、机数
import re, sys
from html.parser import HTMLParser

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/shunzong-shilu.html'
LIBS = {
    'main': '/home/robertsong/workspace/claude/daizhige-simplified/史藏/别史/顺宗实录.txt',
    '韩愈集': '/home/robertsong/workspace/claude/daizhige-simplified/集藏/四库别集/韩愈集.txt',
    '白氏长庆集': '/home/robertsong/workspace/claude/daizhige-simplified/集藏/四库别集/白氏长庆集.txt',
}
SRC = {k: open(v, encoding='utf-8').read() for k, v in LIBS.items()}

def norm(s):
    out = []
    for ch in s:
        if ch.isspace():
            continue
        o = ord(ch)
        if 0x2000 <= o <= 0x206F:  # 一般标点/破折号
            continue
        if 0x3000 <= o <= 0x303F:  # CJK 标点、书名号、
            continue
        if 0xFF01 <= o <= 0xFF65:  # 全角标点与全角数字（脚注标记 [１９８]）
            continue
        if o in (0x005B, 0x005D, 0x25CB):  # [ ] ○
            continue
        out.append(ch)
    return ''.join(out)

NORM = {k: norm(v) for k, v in SRC.items()}

# ---------- .q 收集器：VOID 跳过、最近 q 祖先收字 ----------
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
class QC(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []      # (tag, qref|None)
        self.results = []    # [dict(text, src)]
    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        cls = (dict(attrs).get('class', '') or '')
        if 'q' in cls.split():
            ref = {'text': [], 'src': 'main'}
            if 'data-src' in dict(attrs):
                ref['src'] = dict(attrs)['data-src']
            self.results.append(ref)
            self.stack.append((tag, ref))
        else:
            self.stack.append((tag, None))
    def handle_endtag(self, tag):
        if tag in VOID:
            return
        while self.stack and self.stack[-1][0] != tag:
            self.stack.pop()
        if self.stack:
            self.stack.pop()
    def handle_data(self, data):
        for tag, ref in reversed(self.stack):
            if ref is not None:
                ref['text'].append(data)
                return

page = open(PAGE, encoding='utf-8').read()
errors, warnings = [], []

qc = QC()
qc.feed(page)
qc.close()
qtexts = []
for r in qc.results:
    t = norm(''.join(r['text']))
    qtexts.append((t, r['src']))
    if not t:
        errors.append(f"空 .q 块（src={r['src']}）")
        continue
    if r['src'] not in NORM:
        errors.append(f"未知 data-src：{r['src']}")
        continue
    if t not in NORM[r['src']]:
        errors.append(f".q 未命中库本[{r['src']}]：{t[:48]}…")

# ---------- 「」反扫（剔 style/script 后） ----------
visible = re.sub(r'<style[\s\S]*?</style>', '', page)
visible = re.sub(r'<script[\s\S]*?</script>', '', visible)
spans = re.findall(r'「([^」]*)」', visible)
for sp in spans:
    n = norm(sp)
    if not n:
        continue
    if n not in NORM['main']:
        errors.append(f"「」反扫未命中主库：{sp[:40]}")

# ---------- 关键引文双侧（必须在页面 .q 中出现） ----------
EXPECTED = [
    ('上自二十年九月得风疾，因不能言，使四面求医药，天下皆闻知。', 'main'),
    ('上知内外忧疑，紫衣麻鞋，不俟正冠出九仙门，召见诸军使，京师稍安。', 'main'),
    ('众皆称赞，独叔文无言。', 'main'),
    ('太子识当侍膳问安，不宜言外事。陛下在位久，如疑太子收人心，何以自解？', 'main'),
    ('非先生，寡人无以知此。', 'main'),
    ('今年虽旱，而谷甚好。', 'main'),
    ('市里讙呼，皆袖瓦砾遮道伺之，实由间道获免。', 'main'),
    ('出后宫并教坊女妓六百人，听其亲戚迎于九仙门。百姓相聚，讙呼大喜。', 'main'),
    ('岁进钱物，谓之「羡余」，而经入益少', 'main'),
    ('名为「宫市」，而实夺之。', 'main'),
    ('我有父母妻子，待此然后食。今以柴与汝，不取直而归，汝尚不肯，我有死而已！', 'main'),
    ('此蛇所以致鸟雀而捕之者，今留付汝，幸善饲之，勿令饥渴。', 'main'),
    ('叔文索饭，韦相已与之同餐合中矣。', 'main'),
    ('宰相杜佑、高郢、珣瑜皆停筯以待', 'main'),
    ('吾岂可复居此位！', 'main'),
    ('顾左右取马径归，遂不起。', 'main'),
    ('方今书诏，宜痛自引过罪己，以感人心。昔成汤以罪己致兴', 'main'),
    ('行在制诏始下，闻者虽武人悍卒，无不挥涕感激。', 'main'),
    ('上初即位，与郑余庆、阳城同征，诏始下，而城、贽皆卒。', 'main'),
    ('吾谏官也，不可令天子杀无罪之人而信用奸臣。', 'main'),
    ('抚字心劳，征科政拙，考下下。', 'main'),
    ('朝廷有直臣，天下必太平矣！', 'main'),
    ('太平万岁！太平万岁！', 'main'),
    ('伾中风矣！', 'main'),
    ('时扶坐殿，群臣望拜而已，未尝有进见者。', 'main'),
    ('皇太子涕泣，不答拜。', 'main'),
    ('叔文计无所出，唯曰：「奈何，奈何！」无几而母死', 'main'),
    ('出师未用身先死，长使英雄泪满襟。', 'main'),
    ('朱熹云：「按杜诗，『用』作『捷』。」', 'main'),
    ('每至岭南图，执谊皆命去之，闭目不视。', 'main'),
    ('试就观之，乃崖州图也。', 'main'),
    ('至贬，果得崖州焉。', 'main'),
    ('元和元年正月甲申，太上皇崩于兴庆宫咸宁殿，年四十六。', 'main'),
    ('其山陵制度，务从俭约，并不用以金银锦彩为饰。', 'main'),
    ('七月壬申，葬丰陵，谥曰至德大圣大安孝皇帝，庙曰顺宗。', 'main'),
    ('「景」，原文当作「丙」，以避世祖讳，改为「景」。下同。', 'main'),
    ('宁容蠹政，以害齐人', 'main'),
    ('「驰归」、「之」三字，原本及诸本并无。', 'main'),
    ('宜令皇太子即皇帝位。朕称太上皇，居兴庆宫', 'main'),
    ('王伾开州司马，王叔文渝州司户，并员外置，驰驿发遣。', 'main'),
    ('皇太子既监国，遂逐之，明年乃杀之。', 'main'),
    ('维永贞二年，岁次景戌，正月景寅朔', 'main'),
    ('夫为史者，不有人祸，则有天刑，岂可不畏惧而轻为之哉！', '韩愈集'),
    ('可怜身上衣正单，心忧炭贱愿天寒', '白氏长庆集'),
]
for q, src in EXPECTED:
    n = norm(q)
    if not any(t == n and s == src for t, s in qtexts):
        if any(t == n for t, s in qtexts):
            errors.append(f"期望引文源标错（应为 {src}）：{q[:30]}")
        else:
            errors.append(f"期望引文未以 .q 出现在页面：{q[:36]}")

# ---------- 排版红线 ----------
body_no_style = re.sub(r'<style[\s\S]*?</style>', '', page)
for i, l in enumerate(page.split('\n'), 1):
    if l.count('—'):
        errors.append(f"长划线 — 第{i}行")
    if l.count('–'):
        errors.append(f"短划线 – 第{i}行")
plain = re.sub(r'<[^>]+>', '', body_no_style)
for i, l in enumerate(plain.split('\n'), 1):
    if l.count('·') > 1:
        errors.append(f"一行多· 第{i}行")
if 'http' in page:
    errors.append("出现外部链接")
if '<script' in page:
    errors.append("出现 script")

# ---------- 机数 ----------
lib = SRC['main']
sep = lib.find('-------------------------------------------------------')
body, notes = lib[:sep], lib[sep:]
nb, nn = re.sub(r'\s', '', body), re.sub(r'\s', '', notes)
han = lambda s: sum(1 for c in s if '㐀' <= c <= '鿿' or '\U00020000' <= c <= '\U0002ffff')
checks = [
    ('23,054', str(len(nb) + len(nn))), ('14,483', str(len(nb))), ('11,347', str(han(nb))),
    ('8,571', str(len(nn))),
]
for shown, real in checks:
    if shown not in page:
        errors.append(f"页面缺机数 {shown}（库算 {real}）")
mb = re.findall(r'\[[０-９]+\]', body)
mn = re.findall(r'\[[０-９]+\]', notes)
if len(mb) != 198 or len(mn) != 198:
    errors.append(f"标记数异常 正文{len(mb)} 校记{len(mn)}")
if max(int(re.sub(r'\D', '', m)) for m in mn) != 198:
    errors.append("校记最大号非198")
nall = re.sub(r'\s', '', lib)
freq = {'上曰': 1, '泣': 6, '涕': 6, '叔文': 79, '宫市': 6, '讙呼': 2, '太平万岁': 2,
        '碁': 5, '俱文珍': 4, '宦者': 7, '风疾': 1, '齐人': 1}
for w, c in freq.items():
    real = nall.count(w)
    if real != c:
        errors.append(f"词频 {w} 库算{real} 页写{c}")
if '景 22 见' not in page:
    errors.append("页面缺「景 22 见」")
if nall.count('景') != 22:
    errors.append("景计数不符")
# 页面声称的数字与库算一致
claims = [('叔文', '79'), ('上曰', '1'), ('泣 6 见', None), ('涕 6 见', None)]
if '<span class="bignum">79</span>' not in page:
    errors.append("叔文79 大数缺失")
if '<span class="bignum">198</span>' not in page:
    errors.append("198 大数缺失")
# 结构
if page.count('class="lg"') != 11:
    errors.append(f"账目行 {page.count(chr(34)+'lg'+chr(34))} ≠11")
if page.count('class="day"') + page.count('class="day hot"') != 4:
    errors.append("正月格非4")
if page.count('class="step"') != 6:
    errors.append("六步非6")
for k in ['壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌']:
    if f'<div class="num">{k}</div>' not in page:
        errors.append(f"缺声次 {k}")
if len(re.findall(r'卷[一二三四五]（', body)) != 5:
    errors.append("卷头非5")
extb = {c: lib.count(c) for c in set(lib) if 0x20000 <= ord(c) <= 0x3FFFF}
if len(extb) != 3 or sum(extb.values()) != 7:
    errors.append(f"Ext-B 机数异常 {extb}")
# 纪年两制：丙寅朔→甲申 = 十九日
gz = '甲乙丙丁戊己庚辛壬癸'; dz = '子丑寅卯辰巳午未申酉戌亥'
def gzn(name):
    return gz.index(name[0]) + 60 * 0  # 用标准序
order = [gz[k % 10] + dz[k % 12] for k in range(60)]
d1, d2 = order.index('丙寅') + 1, order.index('甲申') + 1
if d2 - d1 + 1 != 19:
    errors.append(f"干支推日异常 丙寅→甲申 = {d2-d1+1}")
if '十九天' not in page and '十九日' not in page:
    errors.append("页面缺十九日推算")
# 页脚三要素
foot = page[page.find('<footer'):]
for need in ['daizhigev20', '逐字核验', '时代局限']:
    if need not in foot:
        errors.append(f"页脚缺 {need}")
if '之一百一十六' not in page:
    errors.append("缺篇号 之一百一十六")

# ---------- 汇总 ----------
print(f".q 块：{len(qtexts)}　「」反扫：{len(spans)}　期望引文：{len(EXPECTED)}")
if warnings:
    print("WARN:")
    for w in warnings:
        print("  ", w)
if errors:
    print("FAIL", len(errors))
    for e in errors:
        print("  ✗", e)
    sys.exit(1)
print("ALL PASS")
