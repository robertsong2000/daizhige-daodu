#!/usr/bin/env python3
"""checker for canluanlu.html: quote channel vs lib file, prose 6-char anti-scan, layout rules."""
import re, sys
from html.parser import HTMLParser

LIB = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/传记/骖鸾录.txt'
PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/canluanlu.html'

NORM = str.maketrans({'呉':'吴','寳':'宝','逺':'远','歴':'历','竒':'奇','畆':'亩','畧':'略','廰':'厅','搨':'拓','眞':'真','鎭':'镇','鉅':'巨','晣':'晢','歎':'叹','嘆':'叹','戶':'户','龎':'庞','黙':'默','畫':'画','壊':'坏','拠':'据','淸':'清','圎':'圆','髓':'髓'})

def norm(t):
    t = t.translate(NORM)
    return re.sub(r'[^一-鿿㐀-䶿\U00020000-\U0003ffff]', '', t)

lib = norm(open(LIB, encoding='utf-8').read())

class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.quotes = []      # (class, text)
        self.prose = []       # text outside quotes
        self.attrs = []       # data-note / aria-label / title attr values
        self.stack = []       # list of set(cls of open q-ish tags)
        self.qdepth = 0
        self.buf = []
        self.curq = None
    def handle_starttag(self, tag, attrs):
        ad = dict(attrs)
        for k in ('data-note','aria-label','title'):
            if ad.get(k): self.attrs.append(ad[k])
        cls = ad.get('cls') or ad.get('class') or ''
        isq = tag in ('q','b') and ('q' in cls.split() or tag == 'q') or (cls and ('q' in cls.split() or 'qv' in cls.split()))
        if tag == 'q' or 'q' in cls.split() or 'qv' in cls.split():
            self.qdepth += 1
            if self.qdepth == 1:
                self.curq = [cls, []]
        elif self.qdepth == 0:
            pass
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs); self.handle_endtag(tag)
    def handle_endtag(self, tag):
        cls = None
        if self.qdepth > 0:
            pass
        # pop matching: simplified — find nearest open q by scanning stack is unreliable;
        # rely on well-formed nesting.
        if self.qdepth > 0:
            # close if this endtag matches the innermost q-ish tag recorded
            tagcls = None
            # walk back our own record
            if self.curq is not None and self.qdepth == 1:
                cls = self.curq[0]
                self.quotes.append((cls, ''.join(self.curq[1])))
                self.curq = None
            self.qdepth -= 1
    def handle_data(self, data):
        if self.qdepth > 0:
            if self.curq is not None: self.curq[1].append(data)
        else:
            self.prose.append(data)

p = P()
p.feed(open(PAGE, encoding='utf-8').read())
prose_all = ''.join(p.prose) + ''.join(p.attrs)
prose_n = norm(prose_all)

fails = 0

# 1) quote channel: every q must be a substring of lib (normalized)
qn = 0
for cls, txt in p.quotes:
    t = norm(txt)
    if not t: continue
    qn += 1
    if t not in lib:
        fails += 1
        print('QUOTE MISS (%s): %s' % (cls, txt[:50]))
print('quote channel: %d checked' % qn)

# 2) prose anti-scan: any 6-char window of prose found in lib = hit
hits = 0
for i in range(len(prose_n) - 5):
    w = prose_n[i:i+6]
    if w in lib:
        hits += 1
        if hits <= 20:
            print('PROSE HIT: ...%s[%s]...' % (prose_n[max(0,i-8):i], w))
if hits:
    fails += 1
print('prose anti-scan: %d hits' % hits)

# 3) layout: no em/en dash; at most one interpunct per text line
raw = open(PAGE, encoding='utf-8').read()
for ch in ('—','–'):
    if ch in raw:
        fails += 1; print('DASH FOUND:', ch)
for seg in p.prose + p.attrs:
    if seg.count('·') > 1:
        fails += 1; print('INTERPUNCT x%d: %s' % (seg.count('·'), seg.strip()[:60]))

print('RESULT:', 'PASS' if fails == 0 else 'FAIL (%d)' % fails)
sys.exit(0 if fails == 0 else 1)
