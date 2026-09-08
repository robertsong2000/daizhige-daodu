#!/usr/bin/env python3
# 异域录 导读页核验：正向引文对库 + 反扫 + 字数 + 红线 + PUA + mulu 联检
import re, sys, unicodedata

LIB_PATH = 'daizhige-simplified/史藏/地理/异域录.txt'
PAGE = 'daizhige-daodu/yiyu-lu.html'
MULU = 'daizhige-daodu/mulu.html'

lib = open(LIB_PATH, encoding='utf-8').read()
html = open(PAGE, encoding='utf-8').read()

fails = []
def chk(cond, msg):
    if not cond:
        fails.append(msg)

# ---------- 归一：去标点/符号/空白 ----------
def norm(s):
    s = unicodedata.normalize('NFC', s)
    return re.sub(r'[\W_]+', '', s, flags=re.UNICODE)
NLIB = norm(lib)

# ---------- 1 正向：.q 引文块 ----------
hsrc = re.sub(r'<script.*?</script>|<style.*?</style>', '', html, flags=re.S)
q_all = re.findall(r'<q class="q[^"]*"[^>]*>(.*?)</q>', hsrc, re.S)
print(f'.q 引文块 {len(q_all)} 处')
chk(len(q_all) >= 15, f'引文块过少 {len(q_all)}')
for i, q in enumerate(q_all):
    n = norm(re.sub(r'<[^>]+>', '', q))
    if n and n not in NLIB:
        fails.append(f'引文[{i}]不在库本: {q[:50]}')

# ---------- 2 PUA ----------
pua = re.findall(r'[-]', hsrc)
chk(not pua, f'页面含 PUA 占位字 {len(pua)} 处')

# ---------- 3 反扫：未遮罩文本 12 字窗 ----------
masked = hsrc
for pat in [r'<q class="q[^"]*"[^>]*>.*?</q>']:
    masked = re.sub(pat, '§', masked, flags=re.S)
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

# ---------- 4 字数与卷次 ----------
nospace = re.sub(r'\s', '', lib)
chk(len(nospace) == 27509, f'去空白字数 {len(nospace)} != 27509')
vols = re.findall(r'异域录卷(上|下)', lib)
chk(vols.count('上') == 2 and vols.count('下') == 2, f'卷次标记异常 {vols}')
chk('二万七千五百零九' in html, '页面缺字数申报')

# ---------- 5 篇号 ----------
chk('第二百九十一' in html, '篇号缺失')
chk('第<b>二百九十一</b>篇' in html, '页脚篇号格式')
chk('异域录' in html and '殆知阁导读' in html, '标题要素')

# ---------- 6 红线 ----------
chk('—' not in html and '–' not in html, '出现长划线')
over = [ln for ln, line in enumerate(re.sub(r'<[^>]+>', '\n', html).splitlines(), 1)
        if line.count('·') > 1]
chk(not over, f'· 超限行 {over[:3]}')
ext = re.findall(r'(src|href)\s*=\s*"(?!#)([^"]+)"', hsrc)
ext = [u for a, u in ext if not u.startswith('https://github.com/robertsong2000')]
chk(not ext, f'外部依赖 {ext}')

# ---------- 7 mulu 联检 ----------
if '--mulu' in sys.argv:
    mulu = open(MULU, encoding='utf-8').read()
    chk('yiyu-lu.html' in mulu, 'mulu 缺本页链接')
    nums = [int(x) for x in re.findall(r'class="no mono">(\d+)</span>', mulu)]
    chk(sorted(nums) == list(range(1, len(nums)+1)), 'mulu 编号不连续')
    chk(len(nums) == len(set(nums)), 'mulu 编号重复')
    print(f'mulu 条目 {len(nums)} 篇，最大编号 {max(nums)}')
    def cnum(n):
        d = '零一二三四五六七八九'
        if n < 10: return d[n]
        if n < 20: return '十' + (d[n % 10] if n % 10 else '')
        if n < 100:
            return d[n // 10] + '十' + (d[n % 10] if n % 10 else '')
        if n < 1000:
            h = d[n // 100] + '百'
            r = n % 100
            if r == 0: return h
            if r < 10: return h + '零' + d[r]
            return h + cnum(r)
        return str(n)
    chk(f'{cnum(max(nums))}篇导读' in mulu, 'mulu 页脚计数未更新')

print()
if fails:
    print(f'FAIL {len(fails)} 项')
    for f in fails:
        print(' -', f)
    sys.exit(1)
print(f'PASS：引文 {len(q_all)} 处全对库，反扫零命中，字数卷次红线全过')
