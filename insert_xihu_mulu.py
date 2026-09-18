import re, sys
sys.path.insert(0, '.')

MULU = 'mulu.html'
BLOCK = '''
  <div class="vol" style="--vc: var(--c3)">
    <div class="wrap">
      <div class="vol-head">
        <div class="vseal" style="background: var(--c3)">叁百零陆</div>
        <h2>卷三百零六 · 湖影</h2>
        <div class="vsub">石青 · 集藏别集</div>
      </div>
      <p class="vol-desc">一部梦里的西湖导游图：作者前半生在湖上花钱，后半生在纸上还债，七十二处湖山旧迹，是国破之后用记忆搭起来的复制品。本卷收〈西湖梦寻〉导读一篇，引文经脚本与库内文件去标点、归一逐字比对通过（四十九处，白话反扫六字窗零撞）。</p>
      <a class="entry" href="xihu-mengxun.html">
        <span class="no mono">426</span>
        <span class="ti">西湖梦寻<small>明末山阴张岱撰，字宗子，号陶庵，晚号蝶庵居士，前半生是晚明富贵闲人，五十岁遭逢鼎革，避迹山中；据集藏四库别集库本，去空白约五万一千字，前有自序，后为开卷总记一篇，先品明圣二湖；下分五卷，卷一之西湖北路十一则，卷二之西湖西路十二则，卷三之西湖中路十四则，卷四之西湖南路十六则，卷五之西湖外景十八则，连总记恰七十二则，每则记一处湖上旧迹，附前人诗文。书眼＝一座只剩梦里才完好的湖：重游故地见昔日湖庄只剩瓦砾，他掉头急走，宁可守住梦中那座完好的湖，也不肯认眼前的残山剩水，自序分辨李供奉之梦如神女名姝是幻，自己的湖梦如家园眷属是真，全书便是用七十二则文字搭起来的梦中复制品。名场面：崇祯五年的大雪夜独赴湖心亭，长空混茫，上下皆白，湖上只剩长堤如一痕、亭如一点、舟如一芥、人如两三粒，亭上陌生人惊喜同饮，舟子嘀咕他痴而更有人比他更痴；总记把西湖比作声色俱丽的曲中名妓，人人可以狎玩，于是人人轻慢；岳王坟前四铁像反接齐跪，被游人捶得四首齐落，坟边还有抱银瓶殉父的少女；于坟谕祭词里皇帝亲口认错，等于朝廷给自家冤案签收；三生石录东坡圆泽传，圆泽与李源约了来世与十三年后，届时牧童骑牛而歌两偈掉头；昭庆寺香市起花朝尽端午，崇祯庚辰寺火连年饥荒香客断绝，繁花一夜散场；包衙庄楼船歌筵穷奢二十年，张岱赞他索性把繁华过到底。版式＝湖影梦醒壳：首屏夜湖全景SVG，月悬桥畔一舟一灯，梦醒开关拨到醒则灯火俱灭湖山褪色引文对调；自序纸白反白堂；三湖品格三卡；舟程五卷泊位轨收七十一处泊位其中十三处开引文详情；书眼特页大雪四量词一痕一点一芥两三粒配点选显形；湖上两座坟并置南宋岳王与明于少保；尾屏竖排存影之句钤蝶庵印。校字记：目录云牺正文作云栖从正文；香市记辛巳库本作辛已照录；目录宋大内与梵天寺、施公庙与三茅观两处连排据正文标记拆分；自序称甲午与丁酉两度重游，在辛亥落款之前，与通行系年相合。引文经脚本与库内文件去标点、归一逐字比对通过（四十九处，白话反扫六字窗零撞）。</small></span>
        <span class="file mono">xihu-mengxun.html</span>
      </a>
    </div>
  </div>

</footer>'''

s = open(MULU, encoding='utf-8').read()
assert s.count('</footer>') == 1, 'footer count'
old_tail = '  </div>\n\n</footer>'
assert s.count(old_tail) == 1, 'tail anchor not unique: %d' % s.count(old_tail)
s = s.replace(old_tail, '  </div>\n\n' + BLOCK)
n1 = s.count('四百一十六篇导读合订')
n2 = s.count('四百一十六篇短文')
s = s.replace('四百一十六篇导读合订', '四百二十六篇导读合订')
s = s.replace('四百一十六篇短文', '四百二十六篇短文')
open(MULU, 'w', encoding='utf-8').write(s)
print('inserted; anchors updated:', n1, n2)

# 自检：新块编号与计数
nums = [int(x) for x in re.findall(r'<span class="no mono">(\d+)</span>', s)]
print('entries:', len(nums), 'max:', max(nums), '连续:', nums == sorted(nums) and len(set(nums)) == len(nums))
deltas = {b - a for a, b in zip(nums, nums[1:])}
print('跳号检测:', sorted(deltas))
