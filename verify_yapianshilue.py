#!/usr/bin/env python3
# 核验 yapian-shilue.html：引文双侧比对 + script 内引文 + 反扫 + 排版规则 + 香港流水数据联检 + mulu 联检
import re, sys, unicodedata

PAGE = 'yapian-shilue.html'
LIB = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/鸦片事略.txt'
MULU = 'mulu.html'

def norm(s):
    s = unicodedata.normalize('NFKC', s)
    return re.sub(r'[^\w]', '', s)

raw = open(PAGE, encoding='utf-8').read()
lib_raw = open(LIB, encoding='utf-8').read()
mulu = open(MULU, encoding='utf-8').read()
fails = []

lib_flat = re.sub(r'\s', '', lib_raw)
n_flat = len(lib_flat)
L = norm(lib_raw)

# ---- 引文提取：正文 <q>/「」 + script 内 <q>/「」 ----
quotes = []
doc = re.sub(r'<script\b.*?</script>', '', raw, flags=re.S)
doc = re.sub(r'<style\b.*?</style>', '', doc, flags=re.S)
for m in re.finditer(r'<q[^>]*>(.*?)</q>', doc, flags=re.S):
    inner = re.sub(r'<[^>]+>', '', m.group(1))
    quotes.append(('body<q>' + str(len(quotes)+1), inner))
doc_nq = re.sub(r'<q[^>]*>.*?</q>', '', doc, flags=re.S)
text = re.sub(r'<[^>]+>', '\n', doc_nq)
for m in re.finditer(r'「([^」]+)」', text):
    quotes.append(('body「」' + str(len(quotes)+1), m.group(1)))
scripts = ''.join(re.findall(r'<script\b.*?</script>', raw, flags=re.S))
for m in re.finditer(r'<q[^>]*>(.*?)</q>', scripts, flags=re.S):
    quotes.append(('js<q>' + str(len(quotes)+1), m.group(1)))
s_txt = re.sub(r'<[^>]+>', '\n', scripts)
for m in re.finditer(r'「([^」]+)」', s_txt):
    quotes.append(('js「」' + str(len(quotes)+1), m.group(1)))

nq = sum(1 for _, q in quotes if len(norm(q)) >= 2)
print(f'引文总数: {len(quotes)}（norm≥2 计 {nq}）')
for tag, q in quotes:
    n = norm(q)
    if len(n) < 2:
        continue
    if n not in L:
        fails.append(f'引文核验失败 [{tag}]: {q[:70]}')

# ---- 残文反扫 >=6 字组撞库（script 已剥除）----
residual = re.sub(r'「[^」]*」', '', text)
for ln in residual.split('\n'):
    n = norm(ln)
    for i in range(len(n) - 5):
        g = n[i:i+6]
        if g in L:
            fails.append(f'反扫撞库: {g}  行: {ln.strip()[:60]}')
            break

# ---- 排版规则 ----
if '—' in raw or '–' in raw:
    fails.append('出现长划线 —/–')
for i, ln in enumerate(raw.split('\n'), 1):
    if ln.count('·') > 1:
        fails.append(f'第{i}行 · 超限: {ln.strip()[:60]}')
low = raw.lower()
for pat, msg in [('<link', '外部 <link'), ('@import', '@import'), ('url(', 'css url('),
                 ('<img', '<img'), ('<script src', '外链 script'), ('http://', 'http://')]:
    if pat in low:
        fails.append(f'外部依赖: {msg}')
if low.count('https://') != 1 or 'github.com/robertsong2000/daizhigev20' not in low:
    fails.append('https 引用数异常（应为仅页脚仓库链接 1 处）')
for a, b, msg in [('<div', '</div>', 'div'), ('<q', '</q>', 'q'), ('<section', '</section>', 'section'),
                  ('<footer', '</footer>', 'footer'), ('<header', '</header>', 'header'),
                  ('<span', '</span>', 'span'), ('<button', '</button>', 'button')]:
    if raw.count(a) != raw.count(b):
        fails.append(f'标签不配平: {msg} {raw.count(a)}/{raw.count(b)}')
