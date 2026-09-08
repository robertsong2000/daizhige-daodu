import re
import sys
import unicodedata

HTML = 'xie-duo.html'
LIB = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/谐铎.txt'

def norm(s):
    s = unicodedata.normalize('NFKC', s)
    return ''.join(ch for ch in s if '㐀' <= ch <= '鿿')

html = open(HTML, encoding='utf-8').read()
quotes = re.findall(r'class="q"[^>]*>([^<]+)<', html)
lib = norm(open(LIB, encoding='utf-8').read())

bad = 0
seen = set()
for q in quotes:
    nq = norm(q)
    if nq in seen:
        continue
    seen.add(nq)
    if nq not in lib:
        bad += 1
        print(f'FAIL [{len(nq)}字] {q[:50]}')
print(f'{len(quotes)} 处引文（去重 {len(seen)}），未通过 {bad}')
sys.exit(1 if bad else 0)
