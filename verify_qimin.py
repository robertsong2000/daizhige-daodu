#!/usr/bin/env python3
# 核验 qimin-yaoshu.html：引文逐字比对库内文件 + 排版红线 + 机器计数
import re, sys, unicodedata

PAGE = 'qimin-yaoshu.html'
SRC = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/农家/齐民要术.txt'
EXPECTED_NO = 56

def norm(s):
    out = []
    for ch in s:
        if ch.isspace():
            continue
        cat = unicodedata.category(ch)
        if cat.startswith('P') or cat.startswith('S'):
            continue
        out.append(unicodedata.normalize('NFKC', ch))
    return ''.join(out)

src = open(SRC, encoding='utf-8').read()
nsrc = norm(src)
html = open(PAGE, encoding='utf-8').read()

fails = []

# 1. 抽取引文：blockquote（剥掉 .src）+ span.q + .rq
quotes = []
for m in re.finditer(r'<blockquote[^>]*>(.*?)</blockquote>', html, re.S):
    inner = re.sub(r'<span class="src">.*?</span>', '', m.group(1), flags=re.S)
    inner = re.sub(r'<[^>]+>', '', inner).strip()
    quotes.append(('blockquote', inner))
for m in re.finditer(r'<span class="q">(.*?)</span>', html, re.S):
    inner = re.sub(r'<[^>]+>', '', m.group(1)).strip()
    quotes.append(('span.q', inner))
for m in re.finditer(r'<p class="rq">(.*?)</p>', html, re.S):
    inner = re.sub(r'<[^>]+>', '', m.group(1)).strip()
    quotes.append(('rq', inner))

# 2. 逐段比对（……分隔的省略式引文按段核验）
for kind, q in quotes:
    segs = [s for s in re.split(r'……', q) if s.strip()]
    for seg in segs:
        n = norm(seg)
        if not n:
            continue
        if n not in nsrc:
            fails.append(f'[{kind}] 未命中: {seg[:50]}')
        elif nsrc.count(n) < 1:
            fails.append(f'[{kind}] 计数异常: {seg[:50]}')

# 3. 排版红线
if '—' in html or '–' in html or '&mdash;' in html or '&ndash;' in html:
    fails.append('红线：出现长划线/短划线')
for i, line in enumerate(html.split('\n'), 1):
    text = re.sub(r'<[^>]+>', '', line)
    if text.count('·') > 1:
        fails.append(f'红线：第{i}行 · 超过1个')

# 4. 页内序号：title 与 kicker 与页脚同号（本篇 2 处含「之五十六」类字样 + 页脚 1 处「第五十六」）
if f'导读之{EXPECTED_NO}' not in html.replace('之五十六', '之56') and '导读之五十六' not in html:
    fails.append('页内 title/kicker 序号与 EXPECTED_NO 不符')
if html.count('之五十六') < 2:
    fails.append('title/kicker 序号不足 2 处')
if '第五十六篇' not in html:
    fails.append('页脚系列序号缺失')

# 5. 机器计数复核
def has(s):
    return norm(s) in nsrc

# 篇编号覆盖 1..91，缺 28
nums = set()
def cn2int(t):
    d = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9}
    if '十' not in t:
        return d[t]
    a, _, b = t.partition('十')
    return (d.get(a,1) if a else 1)*10 + (d.get(b,0) if b else 0)
for l in src.split('\n'):
    s = l.strip()
    m = re.match(r'^●.{1,40}?第([一二三四五六七八九十]+)', s)
    if m:
        nums.add(cn2int(m.group(1)))
if min(nums) != 1 or max(nums) != 91:
    fails.append(f'篇编号范围异常: {min(nums)}..{max(nums)}')
missing = sorted(set(range(1, 92)) - nums)
if missing != [28]:
    fails.append(f'篇缺号非[28]: {missing}')
if '凡九十二篇，束为十卷' not in src:
    fails.append('序称九十二篇句不见')

# 卷十：▲条目 148，编号至一四九，缺一○三
i10 = src.rfind('●五谷果蓏菜茹非中国物产者')
tail = src[i10:]
ents = re.findall(r'^\s*▲(\S+)\s*$', tail, re.M)
if len(ents) != 148:
    fails.append(f'卷十条目数非148: {len(ents)}')
def cn2int2(t):
    # 卷十条目编号为位值式：九=9、一○=10、一四九=149
    if '十' in t:
        d = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9}
        a, _, b = t.partition('十')
        return (d.get(a,1) if a else 1)*10 + (d.get(b,0) if b else 0)
    pos = {'一':'1','二':'2','三':'3','四':'4','五':'5','六':'6','七':'7','八':'8','九':'9','○':'0','〇':'0'}
    if all(c in pos for c in t) and len(t) > 1:
        return int(''.join(pos[c] for c in t))
    return {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9}.get(t, -1)
idx = []
for e in ents:
    m = re.search(r'([一二三四五六七八九十○]+)$', e)
    if m:
        idx.append(cn2int2(m.group(1)))
if max(x for x in idx if x > 0) != 149:
    fails.append(f'卷十最大编号非149: {max(x for x in idx if x>0)}')
if 103 in idx:
    fails.append('卷十一○三号不应存在')
if '地三年种蜀黍，其后七年多蛇' not in src:
    fails.append('蜀黍蛇条不见')

# 字数
if len(src) != 152806:
    fails.append(f'全帙字符非152806: {len(src)}')
if len(''.join(src.split())) != 141567:
    fails.append('去空白字数非141567')

# 页面声明数字
for s in ['约十五万字符', '一百四十八', '一百四十九', '第二十八篇题不见']:
    if s not in html:
        fails.append(f'页面缺声明: {s}')

print(f'引文抽取: {len(quotes)} 处')
if fails:
    print('FAIL')
    for f in fails:
        print(' ', f)
    sys.exit(1)
print('PASS: 引文逐字比对 + 排版红线 + 机器计数 全部通过')
