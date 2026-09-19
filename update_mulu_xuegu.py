#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""insert xuegu-bian entry into mulu.html: number 476, vol 355 印宗."""
import sys

M = '/home/robertsong/workspace/claude/daizhige-daodu/mulu.html'
s = open(M, encoding='utf-8').read()

assert '<span class="no mono">478</span>' not in s, '478 already taken!'
assert '<span class="no mono">477</span>' in s, '477 missing, numbering broken'
assert 'xuegu-bian.html' not in s, 'xuegu-bian already in mulu'
assert '<h2>卷三百五十七' not in s, 'vol 357 name taken'

TI = ('元吾丘衍撰，据艺藏综合库本，去空白约六千九百字，一序、三十五举、合用文籍品目与附录五篇'
      '（洗印、印油、印谱名录、取字、摹印四妙）。中国文人篆刻的第一部章程：开篇不谈印，先讲字从哪里来，'
      '科斗为字之祖；中段立宪，白文皆用汉篆平方正直字不可圆、必逼于边空便不古，朱文用杂体篆不可大怪、不可逼边；'
      '官印铸择日封拜，军印凿急于行令，一枚印的工期里藏着官阶与兵事；唐相李泌端居室三字印是斋号印之祖。'
      '书眼＝今之篆书即古人平常字：篆书曾是日常书写，唐以后才成古物，这本书把它变回家法。'
      '附录是车间：印油法香油皂角熟艾银朱的元配方，取字法以熨斗熨之干随落，是七百年前的橡皮擦。'
      '版式＝印谱钤格壳（竹青）：点石濡朱三钤渐深开卷显名钤三十五举印；真白居士双笺（库本作真白通行作贞白照录）；'
      '从科斗到摹印五站源流轨；三十五举谱格墙全量照录点格读全文；白朱两律切换印面加铸凿二局；'
      '元人的书架摘品目八种与印谱七录（赵孟颊即赵孟頫讹字照录）；附录工房三方与四妙之匾；尾屏竖排钤印宗印。'
      '校字记：真白通行作贞白、赵孟颊即赵孟頫、崔瑷通行作崔瑗，缺字占位符照录。'
      '时代局限：官爵等第论印、以俗与不古为断、斥道号印与词曲入篆，旧文人正统观底色，照录立此存照。'
      '引文经脚本与库内文件去标点、归一逐字比对通过（一百一十五q，白话反扫六字窗零撞）。')

BLOCK = (
    '\n\n'
    '  <div class="vol" style="--vc: var(--c2)">\n'
    '    <div class="wrap">\n'
    '      <div class="vol-head">\n'
    '        <div class="vseal" style="background: var(--c2)">叁百伍拾柒</div>\n'
    '        <h2>卷三百五十七 · 印宗</h2>\n'
    '        <div class="vsub">竹青 · 艺藏印学</div>\n'
    '      </div>\n'
    '      <p class="vol-desc">一部教人把字刻进方寸的书：篆法讲在前，汉印黑白两律立在后，'
    '书末附一张元人的必读书单和三张作坊方子。本卷收〈学古编〉导读一篇，页面做成一册印谱：'
    '点石濡朱三钤开卷，三十五举全量上墙，点格读全文。</p>\n'
    '      <a class="entry" href="xuegu-bian.html">\n'
    '        <span class="no mono">478</span>\n'
    '        <span class="ti">学古编<small>' + TI + '</small></span>\n'
    '        <span class="file mono">xuegu-bian.html</span>\n'
    '      </a>\n'
    '    </div>\n'
    '  </div>\n'
)

anchor = '<span class="file mono">yanshan-waishi.html</span>\n      </a>\n    </div>\n  </div>'
idx = s.find(anchor)
assert idx > 0, 'sanguo block anchor missing'
ins = idx + len(anchor)
s = s[:ins] + BLOCK + s[ins:]

# counter anchors
rep = [
    ('四百七十七篇导读合订', '四百七十八篇导读合订'),
    ('四百七十七篇短文', '四百七十八篇短文'),
    ('五十六卷分编', '五十七卷分编'),
    ('四百七十七篇导读，2026 年 9 月编', '四百七十八篇导读，2026 年 9 月编'),
    ('雨窗卷听雨。', '雨窗卷听雨，印宗卷濡朱。'),
]
for a, b in rep:
    assert s.count(a) == 1, f'anchor not unique: {a} x{s.count(a)}'
    s = s.replace(a, b)

open(M, 'w', encoding='utf-8').write(s)

chk = open(M, encoding='utf-8').read()
assert chk.count('<span class="no mono">478</span>') == 1
assert '四百七十七' not in chk
assert '印宗卷濡朱' in chk and '卷三百五十七 · 印宗' in chk
for n, line in enumerate(BLOCK.split('\n'), 1):
    assert line.count('·') <= 1, f'new block line {n} has {line.count("·")} ·'
print('mulu updated: 478 / 卷三百五十七·印宗 inserted after yanshan; anchors fixed')
