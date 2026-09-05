# -*- coding: utf-8 -*-
"""那先比丘经 导读页核验：引文保标点严格比对（仅删空白+PUA/□双删）+ 排版红线"""
import re, sys

HTML = '/home/robertsong/workspace/claude/daizhige-daodu/naxian-biqiu-jing.html'
SRC = '/home/robertsong/workspace/claude/daizhige-simplified/佛藏/大藏经/论藏/论集部/那先比丘经--.txt'

PUA = re.compile('[%s-%s]' % (chr(0xe000), chr(0xf8ff)))

def norm(s):
    s = re.sub(r'\s+', '', s)
    s = PUA.sub('', s)
    s = s.replace('□', '')
    return s

html = open(HTML, encoding='utf-8').read()
src = open(SRC, encoding='utf-8', errors='ignore').read()
src_n = norm(src)

body = re.sub(r'<script.*?</script>', '', html, flags=re.S)
body = re.sub(r'<style.*?</style>', '', body, flags=re.S)

quotes = re.findall(r'([^「])「([^」]+)」', body)
qlist = [q[1] for q in quotes]
fails = []
for i, q in enumerate(qlist, 1):
    qn = norm(q)
    if qn not in src_n:
        fails.append((i, q[:40]))

print('引文总数:', len(qlist))
if fails:
    print('未过引文:')
    for i, q in fails:
        print(' %d: %s' % (i, q))
else:
    print('引文核验: 全过')

text = re.sub(r'<br\s*/?>', '\n', body)
text = re.sub(r'</(p|div|h2|h3|span|section|footer|header|main)>', '\n', text)
text = re.sub(r'<[^>]+>', '', text)
lines = [l.strip() for l in text.split('\n') if l.strip()]

bad_dash = [l for l in lines if ('—' in l or '–' in l)]
bad_dot = [l for l in lines if l.count('·') > 1]
print('长划线行:', len(bad_dash))
for l in bad_dash:
    print('  ', l[:60])
print('多·行(>1):', len(bad_dot))
for l in bad_dot:
    print('  ', l[:60])

need = ['文本来源', '引文核验', '时代局限', 'github.com/robertsong2000/daizhigev20']
missing = [k for k in need if k not in body]
print('页脚三要素+仓库链接:', '全在' if not missing else '缺 %s' % missing)

# 引文防重：同一段引文不得重复出现（防复制粘贴凑数）
dups = set(q for q in qlist if qlist.count(q) > 1)
print('重复引文:', len(dups) if dups else 0)

ok = not fails and not bad_dash and not bad_dot and not missing and not dups
print('RESULT:', 'PASS' if ok else 'FAIL')
sys.exit(0 if ok else 1)
