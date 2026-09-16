#!/usr/bin/env python3
# verify chan-shu.html: quote containment vs library, reverse scan, typography rules
import re, unicodedata
from html.parser import HTMLParser

REPO = '/home/robertsong/workspace/claude/daizhige-daodu'
LIB = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/谗书.txt'
PAGE = REPO + '/chan-shu.html'

raw = open(LIB, encoding='utf-8').read()
lib = re.sub(r'\[[^\]]*\]', '', raw).replace('□', '')

def norm(s):
    return ''.join(c for c in s if unicodedata.category(c)[0] in 'LN')

NL = norm(lib)

html = open(PAGE, encoding='utf-8').read()
assert '⟦' not in html.replace('⟦NO⟧', ''), 'unfilled placeholder'
assert html.count('⟦NO⟧') in (0, 3), html.count('⟦NO⟧')
assert '—' not in html and '–' not in html, 'long dash found'

CHANNEL = {'q', 'qv', 'qi', 'qn', 'ext'}
INLINE = {'span', 'b', 'i', 'em', 'small', 'a', 's', 'strong', 'u'}
SKIP = {'script', 'style', 'title', 'head'}

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.quotes = []      # [chan, text] entries, one per channel element
        self.qid = None
        self.qv_children = []
        self.runs = []        # [blockkey, text]
        self.cur = None
    def _flush_run(self):
        if self.cur is not None:
            self.runs.append(self.cur); self.cur = None
    def handle_starttag(self, tag, attrs):
        cls = set((dict(attrs).get('class') or '').split())
        if tag in SKIP:
            self._flush_run()
            self.stack.append((tag, frozenset()))
            return
        self.stack.append((tag, cls))
        if tag not in INLINE:
            self._flush_run()
            if cls & CHANNEL:
                self.quotes.append([(cls & CHANNEL).pop(), ''])
                self.qid = len(self.quotes) - 1
    def handle_endtag(self, tag):
        if tag in SKIP:
            self.stack.pop(); return
        tag, cls = self.stack.pop()
        if tag not in INLINE:
            self._flush_run()
            if cls & CHANNEL:
                self.qid = None
    def handle_data(self, data):
        if not data.strip():
            return
        chan = None
        for t, cls in reversed(self.stack):
            if cls & CHANNEL:
                chan = (cls & CHANNEL).pop(); break
        if chan == 'qv':
            if self.stack and self.stack[-1][0] == 'span':
                self.qv_children.append(data)
            return
        if chan:
            assert self.qid is not None and self.quotes[self.qid][0] == chan
            self.quotes[self.qid][1] += data
            return
        blk = -1
        for idx in range(len(self.stack) - 1, -1, -1):
            t, cls = self.stack[idx]
            if t not in INLINE and t not in SKIP:
                blk = idx; break
        if self.cur is None or self.cur[0] != blk:
            self._flush_run()
            self.cur = [blk, data]
        else:
            self.cur[1] += data

p = P()
p.feed(html)
p._flush_run()

nq = 0
for chan, txt in p.quotes:
    assert txt.count('·') <= 1, f'dots in {chan}: {txt[:50]!r}'
    if chan == 'q':
        n = norm(txt)
        assert len(n) >= 5, f'quote too short: {n!r}'
        assert n in NL, f'quote not in library: {n[:40]!r}'
        nq += 1
print(f'quote blocks verified: {nq}')
assert nq == 28, nq

nv = 0
for t in p.qv_children:
    n = norm(t)
    assert 1 <= len(n) <= 12, f'qv span odd: {n!r}'
    assert n in NL, f'qv span not in library: {n!r}'
    nv += 1
print(f'qv title spans verified: {nv}')
assert nv == 60, nv

exts = [norm(t) for c, t in p.quotes if c == 'ext']
for e in exts:
    assert e not in NL or len(e) < 6, f'ext block unexpectedly inside library: {e[:30]}'
print('ext blocks:', len(exts))

hits = []
for blk, txt in p.runs:
    n = norm(txt)
    for i in range(len(n) - 5):
        if n[i:i + 6] in NL:
            hits.append((blk, n[i:i + 6], n[max(0, i - 8):i + 14]))
print('reverse scan hits:', len(hits))
for blk, w, ctx in hits[:12]:
    print('  HIT', blk, w, '|', ctx)
assert not hits, 'reverse scan found library strings outside quote channels'

for blk, txt in p.runs:
    assert txt.count('·') <= 1, f'dots in block: {txt[:60]!r}'

print('ALL CHECKS PASSED: quotes 28 + qv 60, reverse scan 0 hits, no long dash, dots ok')
