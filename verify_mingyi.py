#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""明夷待访录 导读页核验：引文逐字、排版红线、篇目计数、校记申报项"""
import re, sys, unicodedata, html

PAGE = 'daizhige-daodu/mingyi-daifanglu.html'
MAIN = 'daizhige-simplified/子藏/笔记/明夷待访录.txt'
QSG  = 'daizhige-simplified/史藏/正史/清史稿.txt'

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
t_main = open(MAIN, encoding='utf-8').read()
t_qsg  = open(QSG, encoding='utf-8').read()

QUOTES = [
    ('前年壬寅夏，条具为治大法，未卒数章，遇火而止。', MAIN),
    ('此卷犹未失落于担头舱底', MAIN),
    ('吾虽老矣，如箕子之见访，或庶几焉：岂因夷之初旦，明而未融，遂秘其言也!', MAIN),
    ('古者以天下为主，君为客，凡君之所毕世而经营者，为天下也。今也以君为主，天下为客，凡天下之无地而得安宁者，为君也。', MAIN),
    ('以其未得之也，屠毒天下之肝脑，离散天下之子女，以博我一人之产业，曾不惨然，曰：“我固为子孙创业也。”', MAIN),
    ('故我之出而仕也，为天下，非为君也；为万民，非为一姓也。', MAIN),
    ('天子之所是未必是，天子之所非未必非，天子亦遂不敢自为非是而公其非是于学校。', MAIN),
    ('有明之无善治，自高皇帝罢丞相始也。', MAIN),
    ('后之圣王而欲天下安富，其必废金银乎!', MAIN),
    ('奄宦之如毒药猛兽，数千年以来，人尽知之矣', MAIN),
    ('曰：斯民之苦暴税久矣，有积累莫返之害，有所税非所出之害，有田土无等第之害。', MAIN),
    ('征君自壬寅前，鲁阳之望未绝，天南讣至，始有潮息烟沈之叹，饰巾待尽，是书于是乎出。', MAIN),
    ('原本不止于此，以多嫌讳弗尽出，今并已刻之板亦毁于火。征君著书兼辆，然散亡者什九，良可惜也。', MAIN),
    ('因出大著待访录，读之再三，于是知天下之未尝无人', MAIN),
    ('同于先生者十之六七', MAIN),
    ('古之君子所以著书待后，有王者起，得而师之。', MAIN),
    ('尊素为杨、左同志，以劾魏阉死诏狱', QSG),
    ('宗羲对簿，出所袖锥锥显纯，流血被体', QSG),
    ('思宗闻之，叹曰：“忠臣孤子，甚恻朕怀。”', QSG),
    ('戊午，诏征博学鸿儒。掌院学士叶方蔼寓以诗，敦促就道，再辞以免。', QSG),
    ('宗羲虽不赴征车，而史局大议必咨之。', QSG),
    ('卒，年八十六。', QSG),
]

fails = 0
for q, src in QUOTES:
    n = norm(q)
    assert n, f'空引文: {q[:12]}'
    body = t_main if src == MAIN else t_qsg
    in_lib = n in norm(body)
    in_page = n in page_txt
    tag = '主文' if src == MAIN else '清史稿'
    if not (in_lib and in_page):
        fails += 1
        print(f'✗ [{tag}] 库内={in_lib} 页内={in_page} :: {q[:38]}')
    else:
        print(f'✓ [{tag}] {q[:38]}')

# ---------- 排版红线 ----------
plain = re.sub(r'<[^>]+>', '', page_raw)
plain = html.unescape(plain)
for i, ch in enumerate(plain):
    if ch in '—–':
        fails += 1
        print(f'✗ 排版禁字 {repr(ch)} 位置 {i}: …{plain[max(0,i-14):i+14]}…')
for ln in plain.splitlines():
    if ln.count('·') > 1:
        fails += 1
        print(f'✗ 一行多·: {ln.strip()[:40]}')

# ---------- 篇目计数：处方 21 味，四组 5/4/9/3 ----------
rows = re.findall(r'<div class="rx-row">.*?</div>\s*</div>', page_raw, re.S)
groups = []
for r in rows:
    drugs = re.findall(r'<span class="drug[^"]*">([^<]+)</span>', r)
    groups.append(drugs)
all_drugs = [d for g in groups for d in g]
titles = ['原君','原臣','原法','置相','学校','取士上','取士下','建都','方镇',
          '田制一','田制二','田制三','兵制一','兵制二','兵制三',
          '财计一','财计二','财计三','胥吏','奄宦上','奄宦下']
if sorted(all_drugs) != sorted(titles):
    fails += 1
    print(f'✗ 处方药味不符: {len(all_drugs)} 枚 vs 21')
else:
    print(f'✓ 处方 21 味，与目次 21 篇一一对应')
if [len(g) for g in groups] != [5,4,9,3]:
    fails += 1
    print(f'✗ 分组计数异常: {[len(g) for g in groups]}')
else:
    print('✓ 分组 5+4+9+3=21')

# 库内正文 21 个篇名行（含两处已知形态异常：原法题前带全角缩进，田制二题讹作田制一一）
HEADING_FORMS = {
    '原法': '\n　　原法\n',
    '田制二': '\n田制一一\n',
}
missing = []
for h in titles:
    forms = [f'\n{h}\n', HEADING_FORMS.get(h, '')]
    if not any(f and f in t_main for f in forms):
        missing.append(h)
if missing:
    fails += 1
    print(f'✗ 库内正文缺篇名行: {missing}')
else:
    print('✓ 库内正文 21 个篇名行全部在案（2 处异常形态已申报校记）')

# 库内实测字数
n = len(t_main)
if not (23000 <= n < 24000):
    fails += 1
    print(f'✗ 字数断言失败: {n}')
else:
    print(f'✓ 库内实测 {n} 字，页面称「两万三千余字」')

# ---------- 校记申报项逐条机器复核 ----------
for claim, label in [
    ('黄宗义', '卷首「黄宗义」讹字'),
    ('喟然而欢曰', '「欢」当作叹'),
    ('傅之子孙', '「傅」当作传'),
    ('一二代以下无法', '原法「一二代」串行'),
    ('儿子某某', '「儿子某某」名氏脱'),
    ('四0', '目次半角零'),
]:
    if claim not in t_main:
        fails += 1
        print(f'✗ 校记申报失实: {label}')
    else:
        print(f'✓ 校记有据: {label}')
if len(re.findall(r'^\s*财计三[.…]+', t_main, re.M)) != 2:
    fails += 1
    print('✗ 目次「财计三」重出申报失实')
else:
    print('✓ 目次「财计三」确两见（其一当为财计二）')

# ---------- 页面结构 ----------
for token, label in [
    ('之四十八', '序号 48'),
    ('data-side="控方"', '官司控方'),
    ('data-side="辩方"', '官司辩方'),
    ('候访', '登记卡章·候访'),
    ('积累莫返之害', '黄宗羲定律'),
]:
    if token not in page_raw:
        fails += 1
        print(f'✗ 页面缺 {label}')
stamps = page_raw.count('<div class="rc-stamp">')
if stamps != 5 or [s for s in ['候访','和','禁','印','读'] if f'>{s}</div>' not in page_raw]:
    fails += 1
    print(f'✗ 登记卡章数异常: {stamps}')
else:
    print('✓ 登记卡五行五章：候访 / 和 / 禁 / 印 / 读')

print('=' * 46)
if fails:
    print(f'FAIL: {fails} 项未过')
    sys.exit(1)
print(f'PASS: {len(QUOTES)} 段引文逐字全过，排版与计数全部通过')
