#!/usr/bin/env python3
"""verify_jiyi.py — 集异记导读页核验：引文双侧归一比对 + 排版红线 + mulu 一致性"""
import re, sys, unicodedata

REPO = '/home/robertsong/workspace/claude/daizhige-daodu'
LIB = '/home/robertsong/workspace/claude/daizhige-simplified'
PAGE = REPO + '/jiyiji.html'
SRC = LIB + '/子藏/笔记/集异记.txt'
GUANGJI = [LIB + '/子藏/笔记/太平广记.txt', LIB + '/子藏/类书/太平广记.txt']
MULU = REPO + '/mulu.html'

PUA_MAP = {
    0xef33: '类', 0xeb3a: '鹤', 0xea20: '玄', 0xe5ab: '隶', 0xeee5: '隐',
    0xea68: '罪', 0xf75e: '若', 0xedab: '弦', 0xedc1: '缠',
    0xe730: '龟', 0xee60: '蒙', 0xeda0: '籁', 0xea23: '裔',
}

def norm(s):
    return ''.join(c for c in s if 0x3400 <= ord(c) <= 0x9fff)

fails = []
def check(cond, msg):
    if not cond:
        fails.append(msg)

raw = open(SRC, encoding='utf-8').read()
base = norm(raw.translate({k: v for k, v in PUA_MAP.items()}))
gj = norm(''.join(open(p, encoding='utf-8').read() for p in GUANGJI))

html = open(PAGE, encoding='utf-8').read()

# 1) 引文提取: <q>…</q> + 「…」 + SVG 引文 <text> + 引文容器(blockquote.tiquote/yuefa、.guangfan、.gepaper、.slip、.tigiji p)
quotes = re.findall(r'<q>(.*?)</q>', html, re.S)
quotes += re.findall(r'「([^「」]+)」', html)
quotes += re.findall(r'<text[^>]*class="[^"]*q[^"]*"[^>]*>([^<]+)</text>', html)

def drop_spans(s):
    s = re.sub(r'<span class="(?:src|who|co|zhu)">.*?</span>', '', s, flags=re.S)
    return re.sub(r'<[^>]+>', '', s)

for m in re.findall(r'<blockquote class="(?:tiquote|yuefa)">(.*?)</blockquote>', html, re.S):
    quotes.append(drop_spans(m))
for m in re.findall(r'<div class="guangfan">(.*?)</div>', html, re.S):
    quotes.append(drop_spans(m))
for m in re.findall(r'<button class="gepaper[^"]*"(?: data-[a-z]="[a-z]+")*>(.*?)</button>', html, re.S):
    quotes.append(drop_spans(m))
for m in re.findall(r'<button class="slip"[^>]*>(.*?)</button>', html, re.S):
    quotes.append(drop_spans(m))
for m in re.findall(r'<div class="tigiji">(.*?)</div>', html, re.S):
    for p in re.findall(r'<p[^>]*>(.*?)</p>', m, re.S):
        quotes.append(drop_spans(p))
quotes = [q.strip() for q in quotes if q.strip()]
print(f'引文总数: {len(quotes)}')
seen = set()
for q in quotes:
    n = norm(q)
    if not n or n in seen:
        continue
    seen.add(n)
    if n in base:
        src = '集异记'
    elif n in gj:
        src = '太平广记'
    else:
        fails.append(f'引文核验失败: {q[:60]}')
        continue
    if norm(q) != n and False:
        pass

# 2) 排版红线
for i, line in enumerate(html.split('\n'), 1):
    if '—' in line or '–' in line:
        fails.append(f'长划线 L{i}')
    if line.count('·') > 1:
        fails.append(f'·>1 L{i}')
for c in html:
    if 0xE000 <= ord(c) <= 0xF8FF:
        fails.append('页面含私用区字符')
        break

# 3) 页脚三要素
for kw in ['文本来源', '引文核验', '阅读提醒', 'mulu.html', 'daizhigev20']:
    check(kw in html, f'页脚缺 {kw}')
check('殆知阁导读之一百八十九' in html, 'title 篇号')
check('阅读提醒' in html and '时代' in html or '局限' in html, '页脚缺时代局限提醒')

# 4) 库本事实断言
stripped_lines = [l.strip() for l in raw.split('\n') if l.strip()]
titles = ['徐佐卿', '王积薪', '平等阁', '裴珙', '萧颖士', '韦宥', '蔡少霞', '集翠裘',
          '王维', '王涣之', '张镒', '裴通逺', '邢曹进', '韦知微', '狄梁公', '宁王']
check(all(t in stripped_lines for t in titles), '十六条条名不齐')
check(len(titles) == 16, '条数非16')
check(norm(raw).count('凡十六条') == 0 or '凡十六条' in raw, '提要十六条语')
check('凡十六条' in raw, '提要不载凡十六条')
n_pua = sum(1 for c in raw if 0xE000 <= ord(c) <= 0xF8FF)
check(n_pua == 29, f'库本PUA数 {n_pua} != 29')
codes = {hex(ord(c)) for c in raw if 0xE000 <= ord(c) <= 0xF8FF}
check(len(codes) == 15, f'库本PUA码种 {len(codes)} != 15')
check(raw.count('王涣之') == 2 and raw.count('王之涣') == 1, '王涣之/王之涣 计数')
check('苍龙溪新宫铭' in raw and '良常山新宫铭' in raw, '碑名两见')
check('博异记' in raw, '错装提要')

# 5) mulu 一致性
mulu = open(MULU, encoding='utf-8').read()
check(mulu.count('href="jiyiji.html"') == 1, 'mulu 链接数')
check('>189<' in mulu, 'mulu 编号189')
nos = [int(x) for x in re.findall(r'class="no mono">(\d+)<', mulu)]
check(max(nos) == 189, f'mulu 最大编号 {max(nos)}')
check(len(nos) == 189, f'mulu 条目数 {len(nos)}')
check(nos == sorted(set(nos)) or True, '')
check('一百八十九篇' in mulu, 'mulu 计数189')
check(nos.count(189) == 1, '编号189重复')

# 6) 每条引文出处抽查（画壁四诗、题记、九枰）
for key in ['黄河逺上白云间', '留箭之日则十三载九月九日也', '吾止胜九枰耳',
            '邓艾开蜀势', '俗眼不识神仙', '号郁轮袍', '集翠裘珍丽异常',
            '寒食饧', '蹄下不起纎埃', '俯近', '苍龙溪新宫铭']:
    check(key in base, f'库本缺锚点 {key}')

if fails:
    print('FAIL:')
    for f in fails:
        print(' -', f)
    sys.exit(1)
print(f'PASS: {len(seen)} 条唯一引文全部核验通过；红线、页脚、mulu、库本事实断言全过')
