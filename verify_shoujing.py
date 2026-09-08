#!/usr/bin/env python3
# 君子堂日询手镜 导读页核验：正向引文对库 + 穷尽「」扫描 + 反扫 + 机数 + 红线
import re, sys, unicodedata

LIB_PATH = 'daizhige-simplified/子藏/笔记/君子堂日询手镜.txt'
PAGE = 'daizhige-daodu/shoujing.html'
MULU = 'daizhige-daodu/mulu.html'

lib = open(LIB_PATH, encoding='utf-8').read()
html = open(PAGE, encoding='utf-8').read()

fails = []
def chk(cond, msg):
    if not cond:
        fails.append(msg)

def norm(s):
    s = unicodedata.normalize('NFC', s)
    return re.sub(r'[\W_]+', '', s, flags=re.UNICODE)
NLIB = norm(lib)

# ---------- 1 正向：.q 块 ----------
hsrc = re.sub(r'<script.*?</script>|<style.*?</style>', '', html, flags=re.S)
q_all = [m.group(1) for m in re.finditer(r'class="q"[^>]*>(.*?)</(?:q|span)>', hsrc, re.S)]
print(f'.q 引文块 {len(q_all)} 处')
for i, q in enumerate(q_all):
    q = re.sub(r'<i>.*?</i>', '', q, flags=re.S)
    n = norm(re.sub(r'<[^>]+>', '', q))
    if n and n not in NLIB:
        fails.append(f'引文[{i}]不在库本: {q[:60]}')

# ---------- 2 穷尽「」扫描 ----------
body = re.sub(r'<script.*?</script>|<style.*?</style>', '', html, flags=re.S)
body = re.sub(r'<[^>]+>', '', body)
quotes_all = re.findall(r'「([^」]*)」', body)
print(f'页面「」引语 {len(quotes_all)} 处')
for q in quotes_all:
    n = norm(q)
    if n and n not in NLIB:
        fails.append(f'「」引语不在库本: {q[:60]}')

# ---------- 3 反扫：未被遮罩文本 12 字窗 ----------
masked = re.sub(r'class="q"[^>]*>.*?</(?:q|span)>', '§', html, flags=re.S)
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

# ---------- 4 机数与结构 ----------
nospace = re.sub(r'\s', '', lib)
chk(len(nospace) == 10479, f'去空白字数 {len(nospace)} != 10479')
shang = lib[lib.find('●上卷'):lib.find('●下卷')]
xia = lib[lib.find('●下卷'):]
n_shang = len([p for p in shang.split('\n\n') if p.strip()]) - 1  # 扣掉●上卷标题块
n_xia = len([p for p in xia.split('\n\n') if p.strip() and not p.strip().startswith('●下卷')])
chk(n_shang == 22, f'上卷则数 {n_shang} != 22')
chk(n_xia == 15, f'下卷则数 {n_xia} != 15')
# 批语计数与页面申报一致
for w, n in [('可爱', 10), ('甚佳', 5), ('可笑', 4), ('可鄙', 4), ('甚异', 2)]:
    c = lib.count(w)
    chk(c == n, f'库本「{w}」出现 {c} 次 != {n}')
for s in ['10,479', '可爱十见', '甚佳五见', '可笑四见', '可鄙四见', '甚异两见', '二十五']:
    chk(s in html, f'页面缺申报: {s}')
chk('殆知阁导读 二百八十四' in html, 'title 篇号')
chk('第<b>二百八十四</b>篇' in html, '页脚篇号')
# 首屏两相与图鉴结构
chk('pane-wz' in html and 'pane-hz' in html, '镜相两块缺失')
chk(len(re.findall(r'class="slat"', html)) == 6, '异物谱应为 6 竖简')

# ---------- 5 红线 ----------
chk('—' not in html and '–' not in html, '出现长划线')
for ln, line in enumerate(re.sub(r'<[^>]+>', '\n', html).splitlines(), 1):
    if line.count('·') > 1:
        fails.append(f'行{ln} · 超限: {line.strip()[:40]}')
        break

# ---------- 6 mulu 联检 ----------
if '--mulu' in sys.argv:
    mulu = open(MULU, encoding='utf-8').read()
    chk('shoujing.html' in mulu, 'mulu 缺本页链接')
    nums = [int(x) for x in re.findall(r'class="no mono">(\d+)</span>', mulu)]
    chk(sorted(nums) == list(range(1, len(nums)+1)), 'mulu 编号不连续')
    chk(len(nums) == len(set(nums)), 'mulu 编号重复')
    print(f'mulu 条目 {len(nums)} 篇，最大编号 {max(nums)}')

print()
if fails:
    print(f'FAIL {len(fails)} 项')
    for f in fails:
        print(' -', f)
    sys.exit(1)
print(f'PASS：引文 {len(q_all)} 处全对库，「」{len(quotes_all)} 处全对库，反扫零命中，机数与则数全过，红线全过')
