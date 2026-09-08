#!/usr/bin/env python3
# 于少保萃忠全传 导读页核验：正向引文对库 + 穷尽「」扫描 + 反扫 + 机数 + 红线
import re, sys, unicodedata

LIB_PATH = 'daizhige-simplified/集藏/小说/于少保萃忠全传.txt'
PAGE = 'daizhige-daodu/yushaobao.html'
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
masked = re.sub(r'class="q"[^>]*>.*?</(?:span|p|div)>', '§', html, flags=re.S)
masked = re.sub(r'class="ext"[^>]*>.*?</p>', '§', masked, flags=re.S)
masked = re.sub(r'<script.*?</script>|<style.*?</style>', '', masked, flags=re.S)
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
# 通行本异文须确实异于库本
ext = re.search(r'class="ext"[^>]*>(.*?)</p>', html, re.S)
chk(ext and norm(ext.group(1)) not in NLIB, '通行本异文栏与库本无差异或缺失')

# ---------- 4 机数 ----------
nospace = re.sub(r'\s', '', lib)
chk(len(nospace) == 112185, f'去空白字数 {len(nospace)} != 112185')
heads = re.findall(r'第[一二三四五六七八九十百]+传[^\n]{2,40}', lib)
chk(len(heads) == 80, f'传目行 {len(heads)} != 80（总目40+正文40）')
# 页面 JS 回目数组与库本总目一致
ch = re.findall(r"\['([^']+)','([^']+)'\]", html)
chk(len(ch) == 40, f'JS回目 {len(ch)} != 40')
zhongsu = lib[:lib.find('第五传 于廷益大比登科') if '第五传 于廷益大比登科' in lib else lib.find('第五传')]
for i, (a, b) in enumerate(ch):
    if norm(a + b) not in NLIB:
        fails.append(f'回目{i+1}不在库本: {a}{b}')
# 页面申报数字
for s in ['112,185', '四十传', '五签']:
    chk(s in html, f'页面缺申报: {s}')
# 五折带宽和为四十
foldw = [int(x) for x in re.findall(r'style="flex:(\d+)"', html)]
chk(sum(foldw) == 40, f'五折带宽 {foldw} 不合四十传')
# 篇号
chk('殆知阁导读 二百六十三' in html, 'title 篇号')
chk('第<b>二百六十三</b>篇' in html, '页脚篇号')
# 谶板五签兑现文齐
chk(len(re.findall(r'data-k="[a-e]"', html)) >= 10, '五签结构不全')

# ---------- 5 红线 ----------
chk('—' not in html and '–' not in html, '出现长划线')
for ln, line in enumerate(re.sub(r'<[^>]+>', '\n', html).splitlines(), 1):
    if line.count('·') > 1:
        fails.append(f'行{ln} · 超限')
        break

# ---------- 6 mulu 联检 ----------
if '--mulu' in sys.argv:
    mulu = open(MULU, encoding='utf-8').read()
    chk('yushaobao.html' in mulu, 'mulu 缺本页链接')
    nums = [int(x) for x in re.findall(r'class="no mono">(\d+)</span>', mulu)]
    chk(sorted(nums) == list(range(1, len(nums)+1)), 'mulu 编号不连续')
    print(f'mulu 条目 {len(nums)} 篇，最大编号 {max(nums)}')

print()
if fails:
    print(f'FAIL {len(fails)} 项')
    for f in fails:
        print(' -', f)
    sys.exit(1)
print(f'PASS：引文 {len(q_all)} 处全对库，「」{len(quotes_all)} 处全对库，回目40条对库，反扫零命中，机数全过')
