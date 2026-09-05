# 濒湖脉学 导读页核验：引文双侧 + 排版红线 + 页脚三要素 + mulu 编号
import re, sys, importlib.util
from html.parser import HTMLParser

spec = importlib.util.spec_from_file_location('qb', 'quotes_binhu.py')
qb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qb)
QUOTES = qb.QUOTES

LIB = '/home/robertsong/workspace/claude/daizhige-simplified/医藏/濒湖脉学.txt'
PAGE = 'binhu-maixue.html'
MULU = 'mulu.html'

raw = open(LIB, encoding='utf-8').read()
html = open(PAGE, encoding='utf-8').read()
mulu = open(MULU, encoding='utf-8').read()

fails = []
def chk(name, cond, detail=''):
    if not cond:
        fails.append(f'{name}: {detail}')

def norm(s):
    s = s.strip()
    # 去空白 + 去标点：只保留 CJK、汉字部首区、字母数字
    return re.sub(r'[^\w㐀-鿿豈-﫿]+', '', s)

# ---------- 机数 ----------
nospace = len(re.sub(r'\s', '', raw))
def cnum(n):
    digits = '零一二三四五六七八九'
    units = [(10**8, '亿'), (10**4, '万'), (1000, '千'), (100, '百'), (10, '十')]
    if n == 0: return '零'
    out = ''
    for u, c in units:
        if n >= u:
            q, n = divmod(n, u)
            out += (cnum(q) if q > 9 or u >= 10**4 else digits[q] if q != 1 or u != 10 else '') + c
    if n or not out:
        out += digits[n] if n < 10 else cnum(n)
    return out
chk('机数', cnum(nospace) in html, f'去空白 {nospace} = {cnum(nospace)} 应出现于页面')

# ---------- 引文：库本侧 + 页面全文本侧 ----------
libnorm = norm(raw)
pagetext = re.sub(r'<style.*?</style>', '', html, flags=re.S)
pagetext = re.sub(r'<[^>]+>', '', pagetext)
pagenorm = norm(pagetext)

for name, q in QUOTES:
    chk(f'库本含 {name}', norm(q) in libnorm, q[:24])
    chk(f'页面含 {name}', norm(q) in pagenorm, q[:24])

# ---------- 页面 <q> 反扫：每处引文须命中库本且属于清单 ----------
class QP(HTMLParser):
    def __init__(self):
        super().__init__()
        self.qdepth = 0
        self.buf = []
        self.found = []
    def handle_starttag(self, tag, attrs):
        if tag == 'q':
            self.qdepth += 1
            if self.qdepth == 1: self.buf = []
    def handle_endtag(self, tag):
        if tag == 'q' and self.qdepth:
            self.qdepth -= 1
            if self.qdepth == 0:
                self.found.append(''.join(self.buf))
    def handle_data(self, d):
        if self.qdepth: self.buf.append(d)

qp = QP()
qp.feed(html)
qnorms = [norm(q) for _, q in QUOTES]
for frag in qp.found:
    fn = norm(frag)
    ok = any(fn == qn or (fn and fn in qn) for qn in qnorms)
    chk('<q> 反扫', ok, frag[:30])

# ---------- 字面 「」 反扫 ----------
for m in re.findall(r'「([^」]*)」', pagetext):
    fn = norm(m)
    ok = any(fn == qn or (fn and fn in qn) for qn in qnorms)
    chk('「」 反扫', ok, m[:30])

# ---------- 排版红线 ----------
chk('禁长划线', '—' not in html and '–' not in html)
for i, line in enumerate(html.split('\n'), 1):
    n = line.count('·')
    chk(f'第{i}行·≤1', n <= 1, f'{n} 个')
chk('无外链资源', ('src=' not in html) and ('<link' not in html) and ('@import' not in html) and ('url(http' not in html))

# 正文区（样式之后、去标签后的可见文本）不允许成段英文
body_only = html.split('</style>', 1)[1]
body_text = re.sub(r'<[^>]+>', '', body_only)
eng = re.findall(r'[A-Za-z]{3,}', body_text)
bad = [w for w in eng if w.lower() not in ('github', 'https', 'daizhigev', 'robertsong', 'com')]
chk('正文区英文词', not bad, str(sorted(set(bad))[:10]))

# ---------- 页脚三要素 + 标题编号 ----------
chk('页脚来源', '文本来源' in html and 'daizhigev20' in html and '濒湖脉学' in html)
chk('页脚核验', '引文核验' in html and '逐字' in html)
chk('页脚提醒', '阅读提醒' in html and ('不构成现代医学建议' in html))
chk('标题编号', '一百九十二' in html and ('殆知阁导读之一百九十二' in html))
chk('库本段名', '四言举要' in html and '二十七' in html)
chk('引文计数自述', f'共{cnum(len(QUOTES))}条' in html, f'应含 共{cnum(len(QUOTES))}条')

# ---------- HTML 结构闭合 ----------
try:
    p = HTMLParser()
    p.feed(html)
except Exception as e:
    chk('HTML 可解析', False, str(e))

# ---------- mulu 编号连续性 + 本篇条目（--nomulu 跳过） ----------
if '--nomulu' not in sys.argv:
    nums = [int(n) for n in re.findall(r'<span class="no mono">(\d+)</span>', mulu)]
    chk('mulu 无重', len(nums) == len(set(nums)), str([n for n in set(nums) if nums.count(n) > 1]))
    maxn = max(nums)
    chk('mulu 无缺', sorted(set(nums)) == list(range(1, maxn + 1)), str([i for i in range(1, maxn + 1) if i not in nums]))
    chk('mulu 含本篇', 'href="binhu-maixue.html"' in mulu and f'<span class="no mono">{maxn}</span>' in mulu)
    chk('mulu 页脚计数', cnum(len(nums)) + '篇导读' in mulu.replace(' ', ''), f'条目 {len(nums)}')

print(f'机数：库本去空白 {nospace} 字（{cnum(nospace)}）；引文 {len(QUOTES)} 条；<q> 块 {len(qp.found)} 处')
if fails:
    print(f'FAIL {len(fails)}')
    for f in fails[:40]: print(' ', f)
    sys.exit(1)
print('ALL PASS')
