# -*- coding: utf-8 -*-
"""归田录 引文核验：页面所有 .q / .poemline 引文与库内文件去标点归一逐字比对"""
import re, sys, unicodedata

LIB = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/归田录.txt'
HTML = '/home/robertsong/workspace/claude/daizhige-daodu/guitian-lu.html'

PUNCT_EXTRA = set('□' + '，。！？：；、·“”‘’《》「」〔〕（）()〈〉【】—–-%')

def norm(s):
    out = []
    for ch in s:
        if ch.isspace() or ch in PUNCT_EXTRA or unicodedata.category(ch).startswith('P') or unicodedata.category(ch).startswith('S'):
            continue
        out.append(ch)
    return ''.join(out)

text = norm(open(LIB, encoding='utf-8').read())
html = open(HTML, encoding='utf-8').read()

quotes = []
for m in re.finditer(r'<span class="q[^"]*">(.*?)</span>', html, re.S):
    inner = re.sub(r'<[^>]+>', '', m.group(1))
    quotes.append(('q', inner.strip()))
for m in re.finditer(r'<div class="poemline">(.*?)<span class="by">', html, re.S):
    inner = re.sub(r'<[^>]+>', '', m.group(1))
    quotes.append(('poem', inner.strip()))
quotes.append(('inline', '朝廷之遗事，史官之所不记，与夫士大夫笑谈之馀而可录者，录之以备闲居之览也。'))
quotes.append(('inline', '水底日为天上日'))
quotes.append(('inline', '眼中人是面前人。'))
quotes.append(('inline', '茂陵他日求遗□'))
quotes.append(('inline', '犹喜曾无《封禅书》。'))
quotes.append(('inline', '见其发矢十中八、九'))

bad = []
for kind, q in quotes:
    nq = norm(q)
    if not nq:
        bad.append((q, 'EMPTY'))
        continue
    if nq not in text:
        bad.append((q, 'NOT FOUND'))

print(f'共 {len(quotes)} 处引文，未通过 {len(bad)} 处')
for q, why in bad:
    print('  FAIL[%s] %s : %s' % (why, q[:60], ''))
# 版式红线：长划线
for ch, name in (('—', 'em-dash'), ('–', 'en-dash')):
    if ch in html:
        print('排版FAIL: 页面含 %s' % name)
sys.exit(1 if bad else 0)
