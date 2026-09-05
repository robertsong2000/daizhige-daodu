#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""菽园杂记 导读页核验：引文双侧逐字对库 + 机数 + 红线"""
import re, sys, unicodedata
from html.parser import HTMLParser

LIB = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/菽园杂记.txt'
PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/shuyuan-zaji.html'

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

# ---------- 1. 库本机数 ----------
chk(len(norm(lib)) == 84444, f'库本去空白字数=84444 实测{len(norm(lib))}')
juans = set(re.findall(r'菽园杂记卷([一二三四五六七八九十]+)', lib))
chk(len(juans) == 15, f'卷数=15 实测{sorted(juans)}')
for frag in ['以箸为快儿', '谓窠飜', '作处州某处铜印', '名天灵盌', '娄东三鳯',
             '铅性畏灰故用灰以捕铅', '夜则山谷如昼', '谓之虾蟇跳', '且称呼以翁父矣']:
    chk(norm(frag) in LIBN, f'库内在位：{frag}')

# ---------- 2. 页面 .q 收集 ----------
class QCollector(HTMLParser):
    VOID = {'meta','link','br','hr','img','input','area','base','col','embed','source','track','wbr'}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.qs, self.cur, self.skip = [], [], None, 0
    def handle_starttag(self, tag, attrs):
        if tag in self.VOID: return
        cls = dict(attrs).get('class', '') or ''
        if 'qs' in cls.split(): self.skip += 1
        if 'q' in cls.split() and self.cur is None: self.cur = []
        self.stack.append((tag, 'q' in cls.split(), 'qs' in cls.split()))
    def handle_endtag(self, tag):
        if tag in self.VOID: return
        if not self.stack: return
        t, isq, isqs = self.stack.pop()
        if isqs: self.skip -= 1
        if isq and self.cur is not None:
            self.qs.append(''.join(self.cur))
            self.cur = [] if any(iq for _, iq, _ in self.stack) else None
    def handle_data(self, data):
        if self.cur is not None and self.skip == 0:
            self.cur.append(data)

p = QCollector()
p.feed(page)
page_qs = [norm(x) for x in p.qs if norm(x)]
print(f'页面 .q 共 {len(page_qs)} 块')
for qn in page_qs:
    if qn not in LIBN:
        chk(False, f'页面 .q 库内无：{qn[:24]}…')
chk(len(page_qs) == 14, f'.q 块数=14 实测{len(page_qs)}')
print('页面 .q 全量对库完成')

# ---------- 3. 反扫引号片段 ----------
body = re.sub(r'<[^>]+>', '', page)
frags = re.findall(r'[「“]([^「」“”]{1,120})[」”]', body)
for f in frags:
    fn = norm(f)
    if fn and fn not in LIBN:
        chk(False, f'反扫引号片段库内无：{f}')
print(f'反扫 {len(frags)} 个引号片段完成')

# ---------- 4. 页内机数 ----------
for w in ['十五卷', '八万四千余字', '成化二年（1466）', '娄东三鳯', '灰吹法', '铅驼',
          '窠飜', '处州某处', '九道工序', '殆知阁导读之一百七十五']:
    chk(w in page, f'页内机数词在位：{w}')
tiles = re.findall(r'<div class="tab">', page)
chk(len(tiles) == 6, f'讳字牌=6 实测{len(tiles)}')
chips = re.findall(r'<div class="chain">\s*<span>', page)
chain_spans = re.search(r'<div class="chain">(.*?)</div>', page, re.S)
n_chips = len(re.findall(r'<span', chain_spans.group(1))) if chain_spans else 0
chk(n_chips == 9, f'工序链=9 实测{n_chips}')
rcards = re.findall(r'<div class="rglyph">', page)
chk(len(rcards) == 6, f'火谱卡=6 实测{len(rcards)}')
slips = re.findall(r'<div class="slip">', page)
chk(len(slips) == 3, f'散页签=3 实测{len(slips)}')

# ---------- 5. 红线 ----------
chk('—' not in page and '–' not in page, '无长划线 — –')
bad = [i for i, line in enumerate(page.split('\n'), 1) if line.count('·') > 1]
chk(not bad, f'每行 · ≤1（违例行 {bad}）')
chk('殆知阁导读 之一百七十五 菽园杂记' in page, 'fnav 序号 之一百七十五')
chk('殆知阁古代文献简体库' in page and 'github.com/robertsong2000/daizhigev20' in page, '页脚来源与仓库链接')
chk('逐字核验' in page, '页脚核验声明')
chk('读者当以历史视之' in page, '页脚时代局限提醒')
chk('writing-mode' in page, '竖排书名签（版式自证）')
puas = [c for c in page if 0xE000 <= ord(c) <= 0xF8FF]
chk(not puas, f'页面无私用区字（{len(puas)}个）')

print()
if fails:
    print(f'共 {len(fails)} 项失败'); sys.exit(1)
print('ALL PASS')
