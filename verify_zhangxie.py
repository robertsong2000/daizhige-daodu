#!/usr/bin/env python3
# 核验 zhangxie-zhuangyuan.html：引文双侧逐字（NFKC+去空白+去标点+异体归一）、
# 「」反扫、禁长划线、每行·≤1、结构项。
import re, sys, os, unicodedata

PAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'zhangxie-zhuangyuan.html')
SRC  = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'daizhige-simplified', '诗藏', '剧曲', '张协状元.txt')

page = open(PAGE, encoding='utf-8').read()
src  = open(SRC,  encoding='utf-8').read()

YITI = str.maketrans({
    '𬨎': '輶', '囄': '哩', '𪡏': '㗀',
})

def strip_tags(t):
    t = re.sub(r'<[^>]+>', '', t)
    return t

def norm(t):
    t = unicodedata.normalize('NFKC', t)
    t = ''.join(ch for ch in t if not ch.isspace())
    t = ''.join(ch for ch in t if not unicodedata.category(ch).startswith('P'))
    t = ''.join(ch for ch in t if not unicodedata.category(ch).startswith('S'))
    t = t.translate(YITI)
    return t

nsrc = norm(src)
npage = norm(strip_tags(page))

quotes = []

# .q / .qkuang 块
for m in re.finditer(r'<div class="(?:q|qkuang)">(.*?)</div>', page, re.S):
    body = re.sub(r'<span class="src">.*?</span>', '', m.group(1), flags=re.S)
    quotes.append(('块引', strip_tags(body).strip()))

# .pull 大字引
for m in re.finditer(r'<p class="pull">(.*?)</p>', page, re.S):
    body = re.sub(r'<span class="src">.*?</span>', '', m.group(1), flags=re.S)
    quotes.append(('大字', strip_tags(body).strip()))

# 「」 字面
plain = strip_tags(page)
for m in re.finditer(r'「([^」]+)」', plain):
    quotes.append(('「」', m.group(1).strip()))

# 帐额题目 <b> 行
for m in re.finditer(r'<p class="timu">(.*?)</p>', page, re.S):
    for b in re.finditer(r'<b>(.*?)</b>', m.group(1), re.S):
        quotes.append(('题目', strip_tags(b.group(1)).strip()))

# 戏房声口（去「戏房」签）
for m in re.finditer(r'<p class="xifang">(.*?)</p>', page, re.S):
    body = re.sub(r'<span class="fang">.*?</span>', '', m.group(1), flags=re.S)
    t = strip_tags(body).strip()
    if t:
        quotes.append(('戏房', t))

fails = []
seen = set()
for kind, q in quotes:
    nq = norm(q)
    if not nq or nq in seen:
        continue
    seen.add(nq)
    ok_page = nq in npage
    ok_src  = nq in nsrc
    if not (ok_page and ok_src):
        fails.append((kind, q[:60], 'page:%s src:%s' % (ok_page, ok_src)))

print('引文总数（去重）：%d' % len(seen))
for kind, q, why in fails:
    print('FAIL[%s] %s …… %s' % (kind, q, why))
if fails:
    sys.exit(1)
print('双侧逐字：全过')

# 红线：长划线
for bad in ('—', '–', '―'):
    if bad in page:
        print('FAIL 长划线 %r 在页面' % bad); sys.exit(1)
print('禁长划线：过')

# 红线：每行·≤1（按 HTML 源行 + 按块文本双检）
for i, line in enumerate(page.split('\n'), 1):
    c = line.count('·')
    if c > 1:
        print('FAIL 行%d 含 %d 个·：%s' % (i, c, line.strip()[:50])); sys.exit(1)
for blk in re.findall(r'<(?:p|div|h2|h3|span)[^>]*>(.*?)</(?:p|div|h2|h3|span)>', page, re.S):
    t = strip_tags(blk)
    for ln in t.split('\n'):
        if ln.count('·') > 1:
            print('FAIL 块内行 %r 含多·' % ln.strip()[:50]); sys.exit(1)
print('每行·≤1：过')

# 外部依赖
if re.search(r'(https?://|<script|<link|@import|url\()', page):
    hits = re.findall(r'(https?://[^"<\s]+|<script[^>]*|<link[^>]*|@import[^;]*|url\([^)]*\))', page)
    print('FAIL 外部依赖：%s' % hits[:3]); sys.exit(1)
print('无外部依赖：过')

# 结构项
musts = [
    ('title 含书名', '张协状元' in re.search(r'<title>(.*?)</title>', page).group(1)),
    ('footer 来源', '殆知阁古代文献简体库' in page),
    ('footer 核验声明', '逐字核验' in page),
    ('footer 时代局限', '时代' in page),
    ('总目链接', 'mulu.html' in page),
    ('53 出', len(re.findall(r'第[一二三四五六七八九十]{1,3}出', src)) == 53),
]
for name, ok in musts:
    if not ok:
        print('FAIL 结构：%s' % name); sys.exit(1)
print('结构项：%s' % '、'.join(m[0] for m in musts))
print('ALL PASS')
