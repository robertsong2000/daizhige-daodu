#!/usr/bin/env python3
"""公孙龙子 导读页核验：引文逐字比对 + 白话反扫 + 排版规则"""
import re, html, unicodedata, sys

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/gongsunlongzi.html'
SRC = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/诸子/公孙龙子.txt'

raw = open(PAGE, encoding='utf-8').read()
src = open(SRC, encoding='utf-8').read()

VARI = {'髙': '高', '黒': '黑', '廐': '厩', '鬬': '斗', '柰': '奈',
        '着': '著', '歴': '历', '畧': '略', '毎': '每', '歳': '岁'}

def norm(s):
    s = ''.join(VARI.get(c, c) for c in s)
    s = re.sub(r'【[^】]*】', '', s)   # 库本夹注剔除
    s = re.sub(r'（[^）]*）', '', s)   # 编辑小注剔除
    s = re.sub(r'\s+', '', s)
    s = ''.join(ch for ch in s if unicodedata.category(ch).startswith(('L', 'N')))
    return s

NS = norm(src)
doc = re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>', '', raw)

# ---- 1. 引文比对：class 含 q/qv/qi 的元素 ----
qtexts = []
for m in re.finditer(r'<(\w+)([^>]*\bclass="[^"]*\b(?:q|qv|qi)\b[^"]*"[^>]*)>([\s\S]*?)</\1>', doc):
    inner = re.sub(r'<[^>]+>', '', m.group(3))
    t = html.unescape(inner).strip()
    if t:
        qtexts.append(t)
assert qtexts, 'no quotes found'
miss = [q for q in qtexts if norm(q) not in NS]
for q in miss:
    print('MISS:', q[:60])

# ---- 2. 反扫：非引文文本节点不得出现库本 6 字窗 ----
body = re.sub(r'<(\w+)([^>]*\bclass="[^"]*\b(?:q|qv|qi)\b[^"]*"[^>]*)>[\s\S]*?</\1>', '', doc)
nodes = re.findall(r'>([^<>]+)<', body)
hits = []
for t in nodes:
    t = html.unescape(t).strip()
    if not t or not re.search(r'[一-鿿]', t):
        continue
    n = norm(t)
    for i in range(max(0, len(n) - 5)):
        w = n[i:i+6]
        if len(w) == 6 and re.search(r'[一-鿿]{3}', w) and w in NS:
            hits.append((w, t[:30]))
for w, t in hits:
    print('HIT:', w, '<-', t)

# ---- 3. 排版规则 ----
for ch in ('—', '–'):
    assert ch not in raw, 'long dash found: ' + ch
plain = re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>', '', raw)
for ln in re.sub(r'<[^>]+>', '\n', plain).split('\n'):
    assert ln.count('·') <= 1, 'too many ·: ' + ln.strip()[:60]

print('quotes=%d miss=%d hits=%d' % (len(qtexts), len(miss), len(hits)))
sys.exit(1 if (miss or hits) else 0)
