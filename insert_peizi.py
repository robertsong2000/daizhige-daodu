#!/usr/bin/env python3
import re, sys

MULU = '/home/robertsong/workspace/claude/daizhige-daodu/mulu.html'
PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/peizi-yulin.html'

m = open(MULU, encoding='utf-8').read()
p = open(PAGE, encoding='utf-8').read()

nums = [int(x) for x in re.findall(r'<span class="no mono">(\d+)</span>', m)]
vmax = max(nums)
assert '裴子语林' not in m and 'peizi-yulin' not in m, '已收录或撞车'
n = vmax + 1
if n != 380:
    print('注意：实际取号', n)

assert '<h2>卷二百六十' not in m, '卷二百六十已被占'
assert len(nums) == len(set(nums)), '编号有重复'

# 页面 kicker 改为分类式（与近期各篇一致，不带篇号）
old_k = '<p class="kicker">殆知阁导读 · 第〇〇〇篇</p>'
assert old_k in p
p = p.replace(old_k, '<p class="kicker">殆知阁导读 · 史藏志存</p>')

vol = f'''
  <div class="vol" style="--vc: var(--c4)">
    <div class="wrap">
      <div class="vol-head">
        <div class="vseal" style="background: var(--c4)">贰百陆拾</div>
        <h2>卷二百六十 · 琐语</h2>
        <div class="vsub">赭金 · 史藏志存</div>
      </div>
      <p class="vol-desc">东晋隆和年间最畅销的一册小书：裴启把汉魏以来名士的隽语与笑谈收拢成帙，时流年少争相传抄，几乎人手一通；太傅一句不认账，书当场被判死刑，隋唐志尚著录，宋后亡逸；清人辑佚捞出大半，鲁迅钩沉再补一批，今本三百六十四则全是碎纸重装。本卷收〈裴子语林〉导读一篇，引文经脚本与库内文件去标点、归一逐字比对通过（二十九处，白话反扫六字窗零撞）。</p>
      <a class="entry" href="peizi-yulin.html">
        <span class="no mono">{n}</span>
        <span class="ti">裴子语林<small>题晋裴启撰，原书久佚，后世辑本，去空白约二万一千五百字，辑得三百六十四则。书眼＝一本书的生死档：书一出来年轻士人争相传抄、斋中各置一部；太傅谢安翻到谢安谓裴启那一条短简不认账，另有名士补刀，畅销书从此无人敢抄，隋唐志犹著录、宋后亡逸七百年；字句散进世说注与唐宋类书，像郑玄坐桥下在水上据屐躲过追杀，清人辑出大半、鲁迅古小说钩沉再辑，碎纸重新装订成书。兰阇兰阇、眼烂烂如岩下电、掷果满车、贫士不得如此厕、亡国之筵的汝酒、青牛髯奴、宁为兰摧玉折、手谈诸典皆在其中。版式＝书之生死三幕壳：首屏碎纸飘零竖排书名钤语林印；右缘生废复三签随幕点亮；幕一传写台按印抄书五通、名士九签；幕二罪简挨朱批废字砸落加朱笔两道、郑玄桥下避杀旧闻、五站兴亡带；幕三捞叶六片随滚动归位留两枚墨钉、名段六牍（鹤唳唾壶缺碎珊瑚急性子五处都像搬砖）、残签九纸；尾屏空框双印收梢。校字记：库本羊𬴊为扩展B区字、■〈土回〉复合体引文避开；烈士莫年、举见见日等辑本讹字照录不引。引文经脚本与库内文件去标点、归一逐字比对通过（二十九处，白话反扫六字窗零撞）。</small></span>
        <span class="file mono">peizi-yulin.html</span>
      </a>
    </div>
  </div>
</footer>'''

anchor = '\n</footer>'
assert m.count(anchor) == 1
m = m.replace(anchor, vol)

a1 = '三百七十八篇导读合订'
a2 = '三百七十八篇导读，2026 年 9 月编'
assert m.count(a1) == 1 and m.count(a2) == 1, f'锚计数异常 {m.count(a1)}/{m.count(a2)}'
cn = '三百八十'
m = m.replace(a1, f'{cn}篇导读合订').replace(a2, f'{cn}篇导读，2026 年 9 月编')

open(MULU, 'w', encoding='utf-8').write(m)
open(PAGE, 'w', encoding='utf-8').write(p)
print(f'插入完成：第{n}篇 卷二百六十·琐语，锚已改{cn}')
