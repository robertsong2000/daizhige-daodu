#!/usr/bin/env python3
"""绛守居园池记导读 build+verify:库本锚点切片填充 q,并做六字窗反扫等全套核验。"""
import re, sys

SRC = '/home/robertsong/workspace/claude/daizhige-simplified/集藏/四库别集/绛守居园池记.txt'
PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/jiangshou-yuanchi.html'

raw = open(SRC).read()
src = re.sub(r'\s', '', raw)

def clip(a, z, mainzone=False):
    i = src.find(a)
    assert i >= 0, f'start miss: {a}'
    if mainzone:
        assert i < MAIN_END, f'{a} not in main text zone'
    j = src.find(z, i)
    assert j >= 0, f'end miss: {z}'
    return src[i:j + len(z)]

MAIN_END = src.find('五月十七日') + 8

CONST = {
    't-full': '绛守居园池记',
    't-byline': '唐樊宗师撰',
}

# (start, end) 锚切片;end=None 表示恰为 start 单串;mainzone=True 须落在正文区
CLIPS = {
    'h1':   ('绛即东雍为守理所', '两河润', True),
    'h2':   ('有陶唐冀遗风余思', '晋韩魏之相剥剖世说总', True),
    'h3':   ('木腔瀑三丈余', '虹蜺雄雌穹鞠觑蜃', True),
    'h4':   ('呜呼为附于河渠则可', '书以荐后君子', True),
    'q0':   ('文仅七百七十七字', '终无定论固其宜也', False),
    'q0b':  ('文仅七百七十七字', '终无定论固其宜也', False),
    'qa':   ('退之称樊宗师为文不剽袭', '亦太竒澁矣', False),
    'qb':   ('唐时有王晟刘忱二家注', '今并不传', False),
    'qc':   ('因熟读及逰览园池', '未能过半', False),
    'qc2':  ('因熟读及逰览园池', '未能过半', False),
    'qd':   ('尝至绛州得其旧碑', '其文仍不尽可解', False),
    'qe':   ('尝有人以文投陈尧佐', '半在文半在身', False),
    'qh':   ('其能无疑辞果有不决辞连用六字文竒', None, False),
    'qh2':  ('余退常吁后其能无', '补建者', True),
    'b1':   ('绛即东雍为守理所', '晋韩魏之相剥剖世说总', True),
    'n1':   ('记守居之园池非', '故多误', False),
    'b2':   ('岂新田又蕞猥不可居', '益侈心耗物害时与', True),
    'n2':   ('州字或属上句', '中读则可', False),
    'b3':   ('自将失敦穷华', '终披夷不可知', True),
    'n3':   ('若为太守者失敦厚穷奢华', None, False),
    'b4':   ('横硖旁潭中癸次', '涎玉沫珠', True),
    'n4':   ('腔说文内空也', '出水髙三丈', False),
    'b5':   ('子午梁贯亭曰徊涟', '碍佷岛坻', True),
    'n5':   ('尔雅雄曰虹雌曰蜺', '言二桥如虹蜺然', False),
    'b6':   ('淹淹萎萎', '承守寝晬思', True),
    'n6':   ('香亭名也', None, False),
    'b7':   ('西南有门曰虎豹', '丹碧锦袄', True),
    'n7':   ('此形容虎与彘鬬气也', None, False),
    'b8':   ('东南有亭曰新', '巉隂洽色', True),
    'n8':   ('苍官青士指松竹', '青士皆出于此也', False),
    'b9':   ('可四时合竒士', '赋歌诗', True),
    'n9':   ('自可字下至此一句', '意自见', False),
    'b10':  ('正东曰苍塘', '蹲濒西漭望', True),
    'n10':  ('漭大水貎', '池边蹲踞西望', False),
    'b11':  ('烟溃霭褧', '神君仙人衣裳雅冶', True),
    'n11':  ('言桃李兰蕙加之以烟霭', '禅縠衣也', False),
    'b12':  ('开咍储', '憎乖怜围', True),
    'n12':  ('文章贵不用意溢于正', '不能不竒之为竒也', False),
    'b13':  ('正西曰白濵', '水翠披', True),
    'n13':  ('佾舞列也', '似百行素女雪中舞也', False),
    'b14':  ('迎西引东土长崖', '诡姽绚化', True),
    'n14':  ('风日为灯火也此句妙', None, False),
    'b15':  ('大小亭饾池渠间', '间入汾', True),
    'n15':  ('饾饤饾贮食也', '如贮置于池渠之间', False),
    'b16':  ('巨树木资土悍水沮', '宗族盛茂', True),
    'n16':  ('其间有精到之语', '可但以险怪目之乎', False),
    'b17':  ('考其台亭沼池之増', '果有不补建者', True),
    'nroute': ('此记叙园池景物自正北之池始', '至西而终', False),
    't5':   ('吴师道以为疎漏', '正六十处', False),
    't6':   ('许谦仍以为未尽', '又补正四十一条', False),
    't7':   ('自予始校此文逮今二十年', '尚未得为定藁', False),
    'p1':   ('池由于炀', '几附于污宫', True),
    'n18':  ('雅薛雅也绛人文安者姓裴闻喜人', '葢书之误', False),
    'p2':   ('水本于正平轨', '引古沃澣人便', True),
    'n19':  ('按孙冲序云隋开皇三年内军将军梁轨为临汾令', None, False),
    'p3':   ('呜呼为附于河渠则可', '长庆三年五月十七日', True),
    'n20':  ('其可字用左传襄二十六年子产语', None, False),
    'm1':   ('异哉樊子怪可吁', '一语诘曲百盘纡', False),
    'm2':   ('黒石镌辞涩如棘', '既不可读不可听', False),
    'm3':   ('昌黎盛推绍述谓其词必已出', '则其他文殆不尽若此矣', False),
    'm4':   ('宗师别有越王楼诗序', '其僻涩与此文相类', False),
    'x1':   ('皇庆二年岁在癸丑', None, False),
}

