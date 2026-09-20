#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""单刀会 mulu 插入：编号/卷序动态取 max+1，防并行撞号"""
import re, sys

P = "/home/robertsong/workspace/claude/daizhige-daodu/mulu.html"
s = open(P, encoding="utf-8").read()
assert "dandaohui.html" not in s, "已插入过"

CN = "零一二三四五六七八九"
FIN = "零壹贰叁肆伍陆柒捌玖"

def cn2int(t):
    total, num = 0, 0
    for ch in t:
        if ch in CN:
            num = CN.index(ch)
        elif ch in FIN:
            num = FIN.index(ch)
        elif ch in ("十", "拾"):
            total += (num or 1) * 10; num = 0
        elif ch == "百":
            total += (num or 1) * 100; num = 0
        elif ch == "千":
            total += (num or 1) * 1000; num = 0
        elif ch == "零":
            pass
    return total + num

def int2cn(n, fin):
    D = FIN if fin else CN
    shi = "拾" if fin else "十"
    out = ""
    if n >= 1000:
        out += D[n // 1000] + "千"; n %= 1000
        if 0 < n < 100: out += D[0]
    if n >= 100:
        out += D[n // 100] + "百"; n %= 100
        if 0 < n < 10: out += D[0]
    if n >= 10:
        d = n // 10
        if not (d == 1 and out == ""):
            out += D[d]
        out += shi; n %= 10
    if n:
        out += D[n]
    return out

nos = [int(m) for m in re.findall(r'<span class="no mono">(\d+)</span>', s)]
assert len(nos) == len(set(nos)), "mulu 已有重号"
myno = max(nos) + 1

juan_nums = [cn2int(t) for t in re.findall(r"<h2>卷([一二三四五六七八九十百零]+) · ", s)]
myjuan = max(juan_nums) + 1
assert myjuan == cn2int(int2cn(myjuan, False)), "int2cn自检失败"
assert s.count("· 中流<") == 0, "卷名已占"

BLOCK = """  <div class="vol" style="--vc: var(--c3)">
    <div class="wrap">
      <div class="vol-head">
        <div class="vseal" style="background: var(--c3)">{VSEAL}</div>
        <h2>卷{JUAN} · 中流</h2>
        <div class="vsub">石青 · 元杂剧</div>
      </div>
      <p class="vol-desc">一场被名字剧透干净的鸿门宴：前三折满台都是替关羽背书的人，主角第四折才驾一叶小舟进大江，两支曲子唱了七百年。本卷收〈关大王独赴单刀会〉导读一篇，页面做成中流一叶壳（石青）。</p>
      <a class="entry" href="dandaohui.html">
        <span class="no mono">{NO}</span>
        <span class="ti">关大王独赴单刀会<small>元大都人关汉卿撰，据诗藏剧曲库本，去空白九千三百五十字，四折：折壹鲁肃献三计、乔公数说关羽威名；折贰司马徽推病辞筵、道童抢话；折叁关羽受书、关平问险、黄文自咒；折肆大江中流两支名曲、席上剑戒破镜、扣鲁肃下船收梢。书眼＝传说先于人物到达：戏名把结局全说完了，写法却把主角藏到第四折才登场，前三折满台只有替他背书的人（乔公说其威、司马徽说其怒、关平说其险）；元杂剧正末一人主唱，大轴演员前两折扮劝阻者亲手唱尽关羽的可怕，末两折才改扮本人。看点＝三计三条下场（以礼索取被一句顶回、尽拘战船反押主人陪送、壁衣伏甲被一声击案喝散）、二十年流不尽的英雄血、剑戒三遭、我特来破镜、道童自编缩头乌龟下场、黄文黄泉预报。版式＝中流一叶壳（石青）：首屏横江大水带一叶小舟可点江起波配四折签导航，折屏四扇点亮式亮相，三计牌各挂下场锚，中流双曲击节起唱逐句显形收于血色句，席上菱花镜点碎显我特来破镜，尾声竖排双列钤汉节印并题目正名题壁。校字记：k溪、粗j、大车无m小车无n等库本拉丁残字照录不引，觅二反疑为觅二嫂存照。时代局限：以宴席刀兵相胁、尊刘贬吴正统观、全剧无女性角色而婚姻只作筹码，皆时代产物，请以今日眼光辨之。引文经脚本自库本切片、去标点归一逐字比对通过（四十九q，白话反扫六字窗零撞）。</small></span>
        <span class="file mono">dandaohui.html</span>
      </a>
    </div>
  </div>
</footer>"""

block = BLOCK.format(
    VSEAL=int2cn(myjuan, True),
    JUAN=int2cn(myjuan, False),
    NO=myno,
)
assert s.count("</footer>") == 1
s = s.replace("</footer>", block, 1)
open(P, "w", encoding="utf-8").write(s)
print("inserted: no=%d juan=%d vseal=%s" % (myno, myjuan, int2cn(myjuan, True)))
