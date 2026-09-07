#!/usr/bin/env python3
# 核验 jixia-gewubian.html：引文双侧比对 + 反扫 + 排版规则 + mulu 联检
import re, sys, unicodedata

PAGE = 'jixia-gewubian.html'
LIB = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/几暇格物编.txt'
MULU = 'mulu.html'

def norm(s):
    s = unicodedata.normalize('NFKC', s)
    return re.sub(r'[^\w]', '', s)

raw = open(PAGE, encoding='utf-8').read()
lib_raw = open(LIB, encoding='utf-8').read()
mulu = open(MULU, encoding='utf-8').read()
fails = []

# 库本统计
lib_flat = re.sub(r'\s', '', lib_raw)
n_flat = len(lib_flat)
lib_titles = [l.strip() for l in lib_raw.split('\n') if l.strip() and len(l.strip()) <= 12 and l.strip() != '康熙几睱格物编']
L = norm(lib_raw)

# 剥 script/style
doc = re.sub(r'<script\b.*?</script>', '', raw, flags=re.S)
doc = re.sub(r'<style\b.*?</style>', '', doc, flags=re.S)

# 提 <q>
quotes = [m for m in re.findall(r'<q[^>]*>(.*?)</q>', doc, flags=re.S)]
doc_nq = re.sub(r'<q[^>]*>.*?</q>', '', doc, flags=re.S)
text = re.sub(r'<[^>]+>', '\n', doc_nq)
q2 = re.findall(r'「([^」]+)」', text)
q3 = re.findall(r'『([^』]+)』', text)
allq = [(f'<q>{i+1}', q) for i, q in enumerate(quotes)] + [(f'「」{i+1}', q) for i, q in enumerate(q2)] + [(f'『』{i+1}', q) for i, q in enumerate(q3)]

print(f'引文总数: {len(allq)} (<q> {len(quotes)} + 「」 {len(q2)} + 『』 {len(q3)})')
for tag, q in allq:
    n = norm(q)
    if len(n) < 2:
        continue
    if n not in L:
        fails.append(f'引文核验失败 [{tag}]: {q[:60]}')

# 残文反扫 >=6 字组撞库
residual = re.sub(r'「[^」]*」', '', text)
residual = re.sub(r'『[^』]*』', '', residual)
hits = 0
for ln in residual.split('\n'):
    n = norm(ln)
    for i in range(len(n) - 5):
        g = n[i:i+6]
        if g in L:
            hits += 1
            fails.append(f'反扫撞库: {g}  行: {ln.strip()[:50]}')
            break

# 排版规则
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
for token in ['殆知阁简体库', '逐字核验', '历史眼光', 'href="mulu.html"']:
    if token not in raw:
        fails.append(f'页脚缺: {token}')
for el_id in ['gnomonBox', 'bowlScene', 'pourBtn', 'eyeNote', 'residue', 'residueLabel', 'piWarn', 'spring', 'needle', 'degOut']:
    if f'id="{el_id}"' not in raw:
        fails.append(f'JS 目标缺失: #{el_id}')

print(f'库本: 去空白 {n_flat} 字, 条目 {len(lib_titles)} 条')
if n_flat != 20698:
    fails.append(f'库本去空白字数变动: {n_flat}')
if len(lib_titles) != 93:
    fails.append(f'条目数异常: {len(lib_titles)}')

# mulu 联检
nums = [int(x) for x in re.findall(r'class="no mono">(\d+)<', mulu)]
if sorted(nums) != list(range(1, len(nums) + 1)):
    dup = sorted(set(x for x in nums if nums.count(x) > 1))
    fails.append(f'mulu 编号不连续/重复: 缺{sorted(set(range(1,max(nums)+1))-set(nums))} 重{dup}')
if 'jixia-gewubian.html' not in mulu:
    fails.append('mulu 缺本篇链接')
if '二百二十八篇导读合订' not in mulu:
    fails.append('mulu kicker 计数未更新')
if mulu.count('二百二十八篇导读') < 2:
    fails.append('mulu kicker/footer 计数不足两处')
if '壹佰肆拾贰' not in mulu or '卷一百四十二 · 观物' not in mulu:
    fails.append('mulu 卷头缺 壹佰肆拾贰/卷一百四十二 · 观物')
my_pos = mulu.find('jixia-gewubian.html')
my_block = mulu[max(0, my_pos-1200):my_pos]
if 'class="vol"' not in my_block or 'vseal' not in my_block:
    fails.append('mulu 本篇未用 .vol/.vseal 模板')

if fails:
    print(f'\nFAIL × {len(fails)}')
    for f in fails:
        print(' -', f)
    sys.exit(1)
print('\nALL PASS')
