# -*- coding: utf-8 -*-
"""钦定钱录导读页校验：引文正扫比对 + 全文反扫 + 排版规则。"""
import re, sys, unicodedata

SRC = '/home/robertsong/workspace/claude/daizhige-simplified/艺藏/器物/钦定钱录.txt'
HTML = '/home/robertsong/workspace/claude/daizhige-daodu/qinding-qianlu.html'

src = open(SRC, encoding='utf-8').read()
page = open(HTML, encoding='utf-8').read()

def norm(s):
    out = []
    for ch in s:
        cat = unicodedata.category(ch)
        if cat[0] in ('L', 'N'):
            out.append(ch)
    return ''.join(out)

nsrc = norm(src)

# ---- 1. 正扫：抽取 <q> 与 span.q 引文，逐条比对 ----
body = re.sub(r'<script[\s\S]*?</script>', '', page)
body = re.sub(r'<style[\s\S]*?</style>', '', body)
quotes = re.findall(r'<q[^>]*>([\s\S]*?)</q>', body) + \
         re.findall(r'<span class="q"[^>]*>([\s\S]*?)</span>', body)
quotes = [re.sub(r'<[^>]+>', '', q) for q in quotes]
fails = []
for i, q in enumerate(quotes):
    nq = norm(q)
    if not nq or nq not in nsrc:
        fails.append((i, q[:40]))
print('正扫: %d 条引文, 未过 %d' % (len(quotes), len(fails)))
for f in fails:
    print('  FAIL', f)
if fails:
    sys.exit(1)

# ---- 2. 反扫：引文之外的可见文本，6 字窗不得出现在库内 ----
rest = re.sub(r'<q[^>]*>[\s\S]*?</q>', '', body)
rest = re.sub(r'<span class="q"[^>]*>[\s\S]*?</span>', '', rest)
rest = re.sub(r'<[^>]+>', '', rest)
visible = norm(rest)
W = 6
hits = []
for i in range(0, max(0, len(visible) - W + 1)):
    win = visible[i:i + W]
    if win in nsrc:
        hits.append((i, win))
print('反扫(%d字窗): 撞窗 %d' % (W, len(hits)))
for h in hits[:12]:
    print('  HIT', h[1], '...ctx:', visible[max(0, h[0]-6):h[0]+W+6])
if hits:
    sys.exit(1)

# ---- 3. 排版规则 ----
assert '—' not in page and '–' not in page, '长划线混入'
dot_lines = [(n, l) for n, l in enumerate(page.split('\n'), 1) if l.count('·') > 1]
print('·超1行数:', len(dot_lines))
for d in dot_lines:
    print('  DOT', d)
if dot_lines:
    sys.exit(1)

assert '.q{display:block;background:' in page.replace(' ', ''), '引文块缺纸底'

print('排版: 长划线0, ·规则OK, 纸底引文OK')
print('ALL PASS | quotes verified: %d' % len(quotes))
