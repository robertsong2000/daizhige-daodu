#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""龙江船厂志 导读页核验：引文双侧逐字对库 + 机数 + 红线"""
import re, sys, unicodedata
from html.parser import HTMLParser

LIB = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/地理/龙江船厂志.txt'
PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/longjiang-chuanzhi.html'

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
chk(len(norm(lib)) == 67648, f'库本去空白去标点字数=67648 实测{len(norm(lib))}')
juans = set(re.findall(r'龙江船厂志卷之([一二三四五六七八九十]+)', lib))
chk(len(juans) == 8, f'卷数=8 实测{sorted(juans)}')
QUOTES = [
 '嘉靖庚戌，李子元韬由名进士出宰剧邑，更历老练，擢任斯职',
 '越两寒暑，萃成为志。',
 '厂地外萦天堑，内倚石城，衍沃四望，卢龙、马鞍、挂榜诸峰，前后拱揖，足称形胜',
 '乃括提举司之所修造者，类而为五：曰黄、曰战、曰巡、曰渔、曰湖是已。',
 '船面白头至稍，七丈玖尺叁寸。船底白头至无板处伍丈贰尺肆寸无板虚稍贰丈贰寸。头阔玖尺，深伍尺肆寸。中阔壹丈伍尺，深陆尺贰寸。稍阔壹丈肆寸，深柒尺贰寸。',
 '然自都燕以来百九十年，未尝一御',
 '首尾横大木曰伏狮，两边侧木曰拿狮，以拿伏狮也。',
 '起取浙江、江西、湖广、福建、南直隶滨江府、县居民四百余户，来京造船。隶籍提举司，编为四厢，一厢出船木、梭橹、索匠；二厢出船木、铁、缆匠；三厢出捻匠；四厢出棕蓬匠。',
 '今四厢之丁，日就衰耗，虽本厂之役，亦不克支。苟不稍为矜恤，吾不知其所终也！',
 '兴工之初，工食未领，先称贷以自给，工完支银计其出息，十已损二矣！',
 '故匠工之所得者，仅十之六七耳。',
 '但恐以石压草，石去旋生。',
 '铢铢而称之，至石必差；寸寸而度之，至丈必舛。',
 '及郑灏招系太监郑和子孙，伊祖在日，耕种提举司菜地壹段，虽有誊黄给赐之文，查无文卷可照。太监已死，子孙陆续卖与江宁县已故民人宋谦，得银贰拾两入己。',
 '洪武、永乐中，造船人海取宝。该厂有宝库，故取拨匠丁，赴厂看守。今厂库鞠为茂草，而匠丁之输钱者如故。',
]
for q in QUOTES:
    chk(norm(q) in LIBN, f'库内在位：{q[:16]}…')

# ---------- 2. 页面 .q 收集（src 副题不计入） ----------
class QCollector(HTMLParser):
    VOID = {'meta','link','br','hr','img','input','area','base','col','embed','source','track','wbr'}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.qs, self.cur, self.skip = [], [], None, 0
    def handle_starttag(self, tag, attrs):
        if tag in self.VOID: return
        cls = (dict(attrs).get('class', '') or '').split()
        if 'qs' in cls or 'src' in cls: self.skip += 1
        if 'q' in cls and self.cur is None: self.cur = []
        self.stack.append((tag, 'q' in cls, ('qs' in cls or 'src' in cls)))
    def handle_endtag(self, tag):
        if tag in self.VOID: return
        if not self.stack: return
        t, isq, isskip = self.stack.pop()
        if isskip: self.skip -= 1
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
chk(len(page_qs) == 15, f'.q 块数=15 实测{len(page_qs)}')
print('页面 .q 全量对库完成')

# ---------- 3. 反扫引号片段 ----------
body = re.sub(r'<[^>]+>', '', page)
frags = re.findall(r'[「“]([^「」“”]{1,120})[」”]', body)
for f in frags:
    fn = norm(f)
    if fn and fn not in LIBN:
        chk(False, f'反扫引号片段库内无：{f}')
print(f'反扫 {len(frags)} 个引号片段完成')

# ---------- 4. 页内机数（双侧） ----------
MACHINES = ['北京预备黄船壹拾只', '南京小黄船叁拾陆只', '内官监匠三十八名', '每月输钱，不可复蠲',
            '二百四十五产', '户不及二百', '正德十三年', '弘治十六年榜例', '贰拾壹名',
            '肆顷伍拾捌亩伍分玖厘玖毫', '舟楫忐', '玲当', '皆因象以成名', '预备大黄船',
            '柒百捌拾工', '叁百壹拾工', '叁百工', '贰百贰拾伍工', '壹百叁拾叁工', '壹百叁拾工',
            '壹百叁工', '玖拾壹工伍分', '柒拾肆工', '伍拾捌工',
            '贰千伍百伍拾捌工伍分', '柒拾陆两柒钱捌分伍厘',
            '阔壹百叁拾捌丈', '深叁百伍拾肆丈']
for w in MACHINES:
    wn = norm(w)
    chk(wn in LIBN, f'库内在位：{w}')
    chk(w in page, f'页内在位：{w}')
chk('殆知阁导读 之一百九十七 龙江船厂志' in page, 'fnav 序号 之一百九十七')
chk(len(re.findall(r'<button class="part"', page)) == 12, '名物签=12')
eight = re.search(r'<div class="eight">(.*?)</div>\s*</div>', page, re.S)
chk(eight is not None and len(re.findall(r'<div>', eight.group(1))) == 8, '八志隔舱=8')
chk(len(re.findall(r'<figure>', page)) == 9, f'figure 总数=9 实测{len(re.findall("<figure>", page))}')
vices = re.search(r'<div class="vices">(.*?)</div>\s*<p', page, re.S)
chk(vices is not None and len(re.findall(r'<div class="vice">', vices.group(1))) == 5, '律己五弊=5')
rows = re.search(r'<div class="rows">(.*?)</div>\s*<div class="foot">', page, re.S)
chk(rows is not None and len(re.findall(r'<div class="rowi">', rows.group(1))) == 10, '工账行=10')
chk(len(re.findall(r'<a href="#bay', page)) == 6, '舱位导航=6')

# ---------- 5. 红线 ----------
chk('—' not in page and '–' not in page, '无长划线 — –')
bad = [i for i, line in enumerate(page.split('\n'), 1) if line.count('·') > 1]
chk(not bad, f'每行 · ≤1（违例行 {bad}）')
chk('殆知阁古代文献简体库' in page and 'github.com/robertsong2000/daizhigev20' in page, '页脚来源与仓库链接')
chk('逐字比对' in page, '页脚核验声明')
chk('读者当以历史视之' in page, '页脚时代局限提醒')
puas = [c for c in page if 0xE000 <= ord(c) <= 0xF8FF]
chk(not puas, f'页面无私用区字（{len(puas)}个）')

print()
if fails:
    print(f'共 {len(fails)} 项失败'); sys.exit(1)
print('ALL PASS')
