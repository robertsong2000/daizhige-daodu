#!/usr/bin/env python3
# 核验 guiqian-zhi.html：引文双侧比对（正文+script，含《》〈〉书篇引用）+ 反扫 + 排版规则 + 库本统计 + mulu 联检
import re, sys, unicodedata

PAGE = 'guiqian-zhi.html'
LIB = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/归潜志.txt'
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

# ---- 引文提取：<q> 与 「」《》〈〉（正文+script）----
quotes = []
doc = re.sub(r'<script\b.*?</script>', '', raw, flags=re.S)
doc = re.sub(r'<style\b.*?</style>', '', doc, flags=re.S)
for m in re.finditer(r'<q[^>]*>(.*?)</q>', doc, flags=re.S):
    inner = re.sub(r'<[^>]+>', '', m.group(1))
    quotes.append(('body<q>' + str(len(quotes)+1), inner))
def brace_spans(txt, tag):
    out = []
    for pat in (r'「([^」]+)」', r'《([^》]+)》', r'〈([^〉]+)〉'):
        for m in re.finditer(pat, txt):
            out.append((tag + str(len(out)+1), m.group(1)))
    return out
doc_nq = re.sub(r'<q[^>]*>.*?</q>', '', doc, flags=re.S)
text = re.sub(r'<[^>]+>', '\n', doc_nq)
quotes += brace_spans(text, 'body「」')
scripts = ''.join(re.findall(r'<script\b.*?</script>', raw, flags=re.S))
for m in re.finditer(r'<q[^>]*>(.*?)</q>', scripts, flags=re.S):
    quotes.append(('js<q>' + str(len(quotes)+1), m.group(1)))
s_txt = re.sub(r'<[^>]+>', '\n', scripts)
quotes += brace_spans(s_txt, 'js「」')

nq = sum(1 for _, q in quotes if len(norm(q)) >= 2)
print(f'引文总数: {len(quotes)}（norm≥2 计 {nq}）')
for tag, q in quotes:
    n = norm(q)
    if len(n) < 2:
        continue
    if n not in L:
        fails.append(f'引文核验失败 [{tag}]: {q[:70]}')

# ---- 残文反扫 >=6 字组撞库（剥除引号区后）----
residual = re.sub(r'「[^」]*」|《[^》]*》|〈[^〉]*〉', '', text)
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
for c in ['#191917', '#e8e4dc']:
    if c not in raw:
        fails.append(f'缺系列色 {c}')

# ---- 库本统计 ----
print(f'库本: 去空白 {n_flat} 字')
if n_flat != 82907:
    fails.append(f'库本去空白字数变动: {n_flat}')

# ---- mulu 联检（更新后启用）----
if 'guiqian-zhi.html' in mulu:
    nums = [int(x) for x in re.findall(r'class="no mono">(\d+)<', mulu)]
    if sorted(nums) != list(range(1, len(nums) + 1)):
        dup = sorted(set(x for x in nums if nums.count(x) > 1))
        fails.append(f'mulu 编号不连续/重复: 缺{sorted(set(range(1, max(nums)+1))-set(nums))} 重{dup}')
    print(f'mulu: {len(nums)} 篇, max {max(nums)}')
    if max(nums) != 250:
        fails.append(f'mulu 最新编号应为 250: {max(nums)}')
    if mulu.count('二百五十篇导读') < 2:
        fails.append('mulu kicker/footer 计数不足两处')
    my_pos = mulu.find('guiqian-zhi.html')
    vstart = mulu.rfind('<div class="vol"', 0, my_pos)
    if vstart < 0:
        fails.append('mulu 本篇不在任何 .vol 内')
    else:
        volhead = mulu[vstart:my_pos]
        if 'vseal' not in volhead:
            fails.append('mulu 所在卷缺 vseal 模板')
        if '卷三 · 金源' not in volhead:
            fails.append('mulu 本篇未归入卷三金源')
    prev_no = re.findall(r'class="no mono">(\d+)<', mulu[:my_pos])
    if prev_no and prev_no[-1] == '250':
        fails.append('mulu 本篇前面出现 250（编号区间错误）')
else:
    print('mulu: 本篇尚未收录（先过页面检查，更新后重跑）')

if fails:
    print(f'\nFAIL × {len(fails)}')
    for f in fails:
        print(' -', f)
    sys.exit(1)
print('\nALL PASS')
