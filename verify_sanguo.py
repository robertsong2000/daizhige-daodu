# -*- coding: utf-8 -*-
"""sangguo-zhi-pinghua.html 核验：引文逐字（去标点+去空白）+ 排版红线 + 字数自述"""
import re, json, sys, unicodedata

PAGE = 'daizhige-daodu/sangguo-zhi-pinghua.html'
LIB = 'daizhige-simplified/集藏/话本/三国志平话.txt'
EXPECT_CHARS = 66840

page = open(PAGE, encoding='utf-8').read()
lib = open(LIB, encoding='utf-8').read()
quotes = json.load(open('daizhige-daodu/quotes_sanguo.json', encoding='utf-8'))

fails = []

def strip_punct(s):
    out = []
    for ch in s:
        cat = unicodedata.category(ch)
        if cat.startswith('P') or cat.startswith('S') or ch in '「」『』“”‘’':
            continue
        out.append(ch)
    return ''.join(out)

def norm(s):
    return re.sub(r'\s+', '', strip_punct(s))

# 页面去标签版（用于匹配夹在行内标签中的引文）
page_notag = re.sub(r'<[^>]+>', '', page)
flat_page = norm(page_notag)
flat_lib = norm(lib)

# 1 引文双向比对
for k, v in quotes.items():
    nv = norm(v)
    if nv not in flat_lib:
        fails.append(f'引文不在库本: {k}')
    if nv not in flat_page:
        fails.append(f'引文不在页面: {k}')

# 2 PUA 字
if any(0xE000 <= ord(c) <= 0xF8FF for c in page):
    fails.append('页面含 PUA 字')

# 3 禁长划线
for ch in ['—', '–', '―', '─', '──']:
    if ch in page:
        fails.append(f'禁字符 {ch} x{page.count(ch)}')

# 4 每行 · 最多 1 个（源码行 + 去标签后按行）
for i, line in enumerate(page.split('\n'), 1):
    if line.count('·') > 1:
        fails.append(f'源码行{i} 含 {line.count("·")} 个 ·')
for i, line in enumerate(page_notag.split('\n'), 1):
    if line.count('·') > 1:
        fails.append(f'渲染行{i} 含 {line.count("·")} 个 ·: {line.strip()[:50]}')

# 5 零外部依赖（页脚仓库链接文本除外）
for pat in ['src="http', "src='http", 'href="http', "@import", "url("]:
    for line in page.split('\n'):
        if pat in line and 'github.com' not in line:
            fails.append(f'外部依赖 {pat}: {line.strip()[:70]}')

# 6 字数自述
if str(EXPECT_CHARS) not in page:
    fails.append(f'页面未自述库本字数 {EXPECT_CHARS}')
real = len(re.sub(r'\s+', '', lib))
if real != EXPECT_CHARS:
    fails.append(f'实际去空白 {real} != 自述 {EXPECT_CHARS}')

# 7 页脚三要素
for need in ['殆知阁', 'github.com/robertsong2000/daizhige-daodu', '逐字核验', '时代局限']:
    if need not in page:
        fails.append(f'页脚缺: {need}')

# 8 卷次结构在页面有交代
for need in ['卷上', '卷中', '卷下']:
    if need not in page:
        fails.append(f'页面缺卷次: {need}')

if fails:
    print('FAIL', len(fails))
    for f in fails:
        print(' -', f)
    sys.exit(1)
print('PASS: 引文 %d 条全核验通过；无禁字符；每行·合规；零外部依赖；字数自述 %d 一致' % (len(quotes), EXPECT_CHARS))
