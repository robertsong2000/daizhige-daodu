#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_yanshi.py — 燕市货声 页面核验
1) 库本实测：字数/题头/各行数/玩具数/缺字符号
2) 页面 .q 引文逐字对库（去标点+去空白+集外符归一，页可截尾不可改序）
3) 页面结构断言：月份数据/玩具墙/八大出/字数口径
4) 排版红线：禁 — – 、每行·≤1
"""
import re, sys

LIB = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/燕市货声.txt'
PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/yanshi-huosheng.html'

lib_raw = open(LIB, encoding='utf-8').read()
page = open(PAGE, encoding='utf-8').read()

fails = []
def ck(cond, msg):
    if not cond:
        fails.append(msg)

def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if (0x3400 <= o <= 0x9FFF) or (0x20000 <= o <= 0x3FFFF):
            out.append(ch)
    return ''.join(out)

LIBN = norm(lib_raw)

# ---------- 1) 库本实测 ----------
n_all = len(re.sub(r'\s', '', lib_raw))
ck(n_all == 9039, f'去空白字数 {n_all} != 9039')

SECS = ['序', '凡例', '元旦', '二月', '三月', '四月', '五月', '六月', '七月',
        '八月', '九月', '十月', '冬月', '腊月', '除夕', '通年', '不时', '商贩', '工艺', '铺肆']
lines = [l.strip().replace('　', '') for l in lib_raw.splitlines()]
pos = {}
for i, l in enumerate(lines):
    if l in SECS and l not in pos:
        pos[l] = i
ck(len(pos) == 20, f'题头 {len(pos)}/20')
order = sorted(pos.keys(), key=lambda k: pos[k])
counts = {}
for j, k in enumerate(order):
    end = pos[order[j + 1]] if j + 1 < len(order) else len(lines)
    counts[k] = len([l for l in lines[pos[k] + 1:end] if l])
EXPECT = {'序': 1, '凡例': 6, '元旦': 19, '二月': 28, '三月': 21, '四月': 22, '五月': 31,
          '六月': 14, '七月': 25, '八月': 15, '九月': 11, '十月': 20, '冬月': 9,
          '腊月': 25, '除夕': 9, '通年': 32, '不时': 37, '商贩': 16, '工艺': 29, '铺肆': 3}
for k, v in EXPECT.items():
    ck(counts.get(k) == v, f'{k} 行数 {counts.get(k)} != {v}')
HUOSHENG = sum(v for k, v in counts.items()) - counts['序'] - counts['凡例'] - 2
ck(HUOSHENG == 364, f'货声行数 {HUOSHENG} != 364')

# 玩具数：专卖各种玩艺。到段尾括号闭合，按逗号切分
m = re.search(r'打糖锣挑子。\s*[（(]敲小铜锣,专卖各种玩艺。\s*(.*?)[）)]', lib_raw, re.S)
ck(bool(m), '打糖锣段未找到')
toys = [t for t in re.split(r'[,，]', m.group(1)) if t.strip()]
ck(len(toys) == 53, f'玩具数 {len(toys)} != 53')

# 酸梅汤字数（纯汉字）
mm = re.search(r'又解渴,又带凉,([^!（(]*)！?', lib_raw)
suan = re.search(r'(又解渴[^!]*!)', lib_raw)
ck(bool(suan), '酸梅汤句未找到')
suan_n = len(norm(suan.group(1)))
ck(suan_n == 34, f'酸梅汤字数 {suan_n} != 34')

ck(lib_raw.count('□') == 3, f'□ {lib_raw.count("□")} != 3')
ck(lib_raw.count('?') == 17, f'? {lib_raw.count("?")} != 17')
ck(lib_raw.count('\U00030b38') == 2, '𰬸 != 2')
ck(any(0xE000 <= ord(c) <= 0xF8FF for c in lib_raw), '私有区符号未见')

# ---------- 2) .q 引文收集（全标签栈平衡扫描） ----------
def collect_q(html):
    quotes = []
    for m in re.finditer(r'<([a-zA-Z0-9]+)\b[^>]*\bclass="([^"]*)"[^>]*>', html):
        if 'q' not in m.group(2).split():
            continue
        stack = [m.group(1)]
        j = m.end()
        close_start = None
        while j < len(html) and stack:
            t = re.compile(r'<(/?)([a-zA-Z0-9]+)\b[^>]*?(/?)>').search(html, j)
            if not t:
                break
            if t.group(3) == '/':
                pass  # self-closing
            elif t.group(1) == '/':
                if stack and stack[-1] == t.group(2):
                    stack.pop()
                    if not stack:
                        close_start = t.start()
                        break
            else:
                stack.append(t.group(2))
            j = t.end()
        if close_start is None:
            fails.append(f'.q 未闭合: {m.group(0)[:40]}')
            continue
        txt = re.sub(r'<[^>]+>', '', html[m.end():close_start])
        if len(norm(txt)) >= 2:
            quotes.append(txt)
    return quotes

quotes = collect_q(page)
ck(len(quotes) >= 50, f'.q 引文过少: {len(quotes)}')
for q in quotes:
    qn = norm(q)
    ck(qn in LIBN, f'引文不在库内: {q[:28]}…')

# ---------- 3) 结构断言 ----------
ck('殆知阁导读之八十二' in page, '页顶编号缺失')
ck('之八十二' in page and '卷四十三' in page, '编号/卷次缺失')

# hero 声波 12 段数值
WAVE = [('元旦', 19), ('二月', 28), ('三月', 21), ('四月', 22), ('五月', 31), ('六月', 14),
        ('七月', 25), ('八月', 15), ('九月', 11), ('十月', 20), ('冬月', 9), ('腊月', 25)]
for mo, n in WAVE:
    ck(f'>{n}</text>' in page, f'声波数值 {n} 缺失')
    ck(f'>{mo}</text>' in page, f'声波月份 {mo} 缺失')
    ck(page.count(f'<rect') == 12, '声波 rect != 12') if mo == '元旦' else None

# 声轨行内计数（结构化：月名 span 紧邻计数字 span）
for mo, n in WAVE[1:]:
    got = re.search(r'<span class="m">' + re.escape(mo) + r'</span><span class="c mono"><b>(\d+)</b> 行</span>', page)
    ck(bool(got) and int(got.group(1)) == n, f'声轨 {mo} 计数缺失或不符')

ck(re.search(r'一担共 <b>53</b> 件', page), '玩具墙计数文案缺失')
chips = re.findall(r'<div class="chips">\s*(.*?)</div>', page, re.S)
ck(len(chips) == 1 and len(re.findall(r'<span>', chips[0])) == 53, '玩具墙 chips != 53')

BACHU = ['香山还愿', '铡美案', '高老庄', '五鬼捉刘氏', '武大郎乍尸', '卖豆腐', '王小儿打老虎', '李翠莲']
for nm in BACHU:
    ck(nm in page, f'八大出页面缺 {nm}')
    ck(norm(nm) in LIBN, f'八大出库内缺 {nm}')
ck(page.count('class="nm"') == 8, '八大出名牌 != 8')

for s in ['9,039', '364', '光绪丙午', '延秋山馆', '张次溪', 'github.com/robertsong2000/daizhigev20',
          '逐字核验', '时代印记' ]:
    ck(s in page, f'页面缺关键串: {s}')
ck('三十四个字' in page, '酸梅汤字数文案缺失')

# ---------- 4) 排版红线 ----------
ck('—' not in page, '出现长划线 —')
ck('–' not in page, '出现短划线 –')
for i, ln in enumerate(page.splitlines(), 1):
    c = ln.count('·')
    ck(c <= 1, f'第{i}行含 {c} 个 ·')

# title 一致性
t = re.search(r'<title>(.*?)</title>', page)
ck(bool(t) and '之八十二' in t.group(1), 'title 未自标篇号')

print(f'引文 .q 共 {len(quotes)} 条，库本去空白 {n_all} 字，货声 {HUOSHENG} 行，玩具 {len(toys)} 件')
if fails:
    print(f'\nFAIL {len(fails)} 项:')
    for f in fails:
        print(' -', f)
    sys.exit(1)
print('ALL PASS')
