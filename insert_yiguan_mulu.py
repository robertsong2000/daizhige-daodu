# -*- coding: utf-8 -*-
# 向 mulu.html 追加 医贯 条目:实时取号 = 当前最大篇号 + 1
import re, sys

MULU = '/home/robertsong/workspace/claude/daizhige-daodu/mulu.html'
html = open(MULU, encoding='utf-8').read()

nos = [int(n) for n in re.findall(r'<span class="no mono">(\d+)</span>', html)]
mx = max(nos)
no = mx + 1
if no != 528:
    print('NOTE: 顺延号变为', no)
    sys.exit('unexpected number drift, rerun with updated constants')

if 'yiguan.html' in html:
    sys.exit('yiguan already in mulu')

NO = str(no)
SEAL = '肆百零贰'
VOL = '卷四百零二 · 走马'

TI = ('明赵献可撰，据医藏库本，去空白约七万八千字，凡六卷：卷之一玄元肤论，卷之二主客辨疑，'
'卷之三绛雪丹书，卷之四卷之五先天要论，卷之六后天要论。赵献可字养葵，别号医巫闾子，明万历间名医，温补一派先声。'
'书眼＝把人身之主从心里搬出来：内经十二官论数出十二官，却主张君主之官当与十二官平等，若心便是主，'
'经文主不明则十二官危一句就该说十一官危，故人身别有一主非心也；真君无形，借元宵鳌山走马灯立喻，'
'拜者舞者飞者走者无一不具，中间惟是一火，火旺则动速火微则动缓火熄则寂然不动而躯壳未尝不存；'
'命门即在两肾之间，坎卦一阳陷于二阴之中，内经七节之旁有小心；治法只两句，火之有余缘真水不足，'
'毫不敢去火只补水以配火，壮水之主以镇阳光，火之不足就于水中补火，益火之原以消阴翳，分领六味丸八味丸两粒代表丸药；'
'相火龙雷论把火分阴阳，霹雳火无形有声不焚草木得雨而益炽，善治者以温肾之药从其性而引之归原，龙归大海，'
'力斥以黄柏知母为君者愈寒其肾益速其毙；郁病论谓凡病之起多由于郁，木郁达之火郁发之土郁夺之金郁泄之水郁折之。'
'版式＝走马灯壳（竹青）：首屏一盏可拨火候的走马灯，六屏拜舞飞走剪影绕焰旋转，旺微熄三档拨杆，'
'熄则轮停影在壳犹存；屏一丹灯德书名考与医巫闾子逃名藏山；屏二十二官牌点卯，虚位主牌请出非心之论；'
'屏三鳌山走马之喻；屏四坎卦两水夹一阳与水火两丸；屏五龙雷之火降一场雨火愈炽、引火归原火退水中；'
'屏六五郁字墙；尾屏养生莫先于养火钤医巫闾子印。'
'校字记：库本的以命门为君主之的、相根据而永不相离之根据连文，均依原文照录不归一，引文避开私用区缺字。'
'时代局限：阴阳五行与命门相火属前现代身体观，所载方药治法为历史文献记录不可仿用，对寒凉攻下诸派的门户之评存当日之争，照录不代今人立论。'
'引文经脚本自库本锚点切片生成、去标点归一逐字比对通过（十八q十五qv，白话反扫六字窗零撞）。')

DESC = ('一位万历间的医生看当时的时弊：大家一见上火就用寒凉药去浇，他站出来说，人身真正的主宰是一团火，'
'浇不得，只能养。他把五脏六腑比作满朝官员，却坚持君位虚悬：心只是十二官之一，真主是两肾之间的命门之火，'
'好比元宵走马灯中间那一点火，灯上拜舞飞走的影子全看火候。本卷收〈医贯〉导读一篇，页面做成走马灯壳（竹青）：'
'首屏一盏可拨火候的走马灯，熄了火轮子就停而灯影不散；屏二十二官牌点卯、虚位主牌引出非心之论；'
'屏四坎卦两水夹一阳；屏五一场越浇越旺的龙雷之雨；屏六五郁字墙；收在养生莫先于养火。'
'引文经脚本自库本锚点切片生成、去标点归一逐字比对通过（十八q十五qv，白话反扫六字窗零撞）。')

block = f'''  <div class="vol" style="--vc: var(--c2)">
    <div class="wrap">
      <div class="vol-head">
        <div class="vseal" style="background: var(--c2)">{SEAL}</div>
        <h2>{VOL}</h2>
        <div class="vsub">竹青 · 医藏医论</div>
      </div>
      <p class="vol-desc">{DESC}</p>
      <a class="entry" href="yiguan.html">
        <span class="no mono">{NO}</span>
        <span class="ti">医贯<small>{TI}</small></span>
        <span class="file mono">yiguan.html</span>
      </a>
    </div>
  </div>
'''

anchor = '  </footer>'
if html.count(anchor) != 1:
    sys.exit('footer anchor not found')
html = html.replace(anchor, block + anchor)
open(MULU, 'w', encoding='utf-8').write(html)

# asserts: consecutive numbering
html2 = open(MULU, encoding='utf-8').read()
nos2 = sorted(int(n) for n in re.findall(r'<span class="no mono">(\d+)</span>', html2))
assert len(nos2) == len(set(nos2)), 'dup entry numbers'
missing = [n for n in range(nos2[0], nos2[-1] + 1) if n not in set(nos2)]
assert not missing, f'gaps: {missing[:10]}'
assert max(nos2) == no
print(f'inserted {NO}, seal {SEAL}, {VOL}; entries {len(nos2)}, max {no}, no gaps')
