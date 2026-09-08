#!/usr/bin/env python3
# 核验 xiaoting-zalu.html：引文双侧比对 + script 内「」引文 + 反扫 + 排版规则 + mulu 联检
import re, sys, unicodedata

PAGE = 'xiaoting-zalu.html'
LIB = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/啸亭杂录.txt'
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

# ---- 残文反扫 >=6 字组撞库（script 已剥除；书名题注 〈〉 非引文，一并豁免）----
residual = re.sub(r'「[^」]*」', '', text)
residual = re.sub(r'『[^』]*』', '', residual)
residual = re.sub(r'〈[^〉]*〉', '', residual)
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
for a, b, msg in [('<div', '</div>', 'div'), ('<q', '</q>', 'q'), ('<section', '</section>', 'section'), ('<footer', '</footer>', 'footer')]:
    if raw.count(a) != raw.count(b):
        fails.append(f'标签不配平: {msg} {raw.count(a)}/{raw.count(b)}')
for token in ['殆知阁古代文献', '逐字核验', '历史眼光', 'href="mulu.html"']:
    if token not in raw:
        fails.append(f'页脚缺: {token}')

# ---- 库本统计 ----
print(f'库本: 去空白 {n_flat} 字')
if n_flat != 257307:
    fails.append(f'库本去空白字数变动: {n_flat}')

# ---- mulu 联检（更新后启用）----
if 'xiaoting-zalu.html' in mulu:
    nums = [int(x) for x in re.findall(r'class="no mono">(\d+)<', mulu)]
    if sorted(nums) != list(range(1, len(nums) + 1)):
        dup = sorted(set(x for x in nums if nums.count(x) > 1))
        fails.append(f'mulu 编号不连续/重复: 缺{sorted(set(range(1, max(nums)+1))-set(nums))} 重{dup}')
    print(f'mulu: {len(nums)} 篇, max {max(nums)}')
    if max(nums) != 247:
        fails.append(f'mulu 最新编号应为 247: {max(nums)}')
    if '二百四十七篇导读合订' not in mulu:
        fails.append('mulu kicker 计数未更新（应 247）')
    if mulu.count('二百四十七篇') < 2:
        fails.append('mulu kicker/footer 计数不足两处')
    if '壹佰陆拾' not in mulu or '卷一百六十 · 禁中' not in mulu:
        fails.append('mulu 卷头缺 壹佰陆拾/卷一百六十 · 禁中')
    my_pos = mulu.find('xiaoting-zalu.html')
    my_block = mulu[max(0, my_pos-1200):my_pos]
    if 'class="vol"' not in my_block or 'vseal' not in my_block:
        fails.append('mulu 本篇未用 .vol/.vseal 模板')
    if mulu.count('href="xiaoting-zalu.html"') != 1 or mulu.count('xiaoting-zalu.html') != 2:
        fails.append('mulu 本篇链接异常')
else:
    print('mulu: 本篇尚未收录（先过页面检查，更新后重跑）')

if fails:
    print(f'\nFAIL × {len(fails)}')
    for f in fails:
        print(' -', f)
    sys.exit(1)
print('\nALL PASS')
