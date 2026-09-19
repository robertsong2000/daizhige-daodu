#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""向 mulu.html 追加 482 汉末英雄记条目（卷三百六十一·虎帐），带编号断言。"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MULU = os.path.join(HERE, 'mulu.html')

VOL = '''
  <div class="vol" style="--vc: var(--c1)">
    <div class="wrap">
      <div class="vol-head">
        <div class="vseal" style="background: var(--c1)">叁百陆拾贰</div>
        <h2>卷三百六十二 · 虎帐</h2>
        <div class="vsub">赭金 · 史部志存记录</div>
      </div>
      <p class="vol-desc">一部亡佚之书的残简拼图：建安七子王粲写同时代人，原书早亡，后人从类书里一条条捞回五十一条，条条带着打捞的胎记。本卷收〈汉末英雄记〉导读一篇，页面做成虎帐灯影壳：点灯开卷钤英雄印，九野旗门下五十一盏灯牌逐人读事，五幕名场面（帐中鼓筝三记对照、悬节东门对读、当避白马、火照赤壁、臧洪断炊），尾屏竖排陈容绝笔。引文经脚本自库本锚点切片生成、去标点归一逐字比对通过（九十二q，白话反扫六字窗零撞）。</p>
      <a class="entry" href="yingxiongji.html">
        <span class="no mono">483</span>
        <span class="ti">汉末英雄记<small>魏王粲撰，据史藏志存记录库本，去空白约一万二千字，辑本五十一条人物条目，末附辑者按语。王粲亲历汉末，所记皆同时人；原书久亡，今本自太平御览、三国志裴注等辑出，部分条目后仍括注御览卷数。书眼＝重复即证据：重出条三见，吕布帐中鼓筝遁走三段并存，甲记甲士三十人，乙记三十六兵，丙只记壮士，数字接缝处就是残简的拼合线；白马义从三段并存。名场面：董卓北芒迎驾，我董卓也从我抱来；鼎烹对语不同曰生乃同曰烹；袁绍天下健者岂惟董公横刀长揖悬节东门；高顺陷阵营七百人当千人用谏不见用；公孙瓒煮弩楯啖食之、当避白马长史、北邙祭别观者莫不歔欷；麹义八百人伏楯下大破白马；审配伏弩几中曹操犹恨其少；韩珩歃血拒盟北面曹氏所不能为；刘翊杀驾牛救人视没不救非志士遂俱饿死；臧洪粮尽薄糜遍颁七八千人相枕而死莫有离叛，陈容宁与臧洪同曰死不与将军同曰生；孙坚中石殒命记到月日；周瑜火攻细节版火然则回船走去去复还烧者；曹操南皮马上舞、自咋其舌以失言戒后世、邺中米一斛二万钱。版式＝虎帐灯影壳（赭金）：首屏军帐点灯书名显形钤英雄印；辑本自白两笺；九野旗门分组导航；五十一人灯牌墙点牌亮轶事卡；五幕名场面（三记对照异文标朱、董袁对读悬节显形、白马骑阵北邙祭笺、火船回烧复演、臧洪断炊三站）；尾屏竖排陈容绝笔钤英雄印。校字记：库本曰日多互讹照录；马日磾之磾、青琐门之琐、乔瑁之瑁、董旻之旻、竹艑竹箄竹旁库本存残码，页面以□存照或引文避让；马扌卞舞、孔亻由拆字照录；重出条照录不删。时代局限：本书记乱世惨烈事皆照录存真不讳不饰；清辑本承忠奸褒贬旧框架，立此存照，不代今人立论。引文经脚本自库本锚点切片生成、去标点归一逐字比对通过（九十二q，白话反扫六字窗零撞）。</small></span>
        <span class="file mono">yingxiongji.html</span>
      </a>
    </div>
  </div>

</footer>'''

def main():
    html = open(MULU, encoding='utf-8').read()
    assert 'yingxiongji.html' not in html, 'already inserted'
    # 断言：前一条是 482（并行顺延后实测），且 482 是最后一条
    i482 = html.find('<span class="no mono">482</span>')
    assert i482 > 0, 'prev item 482 not found'
    import re
    nums = [int(m) for m in re.findall(r'<span class="no mono">(\d+)</span>', html)]
    assert max(nums) == 482, f'parallel moved ahead: max={max(nums)}'
    assert '虎帐' not in html, 'juan name taken'
    i_ins = html.rfind('</footer>')
    assert i_ins > i482, 'footer anchor before 482'
    html = html[:i_ins] + VOL.rstrip().rsplit('</footer>', 1)[0].rstrip() + '\n\n</footer>' + html[i_ins + len('</footer>'):]
    # 复核
    assert html.count('<span class="no mono">483</span>') == 1
    assert html.find('yingxiongji.html') > i482
    assert html.count('<h2>卷三百六十二 · 虎帐</h2>') == 1
    open(MULU, 'w', encoding='utf-8').write(html)
    print('OK: mulu updated, 483 after 482, juan 362')

if __name__ == '__main__':
    main()
