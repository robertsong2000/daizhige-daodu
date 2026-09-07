#!/usr/bin/env python3
"""清宫禁二年记 引文核验 + 排版规则检查"""
import re, sys, unicodedata

SRC = '../daizhige-simplified/史藏/志存记录/清宫禁二年记.txt'
HTML = 'qinggong-er-nian-ji.html'

def norm(s):
    s = unicodedata.normalize('NFKC', s)
    return ''.join(ch for ch in s if '一' <= ch <= '鿿')

src = open(SRC, encoding='utf-8').read()
nsrc = norm(src)
html = open(HTML, encoding='utf-8').read()

quotes = re.findall(r'<span class="v">(.*?)</span>', html, re.S) + \
         re.findall(r'<figure class="print">.*?<p>(.*?)</p>', html, re.S)

fails = 0
for q in quotes:
    nq = norm(q)
    if not nq:
        print('EMPTY QUOTE'); fails += 1; continue
    if nq not in nsrc:
        # 定位失败片段
        for i in range(0, len(nq), 10):
            if nq[i:i+10] not in nsrc:
                print('FAIL:', q[:30], '...', nq[i:i+10])
                break
        fails += 1
print(f'引文核验: {len(quotes)} 条, 失败 {fails}')

# 排版规则
rules = []
for bad, name in [('—', '长划线'), ('–', '短划线')]:
    if bad in html: rules.append(f'含{name}')
for ln, line in enumerate(html.split('\n'), 1):
    if line.count('·') > 1:
        rules.append(f'第{ln}行有{line.count("·")}个·')
for pat, name in [('src="http', '外链资源'), ('<link', '外部样式'),
                  ('@import', '外部样式'), ('<script src', '外部脚本')]:
    if pat in html: rules.append(f'含{name}')
if '标题数据条' not in html:
    pass
print('排版规则:', 'PASS' if not rules else rules)

sys.exit(1 if (fails or rules) else 0)
