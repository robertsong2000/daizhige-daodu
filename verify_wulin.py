# -*- coding: utf-8 -*-
"""verify_wulin.py — 武林旧事导读页全量核验
引文逐字对库 + 机数复核 + 排版红线。"""
import re, sys, html
from html.parser import HTMLParser

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/wulin-jiushi.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/地理/武林旧事.txt'

lib = open(LIB, encoding='utf-8').read()
page = open(PAGE, encoding='utf-8').read()

fails, checks = [], 0
def ck(cond, msg):
    global checks
    checks += 1
    if not cond:
        fails.append(msg)

def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if ch.isspace():
            continue
        if 0x3400 <= o <= 0x9FFF or 0x20000 <= o <= 0x3FFFF:
            out.append(ch)
    return ''.join(out)

LIB_NORM = norm(lib)

class QCollector(HTMLParser):
    """栈配平：starttag 入栈（记 is_q），endtag 出栈；.q 闭合时收集缓冲。"""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # [tag, is_q, [chars...]]
        self.collected = []
    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get('class', '') or ''
        self.stack.append([tag, 'q' in cls.split(), []])
    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                break
        else:
            return
        closing = self.stack[i:]
        del self.stack[i:]
        text = ''.join(''.join(b[2]) for b in closing)
        outer = self.stack[-1] if self.stack else None
        if any(b[1] for b in closing):
            self.collected.append(text)
        if outer and outer[1]:
            outer[2].append(text)
    def handle_data(self, data):
        for frame in reversed(self.stack):
            if frame[1]:
                frame[2].append(data)
                break

g = QCollector()
g.feed(page)
quotes = [q.strip() for q in g.collected if q.strip()]
ck(len(quotes) >= 55, f'引文块过少: {len(quotes)}')

seen = set()
for q in quotes:
    qn = norm(q)
    ck(len(qn) >= 2, f'引文过短: {q[:20]!r}')
    if qn in seen:
        continue
    seen.add(qn)
    ck(qn in LIB_NORM, f'引文不在库内: {q[:42]!r}')

# ---------- 机数 ----------
nw = len(re.sub(r'\s', '', lib))
ck(nw == 64959, f'库本去空白字数变了吗: {nw}')

i0 = lib.find('官本杂剧段数', 60000)
i1 = lib.find('张约斋赏心乐事', i0)
seg = lib[i0:i1]
body = re.sub(r'（[^（）]*）', '', seg).replace('\n', '　')
toks = [x for x in body.split('　') if re.fullmatch(r'[㐀-鿿]+', x) and x != '官本杂剧段数']
ck(len(toks) == 275, f'杂剧段名机数不符: {len(toks)}')

i0 = lib.find('凉　　水')
i1 = lib.find('糕\n', i0)
seg = re.sub(r'（[^（）]*）', '', lib[i0:i1]).replace('凉　　水', '').strip()
items = [x for x in re.split(r'[　\s]+', seg) if x]
ck(len(items) == 17, f'凉水味数: {len(items)}')

ck(lib.count('德祐') == 0, '德祐在库内出现，结算行断言崩')

pua = [c for c in lib if 0xE000 <= ord(c) <= 0xF8FF]
ck(len(pua) > 0, '缺字符号计数异常')

# ---------- 排版红线 ----------
text_only = html.unescape(re.sub(r'<[^>]+>', '', page))
for bad in ['—', '–', '―', '‐']:
    ck(bad not in text_only, f'红线: 出现 {bad}')
for ln, line in enumerate(text_only.split('\n'), 1):
    if line.count('·') > 1:
        ck(False, f'红线: 第{ln}行 · 超限: {line.strip()[:50]!r}')

ck('http://' not in page and 'https://' not in page, '红线: 外部依赖')
ck('<script' not in page, '红线: 出现 script')

ck('64,959' in page, '页面字数缺失')
ck('275' in page, '页面杂剧数缺失')
ck('之九十' in page, '页面序号缺失')

print(f'quotes collected: {len(quotes)}  unique: {len(seen)}')
print(f'checks: {checks}')
if fails:
    print('FAIL:')
    for f in fails:
        print('  -', f)
    sys.exit(1)
print('ALL PASS')
