# -*- coding: utf-8 -*-
"""yitongzi-wen.html 核验：引文逐字 + 排版红线 + mulu 计数"""
import re, sys, json

page = open('daizhige-daodu/yitongzi-wen.html', encoding='utf-8').read()
flat = re.sub(r'\s+', '', page)
quotes = json.load(open('daizhige-daodu/quotes_yitongzi.json', encoding='utf-8'))
lib = re.sub(r'\s+', '', open('daizhige-simplified/易藏/易经/易童子问.txt', encoding='utf-8').read())

fails = []

# 1 引文逐字：页面须完整包含每段原文，且原文确在库本
for k, v in quotes.items():
    v = re.sub(r'\s+', '', v)
    if v not in lib:
        fails.append(f'引文不在库本: {k}')
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
if '9662' not in page:
    fails.append('页脚字数自述缺失')
real = len(lib)
if real != 9662:
    fails.append(f'库本去空白字数实为 {real}')

# 6 篇号自述
if '204' not in page:
    fails.append('篇号 204 缺失')

# 7 占位符残留
if '⟦' in page:
    fails.append('占位符残留')

# 8 书脊交互完整性
pills = re.findall(r'data-key="([^"]+)"', page)
for k in ['wenyan', 'xici', 'shuogua', 'xugua', 'zagua']:
    if k not in pills:
        fails.append(f'书脊缺传签 {k}')
for k in ['jingyao', 'tuan', 'xiang']:
    if k not in pills:
        fails.append(f'书脊缺经签 {k}')

# 9 mulu 计数（若已挂目录）
try:
    mulu = open('daizhige-daodu/mulu.html', encoding='utf-8').read()
except FileNotFoundError:
    mulu = ''
if 'yitongzi-wen.html' in mulu:
    nums = sorted(set(int(n) for n in re.findall(r'<span class="no mono">(\d+)</span>', mulu)))
    if nums != list(range(1, len(nums) + 1)):
        fails.append(f'mulu 编号不连续: {nums[:5]}...{nums[-5:]}')
    cn = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'零':0,'十':10}
    def cnum(s):
        if '百' in s:
            b, rest = s.split('百', 1)
            v = cn[b] * 100
            rest = rest.lstrip('零')
            if rest:
                if rest == '十': v += 10
                elif rest.startswith('十'): v += 10 + cn[rest[1]]
                elif '十' in rest:
                    t, u = rest.split('十', 1); v += cn[t] * 10 + (cn[u] if u else 0)
                else: v += cn[rest]
            return v
        if '十' in s:
            t, u = s.split('十', 1)
            return cn[t] * 10 + (cn[u] if u else 0)
        return cn[s]
    for s in re.findall(r'([一-鿿]+)篇导读合订', mulu) + re.findall(r'([一-鿿]+)篇导读，', mulu):
        if cnum(s) != len(nums):
            fails.append(f'mulu 计数「{s}」= {cnum(s)} ≠ 实际 {len(nums)}')

if fails:
    print('FAIL')
    for f in fails: print(' -', f)
    sys.exit(1)
print('PASS：引文', len(quotes), '段逐字过，排版红线全过，书脊签完整')
