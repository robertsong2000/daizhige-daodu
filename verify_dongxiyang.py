#!/usr/bin/env python3
import re, sys
from html.parser import HTMLParser

SRC = 'daizhige-simplified/史藏/地理/东西洋考.txt'
PAGE = 'daizhige-daodu/dongxiyang-kao.html'

src_raw = open(SRC, encoding='utf-8').read()

PUNCT = re.compile(r"[\s　+\-—–·•:：;；,，.。、!！?？~～《》〈〉「」『』()（）【】\[\]〔〕\"'“”‘’◆●○%／/|｜*#@&+=<>\\\\]")
def norm(s, is_src=False):
    if is_src:
        s = s.replace('■〈风贝〉', '飓')
        s = re.sub('■〈[^〉]*〉', '', s)
    s = PUNCT.sub('', s)
    return s

SRCN = norm(src_raw, is_src=True)

class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.qs = []          # (index, text, class)
        self.vis = []         # visible non-q text
        self.stack = []
        self.skip = 0
        self.curq = None
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style'): self.skip += 1; return
        a = dict(attrs)
        cls = a.get('class','')
        if tag == 'q':
            self.curq = {'cls':cls,'buf':[]}
    def handle_endtag(self, tag):
        if tag in ('script','style'):
            self.skip = max(0,self.skip-1); return
        if tag == 'q' and self.curq is not None:
            self.qs.append((self.curq['cls'], ''.join(self.curq['buf'])))
            self.curq = None
    def handle_data(self, d):
        if self.skip: return
        if self.curq is not None:
            self.curq['buf'].append(d)
        else:
            self.vis.append(d)

p = P()
p.feed(open(PAGE, encoding='utf-8').read())

fails = []
okn = 0
for i,(cls,t) in enumerate(p.qs):
    nq = norm(t)
    if nq and nq in SRCN:
        okn += 1
    else:
        fails.append((i, cls, t[:60], nq[:40]))

print(f"quotes total={len(p.qs)} pass={okn} fail={len(fails)}")
for i,cls,t,nq in fails:
    print(f"  FAIL #{i} [{cls}] {t}... norm={nq}")

# anti-scan: 6-gram windows of source inside page text excluding q/qv
vis = ''.join(p.vis)
visn = norm(vis)
grams = set()
for i in range(len(SRCN)-5):
    grams.add(SRCN[i:i+6])
hits = sorted({g for g in grams if g in visn})
print(f"anti-scan 6-char windows: {len(hits)} hits")
for g in hits[:30]:
    idx = visn.find(g)
    print(f"  HIT {g} ...context:{visn[max(0,idx-12):idx+18]}")

# typesetting rules
html = open(PAGE, encoding='utf-8').read()
bad = []
for ln, line in enumerate(html.split('\n'), 1):
    if '—' in line or '–' in line: bad.append(('dash', ln))
    if line.count('·') > 1: bad.append(('multi-dot', ln, line.strip()[:50]))
print("typesetting:", bad if bad else "OK (no long dashes; ≤1 dot per line)")
sys.exit(1 if (fails or hits or bad) else 0)
