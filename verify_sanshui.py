#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""三水小牍 导读页核验：引文双侧逐字对库 + 机数 + 红线"""
import re, sys, unicodedata
from html.parser import HTMLParser

LIB = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/三水小牍.txt'
PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/sanshui-xiaodu.html'

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
lines = [l for l in lib.split('\n')]
tocc = next(i for i, l in enumerate(lines) if l == '卷上')          # 目录卷上
tocx = next(i for i, l in enumerate(lines) if l == '卷下' and i > tocc)
toc_up = [l for l in lines[tocc+1:tocx] if l.strip()]
toc_low = [l for l in lines[tocx+1:tocx+20] if l.strip() and l != '逸文']
chk(len(toc_up) == 17, f'目录卷上篇数=17 实测{len(toc_up)}')
chk(len(toc_low) == 18, f'目录卷下篇数=18 实测{len(toc_low)}')
# 目录标题必须在正文再出现一次（目录与正文一致；库本此处目录与正文题名有异文）
TITLE_VARIANTS = {'风拔斾李钧不终': '暴风拔斾李钧不终'}
for t in toc_up + toc_low:
    cnt = sum(1 for l in lines if l == t)
    ok = cnt >= 2 or (t in TITLE_VARIANTS and TITLE_VARIANTS[t] in lines)
    chk(ok, f'篇目正文在位：{t}')
yiwen = next(i for i, l in enumerate(lines) if l == '逸文' and i > toc_low.index(toc_low[-1]) + tocx)
gj = [l for l in lines[yiwen:] if l.startswith('《广记》')]
xtz = [l for l in lines[yiwen:] if l == '《续谈助》']
chk(len(gj) == 10, f'逸文标《广记》则数=10 实测{len(gj)}')
chk(len(xtz) == 1, f'逸文标《续谈助》则数=1 实测{len(xtz)}')
n_yiwen = len(gj) + len(xtz) + 1
chk(n_yiwen == 12, f'逸文总则数=12 实测{n_yiwen}')
chk(19000 < len(lib) < 22000, f'全书字数两万余 实测{len(lib)}')

# 干支换算（锚 1984 甲子）
STEM = '甲乙丙丁戊己庚辛壬癸'; BRANCH = '子丑寅卯辰巳午未申酉戌亥'
def ganzhi_year(gz, lo, hi):
    s, b = gz
    for y in range(lo, hi + 1):
        if STEM.index(s) == (y - 4) % 10 and BRANCH.index(b) == (y - 4) % 12:
            return y
for gz, want in [('戊子', 868), ('庚寅', 870), ('壬辰', 872), ('丁亥', 867), ('丙戌', 866)]:
    chk(ganzhi_year(gz, 860, 880) == want, f'干支{gz}={want}')
for frag in ['时咸通戊子春正月也', '壬辰岁冬十一月', '咸通丁亥岁', '咸通丙戌岁夏五月', '咸通庚寅岁']:
    chk(norm(frag) in LIBN, f'库内在位（系年依据）：{frag}')

# ---------- 2. 页面 .q 收集 ----------
class QCollector(HTMLParser):
    VOID = {'meta','link','br','hr','img','input','area','base','col','embed','source','track','wbr'}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.qs = []
        self.cur = None
        self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in self.VOID:
            if tag == 'br' and self.cur is not None:
                self.cur.append('\x00')
            return
        cls = dict(attrs).get('class', '') or ''
        isqs = 'qs' in cls.split()
        if isqs:
            self.skip += 1
        isq = 'q' in cls.split()
        if isq and self.cur is None:
            self.cur = []
        self.stack.append((tag, isq, isqs))
    def handle_endtag(self, tag):
        if tag in self.VOID: return
        if not self.stack: return
        t, isq, isqs = self.stack.pop()
        if isqs:
            self.skip -= 1
        if isq and self.cur is not None:
            self.qs.append(''.join(self.cur))
            self.cur = [] if any(iq for _, iq, _ in self.stack) else None
    def handle_data(self, data):
        if self.cur is not None and self.skip == 0:
            self.cur.append(data)

p = QCollector()
p.feed(page)
buckets = []
for b in p.qs:
    buckets.extend(b.split('\x00'))
page_qs = [norm(x) for x in buckets if norm(x)]
print(f'页面 .q 拆分后共 {len(page_qs)} 块')

for qn in page_qs:
    if qn not in LIBN:
        chk(False, f'页面 .q 库内无：{qn[:24]}…')
chk(len(page_qs) >= 14, f'.q 块数≥14 实测{len(page_qs)}')
print(f'页面 {len(page_qs)} 块 .q 全量对库完成')

# ---------- 3. 反扫引号片段 ----------
body = re.sub(r'<[^>]+>', '', page)
frags = re.findall(r'[「“]([^「」“”]{1,120})[」”]', body)
for f in frags:
    fn = norm(f)
    if fn and fn not in LIBN:
        chk(False, f'反扫引号片段库内无：{f}')
print(f'反扫 {len(frags)} 个引号片段完成')

# ---------- 4. 页内机数词 ----------
for w in ['卷上十七篇', '卷下十八篇', '逸文十二则', '十则标明辑自《太平广记》', '两万余字',
          '咸通九年正月', '咸通十一年', '咸通十三年冬', '咸通八年', '咸通七年五月', '广明元年']:
    chk(w in page, f'页内机数词在位：{w}')

# 门额节次
lintels = re.findall(r'<span class="lintel">([^<]+)</span>', page)
exp = ['咸宜观', '李庾宅', '徽安门', '长夏门', '敦化里', '兰陵里', '北邙', '温泉别业', '天明']
chk(lintels == exp, f'门额九座全等 实测{lintels}')

# ---------- 5. 红线 ----------
chk('—' not in page and '–' not in page, '无长划线 — –')
bad = [i for i, line in enumerate(page.split('\n'), 1) if line.count('·') > 1]
chk(not bad, f'每行 · ≤1（违例行 {bad}）')

chk('殆知阁导读 之一百七十一 三水小牍' in page, 'fnav 序号 之一百七十一')
chk('殆知阁古代文献简体库' in page and 'github.com/robertsong2000/daizhigev20' in page, '页脚来源与仓库链接')
chk('逐字核验' in page, '页脚核验声明')
chk('时代局限' in page, '页脚时代局限提醒')
chk('writing-mode' in page, '坊额竖排签（版式自证）')

print()
if fails:
    print(f'共 {len(fails)} 项失败'); sys.exit(1)
print('ALL PASS')
