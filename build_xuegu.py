#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build xuegu-bian.html: slice quotes from 学古编 into tpl tokens, generate 35-cell wall."""
import re

SRC = '/home/robertsong/workspace/claude/daizhige-simplified/艺藏/综合/学古编.txt'
TPL = '/home/robertsong/workspace/claude/daizhige-daodu/xuegu-bian.tpl.html'
OUT = '/home/robertsong/workspace/claude/daizhige-daodu/xuegu-bian.html'

src = open(SRC, encoding='utf-8').read()

QUOTES = {
    'XU':   ('大德四年五月二十五日', '吾丘衍子行序'),
    'S32':  ('仆有古人印式二册', '实为甚详。'),
    'S7':   ('吾衍《古人印式》二卷。', '吾衍《古人印式》二卷。'),
    'ST1':  ('科斗。为字之祖', '象虾蟆子形也。'),
    'ST2':  ('徐铉谓非老手', '石鼓文字也。'),
    'ST3':  ('李斯，方圆廓落', '圆活姿媚'),
    'ST4':  ('汉有摹印篆', '篆法与隶相通。'),
    'ST6':  ('汉篆多变古法', '救其失也。'),
    'LB1':  ('汉魏印章，皆用白文', '大不过寸许。'),
    'LB2':  ('白文印，皆用汉篆', '字不可圆。'),
    'LB3':  ('白文印必逼于边', '空便不古。'),
    'LB4':  ('用崔子玉写《张平子碑》上字', '最为第一。'),
    'LZ1':  ('朱文印。用杂体篆', '免费词说可也。'),
    'LZ2':  ('朱文印，不可逼边', '得中处为相去'),
    'LZ3':  ('自唐用朱文', '绝无知者'),
    'ZHU':  ('朝爵印文皆铸', '可缓者也。'),
    'ZAO':  ('军中印文多凿', '不可缓者也。'),
    'DUAN': ('唯唐相李泌有', '白文玉印。'),
    'PSW1': ('许氏《说文解字》十五卷', '太尉祭酒）。'),
    'PSW2': ('《苍颉》十五篇', '亦曰皇颉）。'),
    'PSW3': ('徐锴《说文解字系传》四十卷', '集贤学士）。'),
    'PSW4': ('史籀《石鼓文》', '或云柱下史）。'),
    'PSW5': ('崔瑷《张平子碑》', '篆全是汉。'),
    'PSW6': ('《古印式》二册', '本仆自集成者。'),
    'PSW7': ('王楚《钟鼎篆韵》七卷', '管衡州露仙观）。'),
    'PSW8': ('《啸堂集古录》', '只具音释也。'),
    'XI':   ('图书久为油朱所炽者', '此法最良。'),
    'YOU':  ('香油浸皂角', '与好事者共之。'),
    'QU':   ('硇砂，瓦粉', '干，随落。'),
    'M1':   ('功侔造化', '谓之神'),
    'M2':   ('笔画之外', '谓之奇'),
    'M3':   ('艺精于一', '谓之工'),
    'M4':   ('繁简相参', '谓之巧'),
    'PS1':  ('《宣和印谱》四卷。', '《宣和印谱》四卷。'),
    'PS2':  ('晁克一《图书谱》一卷', '又名《集古印格》）。'),
    'PS3':  ('王厚之《复斋印谱》。', '王厚之《复斋印谱》。'),
    'PS4':  ('颜叔夏《古印谱》二卷。', '颜叔夏《古印谱》二卷。'),
    'PS5':  ('姜夔《集古印谱》二卷。', '姜夔《集古印谱》二卷。'),
    'PS6':  ('吾衍《古人印式》二卷。', '吾衍《古人印式》二卷。'),
    'PS7':  ('赵孟颊《印史》二卷。', '赵孟颊《印史》二卷。'),
    'V1':   ('汉魏印章，皆用白文', '皆用白文'),
    'V2':   ('平方正直，字不可圆', '字不可圆'),
    'V3':   ('不可有空，空便不古', '空便不古'),
    'PSCAT': ('○合用文籍品目', '○合用文籍品目'),
}

slabs = {}
for name, (a, b) in QUOTES.items():
    ia = src.find(a)
    assert ia >= 0, f'start anchor missing: {name} {a}'
    ib = src.find(b, ia)
    assert ib >= 0, f'end anchor missing: {name} {b}'
    slabs[name] = src[ia:ib + len(b)]

# structure assertions
ms = list(re.finditer(r'[一二三四五六七八九十]{1,3}举[曰；]', src))
assert len(ms) == 35, f'expect 35 举, got {len(ms)}'
assert all(ms[i].start() < ms[i+1].start() for i in range(34)), '举 out of order'
cat = src.find('○合用文籍品目')
assert cat > ms[34].start()
appx = [('洗印法', '○洗印法'), ('印油法', '○印油法'), ('印谱名录', '○世存古今图印谱式'),
        ('取字法', '○取字法'), ('摹印四妙', '○摹印四妙')]
pos = -1
for nm, mark in appx:
    p = src.find(mark, cat)
    assert p > pos, f'appendix order broken at {nm}'
    pos = p
cats = re.findall(r'△[^ □\n]{2,8}', src)
print('品目 categories:', cats)
assert '△小篆品五则' in src and '△附用器品九则' in src

