#!/usr/bin/env python3
# 兰雪集导读页核验：引文双向比对 + 排版红线
import re, sys

SRC = '/home/robertsong/workspace/claude/daizhige-simplified/集藏/四库别集/张大家兰雪集.txt'
PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/lanxue-ji.html'
lib = open(SRC, encoding='utf-8').read()
html = open(PAGE, encoding='utf-8').read()

def norm(s):
    return re.sub(r'[^一-鿿]', '', s)

lib_n = norm(lib)

# 1. 引文 -> 库内
qts = re.findall(r'<span class="qt(?: note)?"[^>]*>(.*?)</span>', html, re.S)
fails = 0
for i, q in enumerate(qts, 1):
    q_clean = re.sub(r'<[^>]+>', '', q)
    qn = norm(q_clean)
    if not qn:
        print(f'[警告] 引文{i}归一后为空'); continue
    if qn not in lib_n:
        fails += 1
        print(f'[失败] 引文{i}不在库内: {q_clean[:40]}...')
print(f'引文核验: {len(qts)} 条, 失败 {fails}')

# 2. 反扫：页面所有 >=14 汉字连续串，非引文命中的报出来
qt_norms = [norm(re.sub(r'<[^>]+>', '', q)) for q in qts]
body = re.sub(r'<script.*?</script>|<style.*?</style>', '', html, flags=re.S)
body = re.sub(r'<[^>]+>', '\n', body)
stray = set()
for chunk in body.split('\n'):
    for s in re.findall(r'[一-鿿]{14,}', chunk):
        sn = norm(s)
        if sn in lib_n and not any(sn in q or q in sn for q in qt_norms):
            stray.add(s)
print(f'未申报复用: {len(stray)} 处')
for s in sorted(stray):
    print('  复用:', s[:50])

# 3. 排版红线
bad1 = [ln for ln in html.split('\n') if '—' in ln or '–' in ln]
print(f'长划线: {len(bad1)} 行')
bad2 = [(i, ln) for i, ln in enumerate(html.split('\n'), 1) if ln.count('·') > 1]
print(f'每行·超1: {len(bad2)} 行')
for i, ln in bad2: print(f'  L{i}: {ln.strip()[:60]}')

sys.exit(1 if (fails or stray or bad1 or bad2) else 0)
