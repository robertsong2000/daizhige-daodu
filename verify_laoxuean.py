#!/usr/bin/env python3
# 核验 laoxuean-biji.html
# 1) 页内 7 段 .q 引文与库内文件逐字比对（宴单段含缺字，去缺位后整段相等）
# 2) 每段引文归属卷次断言  3) 十卷条数/总数机器清点并与页面声明比对
# 4) 排版红线：全文禁 — – ，每行 · 至多 1 个，无外部依赖
import re, sys

ROOT = '/home/robertsong/workspace/claude/daizhige-daodu'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/老学庵笔记.txt'

lib  = open(LIB,  encoding='utf-8').read()
page = open(ROOT + '/laoxuean-biji.html', encoding='utf-8').read()
errs, oks = [], 0

def norm(s):
    return ''.join(c for c in s if c.isalnum())

def is_pua(c):
    return 0xE000 <= ord(c) <= 0xF8FF

# ---------- 库内结构 ----------
lines = lib.split('\n')
marks = [(i, l.strip()) for i, l in enumerate(lines) if l.strip().startswith('●卷')]
xu_i  = next(i for i, l in enumerate(lines) if '续笔记' in l and i > marks[-1][0])
counts = []
for k, (st, _) in enumerate(marks):
    en = marks[k + 1][0] if k + 1 < len(marks) else xu_i
    counts.append(sum(1 for l in lines[st + 1:en] if l.strip()))
xu_count = sum(1 for l in lines[xu_i + 1:] if l.strip())

EXPECT_COUNTS = [67, 62, 48, 79, 64, 60, 49, 50, 44, 55]
if counts != EXPECT_COUNTS:
    errs.append(f'卷条数不符: {counts}')
if xu_count != 21:
    errs.append(f'续笔记条数 {xu_count} != 21')
oks += 1

def region_text(name):
    if name == '续笔记':
        return '\n'.join(lines[xu_i:])
    idx = next(i for i, (_, t) in enumerate(marks) if t == f'●{name}')
    en = marks[idx + 1][0] if idx + 1 < len(marks) else xu_i
    return '\n'.join(lines[marks[idx][0]:en])

# ---------- 页面 .q 引文 ----------
blocks = re.findall(r'<blockquote class="q">(.*?)</blockquote>', page, re.S)
if len(blocks) != 7:
    errs.append(f'.q 段数 {len(blocks)} != 7')

def page_text(block):
    t = re.sub(r'<span class="src">.*?</span>', '', block, flags=re.S)
    t = re.sub(r'<span class="lost"></span>', '', t)
    t = re.sub(r'<[^>]+>', '', t)
    return t

QUOTES = [
    ('卷五', '田登作郡，自讳其名，触者必怒，吏卒多被榜笞。于是举州皆谓灯为火。上元放灯，许人入州治游观。吏人遂书榜揭于市曰：“本州依例放火三日。”'),
    ('卷二', '故都李和炒栗，名闻四方。他人百计效之，终不可及。绍兴中，陈福公及钱上阁恺出使虏庭，至燕山，忽有两人持炒栗各十裹来献，三节人亦人得一裹，自赞曰：“李和儿也。”挥涕而去。'),
    ('卷五', '“夜凉疑有雨，院静似无僧”，潘逍遥诗也。'),
    ('卷一', '高宗在徽宗服中，用白木御倚子。钱大主入觐，见之，曰：“此檀香倚子耶？”张婕妤掩口笑曰：“禁中用烟脂皂荚多，相公已有语，更敢用檀香作倚子耶？”时赵鼎、张浚作相也。'),
    ('续笔记', '唐初，魏郑公等撰《隋书》，以隋文帝之父名忠，故凡“忠”字皆谓之“诚”，谓死事之臣为《诚节传》，书中凡忠臣皆曰“诚臣”。书作于唐，犹为隋避讳，骤读之，殆不可晓。太宗诗云：“疾风知劲草，板荡识诚臣。”亦是避隋讳耳。'),
    ('卷五', '彦衡力持不可，曰：“松当用黄山所产，此平地松岂可用！”人重其有守。'),
]

