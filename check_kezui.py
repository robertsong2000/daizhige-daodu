import re, sys, html as ihtml

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/kezui-zhuiyu.html'
SRC = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/客座赘语.txt'

PUA_MAP = {
    '\ue44f': '\u7440',   # 瑀 作者自称
    '\ue3d7': '\u7950',   # 祐 延祐
    '\ue44d': '\u798b',   # 禋 太禧宗禋院
    '\ue248': '\u5092',   # 傒 揭傒斯
    '\ue4c1': '',          # 夔 库本以PUA+夔两字重复编码，删PUA
}
PUNCT = re.compile('[\s　　-〿﹐-﹫！-～ -⁃「」『』“”‘’…·《》〈〉【】〔〕（）○●□]+')

def norm(s):
    for k, v in PUA_MAP.items():
        s = s.replace(k, v)
    s = ihtml.unescape(s)
    s = PUNCT.sub('', s)
    return s

src = open(SRC, encoding='utf-8').read()
nsrc = norm(src)

raw = open(PAGE, encoding='utf-8').read()
page = re.sub(r'<script\b.*?</script>', '', raw, flags=re.S)
page = re.sub(r'<style\b.*?</style>', '', page, flags=re.S)

# stack-aware split into q / non-q text spans
depth = 0
pos = 0
spans = []
token = re.compile(r'<(/?)(q)\b[^>]*>', re.I)
for m in token.finditer(page):
    spans.append((pos, m.start(), depth))
    pos = m.end()
    depth += -1 if m.group(1) else 1
    if depth < 0:
        print('FATAL: q close without open'); sys.exit(1)
spans.append((pos, len(page), depth))

qtexts, plain_parts = [], []
for (a, b, d) in spans:
    seg = re.sub(r'<[^>]+>', '', page[a:b])
    if d > 0:
        m = re.search(r'<span class="src">(.*?)</span>', page[a:b], re.S)
        if m:
            seg = re.sub(r'<span class="src">.*?</span>', '', page[a:b], flags=re.S)
            seg = re.sub(r'<[^>]+>', '', seg)
            plain_parts.append(re.sub(r'<[^>]+>', '', m.group(1)))
        qtexts.append(seg)
    else:
        plain_parts.append(seg)

print('=== 引文核对 ===')
fails = 0
for i, qt in enumerate(qtexts, 1):
    nq = norm(qt)
    if not nq:
        print(f'Q{i:02d} EMPTY'); fails += 1; continue
    if nq in nsrc:
        print(f'Q{i:02d} OK   ({len(nq)}字) {qt[:22]}...')
    else:
        lo, hi = 0, len(nq)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if nq[:mid] in nsrc: lo = mid
            else: hi = mid - 1
        print(f'Q{i:02d} FAIL {qt[:70]}')
        print(f'      最长前缀 {lo} 字: …{nq[max(0, lo-10):lo]}【{nq[lo:lo+12]}】…')
        fails += 1
print(f'引文 {len(qtexts)} 条, 通过 {len(qtexts)-fails}, 失败 {fails}')

print('=== 白话反扫（六字窗） ===')
plain = norm(''.join(plain_parts))
hits = []
i = 0
while i + 6 <= len(plain):
    w = plain[i:i+6]
    if w in nsrc:
        hits.append((i, w)); i += 6
    else:
        i += 1
if hits:
    for i, w in hits[:50]:
        print(f'撞窗 @plain[{i}]: {plain[max(0,i-14):i]}【{w}】{plain[i+6:i+16]}')
    print(f'反扫撞窗 {len(hits)} 处')
else:
    print('白话反扫零撞窗')

print('=== 排版规则 ===')
vis = ihtml.unescape(re.sub(r'<[^>]+>', '', page))
bad = False
for ch, name in [('—', '长划线—'), ('–', '短划线–'), ('‒', '划线')]:
    n = vis.count(ch)
    if n:
        print(f'发现 {name} ×{n}'); bad = True
for lineno, line in enumerate(vis.split('\n'), 1):
    if line.count('·') > 1:
        print(f'行{lineno} ·×{line.count("·")}: {line.strip()[:80]}'); bad = True
if not bad:
    print('长划线 0，每行·数合规')
