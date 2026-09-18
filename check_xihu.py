import re, sys, unicodedata
from html.parser import HTMLParser

PAGE = 'daizhige-daodu/xihu-mengxun.html'
LIB = 'daizhige-simplified/集藏/四库别集/西湖梦寻.txt'

lib = open(LIB, encoding='utf-8').read()

PUNCT = set('，。、；：？！「」『』“”‘’（）《》〈〉…—－–·〇【】〔〕［］{}[]()<>《》“”‘’ \t\r\n　　,.!?;:"\'`~@#$%^&*_+=|\\/')

def norm(s):
    out = []
    for ch in s:
        if ch in PUNCT or ch.isspace():
            continue
        out.append(ch)
    return ''.join(out)

NLIB = norm(lib)
W = 6

class Ex(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []       # (tag, classes)
        self.quotes = []      # (id_or_src, text)
        self.prose = []       # (where, text)
        self.qid = 0
    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get('class', '') or ''
        self.stack.append((tag, cls))
        if tag in ('q',) or ('q' in cls.split() or 'qv' in cls.split()):
            self.qid += 1
            self.stack[-1] = (tag, cls, 'Q%d' % self.qid)
    def handle_startendtag(self, tag, attrs):
        pass
    def handle_endtag(self, tag):
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()
        else:
            for i in range(len(self.stack)-1, -1, -1):
                if self.stack[i][0] == tag:
                    del self.stack[i:]
                    break
    def handle_data(self, data):
        if not data.strip():
            return
        inq = any(len(t) > 2 and t[2].startswith('Q') for t in self.stack)
        tags = [t[0] for t in self.stack]
        cls = ' '.join(t[1] for t in self.stack)
        if 'script' in tags or 'style' in tags:
            return
        if inq:
            self.quotes.append((self.stack[-1][2], data))
        else:
            self.prose.append((cls or tags[-1] if tags else '?', data))

p = Ex()
p.feed(open(PAGE, encoding='utf-8').read())

# 1) quote verification
fails = []
ok = 0
for qid, txt in p.quotes:
    n = norm(txt)
    if not n:
        continue
    if n in NLIB:
        ok += 1
    else:
        fails.append((qid, txt.strip()[:60]))
print('引文核验: %d 处通过, %d 处失败' % (ok, len(fails)))
for f in fails:
    print('  FAIL', f)

# 2) anti-scan on prose (6-char windows)
hits = []
for where, txt in p.prose:
    n = norm(txt)
    for i in range(0, max(0, len(n) - W + 1)):
        w = n[i:i+W]
        if w in NLIB:
            hits.append((where, w, txt.strip()[:40]))
print('反扫命中: %d' % len(hits))
seen = set()
for h in hits:
    k = (h[0], h[1])
    if k in seen: continue
    seen.add(k)
    print('  HIT', h)

# 3) middle-dot per rendered line (approx: split prose text nodes on newline, count ·)
bad = []
for where, txt in p.prose:
    for line in txt.split('\n'):
        if line.count('·') > 1:
            bad.append(line.strip()[:50])
print('行内·超标: %d' % len(bad))
for b in bad: print('  DOT', b)

# 4) forbidden dashes
raw = open(PAGE, encoding='utf-8').read()
for ch in ['—', '–']:
    if ch in raw:
        print('禁用划线出现:', repr(ch))
print('划线检查完成')

# 5) JS string leak check: quotes must not appear inside script
scripts = re.findall(r'<script.*?</script>', raw, re.S)
nq_all = [norm(t) for _, t in p.quotes]
leak = 0
for s in scripts:
    ns = norm(s)
    for n in nq_all:
        if len(n) >= W and n in ns:
            leak += 1
            print('  JS泄漏:', n[:30])
print('JS引文泄漏: %d' % leak)
