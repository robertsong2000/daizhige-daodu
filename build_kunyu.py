#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_kunyu.py — 从库本程序化切片生成引文，替换模板占位符，输出 kunyu-tushuo.html
引文零手抄：每条按 (起锚, 止锚) 在库本中定位切片，去空白后嵌入。"""
import re, sys

LIB = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/地理/坤舆图说.txt'
TPL = '/home/robertsong/workspace/claude/daizhige-daodu/kunyu.tpl.html'
OUT = '/home/robertsong/workspace/claude/daizhige-daodu/kunyu-tushuo.html'

lib = open(LIB, encoding='utf-8').read()
lib_flat = re.sub(r'\s+', '', lib)

# (占位符, 起锚, 止锚)
QUOTES = [
    ('Q01', '夫地与海本是圆形', '非语其形体也'),
    ('Q02', '天下之经，自顺天府起为初度', '复相接焉'),
    ('Q03', '此何以故？地为圆体，故日出于卯', '乙之半夜也'),
    ('Q04', '人居一面地平之上', '大略能见三百里'),
    ('Q05', '夫月食之故，由大地有日月之间', '则地为圜可知'),
    ('Q06', '物重者，各有体之重心', '物之重心悉欲就之'),
    ('Q06B', '地之圆球悬于空际，居中无著', '常得安然'),
    ('Q07', '一日行游西海，嗅海中气味', '必有人烟国土'),
    ('Q08', '阁龙志坚，促令前行', '果至一地'),
    ('QSH', '有地!', None),
    ('Q09', '寻得赤道以南大地', '故曰亚墨利加'),
    ('Q10', '墨瓦兰惧无以复命', '贾勇而前'),
    ('Q11', '忽得海峡，亘千余里', '又恍一乾坤'),
    ('Q11B', '入夜磷火星流', '因命为火地'),
    ('Q12', '遍绕大地一周', '从古航海未有若斯者'),
    ('Q13', '尝铸一钜铜人，高三十丈', '一指可容一人直立'),
    ('Q14', '上古制造宏工，纪载有七', '天下七奇是也'),
    ('Q15', '城楼上有园囿', '如小河然'),
    ('Q16', '台高二百五十级', '皆细白石为之'),
    ('Q17', '筑造将毕，王后忆念其夫王', '怅闷而殂'),
    ('Q18', '基址建在湖中', '以免地震催倒'),
    ('Q19', '设使这宏大之躯起立', '岂不冲破庙宇乎'),
    ('Q20', '我已安置之', '万不能起立'),
    ('Q21', '顶上安置多火炬', '以便认识港涯丛泊'),
    ('Q22', '能容八万七千人座位', '不相逼碍'),
    ('Q23', '身长数十丈，首有二大孔', '势若悬河'),
    ('Q24', '猛而多力，能与把勒鱼战', '此鱼辄胜'),
    ('Q25', '忽闻起大声，回视所登之岛已没', '方知是一鱼背'),
    ('Q30', '爪如人指，鬃如马', '尽一月不逾百步'),
    ('Q31', '恼怒时血聚于鼻上', '其时开屏如孔雀'),
    ('Q32', '行疾如马', '能化生铁'),
    ('Q33', '有鸟名亚尔爵虐，作巢于水次', '商舶待之以波海'),
    ('Q34', '地极广平，分天下之半', None),
]

out = {}
for key, a, b in QUOTES:
    fa = re.sub(r'\s+', '', a)
    i = lib_flat.find(fa)
    if i < 0:
        sys.exit(f'起锚未命中 {key}: {a}')
    if b is None:
        j = i + len(fa)
        seg = lib_flat[i:j]
    else:
        fb = re.sub(r'\s+', '', b)
        j = lib_flat.find(fb, i)
        if j < 0:
            sys.exit(f'止锚未命中 {key}: {b}')
        j += len(fb)
        seg = lib_flat[i:j]
    out[key] = seg

tpl = open(TPL, encoding='utf-8').read()
for key, seg in out.items():
    tpl = tpl.replace('{{' + key + '}}', seg)
left = re.findall(r'\{\{Q\d+\}\}', tpl)
if left:
    sys.exit(f'模板残留占位符: {left}')
open(OUT, 'w', encoding='utf-8').write(tpl)
print(f'切片 {len(out)} 条全部命中 → {OUT}')
for k, v in list(out.items())[:4]:
    print(f'  {k}: {v[:36]}…')
