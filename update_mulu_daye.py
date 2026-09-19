# -*- coding: utf-8 -*-
"""mulu.html 断言式更新：487 / 卷三百六十六 · 天街"""
import re, sys

P = '/home/robertsong/workspace/claude/daizhige-daodu/mulu.html'
s = open(P, encoding='utf-8').read()
orig = s

# 0) 前置断言：目标编号/卷号未被占用
assert '卷三百七十' not in s, '卷三百六十六已被占用'
assert 'daye-zaji.html' not in s, 'daye-zaji.html 已收录'
assert s.count('四百九十') == 8, '锚计数异常: %d' % s.count('四百九十')

# 1) kicker
old = '殆知阁古代文献 · 四百九十篇导读合订'
assert s.count(old) == 1
s = s.replace(old, '殆知阁古代文献 · 四百九十一篇导读合订')

# 2) sub 行：短文数 + 分编数 + 追加卷句
old = '四百九十篇短文带你看清它的骨架与血肉。三百六十九卷分编'
assert s.count(old) == 1
s = s.replace(old, '四百九十一篇短文带你看清它的骨架与血肉。三百七十卷分编')
old = '梯航卷问洋。'
assert s.count(old) == 1
s = s.replace(old, '梯航卷问洋，天街卷启工。')

# 3) footer
old = '四百九十篇导读，2026 年 9 月编'
assert s.count(old) == 1
s = s.replace(old, '四百九十一篇导读，2026 年 9 月编')

# 4) 追加卷块（插在最后一个 </div> 与 </footer> 之间）
desc = '一部唐人替前朝记的工程账：杜宝以编年记大业一朝营东都、开运河、造龙舟、筑西苑诸事，全书不足七千字，却把每一项工程的尺寸、里程、人数记得清清楚楚。本卷收〈大业杂记〉导读一篇，页面做成天街中轴壳：首屏点启工，运河金线自洛阳画向江都，两岸榆柳次第亮起，龙舟浮出，书名显形钤大业印；迁都谶朱牌照录木命童谣；天街中轴立面自宫城直下龙门，六节点点击对读，端门直南二十里正当龙门；龙舟启行照录四重楼船规格与殿脚账板，随行船队花名册十二格，朱批「未足为苦」；西苑奇观四卡：剪彩为花、风亭月观皆以机成、造山为海、月夜清夜游，十六院名签照库本次第；谶兆与生活六卡：柱中白蛇、大鱼有角、餐桌改名、五色饮五签、丰都市珍奇山积；尾屏竖排照录开江南河欲东巡会稽，全书停笔在一个计划上，钤天街印。引文经脚本自库本锚点切片生成、去标点归一逐字比对通过（二十九q，白话反扫六字窗零撞）。'
ti = '唐杜宝撰，据史藏志存记录库本，去空白约六千四百字，编年一卷：大业元年至十年，营东都、开通济渠、造龙舟、筑西苑、开江南河。书眼＝独夫的加速度：一条中轴二十里正对龙门，一支船队舳舻二百里，一座西苑周围二百里，每个数字后面都跟着征发人夫的数目。名场面：术人章仇太翼以木命童谣劝迁都，帝览表怆然即日东行；龙舟高四十五尺长二百尺四重，殿脚一千八十人着杂锦采装袄子，青丝大绳六条分三番，殿脚船脚四万余人，舳舻相继二百余里骑兵翊两岸二十余万；西苑周二百里，十六院绕龙鳞渠，庭植名花秋冬剪杂彩为之色渝则改著新者，冬月剪采为芰荷，风亭月观皆以机成或起或灭若有神变，每秋八月帝引宫人三五十骑人定之后开阊阖门入西苑歌管；观风行殿一日之内嶷然峙立夷人惊为神异；改吴床为交床胡瓜为白路黄瓜茄子为昆仑紫瓜；五色饮以扶芳叶为青饮乌梅浆为女饮；库本又记弘农殿柱白蛇、通济渠大鱼似鲤有角亦唐兴之兆；而官方口吻的结语竟是于时天下丰乐虽此差科未足为苦。版式＝天街中轴壳（赭金）：首屏运河启工画线；中轴立面六节点点击对读；龙舟花名册账板；西苑四奇观卡；五色饮五签；尾屏竖排右起钤天街印。校字记：库本馀余混用照录不归一，童谣句「云；」分号讹照录，五色饮「女饮」疑避讳讹字照录。时代局限：役夫动辄数十万无一人有名有姓，谶纬灾祥为史笔底色，「未足为苦」是官家口吻，皆旧时代底色，照录立此存照，不代今人立论。引文经脚本自库本锚点切片生成、去标点归一逐字比对通过（二十九q，白话反扫六字窗零撞）。'
block = '''  <div class="vol" style="--vc: var(--c3)">
    <div class="wrap">
      <div class="vol-head">
        <div class="vseal" style="background: var(--c3)">叁百柒拾</div>
        <h2>卷三百七十 · 天街</h2>
        <div class="vsub">赭金 · 史藏志存记录</div>
      </div>
      <p class="vol-desc">%s</p>
      <a class="entry" href="daye-zaji.html">
        <span class="no mono">491</span>
        <span class="ti">大业杂记<small>%s</small></span>
        <span class="file mono">daye-zaji.html</span>
      </a>
    </div>
  </div>
''' % (desc, ti)

anchor = '\n\n</footer>\n</body>\n</html>'
assert s.count('</footer>') == 1
pos = s.rfind('</footer>')
s = s[:pos] + block + '\n' + s[pos:]

# 5) 后置断言
assert s.count('四百九十一') == 3
assert s.count('卷三百七十') == 1
assert s.count('daye-zaji.html') == 2
nos = [int(x) for x in re.findall(r'<span class="no mono">(\d+)</span>', s)]
assert nos[-1] == 491 and len(nos) == len(set(nos)), '编号异常'
vols = re.findall(r'<h2>(卷[^<]+)</h2>', s)
assert len(vols) == 370, 'h2 卷数 %d' % len(vols)

open(P, 'w', encoding='utf-8').write(s)
print('mulu updated: 491 / 卷三百七十 · 天街; h2 vols =', len(vols), '; entries =', len(nos))
