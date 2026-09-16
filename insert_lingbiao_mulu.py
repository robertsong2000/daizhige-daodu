#!/usr/bin/env python3
# 断言式插入 334 岭表录异（卷二百一十七 · 珠还）
import re, sys

MULU = '/home/robertsong/workspace/claude/daizhige-daodu/mulu.html'
s = open(MULU, encoding='utf-8').read()

def die(m):
    print('ASSERT FAIL:', m); sys.exit(1)

nos = [int(n) for n in re.findall(r'<span class="no mono">(\d+)</span>', s)]
if max(nos) != 333: die(f'最大编号 {max(nos)} != 333')
if len(nos) != len(set(nos)): die('编号有重复')
if '岭表录异' in s: die('岭表录异已在 mulu，撞车')
if '卷二百一十六' not in s: die('卷二百一十六不在')
if '卷二百一十七' in s: die('卷二百一十七已被占')

footer_before = s.count('三百三十三篇')
if footer_before != 2: die(f'计数锚 {footer_before} 处，预期页头页脚共 2 处')

BLOCK = '''  <div class="vol" style="--vc: var(--c4)">
    <div class="wrap">
      <div class="vol-head">
        <div class="vseal" style="background: var(--c4); font-size: 12px">贰佰壹拾柒</div>
        <h2>卷二百一十七 · 珠还</h2>
        <div class="vsub">赭金 · 史藏地理杂记</div>
      </div>
      <p class="vol-desc">官做到任满，朝廷没了，回不了乡的人把滞留地写成一部博物志。本卷收〈岭表录异〉导读一篇，页面做成一口珠池：点下水，潜珠人沉底，珠与竖排书名一同浮起，钤珠还印；顶栏一串珠链随读点亮；飓母瘴母沓潮翻牌；舞象宁死不拜，尽杀之印落得极重；鳄鱼滩一船古书随读沉水；鲎摘雄即停；末站五颗珠把散佚、大典、四库辑本、鲁迅校本走成一本珠还账。</p>
      <a class="entry" href="lingbiao-luyi.html">
        <span class="no mono">334</span>
        <span class="ti">岭表录异<small>唐刘恂撰，清四库馆臣自永乐大典辑出三卷一百二十四条，去空白一万三千五百九十字，卷上飓母瘴母沓潮与珠金瑇瑁铜鼓，卷中草木果蔬，卷下海错虫蛇，夹钉唐代岭南掌故。书眼＝人回不去，书也散了，末了都回来了：刘恂昭宗朝出为广州司马，官满正撞上京扰攘，索性居南海成书，四库考出殆书成于五代时；原本久佚，宋人类书征引拆成零件，全靠永乐大典存其条理，乾隆馆臣逐卷裒辑仍成三卷以复唐志之旧，自评十得八九；鲁迅存底本校本两份手稿，行间密批，后入鲁迅辑校古籍手稿。看点＝飓母晕虹翻牌；廉州珠池径寸照室；绿珠井真珠三斛；鹅屎淘金；瑇瑁活揭；铜鼓蛙黾即鼓精；舞象宁死不拜禄山尽杀之；悦城龙母绩筐五卵；周遇漂流狗国野义国流虬国六国；荔枝奴龙眼；橄榄纳盐一夕自落；媚蝶妆奁养虫；跳鱼阵鱼多压沉；鲎雌负雄摘雄即停；鳄鱼滩李德裕一船书画沉失，是全书自带的书劫母题；海镜蟹出拾食；卢亭以蚝易酒；蝤蛑八月与虎斗；蚺蛇取胆余曾亲见；两头蛇其祸安在哉；养柑蚁是最早的生物防治记录之一。版式＝珠还壳：深海珠池首屏点下水潜珠人沉底珠浮书名显形钤珠还印，顶栏珠链六箔随读点亮，风信晕虹弧线加三翻牌，螺匣引文卡，舞象奏乐两拍落尽杀之印，书劫卡点浪起重演沉书，鲎摘雄实验按钮，六国漂流签换 pane，珠还账五珠时间线，尾屏空池珠归位钤珠还合浦印。校字记：沈溺貍瑇麹趫揳幺麽皆库本原字照录；跳<鱼廷><虫葛>等拆字复合字库本原样，引文避之。引文经脚本与库内文件去标点异体归一逐字比对通过（五十二处，另四库提要五处单独核对，白话反扫六字窗零撞）。</small></span>
        <span class="file mono">lingbiao-luyi.html</span>
      </a>
    </div>
  </div>

<footer class="page">'''

anchor = '\n<footer class="page">'
if s.count(anchor) != 1: die('footer 锚不唯一')
s = s.replace(anchor, '\n' + BLOCK, 1)
s = s.replace('三百三十三篇', '三百三十四篇')
open(MULU, 'w', encoding='utf-8').write(s)
print('插入完成: 334 岭表录异 / 卷二百一十七 · 珠还, 计数锚 → 三百三十四篇 x2')
