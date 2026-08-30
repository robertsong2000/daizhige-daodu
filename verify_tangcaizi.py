#!/usr/bin/env python3
"""核验 tang-caizi-zhuan.html 引文与排版规则"""
import re, sys, unicodedata

HTML = '/home/robertsong/workspace/claude/daizhige-daodu/tang-caizi-zhuan.html'
SRC = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/传记/唐才子传.txt'

def norm(s):
    s = unicodedata.normalize('NFC', s)
    return ''.join(c for c in s if re.match(r'[㐀-鿿A-Za-z0-9]', c))

html = open(HTML, encoding='utf-8').read()
src = norm(open(SRC, encoding='utf-8').read())

frags = [(m, 'q') for m in re.findall(r'「([^」]+)」', html)]
frags += [(m, 'b') for m in re.findall(r'<b>([^<]+)</b>', html)]

OWN = {'八位', '两百', '二百七十九个条目标目', '除之', '存之', '一', '无',
       '枫落吴江冷', '第一唱', '第二唱', '第三唱'}
fails, ok = [], 0
for text, kind in frags:
    text = re.sub(r'<[^>]+>', '', text).strip()
    if text in OWN:
        continue
    if norm(text) in src:
        ok += 1
    else:
        fails.append((kind, text[:70]))

print(f'引文核验：{ok} 条通过，{len(fails)} 条失败')
for kind, t in fails:
    print(f'  [{kind}] 未命中库本：{t}')

pua = [c for c in html if '' <= c <= '']
print(f'页面私有区字符：{len(pua)} 个')

bad_dash = [i + 1 for i, line in enumerate(html.splitlines(), 1) if '—' in line or '–' in line]
bad_dot = [i + 1 for i, line in enumerate(html.splitlines(), 1) if line.count('·') > 1]
print(f'长划线：{"无" if not bad_dash else "有 行 " + ",".join(map(str, bad_dash))}')
print(f'每行·超1：{"无" if not bad_dot else "有 行 " + ",".join(map(str, bad_dot))}')

han = len(re.findall(r'[㐀-鿿]', open(SRC, encoding='utf-8').read()))
print(f'库本汉字数：{han}')

sys.exit(1 if fails or bad_dash or bad_dot or pua else 0)
