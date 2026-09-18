#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""核验 kunyu-tushuo.html：引文逐字比对 + 白话反扫 + 排版规则"""
import re, sys, html
from html.parser import HTMLParser

PAGE = 'kunyu-tushuo.html'
BOOK = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/地理/坤舆图说.txt'

PUNCT = re.compile(r'[\s，。！？；：、·“”‘’《》〈〉（）()\[\]【】〔〕—–\-…!?:;,"\'.〜~*&%#@+=|/\\^　]+')

def norm(s):
    return PUNCT.sub('', s)

src = open(PAGE, encoding='utf-8').read()
lib = open(BOOK, encoding='utf-8').read()
libn = norm(lib)

body = re.sub(r'<script[\s\S]*?</script>', '', src)
body = re.sub(r'<style[\s\S]*?</style>', '', body)

def is_quote_tag(tag, attrs):
    if tag == 'q':
        return True
    cl = dict(attrs).get('class', '') or ''
    for tok in cl.split():
        if tok == 'qv' or tok.endswith('vq') or tok.endswith('-qv'):
            return True
    return False

class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = [False]
        self.quotes = []
        self.plain = []
        self._qb = []
    def handle_starttag(self, tag, attrs):
        iq = is_quote_tag(tag, attrs)
        self.stack.append(iq)
        if iq:
            self._qb.append([])
    def handle_startendtag(self, tag, attrs):
        pass
    def handle_endtag(self, tag):
        if len(self.stack) > 1:
            iq = self.stack.pop()
            if iq:
                self.quotes.append(''.join(self._qb.pop()))
    def handle_data(self, data):
        if any(self.stack):
            self._qb[-1].append(data)
        else:
            self.plain.append(data)

p = P()
p.feed(body)
plain_text = html.unescape(''.join(p.plain))
plain_norm = norm(plain_text)

errors = []

ok_q = 0
for i, q in enumerate(p.quotes):
    qn = norm(html.unescape(q))
    if not qn:
        errors.append(f'空引文 #{i}')
        continue
    if qn not in libn:
        errors.append(f'引文不在库本 #{i}: {q[:40]}...')
    else:
        ok_q += 1

hits = []
LIBWIN = set()
for i in range(len(libn) - 5):
    LIBWIN.add(libn[i:i+6])
j = 0
last = -100
while j <= len(plain_norm) - 6:
    w = plain_norm[j:j+6]
    if w in LIBWIN:
        if j > last + 12:
            ctx = plain_norm[max(0,j-10):j+16]
            hits.append((w, ctx))
        last = j
        j += 6
    else:
        j += 1

if '—' in src or '–' in src:
    errors.append('出现长划线')
render = re.sub(r'<[^>]+>', '\n', body)
for ln in render.split('\n'):
    if ln.count('·') > 1:
        errors.append(f'一行多个间隔号: {ln.strip()[:50]}')

if '445' not in src:
    errors.append('缺编号锚 443')
if '卷三百二十四' not in src:
    errors.append('缺卷号锚')

print(f'引文核验：{ok_q}/{len(p.quotes)} 处逐字通过')
print(f'白话反扫：六字窗命中 {len(hits)} 处')
for w, ctx in hits:
    print('  撞窗:', w, '…' + ctx + '…')
for e in errors:
    print('ERROR:', e)
sys.exit(1 if (errors or hits) else 0)
