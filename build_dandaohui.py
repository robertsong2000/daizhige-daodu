#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""单刀会导读页构建：库本切片注入（零誊写）→ dandaohui.html"""
LIB = "/home/robertsong/workspace/claude/daizhige-simplified/诗藏/剧曲/关大王独赴单刀会.txt"
OUT = "/home/robertsong/workspace/claude/daizhige-daodu/dandaohui.html"

lib = open(LIB, encoding="utf-8").read()

def cut(start, end=None):
    assert lib.count(start) == 1, "起锚不唯一: " + start
    if end is None:
        return start
    assert lib.count(end) == 1, "止锚不唯一: " + end
    i = lib.index(start)
    j = lib.index(end)
    assert j >= i, "止锚在起锚前"
    return lib[i:j + len(end)]

def cut2(start, end):
    """止锚允许多见，取起锚之后的第一处。"""
    assert lib.count(start) == 1, "起锚不唯一: " + start
    i = lib.index(start)
    j = lib.index(end, i)
    return lib[i:j + len(end)]

Q = {
    "shangshi":  cut("三尺龙泉万卷书", "彼丈夫兮我丈夫。"),
    "jindaner":  cut("你则索多披上几副甲", "偃月三停刀。"),
    "fuqiao":    cut("你道是岸边厢拘了战船", "水面上搭座浮桥！"),
    "tiaopao":   cut("关云长道", "斜挑锦征袍。"),
    "ji1":       cut("就于饮酒席中间，以礼索取荆州。"),
    "ji2":       cut("将江上应有战船，尽行拘收，不放关公渡江回去。"),
    "ji3":       cut2("第三计：壁衣内暗藏甲士", "囚于江下。"),
    "shiti":     cut("你便休题安排着酒肉", "完全尸首。"),
    "wanchou":   cut("只为你千年勋业三条计", "魂魄悠悠。"),
    "bashiyi":   cut("他圆睁开丹凤眸", "八十一座军州！"),
    "tong1":     cut("我下山赴会走一遭去", "两手送你那荆州。"),
    "tong2":     cut("恼犯云长歹事头", "汴河里走。"),
    "badou":     cut("那里有凤凰杯满捧琼花酿", "巴豆、砒霜！"),
    "zhanchang": cut("也不是待客筵席", "杀人的战场。"),
    "jugong":    cut("我着那厮鞠躬、鞠躬送我到船上。"),
    "huangwen":  cut("小将是黄文", "那里寻黄文？"),
    "wuguan":    cut("单刀会不去呵", "五关斩将。"),
    "huanlai":   cut("欢来不似今朝，喜来那逢今日？"),
    "x1": cut("大江东去浪千叠，"),
    "x2": cut("引着这数十人驾着这小舟一叶。"),
    "x3": cut("又不比九重龙凤阙，"),
    "x4": cut("可正是千丈虎狼穴。"),
    "x5": cut("大丈夫心别，"),
    "x6": cut("我觑这单刀会似赛村社。"),
    "z1": cut("水涌山叠，"),
    "z2": cut("年少周郎何处也？"),
    "z3": cut("不觉的灰飞烟灭，"),
    "z4": cut("可怜黄盖转伤嗟。"),
    "z5": cut("破曹的樯橹一时绝，"),
    "z6": cut("鏖兵的江水犹然热，"),
    "z7": cut("好教我情惨切！"),
    "z8": cut("这也不是江水，"),
    "z9": cut("二十年流不尽的英雄血！"),
    "suo":       cut("你请我吃筵席来那，是索荆州来？"),
    "jieKou":    cut("我根前使不着你", "早该豁口截舌！"),
    "jiuzui":    cut("休怪我十分酒醉也。"),
    "xiangbie":  cut("好生的送我到船上者", "慢慢的相别。"),
    "jianjie":   cut("我这剑戒，头一遭", "第三遭到你也？"),
    "yanerluo":  cut("则为你三寸不烂舌", "渴饮仇人血。"),
    "maifu":     cut("有埋伏也无埋伏？"),
    "lingshi":   cut("你击碎菱花。"),
    "pojing":    cut("我特来破镜！"),
    "liangjian": cut("说与你两件事先生记者", "俺汉家节。"),
    "tiMu":      cut2("题目 孙仲谋独占江东地", "关大王独赴单刀会"),
    "doufu":     cut("来便吃筵席", "豆腐酒吃三钟。"),
}

