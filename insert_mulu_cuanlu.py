#!/usr/bin/env python3
import re, sys

MULU = '/home/robertsong/workspace/claude/daizhige-daodu/mulu.html'
s = open(MULU, encoding='utf-8').read()

PIAOHAO = '456'

# counter anchor: 454 session left it stale; fix to current max
s = s.replace('四百五十五篇导读', '四百五十六篇导读')
assert '四百五十六篇导读' in s

vol = '''
  <div class="vol" style="--vc: var(--c3)">
    <div class="wrap">
      <div class="vol-head">
        <div class="vseal" style="background: var(--c3)">叁百叁拾伍</div>
        <h2>卷三百三十五 · 水程</h2>
        <div class="vsub">石青 · 史藏传记</div>
      </div>
      <p class="vol-desc">一趟走了三个月的出差：南宋诗人范成大外放广西静江府，腊月从苏州解缆，水陆兼程，逐日把路上的山、税、庙、风物记满一卷。本卷收〈骖鸾录〉导读一篇，做成水程长卷·一江到底壳：首屏船篷月洞窗推栓开窗，雪夜江景显出竖排书名；开卷两支竖签看四库馆臣怎么评；主菜是廿六泊的江行长卷，拖动巡游，点泊位读当天的日记；水程六折经折装展开名场面，除夜船袍、三过钓台、一木两千的税卡账、仰山梯田的词眼石碑、浯溪碑下对垒翻案、排衙石峰血点疑案；尾屏竖排韩愈句钤骖鸾印。引文经脚本与库内文件去标点、归一逐字比对通过（三十一处，白话反扫六字窗零撞）。</p>
      <a class="entry" href="canluanlu.html">
        <span class="no mono">456</span>
        <span class="ti">骖鸾录<small>南宋范成大撰，据史藏传记库本，约一万字，一卷逐日记程：自乾道壬辰十二月七日发吴郡，至癸巳三月十日入桂林交府事，凡廿六泊。书眼＝「梯田」一词的出生证明：袁州仰山山腹，岭阪禾田层层叠上山顶，他随手记下这两个字，一个描写大地的常用词就此进入文献，比后世农书的梯田图谱早得多；全书则是南宋士大夫的一线行程档案，物价、税卡、驿路、信仰、风物全在路上。名场面：除夕雪夜披使金旧袍坐船头看富春江，自评连剡溪夜泛都比下去；大年初一扫雪坐严光钓台，三过此地自和三篇，愧对羊裘钓叟；严州浮桥边给一根杉木记账，山价不值百钱到浙江卖两千，重征层层加码；鄱阳湖盗区大雪夜报盗船将近，烧船作势安住一船人；滕王阁故基犹在，楼上租给酒商卖酒；浯溪中兴颂碑下翻黄庭坚诸人的案，替父母上寿只该捧觞善颂，颂功碑不该读成一纸罪案；入桂林界石峰如排衙列队，官道血点疑案原来是嚼槟榔的人一路所唾。版式＝水程长卷·一江到底壳：首屏月洞船窗推栓开窗显雪夜江景；开卷竖签二支；廿六泊江行长卷拖动巡游，泊牌逐日翻读；水程六折经折装（除夜船袍、三过钓台、一木两千价梯、仰山梯田词碑、浯溪对垒、排衙石峰双态）；尾屏竖排飞鸾句钤骖鸾印。校字记：库本呉寳逺竒畧廰诸异体照录，比对时归一；■〈氵〈口上肎下〉〉州、汤■〈山屋〉为造字残记，引文避录；钴𬭁潭扩展区字不入引。时代局限：行纪对岭南风物与沿途吏治的记述均出宋人士大夫视角，照录立此存照，不代今人立论。引文经脚本与库内文件去标点、归一逐字比对通过（三十一处，白话反扫六字窗零撞）。</small></span>
        <span class="file mono">canluanlu.html</span>
      </a>
    </div>
  </div>

</footer>'''

anchor = 'bazhen-hebian-tushuo.html</span>\n      </a>\n    </div>\n  </div>\n\n</footer>'
assert anchor in s, 'insert anchor not found'
s = s.replace(anchor, anchor.replace('</footer>', vol.lstrip('\n')))

# continuity assertion: sorted set of entry nos must be exactly 1..N (mulu orders by theme, not no)
nos = [int(x) for x in re.findall(r'<span class="no mono">(\d+)</span>', s)]
ss = sorted(set(nos))
assert ss == list(range(1, len(ss) + 1)), 'numbering broken'
assert len(nos) == len(ss), 'duplicate nos'
assert max(ss) == int(PIAOHAO), 'max no mismatch: %d' % max(ss)

open(MULU, 'w', encoding='utf-8').write(s)
print('mulu updated: entries=%d, max=%d' % (len(nos), max(nos)))
