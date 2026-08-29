#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_daoyi.py — 岛夷志略页核验：引文逐字比对 + 排版规则 + 机器计数"""
import re, sys, unicodedata

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/daoyi-zhilue.html'
SRC  = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/地理/岛夷志略.txt'

page = open(PAGE, encoding='utf-8').read()
src  = open(SRC, encoding='utf-8').read()

def norm(s):
    out = []
    for ch in s:
        if ch.isspace():
            continue
        cat = unicodedata.category(ch)
        if cat.startswith('P') or cat.startswith('S'):
            continue
        out.append(ch)
    return ''.join(out)

def strip_tags(html):
    return re.sub(r'<[^>]+>', '\n', html)

page_text = strip_tags(page)
pnorm = norm(page_text)
snorm = norm(src)

fails = []

QUOTES = [
 "岛分三十有六，巨细相间，坡陇相望，乃有七澳居其间，各得其名。自泉州顺风二昼夜可至。",
 "地隶泉州晋江县，至元年间，立巡检司",
 "余登此山，则观海潮之消长，夜半则望晹谷之〔日〕出，红光烛天，山顶为之俱明。",
 "每值天清气和，风作浪涌，群龙游戏，出没海濵，时吐涎沬于其屿之上，故以得名。",
 "地每岁望唐舶贩其地，往往以五枚鸡雏出，必唐船一只来；二鸡雏出，必有二只，以此占之，如响斯应。",
 "国初，军士征阇婆，遭风于山下，辄损舟，一舟幸免，唯存钉灰。见其山多木，故于其地造舟一十余只，若樯柁、若帆、若篙，靡不具备，飘然长往。",
 "今唐人与番人丛杂而居之。",
 "汉字书云：咸淳三年八月，毕工。传闻中国之人其年贩彼，为书于石以刻之，至今不磨灭焉。",
 "至顺庚午冬十月有二日，因卸帆于山下，是夜，月明如昼，海波不兴，水清彻底。",
 "此琼树开花也。诚海中之稀有，亦中国之异闻。",
 "每个银钱重二钱八分，准中统钞一十两，易汃子计一万一千五百二十有余，折钱使用。",
 "故贩其地者，十去九不还也。",
 "昔泉之吴宅，发舶梢众百有余人，到彼贸易。既毕，死者十八九，间存一二",
 "失风，针迷舵折，舶遂阁浅。人船货物，俱各漂荡。",
 "石塘之骨，由潮州而生，迤逦如长蛇，横亘海中，越海诸国。",
 "俗云万里石塘，以余推之，岂止万里而已哉？",
 "避之则吉，遇之则凶。",
 "得意之地勿再往，岂可以风涛为径路也哉？",
 "能为飞车，从风远行；见于博物志矣。",
 "舶由玳屿门挂四帆，乘风破浪，海上若飞。",
]

# 1) 引文：库内有、页面有
for q in QUOTES:
    nq = norm(q)
    in_src = nq in snorm
    in_page = nq in pnorm
    tag = 'OK ' if (in_src and in_page) else 'FAIL'
    if not (in_src and in_page):
        fails.append(q[:18])
    print(f'{tag} 页面{"有" if in_page else "无"} 库内{"有" if in_src else "无"}  {q[:24]}')

# 2) 排版红线
for bad, name in [('—','长划线—'), ('–','短划线–')]:
    if bad in page:
        fails.append(name); print(f'FAIL 页面含{name}')
if '—' in page or '–' in page:
    pass
for i, line in enumerate(page_text.split('\n'), 1):
    c = line.count('·')
    if c > 1:
        fails.append(f'行{i}·x{c}'); print(f'FAIL 行{i} 有{c}个·: {line.strip()[:40]}')
if not fails or all('·' not in f for f in fails):
    pass
print('OK  排版：无长短划线，每行·不超过1' if not any('划线' in f or f.startswith('行') for f in fails) else '    排版存在违规')

