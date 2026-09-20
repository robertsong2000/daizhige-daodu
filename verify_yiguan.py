# -*- coding: utf-8 -*-
# 核验 yiguan.html:引文逐字比对 + 白话六字窗反扫 + 排版规则
import re, sys

SRC = '/home/robertsong/workspace/claude/daizhige-simplified/医藏/医贯.txt'
PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/yiguan.html'

PUNC = '。，、；:;?!！“”‘’《》〈〉（）()·.\'\"[]【】〈〉—－~～…◇◆·｛｝〈〉「」『』'

def norm(s):
    s = re.sub(r'<[^>]+>', '', s)
    s = re.sub(r'\s+', '', s)
    for p in PUNC:
        s = s.replace(p, '')
    return s

src_n = norm(open(SRC, encoding='utf-8').read())
page = open(PAGE, encoding='utf-8').read()

# strip scripts
body = re.sub(r'<script.*?</script>', '', page, flags=re.S)

fails = []

# 1) every q / qv must be a verbatim slice of source
qs = re.findall(r'<q\b[^>]*>(.*?)</q>', body, re.S)
qvs = re.findall(r'<qv\b[^>]*>(.*?)</qv>', body, re.S)
ok_q = ok_qv = 0
for i, t in enumerate(qs):
    n = norm(t)
    if not n:
        fails.append(f'q#{i} empty'); continue
    if n in src_n: ok_q += 1
    else: fails.append(f'q#{i} NOT in source: {n[:40]}')
for i, t in enumerate(qvs):
    n = norm(t)
    if not n:
        fails.append(f'qv#{i} empty'); continue
    if n in src_n: ok_qv += 1
    else: fails.append(f'qv#{i} NOT in source: {n[:40]}')

# 2) reverse scan: no 6-gram of source in prose (text minus quotes)
prose = body
prose = re.sub(r'<q\b.*?</q>', '‖', prose, flags=re.S)
prose = re.sub(r'<qv\b.*?</qv>', '‖', prose, flags=re.S)
prose = re.sub(r'<[^>]+>', '', prose)
prose_n = norm(prose)
grams_prose = {prose_n[i:i+6] for i in range(len(prose_n) - 5)}
hits = []
grams_src_seen = set()
for i in range(len(src_n) - 5):
    g = src_n[i:i+6]
    if g in grams_prose:
        hits.append(g)
hits = sorted(set(hits))

# 3) typography
if '—' in page or '–' in page:
    fails.append('long dash present')
for ln_no, ln in enumerate(page.split('\n'), 1):
    if ln.count('·') > 1:
        fails.append(f'line {ln_no} has {ln.count("·")} ·')

# 4) PUA anywhere in rendered text
for ch in prose:
    if '' <= ch <= '':
        fails.append(f'PUA char {hex(ord(ch))} in prose'); break

print(f'q verified: {ok_q}/{len(qs)}   qv verified: {ok_qv}/{len(qvs)}')
print(f'prose norm chars: {len(prose_n)}   source 6-gram collisions: {len(hits)}')
if hits:
    for h in hits[:20]: print('  HIT:', h)
if fails:
    print('FAILS:'); [print('  ', f) for f in fails]
    sys.exit(1)
print('ALL CHECKS PASSED')
