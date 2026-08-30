# -*- coding: utf-8 -*-
"""verify_dongpo.py  东坡志林导读页核验：引文双侧逐字 + 机数 + 排版红线"""
import re, sys
from html.parser import HTMLParser

PAGE = 'dongpo-zhilin.html'
LIB = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/东坡志林.txt'
ALLOWED_LATIN = {'github.com', 'robertsong2000', 'daizhigev20'}

html_txt = open(PAGE, encoding='utf-8').read()
lib = open(LIB, encoding='utf-8').read()

errors, warns = [], []
def chk(cond, msg):
    if not cond: errors.append(msg)

# ---------- norm：只留 CJK 表意字符 ----------
def norm(s):
    out = []
    for c in s:
        o = ord(c)
        if 0x3400 <= o <= 0x9FFF or 0x20000 <= o <= 0x2FFFF or 0x2A000 <= o <= 0x3FFFF:
            out.append(c)
    return ''.join(out)

LIBN = norm(lib)

# ---------- QCollector：html.parser 栈配平，VOID 不入栈 ----------
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
class QC(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # (tag, is_q)
        self.quotes = []         # (line, text)
        self.cur = []
    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get('class', '') or ''
        is_q = 'q' in cls.split()
        if tag not in VOID:
            self.stack.append((tag, is_q))
        if is_q:
            self.cur.append([])
    def handle_startendtag(self, tag, attrs):
        pass
    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break
    def handle_data(self, data):
        if not self.cur: return
        # 回溯最近的 q 祖先（本元素自身在栈中，含其上所有祖先）
        if any(isq for _, isq in self.stack):
            self.cur[-1].append(data)
    def close(self):
        super().close()

parser = QC()
parser.feed(html_txt)
parser.close()
# cur 与栈不成对时兜底：q 开标签必先入 cur，闭合由栈外判定缺失
texts = [''.join(parts) for parts in parser.cur]
texts = [t for t in texts if norm(t)]

# 防御：若收集到 0 条，说明收集器坏了，直接失败
chk(len(texts) > 50, f'QCollector 收集异常：仅 {len(texts)} 条')

# ---------- 引文双侧逐字 ----------
for i, t in enumerate(texts):
    n = norm(t)
    chk(n in LIBN, f'引文未命中库本 #{i}: {t[:40]}')

# 页面查重（完全重复 = fail，包含 = warn）
norms = [norm(t) for t in texts]
dups = {n for n in norms if norms.count(n) > 1}
for d in dups:
    errors.append(f'引文整段重复: {texts[norms.index(d)][:40]}')
for i, a in enumerate(norms):
    for j, b in enumerate(norms):
        if i != j and len(a) < len(b) and a and a in b:
            warns.append(f'引文包含关系 #{i} ⊂ #{j}: {texts[i][:24]}')

# ---------- 机数：卷帙与字数 ----------
chk(len(lib) == 48759, f'库本总长 {len(lib)} != 48759')
chk(len(re.sub(r'\s', '', lib)) == 44524, '去空白 != 44524')
han = sum(1 for c in lib if 0x3400 <= ord(c) <= 0x9FFF or 0x20000 <= ord(c) <= 0x2FFFF)
chk(han == 36982, f'汉字 {han} != 36982')

GATES = '记游 怀古 修养 疾病 梦寐 学问 命分 送别 祭祀 兵略 时事 官职 致仕 隐逸 佛教 道释 异事 异事下 技术 四民 女妾 贼盗 夷狄 古迹 玉石 井河 卜居 亭堂 人物 论古'.split()
lines = lib.split('\n')
toc = lines[:138]
titles, cur = [], None
for l in toc:
    s = l.strip()
    if re.fullmatch('卷[一二三四五]', s):
        cur = []; titles.append(cur); continue
    if not s or s == '目录' or s.startswith('东坡志林') or s in GATES: continue
    if '  ' in s:
        cur += [x for x in re.split(r'\s{2,}', s) if x and x not in GATES]
    else:
        cur.append(s)
counts = [len(v) for v in titles]
chk(counts == [53, 48, 42, 46, 13], f'分卷篇数 {counts} != [53,48,42,46,13]')
chk(sum(counts) == 202, f'总篇数 {sum(counts)} != 202')
chk(len(GATES) == 30, '门数 != 30')

for pat in ['全帙 <b>48,759</b> 字', '去空白 <b>44,524</b>', '汉字 <b>36,982</b>',
            '<div class="bn">卷一</div><div class="bt">53</div>',
            '<div class="bn">卷二</div><div class="bt">48</div>',
            '<div class="bn">卷三</div><div class="bt">42</div>',
            '<div class="bn">卷四</div><div class="bt">46</div>',
            '<div class="bn">卷五</div><div class="bt">13</div>',
            '五卷三十门二百零二篇']:
    chk(pat in html_txt, f'页面缺少结构数据: {pat}')

# ---------- 机数：词频 ----------
FREQ = {'梦': 72, '笑': 32, '仙': 20, '鬼': 10, '黄州': 20, '儋耳': 9, '惠州': 7,
        '眉山': 7, '元丰': 12, '元佑': 10, '元符': 10, '绍圣': 7,
        '吾': 149, '予': 71, '轼': 14, '东坡': 28, '居士': 17, '磨蝎': 2, '闲人': 1}
for w, n in FREQ.items():
    real = lib.count(w)
    chk(real == n, f'库本词频 {w}={real} != 页面所写 {n}')
chk(lib.count('（左蜀右犬）') == 6, '（左蜀右犬） != 6 见')
chk(lib.count('?') == 6, f'缺字符 ? 数 {lib.count("?")} != 6')
for frag in ['<b>72 见</b>', '<b>32 见</b>', '<b>20 见</b>', '<b>10 见</b>',
             '<b>20 见</b>', '<b>9 见</b>', '<b>7 见</b>',
             '<b>12　10　10　7 见</b>', '<b>149　71　14 见</b>', '<b>28　17 见</b>',
             '<b>2　1 见</b>', '<b>6 见</b>']:
    chk(frag in html_txt, f'页面缺词频数字: {frag}')

# 名篇八十三字（去标点）
cheng = '元丰六年十月十二日夜，解衣欲睡，月色入户，欣然起行。念无与乐者，遂至承天寺寻张怀民。怀民亦未寝，相与步于中庭。庭下如积水空明，水中藻荇交横，盖竹柏影也。何夜无月，何处无竹柏，但少闲人如吾两人耳。'
chk(norm(cheng) in LIBN, '承天寺原文不在库本')
chk(sum(1 for c in cheng if 0x3400 <= ord(c) <= 0x9FFF) == 83, '承天寺去标点 != 83 字')
chk('八十三字（去标点）' in html_txt, '页面八十三字声明缺失')

# 页面引文条数自报（页脚说 N 条 → 与实际一致）
m = re.search(r'本篇引文(\d+)条', html_txt)
if m:
    chk(int(m.group(1)) == len(texts), f'页脚引文数 {m.group(1)} != 实际 {len(texts)}')

# ---------- 排版红线 ----------
chk('—' not in html_txt, '出现长划线 —')
chk('–' not in html_txt, '出现短划线 –')
for ln, line in enumerate(html_txt.split('\n'), 1):
    c = line.count('·')
    chk(c <= 1, f'第 {ln} 行有 {c} 个 ·')

# 可见文本中的英文残留（剥 style 与标签后）
vis = re.sub(r'<style[\s\S]*?</style>', '', html_txt)
vis = re.sub(r'<[^>]+>', '', vis)
for w in re.findall(r'[A-Za-z][A-Za-z0-9./_-]+', vis):
    parts = w.split('/')
    for p in parts:
        if p and p not in ALLOWED_LATIN:
            errors.append(f'英文残留: {w}')

# 页脚三要素
chk('殆知阁简体库' in html_txt and 'daizhigev20' in html_txt, '页脚缺文本来源')
chk('逐字核验' in html_txt, '页脚缺核验声明')
chk('不代表' in html_txt and ('时代' in html_txt or '现代' in html_txt), '页脚缺时代局限提醒')

# 篇号与卷号
chk('之一百一十一' in html_txt, '缺页内篇号 之一百一十一')
chk('卷六十三 雪泥' in html_txt, '缺卷号 卷六十三 雪泥')

# ---------- 汇报 ----------
print(f'引文 {len(texts)} 条全部命中库本')
if warns:
    print(f'WARN x{len(warns)}')
    for w in warns: print('  warn:', w)
if errors:
    print(f'FAIL x{len(errors)}')
    for e in errors: print('  ', e)
    sys.exit(1)
print('verify_dongpo: ALL PASS')
