#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""三侠五义 导读页核验：12+7 处引文双侧逐字 + 排版红线 + 机数 + mulu 连续编号。"""
import json, re, sys

LIB = '../daizhige-simplified/集藏/话本/三侠五义.txt'
PAGE = 'sanxia-wuyi.html'
MULU = 'mulu.html'
QS = 'quotes_sxwy.json'

def norm(s):
    s = re.sub(r'\s+', '', s)
    s = ''.join(c for c in s if not (0xE000 <= ord(c) <= 0xF8FF))
    return re.sub(r'[，。、；：？！“”‘’「」『』（）()《》〈〉·…\-.—―~%]', '', s)

lib = open(LIB, encoding='utf-8').read()
page = open(PAGE, encoding='utf-8').read()
quotes = json.load(open(QS, encoding='utf-8'))
nlib, npage_raw = norm(lib), page
npage = norm(re.sub(r'<script[\s\S]*?</script>', '', page))

fails = []
ok = lambda name: print('  PASS', name)

# 1. 引文双侧
for q in quotes:
    nq = norm(q['text'])
    if nq not in nlib: fails.append('库本无引文 %s' % q['key'])
    if nq not in npage: fails.append('页面无引文 %s' % q['key'])
ok('12 处 .q 引文双侧逐字') if not fails else None

# 2. 行内短语 + 回目 双侧
INLINE = [
    '不好说，不忍说，又不能不说',
    '千不是，万不是，全是五弟不是',
    '难道五弟有了英名，你我作哥哥的不光彩么',
    '斩庞昱初试龙头铡', '巧取供单郭槐受戮', '耀武楼南侠封护卫',
    '锦毛鼠初探冲霄楼', '设阴谋临产换太子', '奋侠义替死救皇娘',
]
for t in INLINE:
    nt = norm(t)
    if nt not in nlib: fails.append('库本无行内语 %s' % t)
    if nt not in npage: fails.append('页面无行内语 %s' % t)
if not fails: ok('9 处行内语与回目双侧逐字')

# 3. 红线
if '—' in page or '–' in page: fails.append('页面含长划线')
else: ok('零长划线')
if any(0xE000 <= ord(c) <= 0xF8FF for c in page): fails.append('页面含私用区码位')
else: ok('零私用区码位')
for i, line in enumerate(page.split('\n'), 1):
    if line.count('·') > 1:
        fails.append('第 %d 行有 %d 个·' % (i, line.count('·')))
if not any('·' in l and l.count('·') > 1 for l in page.split('\n')): ok('每行·至多 1 个')
for pat, msg in [('<link', '外链样式'), ('<script src', '外链脚本'), ('@import', '样式导入'),
                 ('url(', 'url 引用'), ('<img', '外链图片'), ('<iframe', '内嵌框架')]:
    if pat in page: fails.append('疑似外部依赖 %s' % msg)
if not any(p in page for p in ['<link', '<script src', '@import', 'url(', '<img', '<iframe']):
    ok('零外部依赖')

# 4. 机数与页脚三件套
if '509,570' not in page: fails.append('页面字数自述缺失')
if '一百二十回' not in page: fails.append('回数自述缺失')
if '十二处引文' not in page: fails.append('引文计数自述与实际 %d 不符' % len(quotes))
for foot in ['文本来源', '库外申报', '时代局限提醒', 'github.com/robertsong2000/daizhigev20', 'mulu.html']:
    if foot not in page: fails.append('页脚缺 %s' % foot)
if all(f in page for f in ['文本来源', '库外申报', '时代局限提醒']): ok('页脚三件套与来源链接')
assert len(quotes) == 12, '引文数应为 12'

# 5. mulu 连续编号与计数
mulu = open(MULU, encoding='utf-8').read()
nos = [int(m) for m in re.findall(r'<span class="no mono">(\d+)</span>', mulu)]
if sorted(set(nos)) != list(range(1, max(nos) + 1)) or len(nos) != len(set(nos)):
    dup = sorted(n for n in set(nos) if nos.count(n) > 1)
    gap = sorted(set(range(1, max(nos) + 1)) - set(nos))
    fails.append('mulu 编号异常 重复:%s 缺口:%s' % (dup, gap))
else: ok('mulu 编号 1..%d 连续无缺口无重复' % max(nos))
if mulu.count('二百五十三') < 2: fails.append('kicker/footer 计数未更新为二百五十三')
else: ok('kicker 与 footer 计数已改二百五十三')
if '<span class="no mono">253</span>' not in mulu or 'sanxia-wuyi.html' not in mulu:
    fails.append('mulu 缺 253 号条目')
else: ok('mulu 已收 253 三侠五义')

print()
if fails:
    for f in fails: print('  FAIL', f)
    sys.exit(1)
print('ALL PASS')