TPL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>单刀会 · 殆知阁导读</title>
<style>
:root{--bg:#191917;--paper:#e8e4dc;--ink:#26241f;--qing:#5e8fbb;--qing-l:#9dbede;--qing-d:#3c5a7e;--xue:#8e4636;--mut:#8a857a;--line:#3a382f}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--paper);font-family:"Songti SC","STSong","Noto Serif CJK SC","Source Han Serif SC","SimSun",serif;line-height:1.9;font-size:16px}
.wrap{max-width:1080px;margin:0 auto;padding:0 28px}
a{color:var(--qing-l)}
q{quotes:none}
.fp{opacity:0;transform:translateY(14px);transition:opacity .6s ease,transform .6s ease}
.fp.on{opacity:1;transform:none}
h2{font-size:25px;font-weight:600;letter-spacing:.08em}
.bai{font-size:15px;color:#c9c4b8}

/* ===== 侧舷行舟 ===== */
.rail{position:fixed;left:16px;top:50%;transform:translateY(-50%);height:44vh;width:2px;background:var(--line);z-index:5;pointer-events:none;display:none}
.rail .bb{position:absolute;left:-8px;width:18px;height:18px;transition:top .1s linear}
@media (min-width:1180px){.rail{display:block}}

/* ===== hero 中流 ===== */
.hero{min-height:96vh;display:flex;align-items:center;position:relative;overflow:hidden;border-bottom:1px solid var(--line)}
.hero-grid{display:grid;grid-template-columns:230px 1fr;gap:46px;align-items:center;width:100%;position:relative;z-index:2}
.kick{color:var(--qing-l);font-size:13px;letter-spacing:.34em;margin-bottom:20px}
.vtitle{writing-mode:vertical-rl;font-size:112px;line-height:1.08;font-weight:600;letter-spacing:.18em;height:max-content;white-space:nowrap}
.vtitle b{color:var(--qing-l);font-weight:inherit}
.vsub{writing-mode:vertical-rl;font-size:15px;letter-spacing:.5em;color:var(--mut);margin-left:14px;height:220px}
.hmeta{margin-top:22px;color:var(--mut);font-size:14px;letter-spacing:.14em;border-top:1px solid var(--line);padding-top:14px;width:170px}
.river-r{display:flex;flex-direction:column;align-items:center;gap:24px}
.riverbox{width:min(560px,94%);cursor:pointer}
.riverbox svg{display:block;width:100%}
.ripple{animation:rip 1.2s ease-out forwards}
@keyframes rip{from{opacity:.85}to{opacity:0}}
.jian{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}
.jian a{appearance:none;background:#1e232b;border:1px solid #41566e;color:var(--paper);cursor:pointer;font-family:inherit;writing-mode:vertical-rl;padding:18px 9px 12px;height:140px;letter-spacing:.22em;font-size:15px;text-decoration:none;position:relative;transition:border-color .3s,color .3s,transform .3s}
.jian a::before{content:"";position:absolute;bottom:-10px;left:50%;transform:translateX(-50%);width:2px;height:10px;background:#41566e}
.jian a i{font-style:normal;font-size:11px;color:var(--qing-l);letter-spacing:.3em;display:block;margin-bottom:10px}
.jian a:hover{border-color:var(--qing);color:var(--qing-l);transform:translateY(-4px)}
.hintro{max-width:640px;margin:32px auto 0;text-align:center;color:#c9c4b8;font-size:15px}
.hintro b{color:var(--qing-l);font-weight:600}

/* ===== 折屏 ===== */
.screens-sec{border-top:1px solid var(--line);background:#1b1d20}
.screens-sec .wrap{padding-top:70px;padding-bottom:70px}
.screens-bai{max-width:760px;margin-bottom:34px}
.screens-bai b{color:var(--qing-l);font-weight:600}
.screens{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.zhe{background:#22252a;border:1px solid #343b44;min-height:330px;padding:22px 16px;cursor:pointer;display:flex;flex-direction:column;transition:background .4s,border-color .4s}
.zhe .zi{writing-mode:vertical-rl;font-size:40px;font-weight:600;letter-spacing:.24em;color:var(--mut);transition:color .4s}
.zhe .who{margin-top:14px;font-size:13px;color:var(--mut);letter-spacing:.16em}
.zhe .st{margin-top:auto;font-size:12px;color:#5c636d;letter-spacing:.14em}
.zhe .neat{max-height:0;overflow:hidden;transition:max-height .5s ease,margin .5s ease;font-size:13.5px;color:#c9c4b8;line-height:1.9}
.zhe.lit{background:#2a3543;border-color:var(--qing-d)}
.zhe.lit .zi{color:var(--qing-l)}
.zhe.lit .st{color:var(--qing-l)}
.zhe.lit .neat{max-height:170px;margin-top:16px;border-top:1px dashed #41566e;padding-top:12px}

/* ===== 折次章 ===== */
.act{border-top:1px solid var(--line)}
.act .wrap{display:grid;grid-template-columns:130px 1fr;gap:46px;padding-top:64px;padding-bottom:64px}
.act-side{display:flex;gap:16px;align-items:flex-start;justify-content:flex-end}
.zheNo{writing-mode:vertical-rl;font-size:14px;color:var(--qing-l);letter-spacing:.4em;white-space:nowrap;border-right:1px solid var(--line);padding-right:14px;height:max-content}
.zheTi{writing-mode:vertical-rl;font-size:46px;font-weight:600;letter-spacing:.3em;white-space:nowrap;height:max-content}
.act-no{font-size:12px;color:var(--mut);letter-spacing:.2em;margin-bottom:12px}
.act-bai{max-width:720px;margin-bottom:24px}
.qrow{display:grid;gap:16px}
.qrow.two{grid-template-columns:1fr 1fr}
.qc{background:var(--paper);color:var(--ink);padding:24px 26px 20px;position:relative;box-shadow:0 14px 36px rgba(0,0,0,.38)}
.qc::before{content:"";position:absolute;left:0;right:0;top:0;height:3px;background:var(--qing)}
.qc .tag{position:absolute;top:-11px;left:20px;background:var(--qing);color:#fff;font-size:11.5px;letter-spacing:.22em;padding:3px 12px}
.qc q{display:block;font-size:16.5px;line-height:2;color:#2c3440;letter-spacing:.03em}
.qc q::before{content:"「";color:var(--qing-d)}
.qc q::after{content:"」";color:var(--qing-d)}
.qc.dk{background:#1e2126;border:1px solid #41566e;box-shadow:none}
.qc.dk::before{background:var(--xue)}
.qc.dk .tag{background:var(--xue)}
.qc.dk q{color:var(--qing-l)}
.qc.dk q::before,.qc.dk q::after{color:var(--xue)}
.qc .cmt{margin-top:12px;font-size:13px;color:#6d675a;letter-spacing:.06em}
.qc.dk .cmt{color:var(--mut)}
.lead-q{margin-top:4px;margin-bottom:12px;font-size:14.5px;color:var(--mut)}
.after-q{margin-top:16px;max-width:720px}

/* ===== 三计牌 ===== */
.ji3{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:28px}
.ji{background:#1e2126;border:1px solid #41566e;padding:26px 24px 22px;position:relative;display:flex;flex-direction:column;gap:14px}
.ji::after{content:attr(data-ji);position:absolute;top:-13px;right:18px;background:var(--bg);border:1px solid var(--qing-d);color:var(--qing-l);font-size:12px;letter-spacing:.3em;padding:3px 12px}
.ji q{display:block;font-size:15px;line-height:2;color:#c9c4b8}
.ji q::before{content:"「";color:var(--qing-d)}
.ji q::after{content:"」";color:var(--qing-d)}
.ji .go{margin-top:auto;align-self:flex-start;font-size:12.5px;letter-spacing:.2em;color:var(--qing-l);text-decoration:none;border-bottom:1px solid var(--qing-d);padding-bottom:2px}
.ji .go:hover{color:#fff;border-color:#fff}

/* ===== 中流双曲 ===== */
.qu{border-top:1px solid var(--line);background:#15181c}
.qu .wrap{padding-top:76px;padding-bottom:76px;text-align:center}
.qu-bai{max-width:700px;margin:0 auto 14px;text-align:left}
.qu-bai q{color:var(--qing-l)}
.qu-h{margin:40px 0 8px;font-size:14px;letter-spacing:.4em;color:var(--qing-l)}
.gest{display:inline-block;appearance:none;background:none;border:1px solid var(--qing);color:var(--qing-l);font-family:inherit;font-size:14px;letter-spacing:.3em;padding:10px 26px;cursor:pointer;margin:26px 0 34px;transition:background .3s,color .3s}
.gest:hover{background:var(--qing);color:#fff}
.geQu{max-width:640px;margin:0 auto;text-align:left}
.kl{display:block;font-size:19px;line-height:2.2;letter-spacing:.05em;color:var(--paper);opacity:0;transform:translateY(10px);transition:opacity .55s ease,transform .55s ease}
.kl.on{opacity:1;transform:none}
.kl.xl{color:#c47a6a;font-size:22px;font-weight:600}
.qu-note{margin-top:30px;font-size:13px;color:var(--mut)}

/* ===== 席上 ===== */
.xi .wrap{display:block}
.xi-head{display:flex;align-items:baseline;gap:18px;margin-bottom:8px}
.xi-grid{display:grid;grid-template-columns:1.1fr .9fr;gap:34px;align-items:start;margin-top:26px}
.xia{display:grid;gap:16px;margin-bottom:34px}
.xia .qc .tag{left:auto;right:20px}
.jianjie-q q{font-size:18px}
.mirror-stage{position:relative;height:300px;display:flex;align-items:center;justify-content:center;margin-bottom:18px;cursor:pointer}
.mirror-stage .pojing-t{position:absolute;font-size:30px;font-weight:600;letter-spacing:.24em;color:var(--paper);opacity:0;transition:opacity .9s ease .5s;pointer-events:none}
.mirror-stage.broken .pojing-t{opacity:1}
.mirror-stage svg{cursor:pointer;max-width:100%;transition:opacity .8s ease .3s}
.mirror-stage.broken svg{opacity:.13}
.mirror-stage .shard{transition:transform .85s ease,opacity .85s ease}
.mirror-stage.broken .s1{transform:translate(-46px,-38px) rotate(-14deg);opacity:0}
.mirror-stage.broken .s2{transform:translate(44px,-46px) rotate(11deg);opacity:0}
.mirror-stage.broken .s3{transform:translate(-52px,36px) rotate(9deg);opacity:0}
.mirror-stage.broken .s4{transform:translate(50px,42px) rotate(-10deg);opacity:0}
.mirror-stage .crk{stroke-dasharray:300;stroke-dashoffset:300;transition:stroke-dashoffset .45s ease}
.mirror-stage.broken .crk{stroke-dashoffset:0}
.mirror-tip{font-size:12.5px;color:var(--mut);letter-spacing:.16em;text-align:center}

/* ===== 尾声 ===== */
.coda{border-top:1px solid var(--line);text-align:center}
.coda .wrap{padding-top:90px;padding-bottom:76px}
.coda-bai{max-width:700px;margin:0 auto 26px;text-align:left}
.coda-bai q{color:var(--qing-l)}
.tibi{background:var(--paper);color:var(--ink);max-width:620px;margin:34px auto;padding:34px 30px;box-shadow:0 16px 40px rgba(0,0,0,.4);position:relative}
.tibi::before{content:"";position:absolute;left:0;right:0;top:0;height:3px;background:var(--xue)}
.tibi .tb-tag{position:absolute;top:-11px;left:20px;background:var(--xue);color:#fff;font-size:11.5px;letter-spacing:.22em;padding:3px 12px}
.tibi q{display:block;white-space:pre-line;font-size:18px;line-height:2.1;color:#2c3440;letter-spacing:.06em}
.coda-vert{display:flex;justify-content:center;align-items:flex-start;gap:54px;margin:44px 0 40px}
.big-vert{writing-mode:vertical-rl;font-size:52px;font-weight:600;letter-spacing:.26em;line-height:1.3;height:max-content;white-space:nowrap;color:var(--paper)}
.big-vert b{color:var(--qing-l);font-weight:inherit}
.big-vert.xv b{color:#c47a6a}
.fancha{max-width:700px;margin:0 auto;text-align:left;border:1px dashed #41566e;padding:20px 24px;font-size:14px;color:#b5ad9c}
.fancha b{color:var(--qing-l);font-weight:600}
.seal{display:inline-grid;place-items:center;width:84px;height:84px;border:3px solid var(--qing);color:var(--qing-l);font-size:30px;font-weight:600;letter-spacing:.1em;transform:rotate(-3deg);margin-top:40px;line-height:1.2;padding:8px}

footer{border-top:1px solid var(--line);padding:34px 0 44px;color:var(--mut);font-size:13px;line-height:2}
footer a{color:var(--qing-l)}

@media (max-width:820px){
  .hero-grid{grid-template-columns:1fr;gap:26px}
  .vtitle{font-size:64px}
  .vsub{height:auto;writing-mode:horizontal-tb;margin-left:0;letter-spacing:.4em}
  .hmeta{width:100%}
  .screens{grid-template-columns:repeat(2,1fr)}
  .zhe{min-height:250px}
  .act .wrap{grid-template-columns:1fr;gap:16px;padding-top:48px;padding-bottom:48px}
  .act-side{justify-content:flex-start;align-items:baseline;flex-direction:row-reverse;gap:14px}
  .zheNo{writing-mode:horizontal-tb;border-right:none;padding-right:0;height:auto}
  .zheTi{writing-mode:horizontal-tb;font-size:30px;height:auto}
  .qrow.two{grid-template-columns:1fr}
  .ji3{grid-template-columns:1fr}
  .xi-grid{grid-template-columns:1fr}
  .coda-vert{gap:24px}
  .big-vert{font-size:34px}
  .jian a{height:110px;padding:12px 8px 10px}
}
</style>
</head>
<body>

<div class="rail" aria-hidden="true">
  <svg class="bb" viewBox="0 0 20 20"><path d="M2 13 Q10 17 18 13 L15 16 Q10 18 5 16 Z" fill="#5e8fbb"/><line x1="10" y1="3" x2="10" y2="12" stroke="#5e8fbb" stroke-width="1.6"/><path d="M10 3 L16 9 L10 9 Z" fill="#9dbede"/></svg>
</div>

<section class="hero" id="top">
  <div class="wrap hero-grid">
    <div>
      <div class="kick">诗藏 ｜ 剧曲</div>
      <div style="display:flex">
        <h1 class="vtitle">单<b>刀</b>会</h1>
        <div class="vsub">关大王独赴</div>
      </div>
      <div class="hmeta">元 ｜ 大都 关汉卿</div>
    </div>
    <div class="river-r">
      <div class="riverbox" id="riverbox" title="点一点江面">
        <svg viewBox="0 0 560 330" aria-hidden="true">
          <rect x="0" y="0" width="560" height="330" fill="#151a20"/>
          <path d="M0 96 Q70 84 140 96 T280 96 T420 96 T560 96" fill="none" stroke="#5e8fbb" stroke-width="2" opacity=".38"/>
          <path d="M0 148 Q70 136 140 148 T280 148 T420 148 T560 148" fill="none" stroke="#5e8fbb" stroke-width="2.4" opacity=".5"/>
          <path d="M0 206 Q70 194 140 206 T280 206 T420 206 T560 206" fill="none" stroke="#9dbede" stroke-width="2" opacity=".34"/>
          <path d="M0 262 Q70 250 140 262 T280 262 T420 262 T560 262" fill="none" stroke="#5e8fbb" stroke-width="2" opacity=".26"/>
          <g id="ripples"></g>
          <g id="boat">
            <animateTransform attributeName="transform" type="translate" values="0 0;0 5;0 0" dur="3.4s" repeatCount="indefinite"/>
            <path d="M212 176 Q280 196 348 176 L332 190 Q280 200 228 190 Z" fill="#26241f" stroke="#e8e4dc" stroke-width="2"/>
            <line x1="280" y1="176" x2="280" y2="118" stroke="#e8e4dc" stroke-width="2.4"/>
            <path d="M280 122 Q322 134 318 160 L280 156 Z" fill="#5e8fbb" opacity=".85"/>
            <line x1="304" y1="128" x2="322" y2="146" stroke="#e8e4dc" stroke-width="3"/>
            <line x1="300" y1="133" x2="293" y2="140" stroke="#e8e4dc" stroke-width="1.6"/>
          </g>
          <text x="34" y="52" fill="#8a857a" font-size="15" letter-spacing="6" font-family="serif">大江东去</text>
          <text x="452" y="308" fill="#4a5563" font-size="12" letter-spacing="4" font-family="serif">驾一叶小舟</text>
        </svg>
      </div>
      <nav class="jian" role="navigation" aria-label="四折导航">
        <a href="#zhe1"><i>折壹</i>乔公</a>
        <a href="#zhe2"><i>折贰</i>水鉴</a>
        <a href="#zhe3"><i>折叁</i>提刀</a>
        <a href="#zhongliu"><i>折肆</i>中流</a>
      </nav>
      <p class="hintro">大都书会里最深谙观众心理的一手：戏名把结局全说完了，主角却压轴到第四折才露面。前三折满台都是鲁肃请来的客人，一个接一个劝他别开这场席；等真主角驾一叶小舟进了大江，<b>两句唱</b>就把全戏送进了元曲的顶点。库本四折，去空白九千三百五十字。</p>
    </div>
  </div>
</section>

<section class="screens-sec" id="zheping">
  <div class="wrap">
    <p class="screens-bai bai fp">这出戏最聪明的地方，是<b>传说先于人物到达</b>。前三折台上根本没有关羽，只有三个替他背书的人：乔公说他的威，司马徽说他的怒，关平说他的险。观众的期待被一层层垫高，等船进大江，人还没开口，气场已经满了。还有一层排场上的讲究：元杂剧一本戏只有正末一人主唱，这位大轴演员前两折扮乔公、扮司马徽，亲手把关羽的可怕唱尽，末两折才改扮关羽本人。点一点每一扇屏。</p>
    <div class="screens fp">
      <div class="zhe" data-zhe>
        <div class="zi">折壹</div>
        <div class="who">台上：乔公</div>
        <div class="st">关羽未登场</div>
        <div class="neat">东吴的老国戚把博望与赤壁讲了一遍，替关羽把威名过了一堂堂之堂。</div>
      </div>
      <div class="zhe" data-zhe>
        <div class="zi">折贰</div>
        <div class="who">台上：司马徽</div>
        <div class="st">关羽未登场</div>
        <div class="neat">一听有关羽当场推病。劝到后来，把自己的全尸都赔进去算了这笔账。</div>
      </div>
      <div class="zhe" data-zhe>
        <div class="zi">折叁</div>
        <div class="who">台上：关平</div>
        <div class="st">关羽登了场，在自家</div>
        <div class="neat">父亲接了请书，儿子一路追问。答话一句比一句大，险字全说在自己嘴里。</div>
      </div>
      <div class="zhe lit" data-zhe>
        <div class="zi">折肆</div>
        <div class="who">台上：关羽、鲁肃</div>
        <div class="st">正主登场</div>
        <div class="neat">中流一叶。两支曲子成了七百年的名唱，起手写江，收梢写血。</div>
      </div>
    </div>
  </div>
</section>

<section class="act" id="zhe1">
  <div class="wrap">
    <div class="act-side fp"><span class="zheNo">折壹</span><span class="zheTi">说刀</span></div>
    <div>
      <div class="act-no fp">第一折 ｜ 鲁肃府中</div>
      <p class="act-bai bai fp">鲁肃开场自报家门，一套三计说得眉飞色舞：先请客，席间好言索取；不给，就扣下江上所有战船；再不给，壁衣后头埋伏甲士，敲金钟为号一齐动手。他先去问乔公。老国戚把博望烧屯和赤壁大火从头讲了一遍，讲到百万军中取上将首级，只留下一句皮里阳秋的忠告：你要真扣了他的船，就得在水面上给他搭座桥。</p>
      <div class="qrow two fp">
        <div class="qc"><span class="tag">折壹</span><q>@@shangshi@@</q><div class="cmt">鲁肃的上场诗。他把对手与自己并称大丈夫，五个字先把自己摆进了对手的传说里。</div></div>
        <div class="qc dk"><span class="tag">折壹</span><q>@@jindaner@@</q><div class="cmt">乔公给鲁肃开的装备清单：多披几副甲，再穿上几层袍。</div></div>
      </div>
      <div class="qrow after-q fp">
        <div class="qc"><span class="tag">折壹</span><q>@@fuqiao@@</q><div class="cmt">说与唱之间的小注（云）（唱）照录，元杂剧的接缝就在这里。</div></div>
      </div>
      <div class="qrow after-q fp">
        <div class="qc dk"><span class="tag">折壹</span><q>@@tiaopao@@</q><div class="cmt">乔公收梢讲的旧事：灞陵桥上刀尖挑袍。曹操的三条计，一条没出过关羽的手。</div></div>
      </div>
      <div class="lead-q after-q fp">三计原文，鲁肃亲口，两条计牌各留一个锚，看它们在第四折怎么一条一条破产。</div>
      <div class="ji3 fp">
        <div class="ji" data-ji="计壹"><q>@@ji1@@</q><a class="go" href="#xia1">看这条计的下场</a></div>
        <div class="ji" data-ji="计贰"><q>@@ji2@@</q><a class="go" href="#xia2">看这条计的下场</a></div>
        <div class="ji" data-ji="计叁"><q>@@ji3@@</q><a class="go" href="#xia3">看这条计的下场</a></div>
      </div>
    </div>
  </div>
</section>

<section class="act" id="zhe2">
  <div class="wrap">
    <div class="act-side fp"><span class="zheNo">折贰</span><span class="zheTi">辞筵</span></div>
    <div>
      <div class="act-no fp">第二折 ｜ 江下草庵</div>
      <p class="act-bai bai fp">第二折换了位证人：水鉴先生司马徽，当年荐过卧龙的名士。鲁肃请他赴会作陪，他一听有关羽，当场改口风疾发作，去不得。劝到后来，他把自己的下场都替鲁肃算好了：陪你坐这一席，咱两个谁都留不下全尸。倒是身边的小道童不知天高地厚，抢过话头要替师父走一遭。</p>
      <div class="qrow fp">
        <div class="qc dk"><span class="tag">折贰</span><q>@@shiti@@</q></div>
      </div>
      <div class="qrow two after-q fp">
        <div class="qc"><span class="tag">折贰</span><q>@@wanchou@@</q><div class="cmt">司马徽反问鲁肃：我的千年道行，抵你哪一条计？</div></div>
        <div class="qc dk"><span class="tag">折贰</span><q>@@bashiyi@@</q><div class="cmt">丹凤眸、卧蚕眉、五蕴山烈火：前三折里关羽的相貌，全是从旁观者嘴里拼出来的。</div></div>
      </div>
      <div class="lead-q after-q fp">全戏的滑稽担当给了道童。师父越怕，徒弟越狂，出门就放了句大话，随后自己给自己编好了下场：</div>
      <div class="qrow after-q fp">
        <div class="qc"><span class="tag">折贰</span><q>@@tong1@@</q></div>
        <div class="qc dk"><span class="tag">折贰</span><q>@@tong2@@</q><div class="cmt">大话与缩头之间，隔着一个周仓。</div></div>
      </div>
    </div>
  </div>
</section>

<section class="act" id="zhe3">
  <div class="wrap">
    <div class="act-side fp"><span class="zheNo">折叁</span><span class="zheTi">提刀</span></div>
    <div>
      <div class="act-no fp">第三折 ｜ 荆州帅府</div>
      <p class="act-bai bai fp">主角终于换妆登场，身边站着儿子关平和周仓。信使黄文捧请书上门，把主人的模样看了个饱，一出门就把怕说破了。关平拉着父亲问了一路：那边筵无好会。关羽的回答一句比一句大，险字全说在自己嘴里。</p>
      <div class="qrow fp">
        <div class="qc"><span class="tag">折叁</span><q>@@huangwen@@</q><div class="cmt">信使的黄泉预报。<q>@@doufu@@</q>他原是个实在人。</div></div>
      </div>
      <div class="qrow two after-q fp">
        <div class="qc dk"><span class="tag">折叁</span><q>@@badou@@</q></div>
        <div class="qc dk"><span class="tag">折叁</span><q>@@zhanchang@@</q></div>
      </div>
      <div class="qrow two after-q fp">
        <div class="qc"><span class="tag">折叁</span><q>@@jugong@@</q><div class="cmt">接应？不用。第四折他真照此办理。</div></div>
        <div class="qc"><span class="tag">折叁</span><q>@@wuguan@@</q><div class="cmt">把这场会折算成旧账：不过是又一次千里独行。</div></div>
      </div>
    </div>
  </div>
</section>

<section class="qu" id="zhongliu">
  <div class="wrap">
    <div class="act-no fp">第四折 ｜ 大江中流</div>
    <p class="qu-bai bai fp">鲁肃还在帐里说<q>@@huanlai@@</q>的好话，船头已经看了半日江景。接下来这两支曲子是全戏的顶点，也是元曲里被唱了七百年的名段。击一次节，唱一句。</p>
    <button class="gest fp" id="gest" type="button">击节起唱</button>
    <div class="geQu">
      <div class="qu-h">【双调 · 新水令】</div>
      <div id="qu1">
        <q class="kl">@@x1@@</q>
        <q class="kl">@@x2@@</q>
        <q class="kl">@@x3@@</q>
        <q class="kl">@@x4@@</q>
        <q class="kl">@@x5@@</q>
        <q class="kl">@@x6@@</q>
      </div>
      <div class="qu-h">【驻马听】</div>
      <div id="qu2">
        <q class="kl">@@z1@@</q>
        <q class="kl">@@z2@@</q>
        <q class="kl">@@z3@@</q>
        <q class="kl">@@z4@@</q>
        <q class="kl">@@z5@@</q>
        <q class="kl">@@z6@@</q>
        <q class="kl">@@z7@@</q>
        <q class="kl">@@z8@@</q>
        <q class="kl xl">@@z9@@</q>
      </div>
    </div>
    <p class="qu-note fp">最后一句前带一句夹白（带云）<q>@@z8@@</q>戏台上唱到此处，满场只等这一个停顿。</p>
  </div>
</section>

<section class="act xi" id="xishang">
  <div class="wrap">
    <div class="xi-head">
      <span class="act-no" style="margin:0">席上 ｜ 三计的破产记录</span>
    </div>
    <p class="act-bai bai after-q fp" style="margin-top:16px">席面上的过招，是三计一条一条破产的流水账。鲁肃备好的每一步，都被原样奉还。</p>
    <div class="xia fp">
      <div class="qc" id="xia1"><span class="tag">计壹下场</span><q>@@suo@@</q><div class="cmt">以礼索取，被一句话顶回席面。跟着挨了一记：<q>@@jieKou@@</q></div></div>
      <div class="qc dk" id="xia2"><span class="tag">计贰下场</span><q>@@jiuzui@@</q><div class="cmt">船全在自家手里又如何？接下来发生的事，鲁肃自己都没想到：<q>@@xiangbie@@</q></div></div>
    </div>
    <div class="xi-grid">
      <div class="fp">
        <div class="qrow">
          <div class="qc dk jianjie-q"><span class="tag">剑戒</span><q>@@jianjie@@</q><div class="cmt">剑在匣中自己响，关羽管它叫戒。头两戒的账，全记在乔公与司马徽讲过的旧事里。</div></div>
          <div class="qc"><span class="tag">雁儿落</span><q>@@yanerluo@@</q></div>
        </div>
      </div>
      <div class="fp">
        <div class="mirror-stage" id="mstage">
          <div class="pojing-t">我特来破镜</div>
          <svg id="mirror" viewBox="0 0 240 240" width="240" height="240" aria-hidden="true">
            <g>
              <path class="shard s1" d="M120 16 L150 34 L128 112 L112 112 L96 30 Z" fill="#31404f" stroke="#5e8fbb" stroke-width="1.6"/>
              <path class="shard s2" d="M224 120 L206 150 L130 128 L130 112 L214 90 Z" fill="#31404f" stroke="#5e8fbb" stroke-width="1.6"/>
              <path class="shard s3" d="M120 224 L90 206 L112 130 L128 130 L146 210 Z" fill="#31404f" stroke="#5e8fbb" stroke-width="1.6"/>
              <path class="shard s4" d="M16 120 L34 90 L110 112 L110 128 L28 152 Z" fill="#31404f" stroke="#5e8fbb" stroke-width="1.6"/>
              <circle cx="120" cy="120" r="62" fill="#1a222b" stroke="#5e8fbb" stroke-width="3"/>
              <circle cx="120" cy="120" r="50" fill="none" stroke="#5e8fbb" stroke-width="1.4" opacity=".6"/>
              <path d="M92 96 Q120 76 150 94" fill="none" stroke="#9dbede" stroke-width="3" opacity=".7"/>
              <path class="crk" d="M120 60 L114 104 L132 120 L112 140 L120 180" fill="none" stroke="#c47a6a" stroke-width="2.4"/>
              <path class="crk" d="M66 108 L104 118 L120 120 L104 132 L72 148" fill="none" stroke="#c47a6a" stroke-width="2"/>
              <path class="crk" d="M176 104 L138 116 L120 120 L142 134 L168 146" fill="none" stroke="#c47a6a" stroke-width="2"/>
            </g>
          </svg>
        </div>
        <p class="mirror-tip">甲士拥出，鲁肃反悔不及。点一点这面菱花镜</p>
        <div class="qrow after-q" style="margin-top:18px">
          <div class="qc"><span class="tag">计叁下场</span><q>@@maifu@@</q><q>@@lingshi@@</q><q>@@pojing@@</q><div class="cmt">击金钟的号令没等来，先等来一声击案。菱花碎，伏兵散。</div></div>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="coda" id="coda">
  <div class="wrap">
    <p class="coda-bai bai fp">收梢最妙：单刀赴会的英雄，护身符是扣在手里的主人。船解缆时，关羽还在道谢，要把狠话留到江心才说完。</p>
    <div class="coda-vert fp">
      <div class="big-vert"><q>百忙里称不了<b>老兄心</b></q></div>
      <div class="big-vert xv"><q>急切里倒不了<b>俺汉家节</b></q></div>
    </div>
    <div class="coda-bai fp" style="text-align:center">
      <div class="qc" style="display:inline-block;text-align:left;max-width:620px"><span class="tag"><q>离亭宴带歇指煞</q></span><q>@@liangjian@@</q></div>
    </div>
    <div class="tibi fp">
      <span class="tb-tag">题目正名</span>
      <q>@@tiMu@@</q>
    </div>
    <p class="coda-bai fp">戏名取自正名末句。台下观众对这八个字早已倒背如流，关汉卿索性把它写成悬念本身。</p>
    <div class="fancha fp"><b>史册的另一面：</b>《三国志·鲁肃传》记的单刀会，是双方各驻兵马百步之外、诸将单刀俱会；席上拍案责问、词色甚厉的，恰是鲁肃。戏台把胆气过给了关羽，把算计留给了鲁肃。这本戏写在《三国演义》成书之前，大都的观众听到的三国，先来自戏台，再来自小说。</div>
    <div class="seal fp">汉节</div>
  </div>
</section>

<footer>
  <div class="wrap">
    文本来源：殆知阁简体库剧曲类〈单刀会〉（诗藏），仓库：<a href="https://github.com/robertsong/daizhige" target="_blank" rel="noopener">daizhige-daodu</a>。<br>
    引文均经脚本自库本切片、去标点归一逐字比对；白话部分经六字窗反扫核验。本页为古籍导读：以宴席刀兵相胁、尊刘贬吴的正统观念、全剧无女性角色而婚姻只作筹码，皆时代产物，请以今日眼光辨之。
  </div>
</footer>

<script>
(function(){
  var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('on');io.unobserve(e.target);}});},{threshold:.12});
  document.querySelectorAll('.fp').forEach(function(el){io.observe(el);});

  document.querySelectorAll('[data-zhe]').forEach(function(p){
    p.addEventListener('click',function(){p.classList.toggle('lit');});
    p.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();p.classList.toggle('lit');}});
  });

  var box=document.getElementById('riverbox'),rip=document.getElementById('ripples');
  box.addEventListener('click',function(ev){
    var svg=box.querySelector('svg'),pt=svg.createSVGPoint();
    pt.x=ev.clientX;pt.y=ev.clientY;
    var loc=pt.matrixTransform(svg.getScreenCTM().inverse());
    var c=document.createElementNS('http://www.w3.org/2000/svg','circle');
    c.setAttribute('cx',loc.x);c.setAttribute('cy',loc.y);c.setAttribute('r','6');
    c.setAttribute('fill','none');c.setAttribute('stroke','#9dbede');c.setAttribute('stroke-width','2');
    c.setAttribute('class','ripple');
    var a1=document.createElementNS('http://www.w3.org/2000/svg','animate');
    a1.setAttribute('attributeName','r');a1.setAttribute('from','6');a1.setAttribute('to','58');a1.setAttribute('dur','1.2s');a1.setAttribute('fill','freeze');
    var a2=document.createElementNS('http://www.w3.org/2000/svg','animate');
    a2.setAttribute('attributeName','opacity');a2.setAttribute('from','.85');a2.setAttribute('to','0');a2.setAttribute('dur','1.2s');a2.setAttribute('fill','freeze');
    c.appendChild(a1);c.appendChild(a2);rip.appendChild(c);
    setTimeout(function(){if(c.parentNode)c.parentNode.removeChild(c);},1300);
  });

  var gest=document.getElementById('gest'),running=false;
  gest.addEventListener('click',function(){
    if(running)return;running=true;
    var lines=document.querySelectorAll('#qu1 .kl,#qu2 .kl');
    lines.forEach(function(l){l.classList.remove('on');});
    var i=0;
    var t=setInterval(function(){
      if(i>=lines.length){clearInterval(t);running=false;gest.textContent='再唱一遍';return;}
      lines[i].classList.add('on');i++;
    },620);
  });

  var ms=document.getElementById('mstage');
  ms.addEventListener('click',function(){ms.classList.toggle('broken');});

  var rail=document.querySelector('.rail'),bb=document.querySelector('.rail .bb');
  if(rail){
    window.addEventListener('scroll',function(){
      var max=document.documentElement.scrollHeight-window.innerHeight;
      var p=max>0?(window.scrollY/max):0;
      bb.style.top=(p*(rail.offsetHeight-20))+'px';
    },{passive:true});
  }
})();
</script>
</body>
</html>
"""

html = TPL
for k, v in Q.items():
    tok = "@@%s@@" % k
    assert tok in html, "模板缺token: " + k
    html = html.replace(tok, v)
assert "@@" not in html, "token残留"

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print("written", OUT, len(html), "bytes,", len(Q), "quotes")
