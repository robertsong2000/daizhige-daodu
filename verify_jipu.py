#!/usr/bin/env python3
# 引文核验 + 白话反扫 + 排版红线检查：鸡谱
import re, sys, unicodedata

HTML = 'jipu.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/艺藏/草木鸟兽虫鱼/鸡谱.txt'

PUNCT = set('，。：；、！？「」『』（）〔〕【】《》〈〉…·“”‘’○｜' + r'\-' + '_.,;:!?()[]{}<>"' + "'")
def norm(s):
    s = re.sub(r'<[^>]+>', '', s)
    s = ''.join(ch for ch in s if not unicodedata.category(ch).startswith('P')
                and not ch.isspace() and ch not in PUNCT)
    return s

lib = open(LIB, encoding='utf-8').read()
libnorm = norm(lib)

html = open(HTML, encoding='utf-8').read()
errs, qcount = [], 0

# ---------- 1. 引文通道：裸 q 标签 + qv/vq 类 ----------
quote_spans = []
work = html
# 先取裸 q 原子（嵌套在内层的先被拿走）
bare = []
for m in re.finditer(r'<q(?:\s[^>]*)?>(.*?)</q>', html, re.S):
    bare.append(m)
quotes = []
for m in bare:
    t = norm(m.group(1))
    if t:
        quotes.append(('q', t))
# 掩掉裸 q 后再扫 qv/vq 容器
work = re.sub(r'<q(?:\s[^>]*)?>.*?</q>', '▪', html, flags=re.S)
for m in re.finditer(r'<(\w+)([^>]*\bclass="[^"]*\b(qv|vq)\b[^"]*"[^>]*)>(.*?)</\1>', work, re.S):
    t = norm(m.group(4).replace('▪', ''))
    if t:
        quotes.append((m.group(3), t))
quotes.append(('', ''))  # guard
for chan, t in quotes[:-1]:
    qcount += 1
    if any(0xE000 <= ord(c) <= 0xF8FF for c in t):
        errs.append(f'引文含私用区字: {t[:24]}')
    if t not in libnorm:
        errs.append(f'[{chan}] 不在库本: {t[:40]}')

# ---------- 2. 白话反扫（6字窗） ----------
work = re.sub(r'<q(?:\s[^>]*)?>.*?</q>', '▪', html, flags=re.S)
work = re.sub(r'<(\w+)([^>]*\bclass="[^"]*\b(qv|vq)\b[^"]*"[^>]*)>.*?</\1>', '▪', work, flags=re.S)
work = re.sub(r'<style.*?</style>', '', work, flags=re.S)
prose = norm(work)
hit = 0
for i in range(len(prose) - 5):
    w = prose[i:i+6]
    if w in libnorm:
        hit += 1
        ctx = prose[max(0,i-8):i+14]
        errs.append(f'反扫6字窗命中[{w}]: …{ctx}…')
        if hit > 25: break

# ---------- 3. 排版红线 ----------
if '—' in html or '–' in html:
    errs.append('出现长划线')
for ln, line in enumerate(html.split('\n'), 1):
    if line.count('·') > 1:
        errs.append(f'L{ln} · 超标({line.count("·")}个): {line.strip()[:50]}')

print(f'引文核验: {qcount} 处')
print(f'反扫: 白话{len(prose)}字')
if errs:
    print('\n'.join(errs)); sys.exit(1)
print('ALL PASS')
