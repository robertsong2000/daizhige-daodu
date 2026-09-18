# -*- coding: utf-8 -*-
"""五国故事 页面核验：
1. 引文（class含 q/qv 的元素）与库本去标点归一逐字比对。
2. 白话反扫：其余文本按块切分，滑6字窗在库本中查撞。
3. 排版规则：禁长短划；每行·至多1个。
"""
import re, sys
from html.parser import HTMLParser

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/wuguo-gushi.html'
LIB = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/载记/五国故事.txt'

def norm(s):
    s = re.sub(r'[①-⑳㉑-㉟㊱-㊿]', '', s)  # 圈号
    return re.sub(r'[^\w一-鿿]', '', s)

FT = norm(open(LIB, encoding='utf-8').read())

BLOCK = {'p','div','li','ul','section','footer','nav','h1','h2','h3','h4','h5','body','head','style','script','title','button','span','main','header'}

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.quotes = []
        self.baihua = []
        self.seg = []
        self.skip = 0
        self.qtags = []
        self.qbuf = []
        self.qkind = []
        self.srctags = []

    def flush(self):
        if self.seg:
            self.baihua.append(''.join(self.seg))
            self.seg = []

    def handle_starttag(self, tag, attrs):
        cls = (dict(attrs).get('class', '') or '')
        toks = cls.split()
        if tag in ('script', 'style'):
            self.skip += 1
            self.flush()
            return
        if tag in BLOCK:
            self.flush()
        if 'qsrc' in toks:
            self.srctags.append(tag)
        if ('q' in toks) or ('qv' in toks):
            self.flush()
            self.qtags.append(tag)
            self.qkind.append('qv' if ('qv' in toks and 'q' not in toks) else 'q')
            self.qbuf.append([])

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip -= 1
            return
        if self.srctags and tag == self.srctags[-1]:
            self.srctags.pop()
        if tag in BLOCK:
            self.flush()
        if self.qtags and tag == self.qtags[-1]:
            self.qtags.pop()
            kind = self.qkind.pop()
            self.quotes.append((kind, ''.join(self.qbuf.pop())))
            self.flush()

    def handle_data(self, data):
        if self.skip or self.srctags:
            return
        if self.qtags:
            self.qbuf[-1].append(data)
        else:
            self.seg.append(data)

p = P()
p.feed(open(PAGE, encoding='utf-8').read())
p.flush()

fails = []
qtexts = []
for kind, text in p.quotes:
    t = norm(text)
    if not t:
        continue
    qtexts.append((kind, t, text.strip()[:50]))
    if t not in FT:
        fails.append((kind, text.strip()[:70]))

hits = []
for seg in p.baihua:
    n = norm(seg)
    if len(n) < 6:
        continue
    for i in range(len(n) - 5):
        w = n[i:i+6]
        if w in FT:
            hits.append((seg.strip()[:44], w))

lines = open(PAGE, encoding='utf-8').read().split('\n')
dash = sum(l.count('—') + l.count('–') for l in lines)
dots = [(i+1, l.count('·')) for i, l in enumerate(lines) if l.count('·') > 1]

print('引文条数(非空):', len(qtexts), ' 去重:', len(set(t for _, t, _ in qtexts)))
print('引文未过:', len(fails))
for f in fails:
    print('  MISS', f)
print('白话反扫撞窗:', len(hits))
for h in hits[:40]:
    print('  HIT', h)
print('长划线:', dash, ' 行·超1:', dots)
sys.exit(1 if (fails or hits or dash or dots) else 0)
