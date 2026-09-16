# -*- coding: utf-8 -*-
"""中馈录导读页校验：引文正扫比对 + qv正扫 + 全文反扫(按块切分) + 排版规则。"""
import re, sys, unicodedata

SRC = '/home/robertsong/workspace/claude/daizhige-simplified/艺藏/饮馔/浦江吴氏中馈录.txt'
HTML = '/home/robertsong/workspace/claude/daizhige-daodu/zhongkuilu.html'

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

body = re.sub(r'<script[\s\S]*?</script>', '', page)
body = re.sub(r'<style[\s\S]*?</style>', '', body)
body = re.sub(r'<title>[\s\S]*?</title>', '', body)

Q_PAT = r'<span[^>]*class="[^"]*\bq\b[^"]*"[^>]*>'
QV_PAT = r'<span[^>]*class="[^"]*\bqv\b[^"]*"[^>]*>'

def clean(q):
    q = re.sub(r'<small[\s\S]*?</small>', '', q)
    return re.sub(r'<[^>]+>', '', q)

# ---- 1. 正扫：.q 引文逐条比对 ----
quotes = [clean(q) for q in re.findall(Q_PAT + r'([\s\S]*?)</span>', body)]
fails = []
for i, q in enumerate(quotes):
    nq = norm(q)
    if not nq or nq not in nsrc:
        fails.append((i, q[:44]))
print('正扫q: %d 条引文, 未过 %d' % (len(quotes), len(fails)))
for f in fails:
    print('  FAIL', f)

# ---- 1b. qv 正扫：展示照录字须为库内子串 ----
qvs = [clean(q) for q in re.findall(QV_PAT + r'([\s\S]*?)</span>', body)]
qvfails = []
for i, q in enumerate(qvs):
    nq = norm(q)
    if not nq or nq not in nsrc:
        qvfails.append((i, q[:30]))
print('正扫qv: %d 条, 未过 %d' % (len(qvs), len(qvfails)))
for f in qvfails:
    print('  FAILqv', f)

# ---- 2. 反扫：引文之外的可见文本按块切分，6字窗不得出现在库内 ----
rest = re.sub(Q_PAT + r'[\s\S]*?</span>', '\n', body)
rest = re.sub(QV_PAT + r'[\s\S]*?</span>', '\n', rest)
rest = re.sub(r'<[^>]+>', '\n', rest)
W = 6
hits = []
for chunk in rest.split('\n'):
    v = norm(chunk)
    for i in range(0, max(0, len(v) - W + 1)):
        win = v[i:i + W]
        if win in nsrc:
            hits.append((chunk[:24], win))
print('反扫(%d字窗,按块): 撞窗 %d' % (W, len(hits)))
for h in hits[:14]:
    print('  HIT', h[1], '块:', h[0])

# ---- 3. 排版规则 ----
dash = [c for c in ('—', '–') if c in page]
dot_lines = [(n, l.strip()[:40]) for n, l in enumerate(page.split('\n'), 1) if l.count('·') > 1]
print('长划线:', dash, '| ·超1行数:', len(dot_lines))
for d in dot_lines:
    print('  DOT', d)

ok = not fails and not qvfails and not hits and not dash and not dot_lines
assert '.q{display:block;background:' in page.replace(' ', ''), '引文块缺纸底'
print('排版: 纸底引文OK')
if not ok:
    sys.exit(1)
print('ALL PASS | q=%d qv=%d' % (len(quotes), len(qvs)))