# 断句擂台:手工拼行,BK=断点标记,去标记后须为库本连续串
BK = '<i class="bk"></i>'
MANUAL = {
    'rz1a': '其土田士人令无硗杂扰' + BK + '宜' + BK + '得地形胜防水施法',
    'rz1b': '其土田士人令无硗杂扰宜' + BK + '得地形胜防水施法',
    'rz2a': '白言谒' + BK + '行旦艮闲',
    'rz2b': '白言谒行' + BK + '旦艮闲',
}

fail = []
vals = {}
for k, (a, z, mz) in CLIPS.items():
    try:
        v = clip(a, z, mz) if z else a
        vals[k] = v
    except AssertionError as e:
        fail.append(str(e))
for k, v in MANUAL.items():
    plain = re.sub(r'<[^>]+>', '', v)
    vals[k] = v
    if plain not in src:
        fail.append(f'manual-q not in src: {k}')

# 引文红线:PUA 一律不许(渲染豆腐块)
for k, v in vals.items():
    if any(0xE000 <= ord(c) <= 0xF8FF for c in re.sub(r'<[^>]+>', '', v)):
        fail.append(f'PUA in clip {k}')

html = open(PAGE).read()
filled = 0
for k, v in {**CONST, **vals}.items():
    pat = re.compile(rf'<q([^>]*)data-k="{k}">(.*?)</q>', re.S)
    m = pat.search(html)
    if not m:
        fail.append(f'missing tag {k}')
        continue
    html = pat.sub(lambda mm: f'<q{mm.group(1)}data-k="{k}">{v}</q>', html, count=1)
    filled += 1
open(PAGE, 'w').write(html)

# ---------- verify ----------
NORM = re.compile(r'[\s,，、。;::?!?!·,.()（）()《》〈〉【】\[\]""''"\'…!?-]')
def norm(s):
    return NORM.sub('', s)

S = norm(src)
NAME = norm('绛守居园池记')

# 1) 切片逐字在库本
for k in CLIPS:
    if k in vals and vals[k] not in src:
        fail.append(f'clip-not-in-src {k}')

# 2) 白话六字窗反扫:剥 script/style/注释/所有 q 后,滑窗比对库本;书名整窗豁免
body = html
plain = re.sub(r'<script.*?</script>', '', body, flags=re.S)
plain = re.sub(r'<style.*?</style>', '', plain, flags=re.S)
plain = re.sub(r'<!--.*?-->', '', plain, flags=re.S)
plain = re.sub(r'<title>.*?</title>', '', plain, flags=re.S)
plain = re.sub(r'<q[^>]*>.*?</q>', '', plain, flags=re.S)
P = norm(plain)
hits = []
for i in range(len(P) - 5):
    w = P[i:i + 6]
    if w == NAME:
        continue
    if w in S:
        hits.append(w)
if hits:
    fail.append(f'6-char window collision: {sorted(set(hits))[:10]}')

# 3) JS 字面量也查(不含 q 内文本的纯 JS 常量串)
for m in re.finditer(r'<script.*?</script>', body, flags=re.S):
    js = norm(re.sub(r'<[^>]+>', '', m.group(0)))
    for i in range(len(js) - 5):
        w = js[i:i + 6]
        if w != NAME and w in S:
            fail.append(f'JS literal collision: {w}')
            break

# 4) 长划线
plain2 = re.sub(r'<(script|style).*?</\1>', '', body, flags=re.S)
for ch, nm in [('—', 'em-dash'), ('–', 'en-dash')]:
    if ch in plain2:
        fail.append(f'{nm} present')

# 5) 每行 · 最多 1
for i, ln in enumerate(body.split('\n'), 1):
    if ln.count('·') > 1:
        fail.append(f'line {i} middots={ln.count("·")}')

# 6) 页面 PUA
if any(0xE000 <= ord(c) <= 0xF8FF for c in body):
    fail.append('PUA in page')

# 7) 空 q 残留
if re.search(r'<q[^>]*></q>', body):
    fail.append('empty q left')

print(f'filled {filled} q ({len(CONST)} const + {len(CLIPS)} clips + {len(MANUAL)} manual)')
print('src chars:', len(S))
if fail:
    print('FAIL:')
    for f in fail:
        print(' -', f)
    sys.exit(1)
print('VERIFY OK: clips verbatim, prose 6-window clean, no dashes, middot<=1/line, no PUA')
