#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把行在阳秋插入 mulu.html：断言编号/卷号/卷名未占用，新增文案过六字窗反扫。"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MULU = os.path.join(HERE, 'mulu.html')
SRC = os.path.join(HERE, '..', 'daizhige-simplified', '史藏', '志存记录', '行在阳秋.txt')

NO = '482'
JUAN = '卷三百六十一'
SEAL = '叁百陆拾壹'
MING = '蒙尘'
FILE = 'xingzai-yangqiu.html'

DESC = ('一部不知道皇帝明天在哪里的编年史：撰人佚名，按月按日记永历朝廷十六年，每条先报驻地，'
        '从肇庆府署一路记到缅甸竹城草房，记到君臣俱尽、历日失考为止。本卷收〈行在阳秋〉导读一篇，'
        '页面做成残历壳：首屏残历页揭历翻落，书名竖排显形钤行在印，日晷影针随全页滚动西斜；'
        '行在谱十六枚驻地牌逐牌点读，先内讧短札交代同室操戈的起点；守土者纸白三幕演瞿式耜枵腹守城'
        '与张同敞泅水来同死，绝命诗竖排右起；荒诞档四卡收水殿牌匾、经筵问难、碎玺散银与假敕截驾；'
        '称帝者时间线六节点从一句戏词到出猎场；咒水七翻牌朱砂段；旧晚坡君臣对峙双栏，拉弦后全屏入夜；'
        '尾屏纸白历犹在编三签，竖排收梢钤阳秋印。引文经脚本自库本锚点切片生成、去标点归一逐字比对通过'
        '（八十q，白话反扫六字窗零撞）。')

TI = ('明末清初撰人佚名，据史藏志存记录库本，去空白约二万九千字，上下两卷编年：上卷起隆武二年冬监国肇庆事，'
      '讫永历五年；下卷起永历六年，讫康熙元年，卷中时有施氏曰史论与杂录附记考异。书眼＝行在二字：'
      '天子驻跸之所，这部书里行在换了近二十处，从肇庆、桂林、全州、武冈、柳州、南宁、端州到安隆小城、'
      '滇都、永昌，再入缅甸井梗、者梗，一支朝廷的地址簿越写越荒。名场面：瞿式耜守桂林，城中断粮，'
      '把署中存米蒸饭分给守卒；城破时端坐署中等清兵来，张同敞泅水过江求同死，被执四十日，'
      '刑前互道多活四十日与得死所；梧州楼船置酒，宰相题水殿二字挂船头，民谣以两位宰相的表字入歌相讥；'
      '安隆十八先生之狱；李定国复桂林，清藩自尽；孙可望降清后陪猎被射死；缅甸咒水之难一夜杀尽从官，'
      '黔国公夺刀，十三岁小厮诈称给银拔刀刺兵；旧晚坡交割，吴三桂入见由倨傲而噤声而伏地汗流；'
      '龚彝进酒毕触地而死；末代太子临刑骂贼语与当日天昏风霾；附记引时人说死期与本书编年不合，'
      '自称未知何据，一部史书在最后一行承认存疑。版式＝残历壳（赭金）：首屏残历翻页书名显形钤行在印，'
      '日晷影针随滚动西斜；行在谱驻地牌十六枚分四级渐暗；守土者纸白三幕含绝命诗竖排右起；荒诞档四卡；'
      '称帝者时间线六节点；咒水七翻牌；旧晚坡对峙双栏加拉弦入夜机关；尾屏历犹在编三签竖排收梢钤阳秋印。'
      '校字记：库本枵号疑为枵腹之讹、雷霆冬发疑为雷动之讹、绝命诗一联带自主与主张两读校勘残留，'
      '均照录不归一；库本补字符与缺字号处引文避让。时代局限：对缅人及边地诸族多用蔑称、'
      '忠君死节观与屠城锯解炙尸等暴力直录皆时代底色，照录立此存照，不代今人立论。'
      '引文经脚本自库本锚点切片生成、去标点归一逐字比对通过（八十q，白话反扫六字窗零撞）。')

PUNCT = re.compile(r'[\s\W_a-zA-Z0-9]+', re.UNICODE)

def block():
    return (
        '  <div class="vol" style="--vc: var(--c4)">\n'
        '    <div class="wrap">\n'
        '      <div class="vol-head">\n'
        '        <div class="vseal" style="background: var(--c4); font-size: 15px">%s</div>\n'
        '        <h2>%s · %s</h2>\n'
        '        <div class="vsub">赭金 · 史藏志存记录</div>\n'
        '      </div>\n'
        '      <p class="vol-desc">%s</p>\n'
        '      <a class="entry" href="%s">\n'
        '        <span class="no mono">%s</span>\n'
        '        <span class="ti">行在阳秋<small>%s</small></span>\n'
        '        <span class="file mono">%s</span>\n'
        '      </a>\n'
        '    </div>\n'
        '  </div>\n'
    ) % (SEAL, JUAN, MING, DESC, FILE, NO, TI, FILE)

def main():
    mulu = open(MULU, encoding='utf-8').read()
    src = PUNCT.sub('', open(SRC, encoding='utf-8').read())
    fails = 0

    for marker, name in [('no mono">%s<' % NO, '编号%s' % NO),
                         (JUAN, JUAN), (SEAL, SEAL), ('· %s<' % MING, '卷名%s' % MING),
                         (FILE, '文件名')]:
        if marker in mulu:
            print('FAIL: %s 已被占用' % name); fails += 1

    for text, label in [(DESC, 'vol-desc'), (TI, 'ti')]:
        plain = PUNCT.sub('', text)
        hits = sorted({plain[i:i + 6] for i in range(len(plain) - 5) if plain[i:i + 6] in src})
        if hits:
            print('FAIL: %s 反扫命中 %d: %s' % (label, len(hits), hits[:8])); fails += 1

    if fails:
        return 1

    anchor = '\n</footer>'
    assert anchor in mulu and mulu.count(anchor) == 1
    mulu = mulu.replace(anchor, '\n' + block() + '\n</footer>')
    open(MULU, 'w', encoding='utf-8').write(mulu)
    print('MULU OK: %s · %s · 编号%s' % (JUAN, MING, NO))
    return 0

if __name__ == '__main__':
    sys.exit(main())
