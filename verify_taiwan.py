#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""台湾外记 导读页核验：32 处引文双侧 + 全页「」『』穷尽扫描 + 排版红线 + mulu 联检。"""
import re, sys

LIB = '../daizhige-simplified/史藏/地理/台湾外记.txt'
PAGE = 'taiwan-waiji.html'
MULU = 'mulu.html'

def norm(s):
    s = re.sub(r'\s+', '', s)
    s = ''.join(c for c in s if not (0xE000 <= ord(c) <= 0xF8FF))
    return re.sub(r'[，。、；：？！“”‘’「」『』（）()《》〈〉·…\-.—―~%■□]', '', s)

lib = open(LIB, encoding='utf-8').read()
page = open(PAGE, encoding='utf-8').read()
mulu = open(MULU, encoding='utf-8').read()
nlib = norm(lib)
npage = norm(page)

fails = []
ok = lambda name: print('  PASS', name)

# 1. 块级引文（blockquote.q + qbank i）双侧
qs = re.findall(r'<blockquote class="q[^"]*" data-k="[^"]*"><p>(.*?)</p>', page, re.S)
qs += re.findall(r'<i data-z="[^"]*">(.*?)</i>', page, re.S)
for q in qs:
    nq = norm(q)
    if nq not in nlib: fails.append('库本无引文：%s…' % q[:24])
    if nq not in npage: fails.append('页面无引文：%s…' % q[:24])
if len(qs) != 32: fails.append('块级引文数 %d != 32' % len(qs))
else: ok('32 处块级引文双侧逐字')

# 2. 全页穷尽扫描：页面内一切「…」「『…』」必须见于库本
brs = re.findall(r'[「『]([^「」『』]{3,})[」』]', page)
bad = sorted(set(b for b in brs if norm(b) not in nlib))
if bad:
    for b in bad: fails.append('括号内语未见库本：%s' % b)
else: ok('全页 %d 处括号引语全部见于库本（去重 %d 处）' % (len(brs), len(set(brs))))

# 3. 界面用字取自库本的短语
UI = ['施侯奏功', '郑氏归诚', '宁靖王尽节', '五姬殉难', '克塽归诚',
      '昼龙桶', '漆红头桶', '土音字说', '郑氏应谶五代记']
for t in UI:
    if norm(t) not in nlib: fails.append('界面短语未见库本：%s' % t)
if not fails: ok('10 处界面短语全部见于库本')

# 4. 红线
if '—' in page or '–' in page: fails.append('页面含长划线')
else: ok('零长划线')
if any(0xE000 <= ord(c) <= 0xF8FF for c in page): fails.append('页面含私用区码位')
else: ok('零私用区码位')
over = [(i, l.count('·')) for i, l in enumerate(page.split('\n'), 1) if l.count('·') > 1]
if over: fails.append('多·行：%s' % over)
else: ok('每行·至多 1 个')
for pat, msg in [('<link', '外链样式'), ('<script src', '外链脚本'), ('@import', '样式导入'),
                 ('url(', 'url 引用'), ('<img', '外链图片'), ('<iframe', '内嵌框架')]:
    if pat in page: fails.append('疑似外部依赖 %s' % msg)
if not any(p in page for p in ['<link', '<script src', '@import', 'url(', '<img', '<iframe']):
    ok('零外部依赖')

# 5. 页内自述与页脚三件套
if '131,997' not in page or '130,633' not in page: fails.append('字数自述缺失')
if '三十二处' not in page: fails.append('引文计数自述与实际 32 不符')
for foot in ['文本来源', '库外申报', '时代局限提醒', 'github.com/robertsong2000/daizhigev20',
             'mulu.html', '殆知阁导读　二百五十六', '台湾外记 · 殆知阁导读 256']:
    if foot not in page: fails.append('页脚/篇号缺 %s' % foot)
if all(f in page for f in ['文本来源', '库外申报', '时代局限提醒']): ok('页脚三件套、来源链接与篇号 256')
for k in ['康熙三年十二月', '无卷之六']:  # 残本说明要点
    if k not in page: fails.append('库本残卷说明缺 %s' % k)


# 6. mulu 联检
nos = [int(m) for m in re.findall(r'<span class="no mono">(\d+)</span>', mulu)]
if sorted(set(nos)) != list(range(1, max(nos) + 1)) or len(nos) != len(set(nos)):
    dup = sorted(n for n in set(nos) if nos.count(n) > 1)
    gap = sorted(set(range(1, max(nos) + 1)) - set(nos))
    fails.append('mulu 编号异常 重复:%s 缺口:%s' % (dup, gap))
else: ok('mulu 编号 1..%d 连续无缺口无重复' % max(nos))
if mulu.count('二百五十六') < 2: fails.append('mulu kicker/footer 计数未改二百五十六')
else: ok('mulu kicker 与 footer 计数已改二百五十六')
if '<span class="no mono">256</span>' not in mulu or 'taiwan-waiji.html' not in mulu:
    fails.append('mulu 缺 256 号条目')
else: ok('mulu 已收 256 台湾外记')

print()
if fails:
    for f in fails: print('  FAIL', f)
    sys.exit(1)
print('ALL PASS')
