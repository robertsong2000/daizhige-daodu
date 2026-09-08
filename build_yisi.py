#!/usr/bin/env python3
"""build_yisi.py — 从库本切分《抱残守缺斋乙巳日记》296则,分类打标,注入模板生成 yisi-riji.html"""
import re, json, sys

LIB = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/抱残守缺斋乙巳日记.txt'
TPL = '/home/robertsong/workspace/claude/daizhige-daodu/yisi-riji.tpl.html'
OUT = '/home/robertsong/workspace/claude/daizhige-daodu/yisi-riji.html'
MONTHS = ['正月','二月','三月','四月','五月','六月','七月','八月','九月','十月']

raw = open(LIB, encoding='utf-8').read()
lines = raw.split('\n')

entries, cur_m, i = [], None, 0
day_head = re.compile(r'^(元旦|[初一二三四五六七八九十]{1,4}日?)（(?:\d+年)?(\d+)月(\d+)日）\s*(.*)$')
while i < len(lines):
    L = lines[i].strip()
    if L in MONTHS:
        cur_m = L
    else:
        m = day_head.match(L)
        if m and cur_m:
            txt, j = [], i + 1
            while j < len(lines):
                t = lines[j].strip()
                if day_head.match(t) or t in MONTHS:
                    break
                if t and (t.startswith('①') or t.startswith('②') or t.startswith('（《')):
                    break
                if t:
                    txt.append(t)
                j += 1
            entries.append({'m': cur_m, 'd': m.group(1), 'gm': int(m.group(2)),
                            'gd': int(m.group(3)), 'wx': m.group(4).strip(),
                            't': '\n'.join(txt)})
            i = j
            continue
    i += 1

assert len(entries) == 296, f'条数 {len(entries)} != 296'
assert sum(1 for e in entries if '临《' in e['t']) == 77
assert sum(1 for e in entries if re.search(r'买|购', e['t'])) == 42
assert sum(1 for e in entries if '老残游记' in e['t']) == 5

SANG = re.compile(r'大哥去矣|成殓|出殡|开吊|辞灵|题主|冥寿|斋戒|哀启|哭之|易衣服')
XING = re.compile(r'开船|上船|启碇|车栈|火车|里至|，宿|到金陵|到杭州')
FEAST = re.compile(r'之约|请吃|宴于|家酒|听戏|落子|碰和|打摊')
DOTS = [('老残游记', '撰老残'), ('龟骨', '殷墟龟骨'), ('突发炸弹', '正阳门炸弹'),
        ('炸弹所伤之车', '验炸弹车'), ('黑眚', '黑眚凶象'), ('大哥去矣', '大哥卒'),
        ('昌寿里火', '昌寿里火'), ('日本海军大胜', '对马海战'), ('俄舰第二队沉六只', '对马海战'),
        ('予初度', '初度'), ('第二孙也', '添孙'), ('第一孙也', '添孙'),
        ('天长节', '天长节'), ('盐务为国家专利', '盐务批驳'), ('竟成谶语', '谶联'),
        ('太谷夫子', '太谷印书')]

for e in entries:
    t = e['t']
    if SANG.search(t):
        e['cat'] = 'sang'
    elif XING.search(t):
        e['cat'] = 'xing'
    elif '临《' in t:
        e['cat'] = 'lin'
    elif re.search(r'买|购', t):
        e['cat'] = 'buy'
    elif FEAST.search(t):
        e['cat'] = 'feast'
    else:
        e['cat'] = 'none'
    e['tags'] = [lab for pat, lab in DOTS if pat in t]
    e['dot'] = 1 if e['tags'] else 0
    e['tw'] = 1 if (e['m'] == '四月' and e['d'] == '十三日') else 0
    e['tornAfter'] = 1 if (e['m'] == '四月' and e['d'] == '二十八日') else 0

tw = [e for e in entries if e['tw']]
assert len(tw) == 1 and tw[0]['gm'] == 5 and tw[0]['gd'] == 15
ta = [e for e in entries if e['tornAfter']]
assert len(ta) == 1 and ta[0]['gm'] == 5 and ta[0]['gd'] == 30

html = open(TPL, encoding='utf-8').read()
assert '__YDATA__' in html
html = html.replace('__YDATA__', json.dumps(entries, ensure_ascii=False))
open(OUT, 'w', encoding='utf-8').write(html)
print('OK 296则 →', OUT, len(html), 'bytes')
