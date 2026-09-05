#!/usr/bin/env python3
"""核验 zibuyu.html 引文与排版规则"""
import re, sys, unicodedata

HTML = '/home/robertsong/workspace/claude/daizhige-daodu/zibuyu.html'
SRC = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/子不语.txt'

VAR = {'貍': '狸', '歎': '叹', '耶': '耶'}

def norm(s):
    s = unicodedata.normalize('NFC', s)
    s = ''.join(VAR.get(c, c) for c in s)
    return ''.join(c for c in s if re.match(r'[㐀-鿿A-Za-z0-9]', c))

html = open(HTML, encoding='utf-8').read()
body = re.sub(r'<script[\s\S]*?</script>', '', html)  # JS 文案单测
src = norm(open(SRC, encoding='utf-8').read())

frags = []
# 1) <q> 标记内的全部文字
frags += [(m, 'q') for m in re.findall(r'<q>([\s\S]*?)</q>', html)]
# 2) 「」直引内容（含 q 内嵌套）
frags += [(m, '「」') for m in re.findall(r'「([^」]+)」', html)]
# 3) JS 中引号文案
js = '\n'.join(re.findall(r'<script>([\s\S]*?)</script>', html))
frags += [(m, 'js') for m in re.findall(r"'([^']{6,})'", js) if re.search(r'[一-鿿]', m)]

bad = 0
for q, kind in frags:
    qc = norm(q)
    if not qc:
        continue
    in_page = qc in norm(body) or qc in norm(js) or kind == 'q'
    in_book = qc in src
    if not in_book:
        bad += 1
        print(f'[BOOK-FAIL/{kind}] {q[:60]}')
        print(f'   -> norm: {qc[:70]}')
    elif kind != 'q' and qc not in norm(body) and qc not in norm(js):
        pass  # 嵌套片段必然在页面内
    if kind == 'q' and qc not in norm(body):
        bad += 1
        print(f'[PAGE-FAIL/q] {q[:60]}')

# 排版红线：长划线、半字线、每行 · 至多 1 个
for pat, label in [(r'—', '长划线—'), (r'–', '半字线–'), (r'――', '双线')]:
    if re.search(pat, html):
        bad += 1
        print(f'[LAYOUT-FAIL] 发现{label}')
for i, line in enumerate(html.split('\n'), 1):
    if line.count('·') > 1:
        bad += 1
        print(f'[LAYOUT-FAIL] 第{i}行 · 超限: {line.strip()[:60]}')

# 页脚三要素
for kw in ['殆知阁', '核验', '时代局限']:
    if kw not in html:
        bad += 1
        print(f'[FOOTER-FAIL] 缺 {kw}')

print('---')
print('引文片段数:', len([1 for _ in frags]))
print('FAIL:', bad)
sys.exit(1 if bad else 0)
