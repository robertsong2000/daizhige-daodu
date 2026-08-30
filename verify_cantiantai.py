#!/usr/bin/env python3
# 核验 cantiantai-wutaishan-ji.html：引文双侧逐字、天气墙复算、机数、排版红线
import re, sys, collections
from html.parser import HTMLParser

PAGE = 'cantiantai-wutaishan-ji.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/参天台五台山记.txt'
NO = '之一百一十四'

def norm(s):
    return re.sub(r'\s+', '', s)

T = norm(open(LIB, encoding='utf-8').read())
page_src = open(PAGE, encoding='utf-8').read()

# ---------- 1. 页面 .q 收集（VOID 安全，栈配平） ----------
class QCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []      # (tag, in_q)
        self.quotes = []
        self.buf = None      # list of chars when inside q
        self.qdepth = 0
        self.cells = []
    def handle_starttag(self, tag, attrs):
        cls = (dict(attrs).get('class') or '').split()
        isq = 'q' in cls
        if 'c' in cls and len(cls) >= 2 and tag == 'i':
            self.cells.append(cls[1])
        if isq:
            self.qdepth += 1
            if self.qdepth == 1:
                self.buf = []
        self.stack.append((tag, isq))
    def handle_endtag(self, tag):
        # pop until matching
        while self.stack and self.stack[-1][0] != tag:
            self.stack.pop()
        if not self.stack:
            return
        _, isq = self.stack.pop()
        if isq:
            self.qdepth -= 1
            if self.qdepth == 0 and self.buf is not None:
                self.quotes.append(norm(''.join(self.buf)))
                self.buf = None
    def handle_data(self, data):
        if self.qdepth > 0 and self.buf is not None:
            self.buf.append(data)
    # void 元素不入栈（handle_startendtag 与常见 void）
    def handle_startendtag(self, tag, attrs):
        pass

p = QCollector()
p.feed(page_src)
p.close()
quotes = [q for q in p.quotes if q]
print(f'页面 .q 引文块：{len(quotes)} 条')

bad = 0
for q in quotes:
    if q not in T:
        bad += 1
        print('引文不在库本：', q[:60])
if bad:
    sys.exit(f'{bad} 条引文核验失败')

# ---------- 2. 「」反扫：页面可见文本中所有「…」必须见于库本 ----------
body = re.sub(r'<style>.*?</style>', '', page_src, flags=re.S)
text = re.sub(r'<[^>]+>', '', body)
for m in re.finditer(r'「([^」]*)」', text):
    seg = norm(m.group(1))
    if seg and seg not in T:
        print('反扫未命中：', m.group(0)[:60]); bad += 1
if bad:
    sys.exit('「」反扫有失败项')

# ---------- 3. 库本解析：逐日条目 / 天气 ----------
lines = open(LIB, encoding='utf-8').read().splitlines()
marks = [(i, l) for i, l in enumerate(lines) if l.startswith('●')]
def juan_of(idx):
    cur = ''
    for i, l in marks:
        if i < idx: cur = l
    return cur.replace('●参天台五台山记', '')
PAT = re.compile(r'(?:^　　|(?<=[。了！？；：]))\s*(\S{0,4}日)\s*[　 ]*([甲乙丙丁戊己庚辛壬癸])')
entries = []
for i, l in enumerate(lines):
    if l.startswith('●') or l.strip().startswith('【'):
        continue
    for m in PAT.finditer(l):
        entries.append((i, juan_of(i), m.group(1), m.group(2), m.start()))
def wcls(e):
    line = lines[e[0]]
    head = line[e[4]:e[4]+80]
    if '雪' in head: return 'X'
    if '雨' in head: return 'R'
    if '翳' in head: return 'D'
    if '风' in head: return 'W'
    if '天晴' in head: return 'S'
    head2 = line[e[4]:e[4]+260]
    if '雨' in head2: return 'R'
    if '天晴' in head2: return 'S'
    return 'N'
wc = collections.Counter(wcls(e) for e in entries)
cn = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10}
def num(s):
    if s == '十': return 10
    if s == '廿': return 20
    if s == '卅': return 30
    if '廿' in s: return 20 + (cn.get(s[1],0) if len(s)>1 and s[1] in cn else 0)
    if '卅' in s: return 30 + (cn.get(s[1],0) if len(s)>1 and s[1] in cn else 0)
    if '十' in s:
        pp = s.split('十')
        return (cn.get(pp[0],1) if pp[0] else 1)*10 + (cn.get(pp[1],0) if len(pp)>1 and pp[1] else 0)
    return cn.get(s,0)