for name, expected in QUOTES:
    rn, ep = norm(region_text(name)), norm(expected)
    if ep not in rn:
        errs.append(f'引文不在库内[{name}]: {expected[:18]}...')
    oks += 1

# 页面引文 == 库内真值（顺序对应上面 6 段 + 宴单段单独处理）
by_region = {}
for name, expected in QUOTES:
    by_region.setdefault(name, []).append(norm(expected))

menu_line = next(l for l in lines if '集英殿宴金国人使' in l)
menu_expect = menu_line[menu_line.find('集英殿'):menu_line.find('看食')]
n_pua = sum(1 for c in menu_expect if is_pua(c))
if n_pua != 1:
    errs.append(f'宴单段缺字符号 {n_pua} 个 != 1')
menu_norm = norm(menu_expect)
if menu_norm not in norm(region_text('卷一')):
    errs.append('宴单真值不在卷一')
oks += 1

page_norms = [norm(page_text(b)) for b in blocks]
used = [False] * len(page_norms)
for name, expected in QUOTES:
    ep = norm(expected)
    if ep in page_norms and not used[page_norms.index(ep)]:
        used[page_norms.index(ep)] = True
    else:
        errs.append(f'页面缺少引文: {expected[:18]}...')
if menu_norm in page_norms and not used[page_norms.index(menu_norm)]:
    used[page_norms.index(menu_norm)] = True
else:
    errs.append('页面缺少宴单引文')
if not all(used):
    errs.append(f'页面有未核验的引文段: {used}')

# 榜书八字 ⊂ 库内田登条
bang = re.search(r'<div class="bang-chars">(.*?)</div>', page, re.S).group(1)
bang_chars = ''.join(re.findall(r'<span>(.)</span>', bang))
if bang_chars != '本州依例放火三日':
    errs.append(f'榜书连排不符: {bang_chars}')
if norm('本州依例放火三日') not in norm(lib):
    errs.append('榜书八字不在库内')
oks += 1

# ---------- 页面计数声明 ----------
tags = re.findall(r'<div class="tag">卷(.)<small>(.+?)</small></div>', page)
ZH = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10}
def zh2num(s):
    if s == '十': return 10
    if '十' not in s: return ZH[s]
    a, b = s.split('十')
    return (ZH[a] if a else 1) * 10 + (ZH[b] if b else 0)
if len(tags) != 10:
    errs.append(f'卷签数 {len(tags)} != 10')
for (vol, small), real in zip(tags, EXPECT_COUNTS):
    if zh2num(small) != real:
        errs.append(f'卷{vol} 页面计 {small} != 实测 {real}')
oks += 1

if '578' not in page or '21' not in page:
    errs.append('页面缺 578/21 总数声明')
if '五百九十九' not in page:
    errs.append('页面缺 五百九十九条 声明')
total_pua = sum(1 for c in lib if is_pua(c) or c in '□�')
if not (160 <= total_pua <= 220):
    errs.append(f'库本污染字符总数 {total_pua} 超出校记声明区间')
oks += 1

li_big = page.count('<div class="li"><small>裹</small></div>')
if li_big != 20:
    errs.append(f'大裹 {li_big} 个 != 20（两位使臣各十裹）')
dish = re.findall(r'<div class="dish">', page)
if len(dish) != 9:
    errs.append(f'菜签 {len(dish)} 盏 != 9')
oks += 2

# ---------- 排版红线 ----------
if '—' in page or '–' in page:
    errs.append('出现长划线 — 或 –')
for i, ln in enumerate(page.split('\n'), 1):
    if ln.count('·') > 1:
        errs.append(f'第 {i} 行 · 超过 1 个')
oks += 1
for bad in ('<script', '@import', '<link '):
    if bad in page:
        errs.append(f'外部依赖: {bad}')

if errs:
    print('FAIL')
    for e in errs:
        print(' -', e)
    sys.exit(1)
print(f'PASS  引文 7 段(8 节)全过  卷条数 {EXPECT_COUNTS}+续{XU if False else xu_count}  污染字符 {total_pua}  菜 9 盏  裹 20  排版红线通过')
