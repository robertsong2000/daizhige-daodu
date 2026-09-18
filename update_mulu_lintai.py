#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""update_mulu_lintai.py — 向 mulu.html 追加 麟台故事 条目并修计数锚（带断言防撞号）"""
import re, sys

M = '/home/robertsong/workspace/claude/daizhige-daodu/mulu.html'
h = open(M, encoding='utf-8').read()

# 0) 撞号断言：目标号与卷名必须空闲
assert '卷三百三十二' not in h, '卷三百三十二已被占用'
assert '>453</span>' not in h and 'no mono">453<' not in h, '453 已被占用'
assert 'lintai-gushi.html' not in h, '本页条目已存在'

# 1) 插入点：452 帝京岁时纪胜 条目块收尾之后
key = 'dijing-suishijisheng.html'
i = h.find(key)
assert i > 0, '未找到 452 条目'
j = h.find('</a>', i)
assert j > 0
end = h.find('</div>\n  </div>', j)
assert end > 0
insert_at = end + len('</div>\n  </div>')

block = '''

  <div class="vol" style="--vc: var(--c4)">
    <div class="wrap">
      <div class="vol-head">
        <div class="vseal" style="background: var(--c4)">叁百叁拾贰</div>
        <h2>卷三百三十二 · 书库</h2>
        <div class="vsub">赭金 · 史藏职官</div>
      </div>
      <p class="vol-desc">一座被战火清空的官署，账本要从灰堆里重抄：南宋复置秘书省，程俱上任时一件旧档都找不到，这本书是他从灰烬泥涂里抠回来的北宋馆阁百年旧例。本卷收〈麟台故事〉导读一篇，页面做成五格书库·煨烬拾简壳：首屏崇文院立面推门开卷，三馆秘阁逐匾点亮；访书三牌出钱买、借来抄、献书给官逐一点亮；荣王宫火点灯焚院，内外院重建方案随焦色展开；五格书库九只书帙逐帙展开库本原文，镇阁之宝单从王羲之数到黄筌白兔，禄廪格挂出政和禄格工资条；卷外三只空帙立此存照，十二篇仅存九篇；煨烬幕三堆故牍拾入进书原状卷，三条归卷圣旨依奏朱印钤下；尾屏竖排馆职序坐钤麟台印。引文经脚本与库内文件去标点、归一逐字比对通过（六十六处，白话反扫六字窗零撞）。</p>
      <a class="entry" href="lintai-gushi.html">
        <span class="no mono">453</span>
        <span class="ti">麟台故事<small>南宋程俱撰，据史藏职官库本，约二万一千字，五卷九篇并进书原状、后序：卷一沿革省舍储藏，卷二修纂职掌，卷三选任，卷四官联，卷五恩荣禄廪。书眼＝给图书馆立传的人，刚经历过图书馆的死亡：绍兴元年复置秘书省，程俱受职之始按求简牍皆无有，老吏奔散死亡之余，或取故牍煨烬泥涂中，全书是他从灰堆里抠回来的旧例，书名取武则天改秘书省为麟台的旧称。名场面：太宗访书小则偿以金帛大则授之以官，数年之间献图书于阙下者不可胜计；淳化三年登新秘阁见群书齐整喜形于色，转头召两位禁军统帅上阁看书赐御酒，帝欲其知文儒之盛故也；大中祥符八年荣王宫火焚及崇文院，陈彭年重修内外院，此后内廷火禁甚严，宿直连口热饭都成问题；馆阁校定南华真经摹刻版本赐辅臣人各一本，而议者已叹墨版一统之后讹字无处对勘；十四岁晏殊殿上移晷而就擢秘书省正字，皇帝怕他年少迁染专派老臣督读；张说儒以道相高不以官阀为先后，馆职序坐以年齿为差沿成成规；政和禄格连米麦石数时令服装都列明，馆里还养着三十名看管巡宿的兵士。版式＝五格书库·煨烬拾简壳：首屏崇文院立面推门，三馆秘阁逐匾点亮；访书三牌逐点；点灯焚院看内外院重建；九帙书库逐帙展开，卷外三空帙存照佚篇；灰堆拾简三条归卷钤依奏印；尾屏竖排钤麟台印。校字记：进书原状题名麒台照录通行作麟台；职掌篇大?如此库本有残字引文避录；后序库本截断于孙伯黡典籍事引文截至完句。引文经脚本与库内文件去标点、归一逐字比对通过（六十六处，白话反扫六字窗零撞）。</small></span>
        <span class="file mono">lintai-gushi.html</span>
      </a>
    </div>
  </div>'''

h = h[:insert_at] + block + h[insert_at:]

# 2) 计数锚
k = h.find('四百五十二篇导读合订')
assert k > 0, 'kicker 锚未找到'
h = h.replace('四百五十二篇导读合订', '四百五十三篇导读合订')
assert '四百五十二篇短文' in h
h = h.replace('四百五十二篇短文', '四百五十三篇短文')
assert '三百三十一卷分编' in h
h = h.replace('三百三十一卷分编', '三百三十二卷分编')
tail_old = '灯月卷放灯。</p>'
assert h.count(tail_old) == 1
h = h.replace(tail_old, '灯月卷放灯，书库卷拾简。</p>')
assert '四百五十二篇导读，2026' in h
h = h.replace('四百五十二篇导读，2026', '四百五十三篇导读，2026')
assert '四百五十二' not in h, '仍有残留旧计数'

# 3) 落盘前终检
nos = re.findall(r'class="no mono">(\d+)</span>', h)
assert nos[-1] == '453', f'尾号 {nos[-1]}'
assert len(set(nos)) == len(nos), '条目号重复'
open(M, 'w', encoding='utf-8').write(h)
print('mulu 更新完成: 453 / 卷三百三十二 · 书库；条目', len(nos))