def dn(ds):
    m = re.match(r'([一二三四五六七八九十]{1,2}月)?([一二三四五六七八九十廿卅]{1,3})日', ds)
    return (m.group(1), num(m.group(2))) if m else None
order = ['卷第一','卷第二','卷第三','卷第四','卷第五','卷第六','卷第七','卷第八']
rows = {j: [e for e in entries if e[1] == j] for j in order}
exp_cells = []
gap_total = 0
for j in order:
    prev = None; month = None
    for e in rows[j]:
        d = dn(e[2])
        if d:
            if d[0]: month = d[0]
            if prev and prev[0] == month and d[1] and prev[1] and d[1] > prev[1] + 1:
                for _ in range(d[1]-prev[1]-1):
                    exp_cells.append('G'); gap_total += 1
        exp_cells.append(wcls(e))
        if d: prev = (month, d[1])
print(f'库本条目：{len(entries)}  天气：{dict(wc)}  缺记：{gap_total}  墙格：{len(exp_cells)}')

# ---------- 4. 页面墙格复算 ----------
pc = p.cells
page_cells = re.findall(r'class="c ([SRDWXNG])"', page_src)
if page_cells != exp_cells:
    diff = next((i for i,(a,b) in enumerate(zip(page_cells, exp_cells)) if a != b), min(len(page_cells), len(exp_cells)))
    sys.exit(f'墙格不一致：页 {len(page_cells)} 格 vs 库 {len(exp_cells)} 格，首异于第 {diff} 格')
print(f'天气墙 {len(page_cells)} 格逐格全等')

# ---------- 5. 机数上页 ----------
def must(n, label):
    if str(n) not in page_src:
        sys.exit(f'页缺机数 {label}={n}')
E = len(entries)
assert E == 452, E
must(E, '条目'); must(wc['S'], '晴'); must(wc['R'], '雨'); must(wc['W'], '风')
must(wc['D'], '翳'); must(wc['X'], '雪'); must(wc['N'], '未记'); must(gap_total, '缺记')
must(wc['S']+wc['R']+wc['W']+wc['D']+wc['X'], '有天气')
for n in (T.count('七时行法'), len(re.findall(r'[过行][一二三四五六七八九十百廿卅0-9]+里', open(LIB, encoding='utf-8').read()))):
    must(n, '计数')
assert T.count('七时行法') == 253
print('机数 253/371 等全部在页')

# ---------- 6. 红线 ----------
if '—' in page_src or '–' in page_src:
    sys.exit('出现长划线')
for ln, line in enumerate(text.splitlines(), 1):
    if line.count('·') > 1:
        sys.exit(f'第 {ln} 行 · 超限')
eng = set(w for w in re.findall(r'[A-Za-z]{2,}', text))
allow = {'github', 'com', 'robertsong', 'daizhigev'}
res = eng - allow
if res:
    sys.exit(f'正文英文残留：{res}')
if page_src.count(NO) != 2:
    sys.exit(f'页内序号 {NO} 出现 {page_src.count(NO)} 次（应 2：title+kicker）')
for token in ('殆知阁古代文献简体库', '逐字核验', '时代局限', '卷十六 行纪'):
    if token not in page_src:
        sys.exit(f'页脚缺：{token}')
# 花名册对库
if norm('頼縁供奉、快宗供奉、圣秀、惟观、心贤、善久、沙弥长明') not in T:
    sys.exit('乘船名单与库本不符')
if norm('永智、寻源、快寻、良徳、一能、翁丸') not in T:
    sys.exit('还人名单与库本不符')
# PUA/ExtB 概况对库
pua = collections.Counter(hex(ord(ch)) for ch in open(LIB, encoding='utf-8').read()
                          if 0xE000 <= ord(ch) <= 0xF8FF or 0x20000 <= ord(ch) <= 0x2FA1F)
assert sum(pua.values()) == 11 and len(pua) == 5, pua
print('红线全过（无长划线、·合规、无英文残留、序号两处、页脚齐全）')
print(f'ALL PASS：引文 {len(quotes)} 条双侧命中，墙 {len(page_cells)} 格全等')
