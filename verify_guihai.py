import re, html, sys

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/guihai-yuheng-zhi.html'
BOOK = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/地理/桂海虞衡志.txt'

def cjk(s):
    return ''.join(ch for ch in s if '一' <= ch <= '鿿')

book_c = cjk(open(BOOK, encoding='utf-8').read())

raw = html.unescape(open(PAGE, encoding='utf-8').read())

# 1) 全部「」引文逐字核验（先剥标签再提取）
plain = re.sub(r'<[^>]+>', '', raw)
quotes = re.findall(r'「([^」]+)」', plain)
fails = 0
for q in quotes:
    qc = cjk(q)
    if qc not in book_c:
        fails += 1
        print('FAIL:', q)
print(f'引文核验: {len(quotes)} 条, 通过 {len(quotes)-fails}, 失败 {fails}')

# 2) 长划线禁用
for name, pat in [('em-dash —', '—'), ('en-dash –', '–'), ('horizontal bar ―', '―')]:
    n = raw.count(pat)
    if n:
        print(f'{name}: {n} 处 (禁用)')

# 3) 每行 · 至多 1 个
bad_lines = 0
for i, line in enumerate(plain.splitlines(), 1):
    if line.count('·') + line.count('・') > 1:
        bad_lines += 1
        print(f'第{i}行 · 超限: {line.strip()[:60]}')

ok = fails == 0 and raw.count('—') == 0 and raw.count('–') == 0 and raw.count('―') == 0 and bad_lines == 0
print('RESULT:', 'PASS' if ok else 'FAIL')
sys.exit(0 if ok else 1)
