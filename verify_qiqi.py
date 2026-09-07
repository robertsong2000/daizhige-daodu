# -*- coding: utf-8 -*-
"""qiqi-tushuo.html 核验：引文逐字 + 排版红线 + mulu 计数"""
import re, sys, json

page = open('daizhige-daodu/qiqi-tushuo.html', encoding='utf-8').read()
flat = re.sub(r'\s+', '', page)
quotes = json.load(open('daizhige-daodu/quotes_qiqi.json', encoding='utf-8'))
lib = re.sub(r'\s+', '', open('daizhige-simplified/艺藏/器物/奇器图说.txt', encoding='utf-8').read())

fails = []

# 1 引文逐字：页面须完整包含每段原文，且原文确在库本
PUA = {'': '扬'}
for k, v in quotes.items():
    if v not in lib:
        fails.append(f'引文不在库本: {k}')
    for a, b in PUA.items():
        v = v.replace(a, b)
    if v not in flat:
        fails.append(f'引文不在页面: {k}')
if any(chr(c) in flat for c in range(0xE000, 0xF900)):
    fails.append('页面含 PUA 字')

# 2 禁长划线
for ch in ['—', '–', '―']:
    if ch in page:
        fails.append(f'禁字符 {ch} x{page.count(ch)}')

# 3 每行·最多 1 个
for i, line in enumerate(page.split('\n'), 1):
    if line.count('·') > 1:
        fails.append(f'行{i} 含 {line.count("·")} 个 ·: {line.strip()[:60]}')

# 4 零外部依赖
for pat in ['src="http', "src='http", 'href="http', "@import", 'url(']:
    if pat in page:
        for line in page.split('\n'):
            if pat in line and 'github.com' not in line:
                fails.append(f'外部依赖 {pat}: {line.strip()[:70]}')
                break

# 5 字数自述
if '28375' not in page:
    fails.append('页脚字数自述缺失')
real = len(lib)
if f'{real}' != '28375':
    fails.append(f'库本去空白字数实为 {real}')

# 6 篇号自述
if '二百' not in page:
    fails.append('篇号二百缺失')

# 7 占位符残留
if '⟦' in page:
    fails.append('占位符残留')

# 8 mulu 计数（若已挂目录）
try:
    mulu = open('daizhige-daodu/mulu.html', encoding='utf-8').read()
    if 'qiqi-tushuo.html' in mulu:
        nums = sorted(set(int(n) for n in re.findall(r'<span class="no mono">(\d+)</span>', mulu)))
        if nums != list(range(1, len(nums) + 1)):
            fails.append(f'mulu 编号不连续: {nums[:5]}...{nums[-5:]}')
        kicks = re.findall(r'([一-鿿]+)篇导读合订', mulu)
        foots = re.findall(r'([一-鿿]+)篇导读', mulu)
        cn = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10}
        def cnum(s):
            if s.startswith('十'): return 10 + (cn[s[1]] if len(s) > 1 else 0)
            if '百' in s:
                b, rest = s.split('百', 1); v = cn[b] * 100
                if rest:
                    if rest.startswith('十'): v += 10 + (cn[rest[1]] if len(rest) > 1 else 0)
                    else: v += cn.get(rest[0], 0)
                return v
            return 0
        for s in kicks + foots:
            if cnum(s) != len(nums):
                fails.append(f'mulu 计数「{s}」= {cnum(s)} ≠ 实际 {len(nums)}')
except FileNotFoundError:
    pass

if fails:
    print('FAIL')
    for f in fails: print(' -', f)
    sys.exit(1)
print('PASS：引文', len(quotes), '段逐字过，排版红线全过')
