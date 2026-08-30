#!/usr/bin/env python3
# verify_yangzhou.py — 扬州十日记 页面核验
import re, sys

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/yangzhou-shiri-ji.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/扬州十日记.txt'

html = open(PAGE, encoding='utf-8').read()
lib  = open(LIB,  encoding='utf-8').read()

def norm(s):
    return ''.join(ch for ch in s if ch.isalnum() and not ch.isascii() or (ch.isascii() and ch.isalnum()))

def nrm(s):
    return ''.join(ch for ch in s if (ch.isascii() and ch.isalnum()) or (not ch.isascii() and ch.isalnum()))

LIBN = nrm(lib)

fails = []

# ---------- 1. 引文收集（标签平衡扫描器） ----------
VOID = {'br', 'img', 'meta', 'link', 'hr', 'input', 'source'}
tag_re = re.compile(r'<(/?)([a-zA-Z][a-zA-Z0-9]*)\b[^>]*?>')

def extract_q(h):
    quotes, stack = [], []  # [tag, cls, buf]
    pos = 0
    def flush(text):
        for fr in stack:
            fr[2].append(text)
    for m in tag_re.finditer(h):
        flush(h[pos:m.start()]); pos = m.end()
        closing, tag = m.group(1) == '/', m.group(2)
        if closing:
            for k in range(len(stack) - 1, -1, -1):
                if stack[k][0] == tag:
                    for fr in stack[k:]:
                        if 'q' in fr[1].split():
                            quotes.append(''.join(fr[2]))
                    del stack[k:]
                    break
        else:
            if tag in VOID: continue
            cm = re.search(r'class="([^"]*)"', m.group(0))
            stack.append([tag, cm.group(1) if cm else '', []])
    flush(h[pos:])
    return quotes

quotes = extract_q(html)
print(f'共收集 .q 引文 {len(quotes)} 段')

seen = set()
for q in quotes:
    qn = nrm(q)
    if not qn:
        fails.append(f'空引文: {q!r}'); continue
    cnt = LIBN.count(qn)
    key = qn[:20]
    if cnt == 0:
        fails.append(f'0 命中: {q[:50]!r}')
    if qn in seen:
        print(f'  [refrain] 整段重复（刻意复现）: {q[:40]}')
    seen.add(qn)
    print(f'  [{"OK" if cnt else "MISS"}] 库内{cnt}见  {q[:36]}')

# ---------- 2. 排版红线 ----------
if '—' in html: fails.append('红线: 页面含长划线 —')
if '–' in html: fails.append('红线: 页面含短划线 –')
for i, line in enumerate(html.split('\n'), 1):
    c = line.count('·')
    if c > 1: fails.append(f'红线: 第{i}行含 {c} 个·')
print(f'红线检查: — – 无, 每行·≤1 -> {"通过" if not any("红线" in f for f in fails) else "见 FAIL"}')

# ---------- 3. 十日墙结构 ----------
cols = re.findall(r'<div class="col (c\d+)" data-a="(\d+)">(.*?)\n      </div>', html, re.S)
if len(cols) != 10: fails.append(f'十日墙列数 {len(cols)} != 10')
seq = []
for idx, (cls, a, body) in enumerate(cols, 1):
    dots = re.findall(r'class="dot (on|off)"', body)
    if len(dots) != 8: fails.append(f'第{idx}列圆点 {len(dots)} != 8'); continue
    seq.append(dots.count('on'))
if seq != [8, 6, 4, 4, 4, 4, 4, 4, 4, 3]:
    fails.append(f'存活序列 {seq} != [8,6,4,4,4,4,4,4,4,3]')
else:
    print('十日墙: 10 列, 每列 8 点, 存活序列 8,6,4,4,4,4,4,4,4,3 通过')
dts = re.findall(r'<div class="dt">([^<]+)</div>', html)
if dts != ['四月廿五','四月廿六','四月廿七','四月廿八','四月廿九','五月朔','五月初二','五月初三','五月初四','五月初五']:
    fails.append(f'日期序列不符: {dts}')
else:
    print('日期序列: 四月廿五至五月初五 通过')

# ---------- 4. 库本计数 ----------
raw = len(lib)
ns  = len(re.sub(r'\s', '', lib))
if raw != 7946: fails.append(f'库本字数 {raw} != 7946')
if ns  != 7899: fails.append(f'去空白 {ns} != 7899')
for s in ('7,946', '7,899'):
    if s not in html: fails.append(f'页面缺计数 {s}')
print(f'库本计数: 全帙 {raw}, 去空白 {ns}')

# ---------- 5. 页脚核验数 ----------
m = re.search(r'共 <span class="mono" id="qcount">(\d+)</span> 段', html)
if not m: fails.append('页脚缺核验计数')
elif int(m.group(1)) != len(quotes): fails.append(f'页脚计数 {m.group(1)} != 实际 {len(quotes)}')
else: print(f'页脚计数与实际一致: {len(quotes)} 段')

# ---------- 6. 结构完整性 ----------
for kw in ('扬州十日记', '江都王秀楚记', '殆知阁简体库', '时代局限', '警惕'):
    if kw not in html: fails.append(f'页面缺关键词 {kw}')

print()
if fails:
    print('FAIL')
    for f in fails: print(' -', f)
    sys.exit(1)
print('ALL PASS')