# 3) 库内条目：100条 + 站号
lines = src.split('\n')
names = []
for l in lines:
    m = re.match(r'^([^\s　]{1,5})\s+(.*)', l)
    if m and m.group(1) != '岛夷志略':
        names.append(m.group(1))
pos = {n: i + 1 for i, n in enumerate(names)}
print(f'{"OK " if len(names)==100 else "FAIL"} 库内条目数 = {len(names)}')
if len(names) != 100:
    fails.append('条目数')
print(f'{"OK " if len(src)==19181 else "FAIL"} 库内字符数 = {len(src)}')

featured = ['彭湖','琉球','龙涎屿','文老古','交栏山','土塔','大佛山','乌爹','古里地闷','急水湾','万里石塘']
for n in featured:
    p = pos[n]
    tag = f'{p:02d}／100' if p < 100 else f'{p}／100'
    if tag not in page:
        fails.append(f'站号{tag}'); print(f'FAIL 页面缺站号 {n} {tag}')
    else:
        print(f'OK  站号 {n} = {tag}')

# 4) 百站墙顺序 = 库内顺序
wall = re.search(r'<div class="wall">(.*?)</div>', page, re.S)
wtokens = re.findall(r'<b[^>]*>(?:<a[^>]*>)?([^<]+?)(?:</a>)?</b>', wall.group(1))
if wtokens == names:
    print('OK  百站墙 100 站顺序与库内一致')
else:
    fails.append('墙序'); print(f'FAIL 百站墙不符：墙{len(wtokens)} vs 库{len(names)}')
    for a, b in zip(wtokens, names):
        if a != b:
            print('   墙:', a, '库:', b)

# 5) 第一人称三处，库内各恰一次
for k in ['余登', '余指舟人', '以余推之']:
    c = src.count(k)
    ok = c == 1 and norm(k) in pnorm
    print(f'{"OK " if ok else "FAIL"} 第一人称「{k}」库内{c}次，页面{"有" if norm(k) in pnorm else "无"}')
    if not ok: fails.append(k)

# 6) 货单芯片均须在库内对应条目原文中
ENT = {}
for l in lines:
    m = re.match(r'^([^\s　]{1,5})\s+(.*)', l)
    if m and m.group(1) != '岛夷志略':
        ENT[m.group(1)] = m.group(2)
GOODS = {
 '琉球': ['土珠','玛瑙','金珠','粗碗','处州瓷器'],
 '龙涎屿': ['金银'],
 '文老古': ['银','铁','水绫','丝布','巫仑','八节那间布','土印布','象齿','烧珠','青瓷器','埕器'],
 '交栏山': ['谷米','五色绢','青布','铜器','青器'],
 '土塔': ['糖霜','五色绢','青鞋','苏木'],
 '乌爹': ['金','银','五色鞋','白丝','丁香','豆蔻','茅香','青白花器','鼓瑟'],
}
ng = 0
for ent, chips in GOODS.items():
    tnorm = norm(ENT[ent])
    for c in chips:
        ng += 1
        if norm(c) not in tnorm:
            fails.append(f'芯片{c}'); print(f'FAIL 芯片「{c}」不在{ent}条原文')
print(f'OK  货单芯片 {ng} 枚全部与库内原文相符' if not any(f.startswith('芯片') for f in fails) else '')

# 7) 外部依赖
if 'http://' in page and 'github' not in page:
    fails.append('外链')
for host in ['cdn.', 'googleapis', 'unpkg', 'jsdelivr']:
    if host in page: fails.append('外部依赖'+host)
print('OK  无外部依赖（仅页脚仓库链接）' if not any('外部' in f or '外链' in f for f in fails) else 'FAIL 外部依赖')

print()
if fails:
    print('未通过', len(fails), '项：', fails); sys.exit(1)
print(f'全部通过：引文 {len(QUOTES)} 段、站号 {len(featured)} 面、百站墙 1 面、第一人称 3 处、芯片 {ng} 枚、排版红线。')
