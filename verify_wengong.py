#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""温公日记 导读页核验：引文双侧逐字、数据一致性、禁字符、机数。"""
import json, re, sys, unicodedata

LIB = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/温公日记.txt'
HTML = '/home/robertsong/workspace/claude/daizhige-daodu/wengong-riji.html'

raw = open(LIB, encoding='utf-8').read()
lines = [l.strip() for l in raw.splitlines() if l.strip()]
entries = lines[1:]

def pua_to_box(s):
    return re.sub(r'[-]', '□', s)

def norm(s):
    s = pua_to_box(s)
    out = []
    for c in s:
        if 0xE000 <= ord(c) <= 0xF8FF or c == '□':
            continue
        cat = unicodedata.category(c)
        if c.isspace() or cat.startswith('P') or cat.startswith('S'):
            continue
        out.append(c)
    return ''.join(out)

errs = []
def check(cond, msg):
    if not cond:
        errs.append(msg)

# ---------- 机数 ----------
whole = re.sub(r'\s', '', raw)
check(len(whole) == 17714, f'库本去空白字数应为17714，实得{len(whole)}')
check(len(entries) == 117, f'条数应为117，实得{len(entries)}')
pua_all = [c for c in raw if 0xE000 <= ord(c) <= 0xF8FF]
check(len(set(pua_all)) == 18, f'PUA种类应为18，实得{len(set(pua_all))}')
check(len(pua_all) == 44, f'PUA处数应为44，实得{len(pua_all)}')

html = open(HTML, encoding='utf-8').read()

# ---------- 抽屉数据与库本一致 ----------
m = re.search(r'const DIARY = (\[.*?\]);', html, re.S)
check(m, '未找到 DIARY 数据')
if m:
    data = json.loads(m.group(1))
    lib_ts = [pua_to_box(t) for t in entries]
    check(len(data) == 117, f'DIARY应为117条，实得{len(data)}')
    for i, (got, exp) in enumerate(zip(data, lib_ts)):
        if got['t'] != exp:
            errs.append(f'DIARY第{i+1}条与库本不符: {got["t"][:30]}')

# ---------- 引文切片（脚本从库本直取） ----------
QUOTES = [
    (13, '甲寅，余初赴经筵', '称美久之。'),
    (14, '光曰：“进读及之耳', '时事臣不敢论也。”'),
    (52, '司马光读《资治通鉴》张释之论啬夫利口', '时吕惠卿在坐，光所论专指惠卿也。'),
    (17, '上谓晦叔曰', '愿陛下更察之。”'),
    (18, '八日，垂拱登对', '只欲苟全素履。'),
    (18, '且轼虽不佳', '欲用为台官。”'),
    (6, '上使中使二人潜察府界青苗', '用之不疑。'),
    (21, '谢景温言：“范镇举苏轼为谏官', '多占兵士。”'),
    (21, '介甫下淮南、江南东西、荆湖北、夔州、成都六路转运司体量其状', '轼因带以来耳。'),
    (106, '是月，命皇城司卒七千余人巡察京城', '谤议时政者收罪之。'),
    (98, '上访于安道，安道曰：“是人有虚名而无实用', '介甫闻而衔之。'),
    (28, '初，赵元昊悉会诸族酋豪', '置髑髅中共饮之'),
    (29, '劝、渭寻遣山遇还', '射而杀之。'),
    (31, '时元昊自称兀卒已数年', '遂谋僭号。'),
    (111, '熙宁四年十月十三日，吴积曰', '名山今为供备使、高州刺史。'),
    (37, '六月己卯，以去夜月食', '修阴教。'),
    (44, '翁氏位有私身韩虫儿者', '乃虫儿自埋之也。'),
    (44, '辅臣皆请诛虫儿，太后曰：“置虫儿于尼寺', '实生子矣。”'),
    (46, '是日，彗行至张而没', '欲何为乎？”'),
    (115, '翰林书待诏请春词', '正如恭己布深仁。”'),
]

qt_blocks = re.findall(r'<p class="qt">(.*?)</p>', html, re.S)
check(len(qt_blocks) == len(QUOTES), f'qt块数应为{len(QUOTES)}，实得{len(qt_blocks)}')

def strict(s):
    s = pua_to_box(s)
    return re.sub(r'\s+', '', s).replace('□', '')

expected_norms = []
for idx, start, end in QUOTES:
    ent = entries[idx]
    i = ent.find(start)
    check(i >= 0, f'引文起点未找到(条{idx+1}): {start[:12]}')
    if i < 0:
        continue
    j = ent.find(end, i)
    check(j >= 0, f'引文终点未找到(条{idx+1}): {end[:12]}')
    if j < 0:
        continue
    expected_norms.append(strict(ent[i:j + len(end)]))

pool = [strict(b) for b in qt_blocks]
for k, en in enumerate(expected_norms):
    if en not in pool:
        # 找最接近的块帮助定位
        best = max(pool, key=lambda p: len(set(p) & set(en)) / max(len(set(en)), 1))
        errs.append(f'引文{k+1}未在qt块中逐字命中（最接近块: {best[:24]}…）')
for p in pool:
    if p not in expected_norms:
        errs.append(f'qt块未匹配任何库本切片: {p[:24]}…')

# ---------- 页面其他逐字主张 ----------
FRAGS = [
    '皆言民便乐之', '故上坚行', '务令边防安静', '介甫闻而衔之', '大悔之',
    '司马光方直，其如迂阔何', '孔子上圣，子路犹谓之迂',
    '时吕惠卿在坐，光所论专指惠卿也', '应天变修阴教',
    '以省钉钅□之费', '上以其言险讠皮', '鲜于亻先在远', '□延路钤辖司',
]
visible = re.sub(r'<style>.*?</style>|<script>.*?</script>|<[^>]+>', '', html, flags=re.S)
vn = norm(visible)
for f in FRAGS:
    check(norm(f) in vn, f'页面主张未命中库本/页面: {f}')
lib_norm_all = norm(raw)
for f in FRAGS:
    fn = norm(f).replace('□', '')
    check(fn in lib_norm_all, f'主张不在库本: {f}')

# ---------- 排版红线 ----------
for ch, name in [('—', '长划线—'), ('–', '短划线–')]:
    check(ch not in html, f'出现禁用字符: {name}')
bad_dot = [l.strip()[:30] for l in visible.splitlines() if l.count('·') > 1]
check(not bad_dot, f'单行出现多个间隔号·: {bad_dot}')
check(html.count('「') == html.count('」'), f'「」不配对: {html.count("「")} vs {html.count("」")}')
check('<a href="http' not in html, '出现外链')
check('src="http' not in html and 'link rel' not in html.lower(), '出现外部资源')
for kw in ['文本来源', '引文已与库内文本逐字核验', '以史料视之']:
    check(kw in html, f'页脚缺声明: {kw}')

if errs:
    print('FAIL')
    for e in errs:
        print(' -', e)
    sys.exit(1)
print(f'PASS：机数(17714字/117条/PUA18种44处)、{len(QUOTES)}块引文双侧逐字、{len(FRAGS)}条主张、排版红线 全过')