for token in ['殆知阁古代文献', '逐字核验', '历史眼光', 'href="mulu.html"']:
    if token not in raw:
        fails.append(f'页脚缺: {token}')

# ---- 库本统计 ----
print(f'库本: 去空白 {n_flat} 字')
if n_flat != 46796:
    fails.append(f'库本去空白字数变动: {n_flat}')

# ---- 香港流水数据联检（库本中文数字 → 页面 HK 数组）----
CN = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'两':2}
def cn2int(s):
    total, section, cur = 0, 0, 0
    for ch in s:
        if ch in CN:
            cur = CN[ch]
        elif ch == '十':
            section += (cur or 1) * 10; cur = 0
        elif ch == '百':
            section += (cur or 1) * 100; cur = 0
        elif ch == '千':
            section += (cur or 1) * 1000; cur = 0
        elif ch == '万':
            section = (section + cur) * 10000; total += section; section, cur = 0, 0
    return total + section + cur

lib_data = []
for m in re.finditer(r'即，?西历(一千八百[一二三四五六七八九十百]+)年，至香港者，([一二三四五六七八九十百千万]+)石', lib_raw):
    lib_data.append((cn2int(m.group(1)), cn2int(m.group(2))))
mjson = re.search(r'const HK = (\[\[.*?\]\]);\n', raw, flags=re.S)
if not mjson:
    fails.append('页面缺 HK 数据')
else:
    hk = eval(mjson.group(1))
    lib_data = [d for d in lib_data if 1865 <= d[0] <= 1886]
    print(f'香港流水: 库本抽得 {len(lib_data)} 年, 页面 {len(hk)} 年')
    if len(lib_data) != 22:
        fails.append(f'库本年数异常: {len(lib_data)}（应为 1865 至 1886 共 22 年）')
    if [list(x) for x in hk] != [list(x) for x in lib_data]:
        for a, b in zip(hk, lib_data):
            if list(a) != list(b):
                fails.append(f'流水不符: 页 {list(a)} vs 库 {list(b)}')
        if len(hk) != len(lib_data):
            fails.append(f'流水年数: 页 {len(hk)} vs 库 {len(lib_data)}')
    peak = max((v for _, v in hk), default=0)
    if peak != 107970:
        fails.append(f'峰值异常: {peak}')

# ---- mulu 联检（更新后启用）----
if 'yapian-shilue.html' in mulu:
    nums = [int(x) for x in re.findall(r'class="no mono">(\d+)<', mulu)]
    if sorted(nums) != list(range(1, len(nums) + 1)):
        dup = sorted(set(x for x in nums if nums.count(x) > 1))
        fails.append(f'mulu 编号不连续/重复: 缺{sorted(set(range(1, max(nums)+1))-set(nums))} 重{dup}')
    print(f'mulu: {len(nums)} 篇, max {max(nums)}')
    if max(nums) != 242:
        fails.append(f'mulu 最新编号应为 242: {max(nums)}')
    if '二百四十二篇导读合订' not in mulu:
        fails.append('mulu kicker 计数未更新')
    if mulu.count('二百四十二篇导读') < 2:
        fails.append('mulu kicker/footer 计数不足两处')
    if '壹佰伍拾陆' not in mulu or '卷一百五十六 · 漏卮' not in mulu:
        fails.append('mulu 卷头缺 壹佰伍拾陆/卷一百五十六 · 漏卮')
    my_pos = mulu.find('yapian-shilue.html')
    my_block = mulu[max(0, my_pos-1200):my_pos]
    if 'class="vol"' not in my_block or 'vseal' not in my_block:
        fails.append('mulu 本篇未用 .vol/.vseal 模板')
else:
    print('mulu: 本篇尚未收录（先过页面检查，更新后重跑）')

if fails:
    print(f'\nFAIL × {len(fails)}')
    for f in fails:
        print(' -', f)
    sys.exit(1)
print('\nALL PASS')
