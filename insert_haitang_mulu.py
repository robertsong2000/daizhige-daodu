#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""海棠谱 mulu 插入：动态解析当前最大篇号/卷号再顺延，断言连续性与唯一性。"""
import re, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
MULU = os.path.join(HERE, 'mulu.html')

CN = '零一二三四五六七八九'
def cn2int(s):
    s = s.replace('两', '二')
    if '百' in s:
        a, rest = s.split('百', 1)
        v = (CN.index(a) if a else 1) * 100
    else:
        rest = s
        v = 0
    if '十' in rest:
        a, b = rest.split('十', 1)
        v += (CN.index(a) if a else 1) * 10
        if b:
            v += CN.index(b)
    elif rest.replace('零', ''):
        v += CN.index(rest.replace('零', ''))
    return v

def int2cn(n):
    out = ''
    h, rest = divmod(n, 100)
    if h:
        out += CN[h] + '百'
    t, o = divmod(rest, 10)
    if t:
        out += (CN[t] if t > 1 else '') + '十'
    if o:
        out += CN[o]
    if not out:
        out = CN[o]
    return out

FIN = '零壹贰叁肆伍陆柒捌玖'
def int2fin(n):
    h, rest = divmod(n, 100)
    t, o = divmod(rest, 10)
    s = (FIN[h] + '百') if h else ''
    if t:
        s += FIN[t] + '拾'
    if o:
        s += FIN[o]
    return s

