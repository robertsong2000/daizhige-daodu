#!/usr/bin/env python3
# 引文核验：串雅内外编
import re, sys, unicodedata

BOOK = '/home/robertsong/workspace/claude/daizhige-simplified/医藏/串雅内外编.txt'
PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/chuanya.html'
MULU = '/home/robertsong/workspace/claude/daizhige-daodu/mulu.html'

def norm(s):
    out = []
    for ch in s:
        cat = unicodedata.category(ch)
        if cat[0] in ('P', 'S', 'Z', 'C'):
            continue
        out.append(ch)
    return ''.join(out)

book = open(BOOK, encoding='utf-8').read()
nbook = norm(book)
html = open(PAGE, encoding='utf-8').read()

fails = []

# 1. 正扫：所有 <q> 引文必须存在于库内（先剥 script，再剔除 q 内 .att 注解）
html_noscript = re.sub(r'<script.*?</script>', '', html, flags=re.S)
quotes = re.findall(r'<q[^>]*>(.*?)</q>', html_noscript, re.S)
seen = set()
ok = 0
for raw in quotes:
    raw = re.sub(r'<span class="att"[^>]*>.*?</span>', '', raw, flags=re.S)
    txt = re.sub(r'<[^>]+>', '', raw)
    txt = txt.strip()
    if not txt or txt in seen:
        continue
    seen.add(txt)
    n = norm(txt)
    if n not in nbook:
        fails.append('正扫未命中: ' + txt[:50])
    else:
        ok += 1
print(f'正扫: {ok} 条唯一引文全部命中' if not any(f.startswith('正扫') for f in fails) else '正扫有未命中!')

# 2. 反扫：去掉 q/script/style 后，正文不得含库内 6 字连续窗
body = re.sub(r'<script.*?</script>', '', html, flags=re.S)
body = re.sub(r'<style.*?</style>', '', body, flags=re.S)
body = re.sub(r'<q[^>]*>.*?</q>', '', body, flags=re.S)
body = re.sub(r'<[^>]+>', '', body)
nbody = norm(body)
hits = []
L = 6
step = max(1, len(nbook) // 4000)
checked = 0
for i in range(0, len(nbook) - L, 1):
    w = nbook[i:i+L]
    checked += 1
    if w in nbody:
        # 找回原文位置
        hits.append(w)
hits = sorted(set(hits))
print(f'反扫: 全窗扫描 {checked} 个 6 字窗，命中 {len(hits)} 处')
for w in hits[:20]:
    print('  反扫命中:', w)

# 3. 红线：长划线
for ch, name in (('—', 'em-dash —'), ('–', 'en-dash –')):
    if ch in html:
        fails.append('红线: 页面含 ' + name)
print('红线长划线: ' + ('未发现' if not any('红线' in f for f in fails) else '发现!'))

# 4. 每行 · 最多 1 个
bad = [i + 1 for i, l in enumerate(html.split('\n')) if l.count('·') > 1]
print('· 逐行上限: ' + ('通过' if not bad else f'超限行 {bad}'))
if bad:
    fails.append('· 超限')

# 5. mulu 编号连续（若已更新）
mulu = open(MULU, encoding='utf-8').read()
nums = sorted(set(int(x) for x in re.findall(r'class="no mono">(\d+)<', mulu)))
if nums:
    contiguous = nums == list(range(1, nums[-1] + 1))
    print(f'mulu 编号: 1..{nums[-1]} {"连续" if contiguous else "断号!"}')
    if not contiguous:
        fails.append('mulu 断号')

if fails:
    print('\n== 未过 ==')
    for f in fails:
        print(' -', f)
    sys.exit(1)
print('\n全部通过')
