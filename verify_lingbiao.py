#!/usr/bin/env python3
# 岭表录异 页面核验：引文逐字 + 白话反扫 + 排版
import re, sys
from html.parser import HTMLParser

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/lingbiao-luyi.html'
LIB = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/地理/岭表录异.txt'
# 四库提要（辑录源文，来自 guoxue123 提要页）
TIYAO = ('嶺表錄異三卷舊本題唐劉恂撰宋僧赞宁笋谱称恂於唐昭宗朝出为广州司马官满上京扰攘遂居南海作岭表录'
         '陈振孙书录解题亦云昭宗时人然考书中云唐乾符四年又云唐昭宗即位唐之臣子宜有内词不应直称其国号且昭宗'
         '时人不应预称谥号殆书成於五代时欤粤东舆地之书如郭义恭广志沈怀远南越志皆已不传诸家所援据者以恂是编'
         '为最古而百川学海及说郛所载寥寥数页首尾不完盖仅从类书抄撮数条以备一种而恂之原本则已久佚宋代太平寰'
         '宇记太平广记太平御览诸书征引颇夥然尚多挂漏惟散见永乐大典者条理较详尚可编次谨逐卷裒辑而佐以旁见诸'
         '书者排比其文仍成三卷以复唐志之旧虽永乐大典阙卷数函无从考验或不免一二之遗而证以诸书似已十得其八九焉'
         '唐人著述传世者稀断简残编已足珍惜此更於放失之馀复成完帙使三四百年博物君子所未睹者一旦顿还其旧观弥足'
         '宝矣')

lib = open(LIB, encoding='utf-8').read()
html = open(PAGE, encoding='utf-8').read()

def norm(s):
    return re.sub(r'[^\w]+', '', s, flags=re.UNICODE)

nlib, nty = norm(lib), norm(TIYAO)

errs, warns = [], []

# ── 排版规则 ──
if '—' in html or '–' in html:
    for i, ln in enumerate(html.splitlines(), 1):
        if '—' in ln or '–' in ln:
            errs.append(f'L{i}: 含长划线')
for i, ln in enumerate(html.splitlines(), 1):
    if ln.count('·') > 1:
        errs.append(f'L{i}: · 超过 1 个')

# ── DOM 解析 ──
class P(HTMLParser):
    VOID = {'meta','br','img','hr','input','link','circle','path','ellipse','stop','rect','text','line'}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.quotes = []      # (kind, text)
        self.cur_q = None     # 'q' | 'tieyao'
        self.buf = []
        self.qdepth = 0
        self.texts = []       # (text, in_quote)
    def handle_starttag(self, tag, attrs):
        if tag in self.VOID: return
        self.stack.append(tag)
        cls = dict(attrs).get('class', '') or ''
        kind = 'tieyao' if 'tieyao' in cls.split() else ('q' if (tag == 'q' or 'q' in cls.split() or 'qv' in cls.split()) else None)
        if kind:
            if self.cur_q is None:
                self.cur_q, self.buf, self.qdepth = kind, [], 1
            else:
                self.qdepth += 1
    def handle_endtag(self, tag):
        if tag in self.VOID: return
        if not self.stack or self.stack[-1] != tag:
            errs.append(f'标签不配平: </{tag}> 栈顶 {self.stack[-1] if self.stack else "空"}')
        else:
            self.stack.pop()
        if self.cur_q:
            if self.qdepth == 1 and tag not in self.VOID:
                self.quotes.append((self.cur_q, ''.join(self.buf)))
                self.cur_q = None
            else:
                self.qdepth -= 1
    def handle_data(self, data):
        if self.stack and self.stack[-1] in ('script', 'style', 'title'):
            return
        if self.cur_q:
            self.buf.append(data)
            self.texts.append((data, True))
        else:
            self.texts.append((data, False))

p = P()
p.feed(html)
if p.stack:
    errs.append(f'未闭合标签: {p.stack}')

# ── 引文核验 ──
nq = nty_q = 0
for kind, t in p.quotes:
    s = norm(t)
    if len(s) < 4:
        continue
    if kind == 'tieyao':
        nty_q += 1
        if s not in nty:
            errs.append(f'提要引文不匹配: {t[:40]}...')
    else:
        nq += 1
        if s not in nlib:
            errs.append(f'引文不匹配: {t[:44]}...')

# ── 白话反扫：非引文文本 6 字窗 ──
hits = 0
for t, inq in p.texts:
    if inq:
        continue
    s = norm(t)
    for i in range(len(s) - 5):
        w = s[i:i+6]
        if re.search(r'[一-鿿]', w) and w in nlib:
            hits += 1
            warns.append(f'反扫撞窗: …{s[max(0,i-6):i+12]}…')

print(f'引文 {nq} 条（另提要 {nty_q} 条），排版 {'通过' if not errs else 'FAIL'}，反扫 {hits} 撞')
for w in warns[:30]:
    print(' WARN', w)
for e in errs[:30]:
    print(' ERR ', e)
sys.exit(1 if errs else 0)
