#!/usr/bin/env python3
import re, sys

HTML = '/home/robertsong/workspace/claude/daizhige-daodu/yehou-waizhuan.html'
SRC  = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/邺侯外传.txt'

html = open(HTML, encoding='utf-8').read()
src  = open(SRC, encoding='utf-8').read()

def norm(s):
    return ''.join(ch for ch in s if '一' <= ch <= '鿿')

S = norm(src)

from html.parser import HTMLParser
class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = []
        self.qtexts = []
        self.visible = []
        self.qdepth = 0
        self.cur = None
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip.append(tag)
        elif tag == 'q':
            self.qdepth += 1
            if self.qdepth == 1:
                self.cur = []
    def handle_endtag(self, tag):
        if tag in ('script', 'style') and self.skip:
            self.skip.pop()
        elif tag == 'q' and self.qdepth:
            self.qdepth -= 1
            if self.qdepth == 0:
                self.qtexts.append(''.join(self.cur))
                self.cur = None
    def handle_data(self, data):
        if self.skip:
            return
        if self.qdepth:
            self.cur.append(data)
        else:
            self.visible.append(data)

p = P(); p.feed(html)

fails = []
for qt in p.qtexts:
    n = norm(qt)
    if not n:
        fails.append('EMPTY q: ' + qt[:20])
    elif n not in S:
        fails.append('q MISS: ' + qt[:40])

vis = norm(''.join(p.visible))
wins = {S[i:i+6] for i in range(len(S) - 5)}
hits = sorted({vis[i:i+6] for i in range(len(vis) - 5) if vis[i:i+6] in wins})
if hits:
    fails.append('six-window collisions: ' + ' | '.join(hits[:12]))

if '—' in html or '–' in html:
    fails.append('forbidden dash')
for seg in p.visible + p.qtexts:
    for ln in seg.split('\n'):
        if ln.count('·') > 1:
            fails.append('multi · line: ' + ln[:40])

ext = re.findall(r'(?:src|href)="https?://', html)
if ext:
    fails.append('external resources: %d' % len(ext))

print('q count:', len(p.qtexts), ' visible chars:', len(vis))
print('collisions:', len(hits))
if fails:
    print('CHECK FAILED')
    for f in fails:
        print('  -', f)
    sys.exit(1)
print('ALL CHECKS PASSED')
