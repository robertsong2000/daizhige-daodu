import re, sys, unicodedata

PAGE = 'daizhige-daodu/huashi.html'
LIB = 'daizhige-simplified/艺藏/绘画/画史.txt'

NORM = {'戯':'戏','戱':'戏','寛':'宽','闗':'关','麄':'粗','甞':'尝','熈':'熙',
        '覩':'睹','厯':'历','歴':'历','牕':'窗','髙':'高','竒':'奇','艶':'艳',
        '慙':'惭','葢':'盖','戸':'户','栢':'柏','乆':'久','呌':'叫','逺':'远',
        '椉':'乘','靣':'面','寳':'宝','屛':'屏','廻':'回','囘':'回','畧':'略'}

PUNC = '，。：；、！？·「」『』《》〈〉（）()[]〔〕—…．.';
PUNC += '·"\'‘’“”　 \t\n\r'

def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if 0xE000 <= o <= 0xF8FF:      # PUA 残字剥除
            continue
        if ch in PUNC:
            continue
        ch = NORM.get(ch, ch)
        out.append(ch)
    return ''.join(out)

lib = norm(open(LIB, encoding='utf-8').read())
html = open(PAGE, encoding='utf-8').read()

# ---- 1. q / qv 正扫 ----
BLOCKS = {'section','div','p','h1','h2','h3','h4','footer','button','li','body','html','head'}
INLINE_Q = set()
quotes = []
for m in re.finditer(r'<(q|qv)\b[^>]*>(.*?)</\1>', html, re.S):
    txt = re.sub(r'<[^>]+>', '', m.group(2))
    quotes.append(txt)
if not quotes:
    print('FAIL: no q found'); sys.exit(1)
bad = 0
for qt in quotes:
    n = norm(qt)
    if n not in lib:
        bad += 1
        print('FAIL q:', qt[:40], '→ norm:', n[:40])
print(f'q total={len(quotes)} fail={bad}')

# ---- 2. 白话反扫（按块切分，q/qv/script/style/title 豁免）----
from html.parser import HTMLParser
class Walker(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks=[]; self.cur=[]; self.skip=0; self.qdepth=0
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style'): self.skip+=1
        if tag in ('q','qv'): self.qdepth+=1
        if tag in BLOCKS and self.qdepth==0 and self.skip==0:
            self.flush()
    def handle_endtag(self, tag):
        if tag in ('script','style'): self.skip=max(0,self.skip-1)
        if tag in ('q','qv'): self.qdepth=max(0,self.qdepth-1)
        if tag in BLOCKS and self.qdepth==0 and self.skip==0:
            self.flush()
    def handle_data(self, d):
        if self.skip==0 and self.qdepth==0:
            self.cur.append(d)
    def flush(self):
        if self.cur: self.blocks.append(''.join(self.cur)); self.cur=[]
w = Walker(); w.feed(html); w.flush()

hits = []
for b in w.blocks:
    n = norm(b)
    for i in range(len(n)-5):
        win = n[i:i+6]
        if win in lib:
            hits.append(win)
if hits:
    print('FAIL reverse-scan hits:', set(hits))
    bad += len(hits)
else:
    print('reverse-scan: 0 hits (6-char window)')

# ---- 3. 红线：长划线 / · 每行至多1 ----
if '—' in html or '–' in html:
    print('FAIL: em/en dash present'); bad += 1
else:
    print('dash check: clean')
dot_bad = [ln for ln in html.splitlines() if ln.count('·') > 1]
if dot_bad:
    print('FAIL: line with >1 ·:', dot_bad[:3]); bad += 1
else:
    print('dot check: clean (≤1 per line)')

print('RESULT:', 'PASS' if bad == 0 else f'FAIL x{bad}')