def main():
    html = open(MULU, encoding='utf-8').read()
    assert '海棠谱' not in html and 'haitang-pu.html' not in html, 'FAIL: 海棠谱已在 mulu'
    assert '· 红妆' not in html, 'FAIL: 卷名红妆已被占'

    k = re.search(r'· (四百[一二三四五六七八九十]+)篇导读合订', html)
    assert k, 'FAIL: kicker 锚未找到'
    no = cn2int(k.group(1)) + 1
    assert int2cn(no - 1) == k.group(1), f'FAIL: 篇号往返校验 {k.group(1)}'
    no_cn = int2cn(no)
    for old, new, tag in [(k.group(1) + '篇导读合订', no_cn + '篇导读合订', 'kicker'),
                          (k.group(1) + '篇短文', no_cn + '篇短文', 'sub')]:
        c = html.count(old)
        assert c == 1, f'FAIL: {tag} 锚出现 {c} 次: {old}'
        html = html.replace(old, new)
    f = re.search(r'(' + k.group(1) + r')篇导读，2026', html)
    assert f, 'FAIL: footer 计数锚未找到'
    html = html.replace(f.group(1) + '篇导读，2026', no_cn + '篇导读，2026', 1)

    vols = re.findall(r'<h2>卷([一二三四五六七八九十百零]+) · ', html)
    ints = [cn2int(v) for v in vols]
    assert ints[-1] == max(ints), 'FAIL: 末位卷号非最大'
    vno = ints[-1] + 1
    assert vno not in ints, 'FAIL: 新卷号已被占'
    assert no - vno == 121, f'FAIL: 卷号与篇号差异常 {vno} vs {no}'
    vno_cn = int2cn(vno)
    assert f'卷{vno_cn} · ' not in html, 'FAIL: 卷号已被占'

    lastvol = re.search(r'(池月卷照夜，佛光卷候光)[，。]', html)
    assert lastvol, 'FAIL: 卷名清单尾锚未找到（清单可能已被并行改写）'
    html = html.replace(lastvol.group(0), lastvol.group(1) + '，红妆卷照花。')

    VOL = f'''  <div class="vol" style="--vc: var(--c3)">
    <div class="wrap">
      <div class="vol-head">
        <div class="vseal" style="background: var(--c3)">{int2fin(vno)}</div>
        <h2>卷{vno_cn} · 红妆</h2>
        <div class="vsub">石青 · 艺藏草木鸟兽虫鱼</div>
      </div>
      <p class="vol-desc">一朵在蜀中开得正好、却被杜甫一辈子不提的花。沉默成了公案，宋人一代代替它翻案：真宗御题列它为首章，东坡为它深夜点烛。编这部谱的既非达官也非隐士，是临安城里一个开书铺的老板。本卷收〈海棠谱〉导读一篇，页面做成夜园点烛壳：银烛一点花蕾显形书名落定钤红妆印；杜甫公案三折卷宗开合、花开三段色卡、墨迹本对照表、九张竖排诗笺（三朝御题加唐宋名家）、六则逸事翻牌、三条养花方笺、书坊专栏；尾屏竖排陆游替花抱不平钤红妆印。引文经脚本自库本锚点切片生成、去标点归一逐字比对通过（四十八q，白话反扫六字窗零撞）。</p>
      <a class="entry" href="haitang-pu.html">
        <span class="no mono">{no}</span>
        <span class="ti">海棠谱<small>宋陈思撰，据艺藏草木鸟兽虫鱼库本，去空白约一万四千字，三卷：上卷叙事录海棠故实二十余条，中下两卷汇次唐宋诸家题咏；开庆元年（1259）自序，四库提要谓此书不见于宋史艺文志、惟焦竑国史经籍志著录三卷，栽种之法仅散见四五条，是数典之书非农书。书眼＝一朵被杜甫沉默过的花：杜子美居蜀累年吟咏殆遍而诗章独不及，郑谷替他翻案（浣花溪上空惆怅子美无情为发扬，原书注杜工部旅两蜀诗集中无海棠之题），杜默王荆公相继补亡，东坡柯丘长篇一出自认平生最得意；公案之外另有春睡典（唐明皇岂妃子醉是海棠睡未足耳）与东坡烧烛诗的墨迹异文（袅袅作渺渺霏霏作空蒙今从墨迹）。名场面：贾耽百花谱封花中神仙、真宗御制后苑杂花十题以海棠为首章、汴京一本价数十金、接花工嫩枝附梨、刘渊材平生五恨（鲥鱼多骨金橘太酸莼菜性冷海棠无香曾子固不能诗）、昌州海棠独香、黎举常欲令梅聘海棠、潘炕爱妾解愁母梦吞花蕊而生、韩持国每花开载酒日饮其下、秦少游醉卧海棠丛题柱如梦令（瘴雨过海棠开春色又添多少）；太宗真宗光宗三朝御题与郑谷苏轼陆游杨万里诸家诗在册，陆游还替花抱不平（讥弹更到无香处常恨人言太刻深）。编者陈思是理宗朝临安书坊主，又编宝刻丛编书小史，序中自承采取诸家杂录彚次唐以来诗句聊预众谱之列，坊贾为花立传，宋代市籍文化的胃口由此可见。版式＝夜园点烛壳（石青）：首屏夜园墙下一枝海棠睡在暗处，点烛光晕亮花蕾显形书名落定钤红妆印；杜甫公案三折卷宗开合；花开三段色卡（胭脂点点缬晕宿妆淡粉）；墨迹本对照表；九张竖排诗笺右起读；六则逸事翻牌；花政三条方笺（冬至糟水浇根花谢剪子美女美男比量对法）；书坊专栏竖排铺号；尾屏竖排陆游诗钤红妆印。校字记：库本OCR讹字照录不归一（麄即粗、侯花谢即候花谢、彚次即汇次、大槩即大概等）。时代局限：以花拟人、花命妇花戚里诸品第与以妃子睡未足论花诸端皆宋人品花风尚底色，照录存照，不代今人立论。引文经脚本自库本锚点切片生成、去标点归一逐字比对通过（四十八q，白话反扫六字窗零撞）。</small></span>
        <span class="file mono">haitang-pu.html</span>
      </a>
    </div>
  </div>
'''

    anchor = '</footer>'
    assert html.count(anchor) == 1
    html = html.replace(anchor, VOL + anchor)

    assert html.count(f'卷{vno_cn} · 红妆') == 1
    assert html.count(f'<span class="no mono">{no}</span>') == 1
    assert html.count('红妆卷照花') == 1
    vols2 = [cn2int(v) for v in re.findall(r'<h2>卷([一二三四五六七八九十百零]+) · ', html)]
    assert vols2[-1] == vno, 'FAIL: 新卷未落在末位'
    open(MULU, 'w', encoding='utf-8').write(html)
    print(f'OK: 篇号{no} 卷{vno_cn}(第{vno}卷)·红妆 已插入 mulu')

if __name__ == '__main__':
    sys.exit(main())
