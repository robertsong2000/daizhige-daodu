# -*- coding: utf-8 -*-
"""从 quotes_qiqi.json 注入原文，生成 qiqi-tushuo.html"""
import json, re, sys

tpl = open('daizhige-daodu/qiqi-tushuo.tpl.html', encoding='utf-8').read()
quotes = json.load(open('daizhige-daodu/quotes_qiqi.json', encoding='utf-8'))

used = set()
PUA = {'': '扬'}
def sub(m):
    key = m.group(1)
    if key not in quotes:
        print('缺引文键', key); sys.exit(1)
    used.add(key)
    v = quotes[key]
    for a, b in PUA.items():
        v = v.replace(a, b)
    return v

out = re.sub(r'⟦q:([a-z_0-9]+)⟧', sub, tpl)
left = re.findall(r'⟦[^⟧]*⟧', out)
if left:
    print('残留占位符', left); sys.exit(1)
unused = set(quotes) - used
if unused:
    print('未使用的引文', unused); sys.exit(1)
open('daizhige-daodu/qiqi-tushuo.html', 'w', encoding='utf-8').write(out)
print('构建完成', len(out), '字符，引文', len(used), '段全部注入')
