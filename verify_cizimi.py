#!/usr/bin/env python3
# 核验 cezi-midi.html：引文逐字对库 + 排版红线 + 机器计数
import re, sys
from html.parser import HTMLParser

PAGE = 'cezi-midi.html'
LIB = '/home/robertsong/workspace/claude/daizhige-simplified/易藏/术数/测字秘牒.txt'

def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if 0x3400 <= o <= 0x9FFF or 0x20000 <= o <= 0x3FFFF:
            out.append(ch)
    return ''.join(out)

VOID = {'br','meta','link','img','hr','input','source','wbr'}

class QC(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.quotes = []
        self._cur = None
    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        cls = dict(attrs).get('class','') or ''
        names = cls.split()
        if self._cur is not None:
            self.stack.append(self._cur)
            self._cur = None
        if 'q' in names:
            self._cur = []
        self.stack.append((tag, attrs))
    def handle_startendtag(self, tag, attrs):
        pass
    def handle_endtag(self, tag):
        if tag in VOID:
            return
        # pop until matching tag
        while self.stack:
            t, _ = self.stack.pop()
            if t == tag:
                break
        if self._cur is not None:
            self.quotes.append(''.join(self._cur))
            self._cur = None
        # restore outer q context if it exists
        for i in range(len(self.stack)-1, -1, -1):
            t, attrs = self.stack[i]
            cls = (dict(attrs).get('class','') or '').split()
            if 'q' in cls:
                self._cur = []
                break
    def handle_data(self, data):
        if self._cur is not None:
            self._cur.append(data)

html = open(PAGE).read()
lib = open(LIB).read()

errors = []
def chk(cond, msg):
    if not cond:
        errors.append(msg)

# ---------- 红线 ----------
chk('—' not in html, '页面出现长划线 —')
chk('–' not in html, '页面出现短划线 –')
for i, line in enumerate(html.split('\n'), 1):
    if line.count('·') > 1:
        errors.append(f'第{i}行有 {line.count("·")} 个·')

# ---------- 收集页面引文 ----------
p = QC()
p.feed(html)
quotes = [q.strip() for q in p.quotes]
nlib = norm(lib)
bad = []
for i, q in enumerate(quotes, 1):
    nq = norm(q)
    if not nq:
        bad.append((i, q[:40], 'EMPTY'))
    elif nq not in nlib:
        bad.append((i, q[:60], 'NOT-IN-LIB'))
if bad:
    for i, q, why in bad:
        errors.append(f'引文#{i} {why}: {q}')

print(f'页面 .q 引文总数: {len(quotes)}，未命中: {len(bad)}')

# ---------- 机器计数 ----------
total = len(lib)
nospace = len(re.sub(r'\s', '', lib))
hanzi = len(re.findall(r'[㐀-鿿\U00020000-\U0003ffff]', lib))
tri = sum(1 for c in lib if (0xE000 <= ord(c) <= 0xF8FF) or (0x20000 <= ord(c) <= 0x3FFFF))
tri_kinds = len(set(c for c in lib if (0xE000 <= ord(c) <= 0xF8FF) or (0x20000 <= ord(c) <= 0x3FFFF)))
kuo = lib.count('囗')
que = lib.count('□')
delta = lib.count('△')
chk('钱字（观梅）' in lib, '库本应有「钱字（观梅）」案（无△记号）')
cases = delta + 1
print(f'库本: 全帙 {total} / 去空白 {nospace} / 汉字 {hanzi}；PUA+ExtB {tri_kinds} 种 {tri} 见；囗 {kuo}；□ {que}；△ {delta} + 钱字 1 = 案例 {cases}')

chk(total == 27097, f'全帙字符数不符: {total}')
chk(nospace == 24129, f'去空白字符数不符: {nospace}')
chk(hanzi == 18423, f'汉字数不符: {hanzi}')
chk(tri_kinds == 20, f'PUA/ExtB 种数不符: {tri_kinds}')
chk(kuo == 21, f'囗 数不符: {kuo}')
chk(que == 11, f'□ 数不符: {que}')
chk(cases == 54, f'案例数不符: {cases}')

# 页面声称的数字须与上一致
for token in ['27,097', '24,129', '18,423']:
    chk(token in html, f'页面缺计数 {token}')
chk('案例五十四案' in html and '五十四个现场案例' in html, '页面缺案例数 54 表述')
chk('二十种' in html and '十一处' in html and '二十一处' in html, '页面缺缺陷字符计数')

# ---------- 结构断言 ----------
fa10 = ['装头','接脚','穿心','包笼','破解','添笔','减笔','对关','摘字','观梅']
for n in fa10:
    key = n + '测法' if n != '观梅' else '观梅测字'
    chk(key in lib, f'库本缺法名 {key}')
    chk(key in html, f'页面缺法名 {key}')
fa6 = ['象形','会意','假借','谐声','指事','转注']
for n in fa6:
    chk(n + '测法' in lib, f'库本缺六法 {n}测法')
    chk(n + '</h4>' in html, f'页面缺六法 {n}')
for v in ['卷一','卷二','卷三','卷四','卷五','卷六','卷七']:
    chk(v in lib, f'库本缺 {v}')
chk('双句格法' in lib and '测字散格法' in lib and '杂占赋' in lib and '至理测法' in lib, '库本缺卷名')
# 库本怪相：卷四卷五卷头连排
chk(re.search(r'双句格法卷五\s*测字散格法', lib) is not None, '库本应有卷四卷五卷头连排一行')
# 库本怪相：门字案「余曰」后无冒号
chk('余曰“必死！”' in lib, '库本门字案应作「余曰“必死！”」无冒号')
# 邵康节句引号错配
chk('邵康节先生曰：”字同事不同' in lib, '库本邵康节句应以右引号起')
# 指事十目
chk('曰正论勿好奇，曰言语不可杂' in lib, '库本缺指事十目末二目')
# 四时假借
chk('此四时借用于一日也' in lib, '库本缺四时假借结句')
# 页面版式
chk('拆字' in html and '朱砂' in html, '页面缺卷名/色标')

# ---------- 引文计数与点验单一致 ----------
CN = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9}
def cn2int(s):
    total, cur = 0, 0
    for ch in s:
        if ch in CN:
            cur += CN[ch]
        elif ch == '十':
            cur = (cur or 1) * 10 if cur < 10 else cur * 10
        elif ch == '百':
            total += (cur or 1) * 100; cur = 0
    return total + cur
m = re.search(r'引文共([一二三四五六七八九十百]+)条', html)
chk(m is not None, '点验单缺引文计数表述')
if m:
    chk(cn2int(m.group(1)) == len(quotes), f'点验单引文计数 {m.group(1)} 与实际 {len(quotes)} 不符')

print('FAIL:\n' + '\n'.join(errors) if errors else 'ALL PASS')
sys.exit(1 if errors else 0)
