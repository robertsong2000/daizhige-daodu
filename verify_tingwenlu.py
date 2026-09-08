#!/usr/bin/env python3
# 庭闻录 导读页核验：正向引文对库 + 穷尽「」扫描 + 反扫 + 机数 + 红线
import re, sys, unicodedata

LIB_PATH = 'daizhige-simplified/史藏/志存记录/庭闻录.txt'
PAGE = 'daizhige-daodu/tingwenlu.html'
MULU = 'daizhige-daodu/mulu.html'

lib = open(LIB_PATH, encoding='utf-8').read()
html = open(PAGE, encoding='utf-8').read()

fails = []
def chk(cond, msg):
    if not cond:
        fails.append(msg)

# ---------- 归一：去标点/符号/空白，保留字与数字 ----------
def norm(s):
    s = unicodedata.normalize('NFC', s)
    return re.sub(r'[\W_]+', '', s, flags=re.UNICODE)
NLIB = norm(lib)

# ---------- 1 正向：.q 块 ----------
hsrc = re.sub(r'<script.*?</script>|<style.*?</style>', '', html, flags=re.S)
q_all = [m.group(1) for m in re.finditer(r'class="q"[^>]*>(.*?)</(?:span|p|div)>', hsrc, re.S)]
print(f'.q 引文块 {len(q_all)} 处')
for i, q in enumerate(q_all):
    n = norm(re.sub(r'<[^>]+>', '', q))
    if n and n not in NLIB:
        fails.append(f'引文[{i}]不在库本: {q[:60]}')

# ---------- 2 穷尽「」扫描 ----------
body = re.sub(r'<script.*?</script>|<style.*?</style>', '', html, flags=re.S)
body = re.sub(r'<[^>]+>', '', body)
quotes_all = re.findall(r'「([^」]*)」', body)
print(f'页面「」引语 {len(quotes_all)} 处')
for q in quotes_all:
    n = norm(re.sub(r'<[^>]+>', '', q))
    if n and n not in NLIB:
        fails.append(f'「」引语不在库本: {q[:60]}')

# ---------- 3 反扫：未被遮罩文本 12 字窗 ----------
masked = re.sub(r'class="q"[^>]*>.*?</(?:span|p|div)>', '§', hsrc, flags=re.S)
visible = re.sub(r'<[^>]+>', '', masked)
NVIS = norm(visible)
bad = 0
for i in range(len(NVIS) - 11):
    w = NVIS[i:i+12]
    if w in NLIB:
        bad += 1
        if bad <= 5:
            fails.append(f'反扫命中未申报12字窗: {w}')
if bad > 5:
    fails.append(f'反扫共命中 {bad} 处')
print(f'反扫12字窗命中 {bad} 处')

# ---------- 4 机数 ----------
nospace = re.sub(r'\s', '', lib)
chk(len(nospace) == 31667, f'去空白字数 {len(nospace)} != 31667')
for jt in ['乞师逐寇', '镇秦徇蜀', '收滇入缅', '开藩专制', '称兵灭族', '杂录备遗']:
    chk(jt in lib, f'卷题不在库本: {jt}')
    chk(jt in html, f'页面缺卷题: {jt}')
chk(len(re.findall(r'class="jn"', html)) == 6, '六帙卷题带不是六格')
for s in ['31,667', '二百八十二', '庭闻录']:
    chk(s in html, f'页面缺申报: {s}')
chk('殆知阁导读 二百八十二' in html, 'title 篇号')
chk('第<b>二百八十二</b>篇' in html, '页脚篇号')
chk('daizhige-daodu/tingwenlu.html' not in html, '页面不应自引仓库路径')

# ---------- 5 红线 ----------
chk('—' not in html and '–' not in html, '出现长划线')
for ln, line in enumerate(re.sub(r'<[^>]+>', '\n', html).splitlines(), 1):
    if line.count('·') > 1:
        fails.append(f'行{ln} · 超限: {line.strip()[:50]}')
        break

# ---------- 6 mulu 联检 ----------
if '--mulu' in sys.argv:
    mulu = open(MULU, encoding='utf-8').read()
    chk('tingwenlu.html' in mulu, 'mulu 缺本页链接')
    nums = [int(x) for x in re.findall(r'class="no mono">(\d+)</span>', mulu)]
    chk(sorted(nums) == list(range(1, len(nums)+1)), 'mulu 编号不连续')
    print(f'mulu 条目 {len(nums)} 篇，最大编号 {max(nums)}')

print()
if fails:
    print(f'FAIL {len(fails)} 项')
    for f in fails:
        print(' -', f)
    sys.exit(1)
print(f'PASS：引文 {len(q_all)} 处全对库，「」{len(quotes_all)} 处全对库，反扫零命中，机数全过')
