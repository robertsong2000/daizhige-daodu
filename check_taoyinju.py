import re, sys, html as ihtml

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/huayang-taoyinjuji.html'
SRC = '/home/robertsong/workspace/claude/daizhige-simplified/道藏/正统道藏太玄部/华阳陶隐居集.txt'

def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if (0x3400 <= o <= 0x9FFF) or (0xF900 <= o <= 0xFAFF) or (0x20000 <= o <= 0x3FFFF):
            out.append(ch)
    return ''.join(out)

nsrc = norm(open(SRC, encoding='utf-8').read())

raw = open(PAGE, encoding='utf-8').read()
page = re.sub(r'<script\b.*?</script>', '', raw, flags=re.S)
page = re.sub(r'<style\b.*?</style>', '', page, flags=re.S)

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
        print(f'Q{i:02d} OK   ({len(nq)}字) {qt.strip()[:22]}')
    else:
        lo, hi = 0, len(nq)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if nq[:mid] in nsrc: lo = mid
            else: hi = mid - 1
        print(f'Q{i:02d} FAIL {qt.strip()[:70]}')
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
        k = 6
        while i + k < len(plain) and plain[i:i+k+1] in nsrc:
            k += 1
        hits.append((i, plain[i:i+k])); i += k
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

ok = fails == 0 and len(hits) == 0 and not bad
print('RESULT:', 'PASS' if ok else 'FAIL')
sys.exit(0 if ok else 1)
