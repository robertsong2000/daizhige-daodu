#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_juzhen.py — 引文核验 + 白话反扫 for juzhen-chengshi.html
通道约定:
  .q / .qv            引文通道, 归一后必须逐字命中库本
  [data-t]            豁免通道, 整棵子树跳过反扫
  title               单独参与反扫
  script/style        跳过
  其余全部文本        按块级元素边界切分后做 6 字滑窗反扫
"""
import re, sys
from html.parser import HTMLParser

LIB_PATH = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/政书/钦定武英殿聚珍版程式.txt'
PAGE = 'juzhen-chengshi.html'
WIN = 6

NORM = {'寛': '宽', '髙': '高', '騐': '验', '熈': '熙', '厯': '历', '冐': '冒',
        '様': '样', '竝': '并', '曽': '曾', '叅': '参', '戸': '户', '槩': '概'}

def norm(s):
    s = re.sub(r'\s+', '', s)
    s = re.sub(r'[^\w㐀-䶿一-鿿豈-﫿\U00020000-\U0002a6ff]+', '', s)
    for k, v in NORM.items():
        s = s.replace(k, v)
    return s

BLOCK = {'div','p','h1','h2','h3','h4','h5','h6','section','header','footer','nav','main',
         'table','thead','tbody','tr','td','th','li','ul','ol','blockquote','button','svg',
         'text','figure','figcaption'}

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []      # [tag, q_active, ex_active, buf, is_block]
        self.qtexts = []
        self.segs = []
        self.skipdepth = 0
        self.intitle = False
        self.titlebuf = []

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.intitle = True; return
        if tag in ('script', 'style'):
            self.skipdepth += 1; return
        if self.skipdepth: return
        a = dict(attrs)
        classes = (a.get('class') or '').split()
        qchan = ('q' in classes) or ('qv' in classes)
        exempt = a.get('data-t') is not None
        parent = self.stack[-1] if self.stack else None
        q_active = (qchan and not exempt) or bool(parent and parent[1] and not exempt)
        ex_active = exempt or bool(parent and parent[2])
        self.stack.append([tag, q_active, ex_active, [], tag in BLOCK])

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if tag == 'title':
            self.intitle = False
            t = norm(''.join(self.titlebuf))
            if t: self.segs.append(('title', t))
            return
        if tag in ('script', 'style'):
            self.skipdepth = max(0, self.skipdepth - 1); return
        if self.skipdepth or not self.stack: return
        idx = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                idx = i; break
        if idx is None: return
        for j in range(len(self.stack) - 1, idx - 1, -1):
            self._close(j)

    def _close(self, j):
        tag, q, ex, buf, block = self.stack[j]
        txt = norm(''.join(buf))
        del self.stack[j:]
        if ex:
            return
        if q and txt:
            self.qtexts.append(txt)
            return
        if not self.stack:
            if txt: self.segs.append((tag, txt))
        elif block:
            if txt: self.segs.append((tag, txt))
        else:
            if txt: self.stack[-1][3].append(txt)

    def handle_data(self, data):
        if self.intitle:
            self.titlebuf.append(data); return
        if self.skipdepth: return
        if not self.stack:
            t = norm(data)
            if t: self.segs.append(('body', t))
            return
        self.stack[-1][3].append(data)

def main():
    lib = norm(open(LIB_PATH, encoding='utf-8').read())
    html = open(PAGE, encoding='utf-8').read()
    p = P()
    p.feed(html)
    errs = 0

    print('== 引文通道: %d 条 ==' % len(p.qtexts))
    miss = 0
    for t in p.qtexts:
        if t not in lib:
            miss += 1
            errs += 1
            print('  MISS: %s' % t[:70])
    print('  命中 %d / %d, 唯一 %d' % (len(p.qtexts) - miss, len(p.qtexts), len(set(p.qtexts))))

    print('== 反扫: %d 段 ==' % len(p.segs))
    hits = []
    for tag, t in p.segs:
        for i in range(len(t) - WIN + 1):
            w = t[i:i+WIN]
            if w in lib:
                hits.append((tag, w, t[max(0, i-10):i+WIN+10]))
    if hits:
        errs += len(hits)
        seen = set()
        shown = 0
        for tag, w, ctx in hits:
            key = (tag, w)
            if key in seen: continue
            seen.add(key)
            shown += 1
            if shown <= 40:
                print('  撞窗[%s] %s | …%s…' % (tag, w, ctx))
        print('  共 %d 处 (%d 种)' % (len(hits), len(seen)))
    else:
        print('  六字窗零撞')

    print('== 排版 ==')
    for i, line in enumerate(html.split('\n'), 1):
        if '—' in line or '–' in line:
            errs += 1; print('  长划线 L%d' % i)
        if line.count('·') > 1:
            errs += 1; print('  多· L%d: %s' % (i, line.strip()[:60]))

    print('== 结果 ==')
    print('PASS' if errs == 0 else 'FAIL (%d)' % errs)
    sys.exit(0 if errs == 0 else 1)

main()
