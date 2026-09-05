#!/usr/bin/env python3
# 核验 shange.html：引文与库本逐字比对（去标点+空白归一）、禁长划线、每行·≤1、零外部依赖、
# 库本统计断言、编号与 mulu 联动（commit 前：页码==mulu max+1；发布后：页码==max 且已入库）。
import re, sys, os
from html.parser import HTMLParser

BASE = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(BASE, 'shange.html')
SRC  = '/home/robertsong/workspace/claude/daizhige-simplified/诗藏/剧曲/山歌.txt'
MULU = os.path.join(BASE, 'mulu.html')

errors, warns = [], []
def err(m): errors.append(m)
def warn(m): warns.append(m)

html = open(PAGE, encoding='utf-8').read()
src  = open(SRC, encoding='utf-8').read()

# ---------- 1. HTML 结构 ----------
class Chk(HTMLParser):
    VOID = {'meta','br','img','hr','input','link','wbr'}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.bad = []
    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)
    def handle_endtag(self, tag):
        if tag in self.VOID: return
        if not self.stack or self.stack[-1] != tag:
            self.bad.append(tag)
        else:
            self.stack.pop()
chk = Chk(); chk.feed(html)
if chk.bad: err('HTML 闭合异常: %s' % chk.bad[:5])
if chk.stack: err('HTML 未闭合标签: %s' % chk.stack)

# ---------- 2. 引文收集 ----------
# .q 块（含 .src 出处行，核验时去掉）、.pi .body、.pai .ln（剔除 .h 注）、.vsong
QUOTE_SEL = []
# .q blocks
for m in re.finditer(r'<div class="q">(.*?)</div>', html, re.S):
    t = re.sub(r'<span class="src">.*?</span>', '', m.group(1), flags=re.S)
    QUOTE_SEL.append(('q', t))
# .pi body（剔除 .psrc 出处行）
for m in re.finditer(r'<div class="body">(.*?)</div>', html, re.S):
    t = re.sub(r'<span class="psrc">.*?</span>', '', m.group(1), flags=re.S)
    QUOTE_SEL.append(('pi', t))
# .pai lines minus .h
for m in re.finditer(r'<button class="ln"[^>]*>(.*?)</button>', html, re.S):
    t = re.sub(r'<span class="h">.*?</span>', '', m.group(1), flags=re.S)
    QUOTE_SEL.append(('ln', t))
# .vsong（剔除 small 出处）
for m in re.finditer(r'<div class="vsong">(.*?)</div>', html, re.S):
    t = re.sub(r'<small>.*?</small>', '', m.group(1), flags=re.S)
    QUOTE_SEL.append(('vsong', t))

PUNCT = re.compile('[，。、；：？！「」『』（）〔〕［］《》〈〉“”‘’"\'·.,;:?!()\\-—―–…□\\s]')
def norm(s):
    s = re.sub(r'<[^>]+>', '', s)
    return PUNCT.sub('', s)
NSRC = norm(src)

n_quotes = 0
for kind, t in QUOTE_SEL:
    n = norm(t)
    if not n:
        err('引文块为空 (%s)' % kind); continue
    n_quotes += 1
    if n not in NSRC:
        err('引文未过库本核验 (%s): %s' % (kind, n[:40]))

# ---------- 3. 长划线禁用 ----------
for i, ch in enumerate(html):
    if ch in '—–―':
        line = html.count('\n', 0, i) + 1
        err('禁用长划线 %r 位于第 %d 行' % (ch, line))

# ---------- 4. 每行 · ≤ 1 ----------
for i, line in enumerate(html.split('\n'), 1):
    if line.count('·') > 1:
        err('第 %d 行 · 超限 (%d 个)' % (i, line.count('·')))

# ---------- 5. 零外部依赖 ----------
if re.search(r'(src|href)\s*=\s*["\']https?://', html):
    err('存在外部资源引用')
if re.search(r'url\(\s*["\']?https?://', html):
    err('CSS 存在外部资源')
if re.search(r'<link\s', html):
    err('存在 <link> 标签')
# 允许正文/页脚出现的 github 裸文本，但禁止 http 前缀
if re.search(r'https?://', html):
    err('存在 http(s) 明文链接')

# ---------- 6. 库本统计断言 ----------
nws = len(re.sub(r'\s', '', src))
if nws != 33973:
    err('库本去空白字数断言失败: %d != 33973' % nws)
i1 = src.find('卷一私情四句')
front = src[:i1]
titles_front = re.findall(r'[［〔\[]([^］〕\[\n]{1,14})[］〕\]]', front)
titles_front = [t for t in titles_front if t not in ('叠', '又')]
if len(titles_front) != 33:
    err('卷前带批示例断言失败: %d != 33' % len(titles_front))
o7 = len(re.findall('○', src[src.find('●山歌卷七'):]))
if o7 != 65:
    err('卷七至卷十篇题断言失败: %d != 65' % o7)

# 页面文字中的数字声明
for num in ('33,973', '三十三首', '六十五个'):
    if num not in html:
        err('页面缺少统计声明: %s' % num)

# ---------- 7. 编号与 mulu 联动 ----------
mulu = open(MULU, encoding='utf-8').read()
nos = [int(x) for x in re.findall(r'class="no mono">(\d+)<', mulu)]
mx = max(nos)
m_fnav = re.search(r'殆知阁导读 之一百七十', html)
m_kick = re.search(r'第 170 篇', html)
if not (m_fnav and m_kick):
    err('页面编号三处声明不齐（fnav/kicker）')
linked = 'href="shange.html"' in mulu
if linked:
    if mx != 170:
        err('已入库态: mulu max=%d，页脚应为 170' % mx)
    # mulu 编号连续无重
    if sorted(nos) != list(range(1, mx + 1)):
        err('mulu 编号不连续或有重')
else:
    if mx + 1 != 170:
        err('未入库态: mulu max=%d，页码应为 %d' % (mx, mx + 1))
    if re.findall(r'之一百七十', mulu):
        err('mulu 已含 之一百七十 文案但未挂链接')

# ---------- 汇总 ----------
print('引文核验: %d 处（.q/.pi/.ln/.vsong）' % n_quotes)
print('库本: 去空白 %d 字, 卷前批题 %d, 卷七至十篇题 %d' % (nws, len(titles_front), o7))
print('mulu: %d 条, max=%d, shange 已入库=%s' % (len(nos), mx, linked))
for w in warns: print('WARN:', w)
if errors:
    print('\nFAIL')
    for e in errors: print(' -', e)
    sys.exit(1)
print('\nALL PASS')
