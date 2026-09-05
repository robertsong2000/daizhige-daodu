#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""酌中志 导读页核验：引文双侧逐字对库 + 机数 + 红线"""
import re, sys, unicodedata

LIB = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/酌中志.txt'
PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/zhuozhong-zhi.html'

lib = open(LIB, encoding='utf-8').read()
page = open(PAGE, encoding='utf-8').read()
fails = []

def norm(s):
    out = []
    for ch in s:
        if ch.isspace():
            continue
        if unicodedata.category(ch).startswith(('P', 'S')):
            continue
        out.append(ch)
    return ''.join(out)

LIBN = norm(lib)

def chk(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: fails.append(msg)

# ---------- 1. 从页面抽取全部引文 ----------
quotes = []
quotes += re.findall(r'<q>(.*?)</q>', page, re.S)
quotes += re.findall(r'「(.*?)」', page, re.S)
quotes += re.findall(r'<div class="quote">\s*(.*?)\s*<span class="src">', page, re.S)
quotes += re.findall(r'<p class="koujian">(.*?)</p>', page, re.S)
quotes = [re.sub(r'<[^>]+>', '', q) for q in quotes]
quotes = [q.strip() for q in quotes if q.strip() and q.strip() != '■']  # 页脚「■」为占位符说明，非引文
chk(len(quotes) >= 15, f'页面引文条数>=15 实测{len(quotes)}')

bad = 0
for q in quotes:
    nq = norm(q)
    ok = nq in LIBN
    if not ok:
        bad += 1
        print('  未命中: ' + q[:40])
chk(bad == 0, f'引文逐字命中库本 {len(quotes) - bad}/{len(quotes)}')

# 引文不含缺字占位符
chk(not any('■' in q for q in quotes), '引文不含■占位符')

# ---------- 2. 机数 ----------
nchar = len(lib)
chk(page.count('126,676') >= 1, f'页面字数标注与库本一致 {nchar}')
lines = lib.split('\n')
toc_a = next(i for i, l in enumerate(lines) if l.strip() == '自序')
toc_b = next(i for i, l in enumerate(lines[toc_a + 1:], toc_a + 1) if l.strip() == '自序')
toc = [l for l in lines[toc_a:toc_b] if re.match(r'^　　卷[一二三四五六七八九十]+', l)]
chk(len(toc) == 24, f'目录卷数=24 实测{len(toc)}')
chk('兹略具二十三篇' in LIBN, '自序自称二十三篇（与24卷目录差一附卷）')

# ---------- 3. 卷签墙 24 签 ----------
chips = re.findall(r'<div class="qie[^"]*"><i>(.*?)</i>(.*?)</div>', page)
chk(len(chips) == 24, f'卷签墙签数=24 实测{len(chips)}')
miss = [t for _, t in chips if norm(t) not in LIBN]
chk(not miss, '卷签墙签题全部见于库本目录 ' + (str(miss) if miss else ''))

# ---------- 4. 二十四衙门 ----------
yamen = re.findall(r'<div class="wei">(.*?)</div>', page, re.S)
names = []
for blk in yamen:
    names += re.findall(r'<span>(.*?)</span>', blk)
chk(len(names) == 24, f'衙门名目=24 实测{len(names)}')
missing = [n for n in names if norm(n) not in LIBN]
chk(not missing, '衙门名目全部见于卷十六 ' + (str(missing) if missing else ''))

# ---------- 5. 红线 ----------
for bad_ch, name in [('—', '长划线—'), ('–', '短划线–'), ('―', '水平线―')]:
    chk(bad_ch not in page, f'页面无{name}')
text = re.sub(r'<[^>]+>', '', page)
over = [l for l in text.split('\n') if l.count('·') > 1]
chk(not over, '每行·不多于1个 ' + (str(over[:2]) if over else ''))

print()
if fails:
    print('共 %d 项未通过' % len(fails)); sys.exit(1)
print('全部通过')
