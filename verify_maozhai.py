#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""懋斋诗钞 导读页核验：引文逐字（库内+库外转引分检）、排版红线、机器计数、校记申报项"""
import re, sys, unicodedata, html

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/maozhai-shichao.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/集藏/四库别集/懋斋诗钞.txt'

def norm(s):
    s = html.unescape(s)
    s = re.sub(r'<[^>]+>', '', s)
    out = []
    for ch in s:
        if ch.isspace() or unicodedata.category(ch).startswith('P') or ch in '「」『』“”‘’·／':
            continue
        out.append(ch)
    return ''.join(out)

page_raw = open(PAGE, encoding='utf-8').read()
page_txt = norm(page_raw)
t_lib = open(LIB, encoding='utf-8').read()
fails = []

# ---------- 1. 库内引文：必须页内+库内双中 ----------
QUOTES = [
    '自山海归，谢客闭门，唯时时来往东皋间',
    '渔罾钓渚，时绘目前',
    '大约烟波渔艇之作居多',
    '芹圃曹君（沾）别来已一载余矣偶过明君（琳）养石轩隔院闻高谈声疑是曹君急就相访惊喜意外因呼酒话旧事感成长句',
    '可知野鹤在鸡群，隔院惊呼意倍殷。雅识我惭褚太傅，高谈君是孟叅军。秦淮旧梦人犹在，燕市悲歌酒易醺。忽漫相逢频把袂，年来聚散感浮云。',
    '傲骨如君世已竒，嶙峋更见此支离。醉余奋扫如椽茟，写出胸中磈礧时。',
    '碧水青山曲径遐，薜萝门巷足烟霞，寻诗人去留僧舍，卖画钱来付酒家。燕市哭歌悲遇合，秦淮风月忆繁华。新愁旧恨知多少，一醉酕醄白眼斜。',
    '野浦冻云深，柴扉晚烟薄。山村不见人，夕阳寒欲落。',
    '东风吹杏雨，又早落花辰。好枉故人驾，来看小院春。诗才忆曹植，酒盏愧陈遵。上已前三日，相劳醉碧茵。',
    '花明両岸桞霏微，到眼风光春欲归。逝水不留诗客杳，登楼空忆酒徒非。河干万木飘残雪，村落千家带逺晖。',
    '疑是曹君',
    '急就相访',
    '典裘为春服',
    '凭吊应怜诗客杳，王园园畔问东皋。',
    '清明东郊（已下己夘）',
    '古刹小憇（癸未）',
    '谒三忠祠（诸葛武矦　岳武穆　文信国）',
    '上已前三日，相劳醉碧茵',
    '癸未夏，长日如年',
    '丁丑榆闗除夕',
    '秋夜偶思丁丑岁客居锦州天桥厂',
    '先慈自丁丑见弃迄今七载',
]
for q in QUOTES:
    n = norm(q)
    in_lib = n in norm(t_lib)
    in_pg = n in page_txt
    if not (in_lib and in_pg):
        fails.append(f'库内引文 库内={in_lib} 页内={in_pg} :: {q[:38]}')

# ---------- 2. 库外转引：页内必须逐字在，且标注转引 ----------
EXTERNAL = [
    ('壬午除夕，书未成，芹为泪尽而逝。', '甲戌本眉批'),
]
for q, tag in EXTERNAL:
    if norm(q) not in page_txt:
        fails.append(f'库外转引缺页内 :: {q[:30]}')
    if '转引' not in page_raw:
        fails.append('库外转引未标注「转引」')

# ---------- 3. 排版红线 ----------
if '—' in page_raw or '–' in page_raw:
    fails.append('页面出现长划线 — 或 –')
for i, line in enumerate(page_raw.splitlines(), 1):
    c = line.count('·')
    if c > 1:
        fails.append(f'第{i}行 · 出现 {c} 次（上限 1）:: {line.strip()[:40]}')

# ---------- 4. 库内机器计数（页面声称值 vs 实测） ----------
expect = {
    'len(t)': (len(t_lib), 16585),
    '雪芹': (t_lib.count('雪芹'), 3),
    '芹圃': (t_lib.count('芹圃'), 3),
    '曹君': (t_lib.count('曹君'), 2),
    '敬亭': (t_lib.count('敬亭'), 60),
    '贻谋': (t_lib.count('贻谋'), 16),
}
for k, (got, want) in expect.items():
    if got != want:
        fails.append(f'计数不符 {k}: 页面称 {want}, 实测 {got}')
for absent in ('壬午', '庚辰', '辛巳'):
    if absent in t_lib:
        fails.append(f'卷内意外出现纪年 {absent}（页面称四年无纪年）')

# 涉曹诗恰 6 首：按诗题行统计
lines = t_lib.splitlines()
caoping = [l.strip() for l in lines if l.strip().startswith(('芹圃曹君', '题芹圃画石', '赠芹圃', '访曹雪芹不值', '小诗代简寄曹雪芹', '河干集饮题壁兼吊雪芹'))]
if len(caoping) != 6:
    fails.append(f'涉曹诗实测 {len(caoping)} 首，页面称 6 首')
# 小诗代简须为「癸未」标记后第 3 首
try:
    i_mark = next(i for i, l in enumerate(lines) if l.strip().startswith('古刹小憇'))
    i_inv = next(i for i, l in enumerate(lines) if l.strip().startswith('小诗代简寄曹雪芹'))
    between = [l for l in lines[i_mark + 1:i_inv] if l.startswith('　　') and l.strip() and not l.startswith('　　　')]
    if len(between) + 1 != 3:
        fails.append(f'癸未标记后第 {len(between) + 1} 首，页面称第三首')
except StopIteration:
    fails.append('库内找不到 古刹小憇 / 小诗代简 锚点')

# ---------- 5. 页面结构件 ----------
for need in ('之五十', '卷二十七', '初见', '二见', '三见', '四见', '五见', '末见',
             'verify_maozhai.py', 'daizhigev20', '历史眼光', 'mulu.html',
             '殆知阁简体库', '引文经脚本与库内文件逐字核验'):
    if need not in page_raw:
        fails.append(f'页面缺结构件 :: {need}')
# 无外部依赖
if re.search(r'(src=|href=)\s*["\']https?://(?!github\.com/robertsong2000)', page_raw):
    fails.append('页面引入了外部资源链接')

print(f'引文核验 {len(QUOTES)} 段（库内）+ {len(EXTERNAL)} 段（库外转引）')
if fails:
    print(f'✗ {len(fails)} 项未过:')
    for f in fails:
        print('  -', f)
    sys.exit(1)
print('✓ 全部通过')
