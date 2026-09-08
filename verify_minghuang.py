#!/usr/bin/env python3
# 明皇杂录 导读页核验：正向引文对库 + 谶签对读列 + 反扫 + 机数 + 红线 + mulu 联检
import re, sys, unicodedata

LIB_PATH = 'daizhige-simplified/史藏/志存记录/明皇杂录.txt'
PAGE = 'daizhige-daodu/minghuang-zalu.html'
MULU = 'daizhige-daodu/mulu.html'

lib = open(LIB_PATH, encoding='utf-8').read()
html = open(PAGE, encoding='utf-8').read()

fails = []
def chk(cond, msg):
    if not cond:
        fails.append(msg)

# ---------- 归一：去标点/符号/空白，従归从 ----------
def norm(s):
    s = unicodedata.normalize('NFC', s)
    s = s.replace('従', '从')
    return re.sub(r'[\W_]+', '', s, flags=re.UNICODE)
NLIB = norm(lib)

# ---------- 1 正向：.q 引文块 ----------
hsrc = re.sub(r'<script.*?</script>|<style.*?</style>', '', html, flags=re.S)
q_all = re.findall(r'<q class="q[^"]*"[^>]*>(.*?)</q>', hsrc, re.S)
print(f'.q 引文块 {len(q_all)} 处')
for i, q in enumerate(q_all):
    n = norm(re.sub(r'<[^>]+>', '', q))
    if n and n not in NLIB:
        fails.append(f'引文[{i}]不在库本: {q[:60]}')

# ---------- 2 舞马面板 .qk ----------
qk_all = re.findall(r'<q class="qk"[^>]*>(.*?)</q>', hsrc, re.S)
print(f'.qk 面板引文 {len(qk_all)} 处')
for i, q in enumerate(qk_all):
    n = norm(re.sub(r'<[^>]+>', '', q))
    if n and n not in NLIB:
        fails.append(f'面板引文[{i}]不在库本: {q[:60]}')

# ---------- 3 谶签对读列 .qz / .qj ----------
qz_all = re.findall(r'<div class="qz">(.*?)</div>', hsrc, re.S)
qj_all = re.findall(r'<div class="qj">(.*?)</div>', hsrc, re.S)
print(f'.qz 谶句 {len(qz_all)} 处，.qj 自注 {len(qj_all)} 处')
chk(len(qz_all) == 4 and len(qj_all) == 4, '谶签对读列应为四对')
for i, q in enumerate(qz_all + qj_all):
    n = norm(re.sub(r'<[^>]+>', '', q))
    if n and n not in NLIB:
        fails.append(f'对读列[{i}]不在库本: {q[:40]}')

# ---------- 4 首屏题记 ----------
epi = re.search(r'<q id="epiQ">(.*?)</q>', hsrc, re.S)
chk(bool(epi), '首屏题记缺失')
if epi:
    n = norm(epi.group(1))
    if n not in NLIB:
        fails.append(f'首屏题记不在库本: {epi.group(1)[:40]}')

# ---------- 5 穷尽「」扫描 ----------
body = re.sub(r'<script.*?</script>|<style.*?</style>', '', hsrc, flags=re.S)
body = re.sub(r'<[^>]+>', '', body)
quotes_all = re.findall(r'「([^」]*)」', body)
print(f'页面「」引语 {len(quotes_all)} 处')
for q in quotes_all:
    n = norm(q)
    if n and n not in NLIB:
        fails.append(f'「」引语不在库本: {q[:60]}')

# ---------- 6 反扫：未遮罩文本 12 字窗 ----------
masked = hsrc
for pat in [r'<q class="q[^"]*"[^>]*>.*?</q>', r'<q class="qk">.*?</q>',
            r'<div class="qz">.*?</div>', r'<div class="qj">.*?</div>',
            r'<q id="epiQ">.*?</q>']:
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

# ---------- 7 机数 ----------
nospace = re.sub(r'\s', '', lib)
chk(len(nospace) == 12248, f'去空白字数 {len(nospace)} != 12248')
secs = re.findall(r'●(卷上|卷下|补遗)', lib)
chk(secs == ['卷上','卷下','补遗'], f'卷次异常 {secs}')
paras = {'卷上':0,'卷下':0,'补遗':0}
sec = None
for l in lib.split('\n'):
    l = l.strip()
    if not l: continue
    m = re.match(r'●(卷上|卷下|补遗)', l)
    if m: sec = m.group(1)
    elif sec: paras[sec] += 1
chk(paras == {'卷上':15,'卷下':15,'补遗':13}, f'分段计数异常 {paras}')
for s in ['12,248', '43', '卷上十五段', '卷下十五段', '补遗十三段']:
    chk(s in html, f'页面缺申报: {s}')

# ---------- 8 篇号 ----------
chk('第二百八十九' in html, '篇号缺失')
chk('第<b>二百八十九</b>篇' in html, '页脚篇号格式')
chk('明皇杂录' in html and '殆知阁导读' in html, '标题要素')

# ---------- 9 红线 ----------
chk('—' not in html and '–' not in html, '出现长划线')
for ln, line in enumerate(re.sub(r'<[^>]+>', '\n', html).splitlines(), 1):
    if line.count('·') > 1:
        fails.append(f'行{ln} · 超限: {line[:50]}')
        break

# ---------- 10 mulu 联检 ----------
if '--mulu' in sys.argv:
    mulu = open(MULU, encoding='utf-8').read()
    chk('minghuang-zalu.html' in mulu, 'mulu 缺本页链接')
    nums = [int(x) for x in re.findall(r'class="no mono">(\d+)</span>', mulu)]
    chk(sorted(nums) == list(range(1, len(nums)+1)), 'mulu 编号不连续')
    chk(len(nums) == len(set(nums)), 'mulu 编号重复')
    print(f'mulu 条目 {len(nums)} 篇，最大编号 {max(nums)}')
    chk('二百八十九篇导读' in mulu, 'mulu 页脚计数未更新')

print()
if fails:
    print(f'FAIL {len(fails)} 项')
    for f in fails:
        print(' -', f)
    sys.exit(1)
print(f'PASS：引文 {len(q_all)}+{len(qk_all)} 处、对读列 {len(qz_all)+len(qj_all)} 处、题记 1 处全对库，反扫零命中，机数全过')
