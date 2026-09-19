#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build caigentan.html: slice quotes from library file into tpl tokens."""
import re, sys

SRC = '/home/robertsong/workspace/claude/daizhige-simplified/儒藏/修身治家/菜根谭.txt'
TPL = '/home/robertsong/workspace/claude/daizhige-daodu/caigentan.tpl.html'
OUT = '/home/robertsong/workspace/claude/daizhige-daodu/caigentan.html'

src = open(SRC, encoding='utf-8').read()

# name: (start_anchor, end_anchor)  -> slice src[start : find(end)+len(end)]
QUOTES = {
    'shi1':  ('余过古刹', '一录。'),
    'shi2':  ('翻视之，虽属禅宗', '相发明者。'),
    'shi5':  ('亟携归', '缮写成帙。'),
    'shi3':  ('旧有序，文不雅驯', '何许人也。'),
    'shi4':  ('乾隆五十九年二月二日', '遂初堂主人识'),
    'chew1': ('𬪩肥辛甘非真味', '真味只是淡'),
    'chew2': ('神奇卓异非至人', '至人只是常。'),
    'chew3': ('向三时饮食中', '方为切实工夫。'),
    'chew4': ('趋炎附势之祸', '最淡亦最长。'),
    'die1':  ('欲做精金美玉的人品', '须向薄冰上履过。'),
    'die2':  ('处世让一步为高', '利人实利己的根基。'),
    'die3':  ('不责人小过', '三者可以养德，亦可以远害。'),
    'die4':  ('从静中观物动', '处闹中能取静'),
    'zhu1':  ('一念错，便觉百行皆非', '勿容一针之罅漏'),
    'zhu2':  ('昨日之非不可留', '尘情终累乎理趣'),
    'zhu3':  ('宠辱不惊', '支卷云舒。'),
    'zhu4':  ('天地有万古', '此日最易过。'),
    'zhu5':  ('荣宠旁边辱等待', '何须戚戚。'),
    'zhu6':  ('天地不可一日无和气', '人心不可一日无喜神。'),
    'zhu7':  ('炎凉之态', '骨肉尤狠于外人。'),
    'zhu8':  ('完名美节', '韬光养德。'),
    'ren1':  ('为鼠常留饭', '一点生生之机'),
    'ren2':  ('世态有炎凉', '而我无欣厌。'),
    'coda1a': ('幸生其间者', '有生之乐，'),
    'coda1b': ('亦不可不怀', '虚生之忧。'),
    'coda2a': ('遍阅人情', '疏狂之足贵；'),
    'coda2b': ('备尝世味', '淡泊之为真。'),
    'coda3': ('究不知其为何许人也', '究不知其为何许人也'),
}

slabs = {}
for name, (a, b) in QUOTES.items():
    ia = src.find(a)
    assert ia >= 0, f'start anchor missing: {name} {a}'
    ib = src.find(b, ia)
    assert ib >= 0, f'end anchor missing: {name} {b}'
    slabs[name] = src[ia:ib + len(b)]
    print(f'{name}: {len(slabs[name])}字  {slabs[name][:24]}…')

# door counts assertion
secs = [(m.group(1).strip(), m.start()) for m in re.finditer(r'●(.+)', src)]
assert [s[0] for s in secs] == ['修身', '应酬', '评议', '闲适'], secs
bounds = [s[1] for s in secs] + [len(src)]
cnt = [len([l for l in src[bounds[i]:bounds[i+1]].split('\n')
            if l.strip() and not l.strip().startswith('●')]) for i in range(4)]
assert cnt == [30, 46, 44, 238], cnt
print('door lines:', cnt, 'total', sum(cnt))

html = open(TPL, encoding='utf-8').read()
for name, t in slabs.items():
    tok = f'⟦{name}⟧'
    assert tok in html, f'token missing in tpl: {name}'
    html = html.replace(tok, t)
assert '⟦' not in html, 'unreplaced tokens remain'
open(OUT, 'w', encoding='utf-8').write(html)
print('written', OUT, len(html), 'bytes')
