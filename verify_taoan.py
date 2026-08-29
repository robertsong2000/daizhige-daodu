#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_taoan.py — 陶庵梦忆页核验：引文逐字比对 + 排版红线 + 机算计数"""
import re, sys, unicodedata

LIB = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/陶庵梦忆.txt'
HTML = '/home/robertsong/workspace/claude/daizhige-daodu/taoan-mengyi.html'

lib = open(LIB, encoding='utf-8').read()
html = open(HTML, encoding='utf-8').read()

def norm(s: str) -> str:
    out = []
    for ch in s:
        o = ord(ch)
        if 0x4e00 <= o <= 0x9fff or 0x3400 <= o <= 0x4dbf or 0x20000 <= o <= 0x2ffff:
            out.append(ch)
    return ''.join(out)

nlib = norm(lib)
errs, oks = [], 0

# ---------- 1. 引文逐字比对 ----------
quotes = re.findall(r'<([a-zA-Z]+)[^>]*\bclass="[^"]*\bq\b[^"]*"[^>]*>(.*?)</\1>', html, re.S)
qtexts = []
for tag, inner in quotes:
    inner = re.sub(r'<small[^>]*>.*?</small>', '', inner, flags=re.S)
    txt = re.sub(r'<[^>]+>', '', inner)
    txt = txt.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
    if norm(txt):
        qtexts.append((txt, norm(txt)))
print(f'页面 .q 引文/片段共 {len(qtexts)} 处')
for raw, nq in qtexts:
    if nq in nlib:
        oks += 1
    else:
        errs.append(f'引文不在库内: {raw[:60]}...')

# ---------- 2. 排版红线（按渲染行近似：标签换行拆行） ----------
if '—' in html: errs.append('出现长划线 —')
if '–' in html: errs.append('出现短划线 –')
rendered = re.sub(r'<[^>]+>', '\n', html)
for i, ln in enumerate(rendered.split('\n'), 1):
    if ln.count('·') > 1:
        errs.append(f'渲染第{i}行 · 超过1个: {ln.strip()[:40]}')
        break

# ---------- 3. 机算计数 ----------
# 3.1 目录结构
i_dir = lib.find('目录')
i_body_ta = lib.find('台静农序', lib.find('琅嬛福地', i_dir) + 10)  # 目录区卷八之末紧接的序题/正文
toc = lib[i_dir:i_body_ta]
secs = re.split(r'卷[一二三四五六七八]', toc)
per = []
for s in secs[1:9]:
    titles = [x.strip('　 \n') for x in s.strip().split('\n') if x.strip('　 \n')]
    per.append(len(titles))
if per != [14, 15, 16, 15, 16, 16, 17, 13]:
    errs.append(f'目录各卷篇数机算不符: {per}')
front = [x.strip('　 \n') for x in secs[0].strip().split('\n') if x.strip('　 \n') and x.strip('　 \n') != '目录']
if front != ['台静农序', '自序']:
    errs.append(f'目录卷前序目机算不符: {front}')
if '葑门荷宕' in toc: errs.append('目录区不应含葑门荷宕')
if lib.count('葑门荷宕') != 1: errs.append(f'葑门荷宕正文出现次数={lib.count("葑门荷宕")} 应为1')
if '14、15、16、15、16、16、17、13' not in html: errs.append('页面缺目录各卷篇数串')
if '一百二十三' not in html or '一百二十二' not in html: errs.append('页面缺123/122篇数表述')

# 3.2 湖心亭看雪字数
a = lib.find('崇祯五年十二月'); b = lib.find('更有痴似相公者', a)
seg = lib[a:b + len('更有痴似相公者')]
cnt = sum(1 for c in seg if 0x4e00 <= ord(c) <= 0x9fff)
if cnt != 160: errs.append(f'湖心亭看雪汉字数机算={cnt} 应为160')
if '一百六十字' not in html: errs.append('页面未标湖心亭看雪一百六十字')

# 3.3 五类看月
i7 = lib.find('西湖七月半', lib.find('西湖七月半', lib.find('西湖七月半') + 1) + 1)
seg7 = lib[i7:lib.find('及时雨', i7)]
if seg7.count('其一，') != 5: errs.append(f'西湖七月半 其一,机算={seg7.count("其一，")} 应为5')
five = re.findall(r'<span class="no">其([一二三四五])</span>', html)
if five != ['一', '二', '三', '四', '五']: errs.append(f'页面五席序号异常: {five}')

# 3.4 果报七笔
chou = ['仇簪履也', '仇轻暖也', '仇甘旨也', '仇温柔也', '仇爽垲也', '仇香艳也', '仇舆从也']
for c in chou:
    if c not in lib: errs.append(f'库内缺 {c}')
    if c not in html: errs.append(f'页面缺 {c}')
if len(re.findall(r'<span class="chou q">', html)) != 7: errs.append('果报行数不足7')

# 3.5 五癖
pi = ['书画癖', '蹴鞠癖', '鼓钹癖', '鬼戏癖', '梨园癖']
chip = re.findall(r'<span class="q(?: zhu)?">(财)?(书画癖|蹴鞠癖|鼓钹癖|鬼戏癖|梨园癖)</span>', html)
if len(chip) != 5: errs.append(f'五癖 chips 机算={len(chip)} 应为5')
for p in pi:
    if p not in lib: errs.append(f'库内缺 {p}')

# 3.6 蟹会菜单
menu_names = ['蟹', '肥腊鸭', '牛乳酪', '醉蚶如琥珀', '鸭汁煮白菜如玉版', '谢橘', '风栗',
              '风菱', '玉壶冰', '兵坑笋', '新余杭白', '兰雪茶']
all_q = ' '.join(nq for _, nq in qtexts)
for nm in menu_names:
    if norm(nm) not in all_q: errs.append(f'菜单缺品: {nm}')
    if norm(nm) not in nlib: errs.append(f'库内缺品: {nm}')
if len(menu_names) - 1 != 11: errs.append('蟹外品数应为11')
if '惭愧惭愧' not in lib: errs.append('库内缺惭愧惭愧')
if '人六只' not in lib: errs.append('库内缺人六只')

# 3.7 序引与自序异文两形俱在
for s in ['骇骇为野人', '駴駴为野人', '尚视息人间', '尚视息人世']:
    if s not in lib: errs.append(f'库内缺 {s}')

# 3.8 全帙字符数
if len(lib) != 45113: errs.append(f'库文件字符数={len(lib)} 与页脚45113不符')
if '45113' not in html: errs.append('页脚缺45113')

# ---------- 汇总 ----------
print(f'引文核验通过 {oks}/{len(qtexts)}')
if errs:
    print('\n== 失败 ==')
    for e in errs: print(' -', e)
    sys.exit(1)
print('排版红线(—/–/·)全过')
print('机算计数(目录122+序目2/各卷14,15,16,15,16,16,17,13/葑门荷宕粘连/160字/五席/七笔/五癖/菜单12名/45113)全过')
print('VERIFY OK')
