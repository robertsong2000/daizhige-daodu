# -*- coding: utf-8 -*-
"""纪效新书导读页核验：引文逐字、排版红线、机器计数。"""
import re, sys

SRC = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/兵家/纪效新书.txt'
PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/jixiao-xinshu.html'

src = open(SRC, encoding='utf-8').read()
page = open(PAGE, encoding='utf-8').read()
fails = []

def norm(s):
    return ''.join(ch for ch in s if not ch.isspace() and ch not in
                   '，。；：、！？「」『』（）《》·—–…〔〕【】[]／')

# ---------- 1. 引文：扫页面全部 .q/.qzhu ----------
spans = re.findall(r'<span class="(?:q|qzhu)">(.*?)</span>', page, re.S)
assert len(spans) == 44, f'.q/.qzhu 数量 {len(spans)} != 44'
N = norm(src)
for i, q in enumerate(spans, 1):
    text = re.sub(r'<[^>]+>', '', q)
    if norm(text) not in N:
        fails.append(f'引文{i}不在库本: {text[:40]}')
    if any(0xE000 <= ord(ch) <= 0xF8FF for ch in text):
        fails.append(f'引文{i}含PUA: {text[:30]}')

# ---------- 2. 排版红线 ----------
body = page[page.find('<body'):]
plain = re.sub(r'<style.*?</style>', '', body, flags=re.S)
plain = re.sub(r'<[^>]+>', '', plain)
for ln, line in enumerate(plain.split('\n'), 1):
    if '—' in line or '–' in line:
        fails.append(f'行{ln}含长划线: {line.strip()[:40]}')
    if line.count('·') > 1:
        fails.append(f'行{ln}·超限: {line.strip()[:40]}')

# ---------- 3. 机器计数 ----------
# 3a. 卷目带 18 枚，篇名逐一在库本卷题内
vols = re.findall(r'卷[一二三四五六七八九十]{1,3}[^　\n，。]{2,14}篇?$', src, re.M)
assert len(vols) == 18, f'库本卷题 {len(vols)}'
tiles = re.findall(r'<span class="juan[^"]*"><span class="n mono">(卷[^<]+)</span><span class="t">([^<]+)</span>', page)
assert len(tiles) == 18, f'卷目带 {len(tiles)} 枚'
NV = norm(''.join(vols))
for n, t in tiles:
    if norm(n + t) not in NV:
        fails.append(f'卷目带条目不在库本卷题: {n}{t}')

# 3b. 队制 chips 求和 = 12
duiwu = re.findall(r'<span class="chip">([^<]+?) <b>(\d+)</b></span>', page)
total = sum(int(v) for _, v in duiwu)
names = {n.strip(): int(v) for n, v in duiwu}
expect = {'队长': 1, '长牌': 1, '藤牌': 1, '狼筅': 2, '长枪': 4, '短兵': 2, '火兵': 1}
if names != expect or total != 12:
    fails.append(f'队制 chips {names} 合计{total} != 库本 12 人')
if '合 12 人' not in page:
    fails.append('页面缺「合 12 人」')

# 3c. 首级分账
for kw in ['三十两', '二十两', '砍首兵', '二两', '一两', '五钱', '鸟铳手']:
    if kw not in page:
        fails.append(f'首级账缺: {kw}')

# 3d. 武林名录 19 家，逐一在库本
WL = ['宋太祖三十二势长拳', '六步拳', '猴拳', '囵拳', '温家七十二行拳', '三十六合锁',
      '二十四弃探马', '八闪番', '十二短', '吕红八下', '绵张短打', '山东李半天之腿',
      '鹰爪王之拿', '千跌张之跌', '张伯敬之打', '少林寺之棍', '青田棍法', '杨氏枪法', '巴子拳棍']
pais = re.findall(r'<span class="pai">([^<]+)</span>', page)
if len(pais) != 19:
    fails.append(f'武林名录 {len(pais)} 家 != 19')
for p in pais:
    if norm(p) not in N:
        fails.append(f'武林名录不在库本: {p}')

# 3e. 练力四则
lis = re.findall(r'<div class="li"><b>练(.)之力', page)
if lis != ['兵', '手', '足', '身']:
    fails.append(f'练力四则 {lis}')

# 3f. 五方旗 5 面
flags = re.findall(r'<div class="flag"><i[^>]*></i><span>(.)　(.)</span>', page)
if [tuple(f) for f in flags] != [('前', '红'), ('后', '黑'), ('左', '青'), ('右', '白'), ('中', '黄')]:
    fails.append(f'五方旗 {flags}')

# 3g. 福船结算 64
roster = norm('每福船一只，捕盗一名，舵工二名，缭手二名，扳招一名，上斗一名，碇手二名。上用甲长五名，每甲兵十名。')
assert roster in N
if 1 + 2 + 2 + 1 + 1 + 2 + 5 + 50 != 64:
    fails.append('福船结算式错误')
if '64 人' not in page:
    fails.append('页面缺「64 人」')

# 3h. 页内序号
if '之五十四' not in page:
    fails.append('页内缺序号 之五十四')

if fails:
    print('FAIL', len(fails))
    for f in fails:
        print(' -', f)
    sys.exit(1)
print(f'ALL PASS: 44 引文 + 18 卷牌 + 12人队制 + 19家武林 + 五方旗 + 福船64 + 排版红线')
