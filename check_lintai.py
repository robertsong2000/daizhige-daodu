# -*- coding: utf-8 -*-
# 麟台故事 页面核验：引文逐字比对 + 白话反扫 + 排版规则
import re, sys

SRC = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/职官/麟台故事.txt'
PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/lintai-gushi.html'

def norm(s):
    return re.sub(r'[\s\W_]+', '', s)

src = norm(open(SRC, encoding='utf-8').read())
html = open(PAGE, encoding='utf-8').read()

fails = []

# 1) 禁字
for ch, name in [('—', 'em dash'), ('–', 'en dash')]:
    if ch in html:
        fails.append('file contains ' + name)

# 2) 每行 · 至多1（按源文件行 + 按文本节点双查）
for i, line in enumerate(html.split('\n'), 1):
    if line.count('·') > 1:
        fails.append('line %d has %d ·' % (i, line.count('·')))

# 3) 引文核验：抓所有 <q ...>...</q>
body = re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>', '', html)
qs = re.findall(r'<q[^>]*>([\s\S]*?)</q>', body)
bad = 0
for q in qs:
    t = norm(re.sub(r'<[^>]+>', '', q))
    if t and t not in src:
        bad += 1
        fails.append('QUOTE MISS: ' + t[:40])
print('quotes checked:', len(qs), 'miss:', bad)

# 4) 白话反扫：剥掉 q 元素后取全文本
bq = re.sub(r'<q[^>]*>[\s\S]*?</q>', '', body)
bq = re.sub(r'<title>[\s\S]*?</title>', '', bq)
text = re.sub(r'<[^>]+>', '', bq)
bai = norm(text)

W = 6
grams = {src[i:i+W] for i in range(len(src) - W + 1)}
hits = []
i = 0
while i <= len(bai) - W:
    w = bai[i:i+W]
    if w in grams:
        hits.append((i, w))
        i += W
    else:
        i += 1
print('baihua len:', len(bai), 'hits:', len(hits))
for i, w in hits:
    fails.append('BAIHUA HIT @%d: %s | ctx: %s' % (i, w, bai[max(0,i-10):i+W+10]))

if fails:
    print('FAIL')
    for f in fails:
        print(' -', f)
    sys.exit(1)
print('ALL PASS')
