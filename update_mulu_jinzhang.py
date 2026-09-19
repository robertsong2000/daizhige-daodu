#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mulu.html 更新：481 金漳兰谱 / 卷三百六十 · 国香。断言式，防撞号。"""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
MULU = os.path.join(HERE, 'mulu.html')

s = open(MULU, encoding='utf-8').read()

# 防撞前置断言
assert '<span class="no mono">481</span>' not in s, '481 已被占用'
assert '卷三百六十' not in s, '卷三百六十已被占用'
assert '金漳兰谱' not in s, '金漳兰谱已收录'

# 1) kicker 计数锚
a = '<div class="kicker">殆知阁古代文献 · 四百八十篇导读合订</div>'
b = '<div class="kicker">殆知阁古代文献 · 四百八十一篇导读合订</div>'
assert s.count(a) == 1; s = s.replace(a, b)

# 2) sub 计数锚 + 卷分编清单
a = '一个 4.79 GB 的古代文献库，四百八十篇短文带你看清它的骨架与血肉。三百五十九卷分编：'
b = '一个 4.79 GB 的古代文献库，四百八十一篇短文带你看清它的骨架与血肉。三百六十卷分编：'
assert s.count(a) == 1; s = s.replace(a, b)
a = '天青卷问釉。</p>'
b = '天青卷问釉，国香卷问香。</p>'
assert s.count(a) == 1; s = s.replace(a, b)

# 3) footer 计数锚
a = '四百八十篇导读，2026 年 9 月编，数据均经实测核验'
b = '四百八十一篇导读，2026 年 9 月编，数据均经实测核验'
assert s.count(a) == 1; s = s.replace(a, b)

# 4) 插入 481 条目（480 条目之后、footer 之前）
DESC = ('世界最早的兰花专谱：宗室子弟赵时庚少年痴兰，三十年不肯外传，被朋友一句岂予一身可得而私有点破才成书。'
        '本卷收〈金漳兰谱〉导读一篇，页面做成三盆开卷壳：首屏案上紫白奇三盆，逐盆点开兰花开、书名四字逐字亮起钤澹斋印；'
        '缘起两笺对读园里的少年与不肯外传的人，中轴自嘉定改元到绍定癸巳三十年；'
        '品第左紫右白两榜二十一品各系品辞，甲印落陈梦良，鱼魫兰沉水交互演无影可指；'
        '得名考翻出大张青读书岩谷与蒲统领引兵逐寇两桩来历；手泽碎盆戒三步与八签老手艺；'
        '尾屏竖排岂非真兰室乎岂非有国香乎钤国香印。'
        '引文经脚本自库本锚点切片生成、去标点归一逐字比对通过（五十九q，白话反扫六字窗零撞）。')
TI = ('宋赵时庚撰，据艺藏草木鸟兽虫鱼库本，去空白约六千四百字，卷首冠四库提要，次原序，正文上中下三卷，末系跋，'
      '绍定癸巳（一二三三）自序。时庚为宗室子，提要推为魏王廷美九世孙，始末未详。世界现存最早兰花专谱，'
      '与王贵学兰谱相为出入，说郛所收佚其下卷，库本三卷独完。'
      '书眼＝一部雅到极致的谱录里坐着两个奇怪的名字：大张青是张姓书生读书岩谷所得，'
      '蒲统领是淳熙间引兵逐寇至一所得之，儒与兵各占一名。'
      '名场面：陈梦良朝晖微照晓露暗湿则灼然腾秀，最难种故人稀得其真；潘花艳中之艳花中之花，视之愈久愈见精神；'
      '济老如淡妆西子素裳缟衣不染一尘；灶山俗呼绿衣郎，跋里犹绿衣郎挺节独立；鱼魫兰花片澄彻，采而沉之水中无影可指；'
      '品第哲学句兰不能自异而人异之耳；碎盆戒分吴兰不忍击碎因剔出而根已伤三年始茂深以为戒，故须轻手击碎其盆；'
      '灌溉诀叶耸则不虑其花之不繁盛；浇花切不可用井水；除虫研大蒜和水以白笔蘸水拂叶；转盆三两日一番则四畔皆有花。'
      '版式＝三盆开卷壳（竹青）：首屏三盆点开显名钤澹斋印；两笺缘起三十年轴；紫白两榜二十一品签；鱼魫沉水交互；'
      '得名考两卡；手泽碎盆戒八签；尾屏竖排钤国香印。'
      '校字记：金殿边与金棱边、澹斋与滔斋、嬾真子与懒真子、鱼魫兰与鱼鲩兰、名第与名弟、云矫与云娇诸两形并存照录不归一；'
      '鱼魫条宛如鱼句疑有脱字照录；序中清香之夐后残一字，相关引文避让。'
      '时代局限：以色相姿态定甲乙的赏玩品第观、视兰为清玩的士人趣味、提要据宗室联名推世系的旧式考据皆时代底色，'
      '照录立此存照，不代今人立论。'
      '引文经脚本自库本锚点切片生成、去标点归一逐字比对通过（五十九q，白话反扫六字窗零撞）。')

block = '''
  <div class="vol" style="--vc: var(--c2)">
    <div class="wrap">
      <div class="vol-head">
        <div class="vseal" style="background: var(--c2)">叁百陆拾</div>
        <h2>卷三百六十 · 国香</h2>
        <div class="vsub">竹青 · 艺藏谱录</div>
      </div>
      <p class="vol-desc">{DESC}</p>
      <a class="entry" href="jinzhang-lanpu.html">
        <span class="no mono">481</span>
        <span class="ti">金漳兰谱<small>{TI}</small></span>
        <span class="file mono">jinzhang-lanpu.html</span>
      </a>
    </div>
  </div>

</footer>'''
block = block.replace('{DESC}', DESC).replace('{TI}', TI)
a = '</footer>'
assert s.count(a) == 1
s = s.replace(a, block)

open(MULU, 'w', encoding='utf-8').write(s)

# 插入后断言：1..481 无缺号无重号（DOM 按主题分组，不要求升序）
nos = [int(n) for n in re.findall(r'<span class="no mono">(\d+)</span>', s)]
assert len(nos) == len(set(nos)) == 481, f'条数异常: {len(nos)}'
assert set(nos) == set(range(1, 482)), '缺号或重号'
print(f'OK: mulu updated, {len(nos)} entries, max={max(nos)}')