# 35 举 full texts
jubodies = []
for i in range(35):
    start = ms[i].start()
    end = ms[i+1].start() if i < 34 else cat
    jubodies.append(' '.join(src[start:end].split()))
    assert len(jubodies[i]) > 20, f'ju{i+1} body too short'

CN = ['一','二','三','四','五','六','七','八','九','十','十一','十二','十三','十四','十五',
      '十六','十七','十八','十九','二十','二十一','二十二','二十三','二十四','二十五',
      '二十六','二十七','二十八','二十九','三十','三十一','三十二','三十三','三十四','三十五']

BLURBS = {
 1: '字之祖是蝌蚪：竹硬漆腻，写不动，才拖出头粗尾细的尾巴。',
 2: '篆书本是古人的日常字，历代变迁才显得古奥。',
 3: '学篆先博古：识得古器款识，字里自有敦朴之气。',
 4: '《说文》是根本，通了他写不差。',
 5: '《说文》检字费力，先熟《复古编》便得大概。',
 6: '篆法讲一致：首笔接与不接，后笔都要跟齐；圆点圆圈非小篆所有。',
 7: '篆以扁为上，扁到极处是石鼓文，老手才到得了。',
 8: '同是小篆，李斯廓落、阳冰姿媚，二徐如钗如箸，各有面目。',
 9: '写篇章只用小篆一体，取法二徐或二李随人；词曲不许入篆。',
 10: '小篆忌太长：一字正体加半字垂脚，垂脚不过三。',
 11: '写碑匾字画要肥，体势要方圆，碑额同理。',
 12: '拿鼎篆古文来杂着用，以看不出拼凑痕迹为上，法度仍归小篆。',
 13: '格眼里的字别塞满，学斗和井悬着一枚，空着反而自然。',
 14: '执笔单钩，中指藏在下头夹衬，笔画才有着落。',
 15: '篆大字须虚腕悬笔，腕一着纸字就死了。',
 16: '汉人写篆已乱了古法，许慎作《说文》正是来救场。',
 17: '隶书妙在不扁：笔势平硬，转折带刀头意，方是汉人骨。',
 18: '摹印篆要的只是方正，笔法与隶书相通；后人写歪，本相就失了。',
 19: '汉魏印皆白文，尺度不过寸许：官印铸、军印凿，缓急两分。',
 20: '白文一律汉篆，横平竖直地排，字不许圆，斜笔也要想法拉直。',
 21: '三字印右一左二，两字处与一字处等量，忌中断也忌紧贴。',
 22: '四字印前两字间留空、后两字不留，就要空出一笔作界。',
 23: '斋轩印古无此式，李泌端居室是孤例，终非古法，不若朱文。',
 24: '朱文许用杂体篆，但以不怪为限，挑近人情的写。',
 25: '白文取字最上等：崔子玉《张平子碑》字与汉器碑盖之字。',
 26: '姓名与表字入印，古有定式，不许拿杂篆朱文随俗乱来。',
 27: '白文要顶到印边，留出空便失了古意。',
 28: '朱文离边要留余地，距离从字的空白里找。',
 29: '拿金文款识的样子来治印，此路不通：汉代印文不长那样。',
 30: '道号唐人有而印无，不可以道号入印。',
 31: '印文里天生的空缺，别去联，别去带，由它去。',
 32: '他自家收着两册汉印摹本，官印私印各一，条列得极详。',
 33: '名印写法有等差：姓某印章最正，回文自有回文的规矩。',
 34: '表字印只二字为正式，添姓氏是近人的妄作。',
 35: '印文底下有空就让它空着，别硬拉笔画去凑满。',
}
assert len(BLURBS) == 35

DIRTY = re.compile(r'[-□\[]')
EXOVR = {7: ('徐铉谓非老手', 18), 13: ('不可填满', 16)}

cells = []
excerpts = []
for i in range(35):
    body = src[ms[i].start():(ms[i+1].start() if i < 34 else cat)]
    flat = ''.join(body.split())
    if i + 1 in EXOVR:
        a, n = EXOVR[i + 1]
        ja = flat.find(a)
        assert ja >= 0, f'excerpt anchor missing ju{i+1}'
        ex = flat[ja:ja+n]
    else:
        ex = flat[:16]
        while DIRTY.search(ex) and ex:
            k = DIRTY.search(ex).start()
            ex = flat[k+1:].lstrip()[:16]
    excerpts.append(ex)
    assert len(ex) >= 10, f'excerpt ju{i+1} too short: {ex}'
    assert not DIRTY.search(ex), f'excerpt ju{i+1} dirty: {ex}'
    cells.append(
        f'<button class="cell" aria-label="第{CN[i]}举">'
        f'<span class="no">第{CN[i]}举</span>'
        f'<q>{ex}</q>'
        f'<span class="go">全文</span>'
        f'<span class="full"><q>{jubodies[i]}</q></span>'
        f'<span class="blurb">{BLURBS[i+1]}</span>'
        f'</button>')
    print(f'ju{i+1}: {ex}')

html = open(TPL, encoding='utf-8').read()
tokens = dict(slabs)
tokens['CELLS'] = '\n          '.join(cells)
for name, t in tokens.items():
    tok = f'⟦{name}⟧'
    assert tok in html, f'token missing in tpl: {name}'
    html = html.replace(tok, t)
assert '⟦' not in html, 'unreplaced tokens remain'
open(OUT, 'w', encoding='utf-8').write(html)
print('written', OUT, len(html), 'bytes')
