#!/usr/bin/env python3
"""核验 maoyuan.html 引文与排版规则"""
import re, sys, unicodedata

HTML = '/home/robertsong/workspace/claude/daizhige-daodu/maoyuan.html'
SRC = '/home/robertsong/workspace/claude/daizhige-simplified/艺藏/草木鸟兽虫鱼/猫苑.txt'

VAR = {'貍': '狸', '啣': '衔', '一': '一'}

def norm(s):
    s = unicodedata.normalize('NFC', s)
    s = ''.join(VAR.get(c, c) for c in s)
    return ''.join(c for c in s if re.match(r'[㐀-鿿A-Za-z0-9]', c))

html = open(HTML, encoding='utf-8').read()
src = norm(open(SRC, encoding='utf-8').read())

frags = []
frags += [(m, '「」') for m in re.findall(r'「([^」]+)」', html)]
frags += [(m, 'i') for m in re.findall(r'<i>([^<]+)</i>', html)]
frags += [(m, 'b') for m in re.findall(r'<b>([^<]+)</b>', html)]
frags += [(m, 'why') for m in re.findall(r'<span class="why">([^<]+)</span>', html)]
frags += [(m, 'poem') for m in re.findall(r'<div class="poem">(.*?)</div>', html, re.S)]

OWN = {'附', '行情', '奇品', '灵异门一笔账', '同名物门可看的', '缘起', '卷中事',
       '九十五', '十二时辰', '111 处按语', '十三位供稿人', '一位日昌', '九十七'}

fails, ok = [], 0
for text, kind in frags:
    text = re.sub(r'<[^>]+>', '', text)
    if kind == 'b' and len(norm(text)) < 6:
        if text.strip() in OWN:
            continue
    if text.strip() in OWN:
        continue
    if norm(text) in src:
        ok += 1
    else:
        fails.append((kind, text.strip()[:60]))

print(f'引文核验：{ok} 条通过，{len(fails)} 条失败')
for kind, t in fails:
    print(f'  [{kind}] 未命中库本：{t}')

bad_dash = [i + 1 for i, line in enumerate(html.splitlines(), 1) if '—' in line or '–' in line]
bad_dot = [i + 1 for i, line in enumerate(html.splitlines(), 1) if line.count('·') > 1]
print(f'长划线：{"无" if not bad_dash else "有 行 " + ",".join(map(str, bad_dash))}')
print(f'每行·超1：{"无" if not bad_dot else "有 行 " + ",".join(map(str, bad_dot))}')

han = len(re.findall(r'[㐀-鿿]', open(SRC, encoding='utf-8').read()))
print(f'库本汉字数：{han}')

sys.exit(1 if fails or bad_dash or bad_dot else 0)
