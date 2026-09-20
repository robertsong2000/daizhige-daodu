#!/usr/bin/env python3
# 粘条补叶壳：本草纲目拾遗。引文全部由库本锚点切片生成，页面里的引文零誊写。
import re, sys, unicodedata

SRC = '/home/robertsong/workspace/claude/daizhige-simplified/医藏/本草纲目拾遗.txt'
OUT = '/home/robertsong/workspace/claude/daizhige-daodu/bencao-shiyi.html'

text = open(SRC, encoding='utf-8').read()

# ---- 锚点切片 ----
def cut(a, b):
    assert text.count(a) == 1, 'start anchor not unique: ' + a
    assert text.count(b) == 1, 'end anchor not unique: ' + b
    i = text.index(a)
    j = text.index(b) + len(b)
    s = text[i:j]
    assert '\n' not in s, 'anchor pair crosses lines: ' + a
    return s

Q = {}
Q['xu_bo']   = cut('濒湖博极群书', '悉详采以成一家之言')
Q['xu_ke']   = cut('亦何有遗之待拾欤', '骈疣之赘欤')
Q['xu_bo2']  = cut('唯唯否否', '则珍尤毕集')
Q['xu_fei']  = cut('非有继者', '谁能宏其用也')
Q['xu_sh']   = cut('如石斛一也', '此而不书')
Q['qs_1']    = cut('西洋人所造，性最猛烈', '能蚀五金')
Q['qs_2']    = cut('其水至强', '惟玻璃可盛')
Q['qs_3']    = cut('西人凡画洋画', '胜于雕刻')
Q['yl_1']    = cut('凡物之有质者，皆可取露', '其法始于大西洋，传入中国')
Q['yl_2']    = cut('大则用甑', '皆可蒸取')
Q['yl_3']    = cut('时医多有用药露者', '腻滞肠膈也')
Q['xs_1']    = cut('从新云：出大西洋佛兰西', '其气甚薄')
Q['xs_2']    = cut('苦寒微甘，味浓气薄', '虚而有火者相宜')
Q['dy_1']    = cut('盖因上年壬子冬', '遂大行于时')
Q['dy_2']    = cut('今苏州有东洋参店', '专市此参者')
Q['yp_1']    = cut('鸦片烟用麻葛', '于铜铛内煮成')
Q['yp_2']    = cut('吸一二次后', '可竟夜不寐')
Q['yp_3']    = cut('官弁每为严禁', '再吸一筒者')
Q['yp_4']    = cut('中燃一灯', '至数百口')
Q['yp_5']    = cut('侧开一孔如小指大', '以黄泥掐成葫芦样')
Q['yp_6']    = cut('初服数月', '卒至破家丧身')
Q['ba_1']    = cut('初稿纸短', '故传钞错乱耳')
Q['ba_2']    = cut('迨庚申寇乱', '幸携带仅存')
Q['lj_1']    = cut('贮甲乙卷于养素园', '辄寝食其中')
Q['lj_2']    = cut('塘成，名曰利济', '塘成，名曰利济')
Q['lj_3']    = cut('甫生余昆季二人', '乳字之曰利济')
Q['ts_1']    = cut('广人每以七夕鸡初鸣', '经年味不变')
Q['cs_1']    = cut('立夏前三日出后七日止', '其水始出')
Q['hd_1']    = cut('夏日黎明日将出时', '以伏露为佳')
Q['js_1']    = cut('择大萝卜一个', '开一大孔')
Q['js_2']    = cut('孔内入鸡蛋一枚', '其明如童')
Q['gx_1']    = cut('传云：晋葛洪隐此乏粮', '采以为食，故名')
Q['zg_1']    = cut('疗小儿腹中虫积', '食之即下如神')
Q['pd_1']    = cut('出安南大洞山', '其性纯阴')
Q['pd_2']    = cut('以水泡之', '如浮藻然')
Q['zx_1']    = cut('杀邪治祟', '功同苍术')

TPL = r'''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>补叶粘条 · 拾遗十卷导读</title>
<style>
:root{
  --ink:#191917; --ink2:#222220; --ink3:#2a2a26;
  --paper:#e8e4dc; --paper2:#ded9cc; --faint:#a9a396;
  --bam:#5f9270; --bam-d:#3e6b4f; --bam-l:#8fb69b;
  --mut:#8b8578; --red:#a03a30;
}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{background:var(--ink);color:var(--paper);font-family:"Songti SC","Noto Serif CJK SC","STSong","SimSun",serif;line-height:1.9;overflow-x:hidden}
q{quotes:none}
.mono{font-family:ui-monospace,Menlo,Consolas,monospace}
main{max-width:1080px;margin:0 auto;padding:0 22px}
section{padding:84px 0}
.rv{opacity:0;transform:translateY(16px);transition:opacity .9s ease,transform .9s ease}
.rv.on{opacity:1;transform:none}

/* ---------- hero ---------- */
.hero{min-height:100vh;display:flex;flex-direction:column;justify-content:center;padding:64px 0 40px}
.kicker{font-size:13px;letter-spacing:.4em;color:var(--bam-l);margin-bottom:34px}
.stage{display:grid;grid-template-columns:1fr 380px;gap:56px;align-items:center}
.intro h1{font-size:40px;letter-spacing:.14em;font-weight:600;margin-bottom:8px}
.intro .sub{color:var(--bam-l);letter-spacing:.3em;font-size:14px;margin-bottom:26px}
.intro p.lead{font-size:16.5px;color:#cfc9bb;max-width:34em}
.intro .hint{margin-top:30px;font-size:13px;color:var(--mut);letter-spacing:.2em}
.intro .hint::before{content:"";display:inline-block;width:26px;height:1px;background:var(--bam);vertical-align:middle;margin-right:10px}
.leafwrap{position:relative;justify-self:center}
.leaf{position:relative;width:300px;height:432px;background:var(--paper);color:#33322d;transform:rotate(1.4deg);box-shadow:0 18px 50px rgba(0,0,0,.55),0 2px 0 #cfcabc;border-radius:2px}
.leaf::before{content:"";position:absolute;inset:10px;border:1px solid rgba(95,146,112,.55);pointer-events:none}
.leaf::after{content:"";position:absolute;inset:0;background:repeating-linear-gradient(0deg,transparent 0 34px,rgba(51,50,45,.05) 34px 35px);pointer-events:none}
.vtitle{position:absolute;top:26px;right:30px;writing-mode:vertical-rl;font-size:58px;letter-spacing:.18em;font-weight:700;color:#2e2d28}
.leafby{position:absolute;top:30px;left:26px;writing-mode:vertical-rl;font-size:14px;letter-spacing:.34em;color:#7a766a}
.leafslip{position:absolute;bottom:34px;left:24px;writing-mode:vertical-rl;background:var(--bam);color:#eef3ee;font-size:20px;letter-spacing:.3em;padding:14px 7px;transform:rotate(-2deg);box-shadow:2px 3px 8px rgba(0,0,0,.28)}
.slips{position:absolute;left:0;right:0;bottom:100%;height:0;z-index:3}
.slip{position:absolute;bottom:0;writing-mode:vertical-rl;background:linear-gradient(180deg,var(--bam) 0%,var(--bam-d) 100%);color:#f0f4ef;font-size:15px;letter-spacing:.22em;padding:12px 7px 8px;cursor:pointer;box-shadow:0 4px 10px rgba(0,0,0,.4);transition:transform .55s cubic-bezier(.2,.7,.2,1);border-radius:0 0 2px 2px}
.slip .nm{opacity:0;transition:opacity .35s ease .12s}
.slip .tag{font-size:11px;color:#cfe0d3;letter-spacing:.1em;margin-top:8px;opacity:.75}
.slip:hover{filter:brightness(1.08)}
.slip.down{transform:translateY(206px)}
.slip.down .nm{opacity:1}

/* ---------- 通用章节头 ---------- */
.shead{display:flex;align-items:baseline;gap:16px;margin-bottom:40px}
.sno{writing-mode:vertical-rl;font-size:12px;letter-spacing:.3em;color:var(--bam);border:1px solid var(--bam);padding:10px 4px}
.shead h2{font-size:26px;letter-spacing:.22em;font-weight:600}
.shead .en{font-size:12.5px;color:var(--mut);letter-spacing:.24em}

/* ---------- 序答 ---------- */
.paper{background:var(--paper);color:#33322d}
.paper .shead h2{color:#2c2b26}
.paper .shead .en{color:#8d887a}
.paper .sno{color:var(--bam-d);border-color:var(--bam-d)}
.qa{display:grid;grid-template-columns:1fr 1fr;gap:26px}
.qacol{position:relative;border:1px solid rgba(62,107,79,.4);padding:26px 22px;background:rgba(255,255,255,.28)}
.qacol .who{position:absolute;top:-13px;right:18px;background:var(--bam-d);color:#f0f4ef;font-size:12.5px;letter-spacing:.3em;padding:3px 12px}
.vcol{writing-mode:vertical-rl;height:340px;font-size:16.5px;letter-spacing:.14em;color:#3a3931;margin-top:6px}
.vcol q{color:#2c2b26}
.qacol.ke .vcol{margin-left:auto}
.vcol .say{display:inline;margin-right:6px}
.xucard{margin-top:44px;border-left:3px solid var(--bam);padding:6px 0 6px 22px}
.xucard h3{font-size:17px;letter-spacing:.2em;color:var(--bam-d);margin-bottom:8px}
.xucard p{font-size:15px;color:#55524a;max-width:44em}
.xucard .qt{display:block;margin-top:10px;font-size:15.5px;color:#2c2b26}
.stampbtn{margin-top:26px;background:none;border:1px solid var(--bam-d);color:var(--bam-d);font-family:inherit;font-size:13px;letter-spacing:.3em;padding:8px 20px;cursor:pointer}
.stampbtn:hover{background:rgba(62,107,79,.12)}
.yseal{position:absolute;right:44px;bottom:30px;width:64px;height:64px;border:3px solid var(--red);color:var(--red);display:flex;align-items:center;justify-content:center;writing-mode:vertical-rl;font-size:19px;letter-spacing:.1em;font-weight:700;transform:rotate(-9deg) scale(.2);opacity:0;transition:transform .35s cubic-bezier(.2,1.6,.4,1),opacity .3s;border-radius:4px}
.yseal.on{transform:rotate(-9deg) scale(1);opacity:.88}

/* ---------- 西来三味 ---------- */
.dark{background:var(--ink2)}
.wcards{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}
.wcard{border:1px solid rgba(143,182,155,.28);background:rgba(232,228,220,.035);padding:20px 18px;display:flex;flex-direction:column}
.wcard h3{font-size:18px;letter-spacing:.24em;color:var(--bam-l);margin-bottom:4px}
.wcard .from{font-size:12px;color:var(--mut);letter-spacing:.16em;margin-bottom:12px}
.wsvg{display:block;width:100%;height:auto;margin-bottom:14px}
.wbtn{align-self:flex-start;background:var(--bam);border:none;color:#10130f;font-family:inherit;font-size:13.5px;letter-spacing:.3em;padding:8px 22px;cursor:pointer;margin-bottom:14px}
.wbtn:hover{background:var(--bam-l)}
.wcard p{font-size:14px;color:#b9b3a5;margin-bottom:10px}
.qt{font-size:14.5px;color:var(--paper);line-height:2}
.wcard .qt{display:block;margin-bottom:10px}
[data-who]::after{content:attr(data-who);display:block;font-size:11.5px;color:var(--mut);letter-spacing:.18em;margin-top:2px}

/* 强水蚀铜 */
.etchplate{fill:#6e5b45;stroke:#8a7357;stroke-width:1}
.etchline{stroke:var(--bam-l);stroke-width:2.2;fill:none;stroke-linecap:round;stroke-dasharray:100;stroke-dashoffset:100;transition:stroke-dashoffset 2.4s ease}
.etchcard.live .e1{transition-delay:.1s}
.etchcard.live .e2{transition-delay:.5s}
.etchcard.live .e3{transition-delay:.9s}
.etchcard.live .e4{transition-delay:1.4s}
.etchcard.live .etchline{stroke-dashoffset:0}
.wax{fill:#d8cba2;stroke:#b3a377;stroke-width:1}
.wlabel{font-size:12px;fill:var(--mut);letter-spacing:.2em}
.jarline{stroke:rgba(143,182,155,.5);fill:none;stroke-width:1.4}
.acid{fill:rgba(95,146,112,.16)}
.acidwave{stroke:var(--bam);stroke-width:1.2;fill:none;opacity:.8}

/* 药露蒸取 */
.stillbody{fill:none;stroke:var(--bam-l);stroke-width:1.6}
.tube{stroke:var(--bam-l);stroke-width:1.6;fill:none}
.vapor{fill:rgba(143,182,155,.7);opacity:0}
.stillcard.live .vapor{animation:rise 2.1s ease-in-out infinite}
.stillcard.live .v2{animation-delay:.4s}
.stillcard.live .v3{animation-delay:.9s}
@keyframes rise{0%{opacity:0;transform:translateY(6px)}30%{opacity:.85}100%{opacity:0;transform:translateY(-26px)}}
.drop{fill:var(--bam-l);opacity:0}
.stillcard.live .drop{animation:fall 1.5s linear infinite}
.stillcard.live .d2{animation-delay:.5s}
.stillcard.live .d3{animation-delay:1s}
@keyframes fall{0%{opacity:0;transform:translateY(-10px)}25%{opacity:1}100%{opacity:0;transform:translateY(34px)}}
.fillrect{fill:rgba(95,146,112,.35);height:3px;transition:height 3s ease .4s}
.stillcard.live .fillrect{height:46px}
.flame{fill:#c98b3f}
.fireset{opacity:.45;transition:opacity .4s}
.stillcard.live .fireset{opacity:1}
.slabel{font-size:12px;fill:var(--mut);letter-spacing:.2em}

/* 参市 */
.gtabs{display:flex;gap:0;margin-bottom:14px}
.gtab{flex:1;text-align:center;font-family:inherit;font-size:14px;letter-spacing:.3em;padding:9px 0;background:rgba(232,228,220,.05);color:var(--mut);border:1px solid rgba(143,182,155,.3);cursor:pointer;border-right:none}
.gtab:last-child{border-right:1px solid rgba(143,182,155,.3)}
.gtab.on{background:var(--bam);color:#10130f;border-color:var(--bam)}
.gpane .gq{display:none}
.gpane[data-tab="a"] .gq.a{display:block}
.gpane[data-tab="b"] .gq.b{display:block}
.gq{margin-bottom:12px}

/* ---------- 烟灯 ---------- */
.deep{background:#121210}
.deep .shead h2{color:#ddd7c9}
.lampwrap{display:grid;grid-template-columns:420px 1fr;gap:44px;align-items:start}
.lampbox .part{transition:filter .35s,opacity .35s}
.lampbox .dim{opacity:.4}
.lampbox.s1 .p-ding,.lampbox.s2 .p-tong,.lampbox.s3 .p-deng{filter:drop-shadow(0 0 6px rgba(224,170,90,.75))}
.lampbox.s2 .p-tong{opacity:1}
.lampbox.s3 .p-deng .flame2{animation:flick .5s ease-in-out infinite alternate}
@keyframes flick{from{transform:scaleY(1)}to{transform:scaleY(1.25)}}
.lampbox.end .flame2{opacity:.12;animation:none}
.lampbox.end .lframe{stroke:var(--red)}
.lsteps{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:22px}
.lstep{background:none;border:1px solid rgba(224,170,90,.4);color:#c9a06a;font-family:inherit;font-size:13px;letter-spacing:.2em;padding:7px 16px;cursor:pointer}
.lstep.on{background:#c9a06a;color:#1c120a;border-color:#c9a06a}
.lquotes .lq{display:none}
.lampbox.s1 .lq[data-s="1"],.lampbox.s2 .lq[data-s="2"],.lampbox.s3 .lq[data-s="3"],.lampbox.s4 .lq[data-s="4"],.lampbox.s5 .lq[data-s="5"]{display:block}
.lq{margin-bottom:14px;font-size:15px;color:#ddd7c9}
.ywarn{margin-top:34px;border-top:1px solid rgba(224,170,90,.3);padding-top:20px;font-size:14px;color:#a89e88;max-width:52em}
.ywarn b{color:#c9a06a;font-weight:600}
.yline{display:flex;gap:0;margin-top:26px;font-size:12.5px;letter-spacing:.16em;color:var(--mut)}
.yline span{padding:8px 14px;border:1px solid rgba(232,228,220,.18);border-right:none}
.yline span:last-child{border-right:1px solid rgba(232,228,220,.18)}
.yline .now{background:rgba(224,170,90,.14);color:#d8b47e}

/* ---------- 十二种 ---------- */
.spines{display:grid;grid-template-columns:repeat(12,1fr);gap:10px;margin-bottom:26px}
.spine{writing-mode:vertical-rl;height:216px;display:flex;align-items:center;justify-content:flex-start;font-size:14.5px;letter-spacing:.24em;padding:16px 0 12px;background:#d7d1c2;color:#5b574c;border-radius:2px;box-shadow:inset 0 0 0 1px rgba(0,0,0,.08),2px 3px 6px rgba(0,0,0,.22);transition:opacity .3s}
.spine.dead{opacity:.26}
.spine.live{background:var(--bam-d);color:#eef3ee;cursor:pointer}
.spine.live:hover{background:var(--bam)}
.spine.live.sel{outline:2px solid var(--bam-d);outline-offset:2px}
.spine .vol{font-size:11px;opacity:.7;margin-top:10px}
.ppanes{position:relative;min-height:210px}
.ppane{display:none;border:1px solid rgba(62,107,79,.4);background:rgba(255,255,255,.3);padding:24px 26px}
.ppane.on{display:block}
.ppane h3{font-size:17px;letter-spacing:.22em;color:var(--bam-d);margin-bottom:10px}
.ppane p{font-size:15px;color:#4a473f;max-width:46em;margin-bottom:12px}
.ppane .qt{color:#2c2b26;display:block;margin-bottom:12px;font-size:15px}

/* ---------- 抽检 ---------- */
.alt{background:var(--paper2)}
.chips{display:flex;flex-wrap:wrap;gap:9px;margin-bottom:34px}
.chip{font-size:13.5px;letter-spacing:.2em;color:#4d4a41;border:1px solid rgba(62,107,79,.45);padding:6px 15px;background:rgba(255,255,255,.3)}
.chip.hot{background:var(--bam);color:#f0f4ef;border-color:var(--bam)}
.drawrow{display:flex;align-items:center;gap:22px;margin-bottom:26px}
.drawbtn{background:var(--ink);color:var(--paper);border:none;font-family:inherit;font-size:15px;letter-spacing:.4em;padding:13px 34px;cursor:pointer}
.drawbtn:hover{background:var(--bam-d)}
.drawnote{font-size:13px;color:#6e6a5e;letter-spacing:.14em}
#drawbox{border:1px solid rgba(62,107,79,.5);background:rgba(255,255,255,.42);padding:26px 30px;min-height:120px;display:none}
#drawbox.on{display:block}
#drawbox .dname{font-size:24px;letter-spacing:.3em;color:var(--bam-d);margin-bottom:10px}
#drawbox .dq{font-size:15.5px;color:#33322d;line-height:2.1}
#qbank{display:none}

/* ---------- 尾屏 ---------- */
.fin{background:var(--ink);text-align:left}
.fin .cols{display:flex;justify-content:flex-end;gap:34px;padding-right:8%}
.fcol{writing-mode:vertical-rl;height:300px;font-size:17.5px;letter-spacing:.2em;color:#cfc9bb}
.fseal{width:58px;height:58px;border:3px solid var(--red);color:var(--red);writing-mode:vertical-rl;display:flex;align-items:center;justify-content:center;font-size:17px;letter-spacing:.08em;font-weight:700;transform:rotate(-7deg);border-radius:4px;opacity:.9}
.fin .end{margin-top:44px;text-align:center;font-size:13px;letter-spacing:.4em;color:var(--mut)}

footer{border-top:1px solid rgba(232,228,220,.15);padding:30px 22px 46px;font-size:12.5px;color:#7d786b;line-height:2.1}
footer b{color:#a39d8e;font-weight:600}
footer p{max-width:900px;margin:0 auto}

/* ---------- 响应式 ---------- */
@media (max-width:920px){
  .stage{grid-template-columns:1fr;gap:70px}
  .leafwrap{justify-self:center;margin-top:130px}
  .wcards{grid-template-columns:1fr}
  .lampwrap{grid-template-columns:1fr}
  .spines{grid-template-columns:repeat(6,1fr)}
  .spine{height:150px;font-size:13px}
}
@media (max-width:600px){
  .qa{grid-template-columns:1fr}
  .vcol{height:280px;font-size:15px}
  .intro h1{font-size:31px}
  .spines{grid-template-columns:repeat(4,1fr)}
  .fin .cols{padding-right:0;justify-content:center;gap:22px}
  .fcol{font-size:15px;height:260px}
  .leaf{width:252px;height:380px}
  .vtitle{font-size:48px}
  .slip.down{transform:translateY(180px)}
}
</style>
</head>
<body>

<header class="hero">
  <main>
    <p class="kicker">医藏本草｜清 赵学敏恕轩</p>
    <div class="stage">
      <div class="intro">
        <h1>给本草续账的人</h1>
        <p class="sub">拾遗十卷 · 粘条补叶</p>
        <p class="lead">乾隆乙酉（1765）秋，钱塘人赵学敏在双砚草堂为一部书写下自序。做的是替李时珍查漏补缺的活：濒湖先生的书行世百七十年，人以为无可复加；他偏说，物类还在生长，新味还在靠岸，本草这部账，得一直记下去。书里收着西洋来的酸水与蒸露法，收着安南的胖大海与吕宋的烟，也收着他自家药圃里兄弟二人寝食其中的少年光阴。</p>
        <p class="hint">点书叶上方的粘条，看补录诸味</p>
      </div>
      <div class="leafwrap">
        <div class="slips" aria-hidden="false">
          <div class="slip" style="left:2%;height:130px" role="button" tabindex="0"><span class="nm">强水</span><span class="tag">西来酸</span></div>
          <div class="slip" style="left:17%;height:140px" role="button" tabindex="0"><span class="nm">各种药露</span><span class="tag">蒸法</span></div>
          <div class="slip" style="left:36%;height:145px" role="button" tabindex="0"><span class="nm">西洋参</span><span class="tag">佛兰西</span></div>
          <div class="slip" style="left:54%;height:125px" role="button" tabindex="0"><span class="nm">鸦片烟</span><span class="tag">火部</span></div>
          <div class="slip" style="left:71%;height:135px" role="button" tabindex="0"><span class="nm">胖大海</span><span class="tag">安南</span></div>
          <div class="slip" style="left:86%;height:120px" role="button" tabindex="0"><span class="nm">天孙水</span><span class="tag">七夕</span></div>
        </div>
        <div class="leaf">
          <h1 class="vtitle">本草纲目</h1>
          <p class="leafby">濒湖氏旧帙</p>
          <p class="leafslip">拾遗</p>
        </div>
      </div>
    </div>
  </main>
</header>

<section class="paper" id="xuda">
  <main>
    <div class="shead rv"><span class="sno">卷首</span><h2>一问一答</h2><span class="en">自序是一场抬杠</span></div>
    <div class="qa rv">
      <div class="qacol yu">
        <span class="who">予答</span>
        <div class="vcol"><q>@@xu_bo2@@</q>。<q>@@xu_fei@@</q>。</div>
        <button class="stampbtn" id="sealbtn">钤一印</button>
        <div class="yseal" id="xuseal">恕轩</div>
      </div>
      <div class="qacol ke">
        <span class="who">客问</span>
        <div class="vcol"><q>@@xu_bo@@</q>。遂诘：<q>@@xu_ke@@</q>？</div>
      </div>
    </div>
    <p style="font-size:12.5px;color:#8d887a;letter-spacing:.14em;margin-top:14px">客之难在右，予之答在左，皆自序原文，竖排右起。</p>
    <div class="xucard rv">
      <h3>近所变产</h3>
      <p>他举的证据很实在：同是一味药，产地变了，形性跟着变。本草不续记，后人连这些东西叫什么都不知道。</p>
      <q class="qt">@@xu_sh@@。</q>
    </div>
  </main>
</section>

<section class="dark" id="xilai">
  <main>
    <div class="shead rv"><span class="sno">新味</span><h2>西来三味</h2><span class="en">酸水蒸露与参市</span></div>
    <div class="wcards">
      <div class="wcard etchcard rv" id="etchcard">
        <h3>强水</h3>
        <p class="from">卷一水部 · 西洋所造</p>
        <svg class="wsvg" viewBox="0 0 300 190" aria-hidden="true">
          <path class="jarline" d="M38,26 h224 v118 a14,14 0 0 1 -14,14 h-196 a14,14 0 0 1 -14,-14 z"/>
          <rect class="acid" x="46" y="70" width="208" height="80"/>
          <path class="acidwave" d="M46,78 q26,-8 52,0 t52,0 t52,0 t52,0"/>
          <rect class="etchplate" x="58" y="94" width="184" height="42" rx="2"/>
          <path class="etchline e1" pathLength="100" d="M70,126 l30,-20 l22,14 l26,-22"/>
          <path class="etchline e2" pathLength="100" d="M158,120 q18,-18 34,-6 t28,-10"/>
          <path class="etchline e3" pathLength="100" d="M70,112 q20,10 40,-2"/>
          <path class="etchline e4" pathLength="100" d="M196,128 l24,-8"/>
          <rect class="wax" x="96" y="100" width="40" height="14" rx="2"/>
          <text class="wlabel" x="104" y="110" fill="#6e6248" stroke="none">蜡</text>
          <text class="wlabel" x="58" y="168">铜版 · 渍一夜则画成</text>
        </svg>
        <button class="wbtn" id="etchbtn">渍之</button>
        <q class="qt">@@qs_1@@。</q>
        <q class="qt" data-who="王怡堂先生云">@@qs_2@@。</q>
        <q class="qt">@@qs_3@@。</q>
      </div>
      <div class="wcard stillcard rv" id="stillcard">
        <h3>各种药露</h3>
        <p class="from">卷一水部 · 法始大西洋</p>
        <svg class="wsvg" viewBox="0 0 300 190" aria-hidden="true">
          <g class="fireset">
            <path class="flame" d="M96,160 q6,-14 12,0 q-6,10 -12,0z"/>
            <path class="flame" d="M120,162 q5,-11 10,0 q-5,8 -10,0z"/>
            <path class="flame" d="M74,162 q5,-11 10,0 q-5,8 -10,0z"/>
          </g>
          <path class="stillbody" d="M70,108 q-16,10 -16,28 q0,22 38,22 q38,0 38,-22 q0,-18 -16,-28 z"/>
          <path class="stillbody" d="M64,106 h76"/>
          <path class="tube" d="M102,106 v-30 h96 v22"/>
          <rect class="stillbody" x="182" y="98" width="34" height="56" rx="4"/>
          <rect class="fillrect" x="186" y="148" width="26" height="3"/>
          <circle class="vapor" cx="116" cy="92" r="3.4"/>
          <circle class="vapor v2" cx="140" cy="88" r="3"/>
          <circle class="vapor v3" cx="170" cy="90" r="3.4"/>
          <circle class="drop" cx="199" cy="112" r="2.6"/>
          <circle class="drop d2" cx="199" cy="112" r="2.6"/>
          <circle class="drop d3" cx="199" cy="112" r="2.6"/>
          <text class="slabel" x="52" y="146">甑</text>
          <text class="slabel" x="188" y="176">瓶</text>
          <text class="slabel" x="108" y="182">文武火</text>
        </svg>
        <button class="wbtn" id="stillbtn">蒸之</button>
        <q class="qt">@@yl_1@@。</q>
        <q class="qt">@@yl_2@@。</q>
        <q class="qt" data-who="敏按诸语">@@yl_3@@</q>
      </div>
      <div class="wcard rv">
        <h3>参市</h3>
        <p class="from">卷三草部 · 两洋参并录</p>
        <div class="gtabs" role="tablist">
          <button class="gtab on" data-tab="a">西洋参</button>
          <button class="gtab" data-tab="b">东洋参</button>
        </div>
        <div class="gpane" id="gpane" data-tab="a">
          <div class="gq a">
            <q class="qt" data-who="从新">@@xs_1@@</q>
            <q class="qt">@@xs_2@@。</q>
            <p>这是西洋参在中文文献里最早的一批记录之一，产地写得明白：出自大西洋的佛兰西。</p>
          </div>
          <div class="gq b">
            <q class="qt">@@dy_1@@</q>
            <q class="qt">@@dy_2@@。</q>
            <p>一场痘疫带火的生意：疫后此参大行，苏州竟有专市此参的店铺。</p>
          </div>
        </div>
      </div>
    </div>
  </main>
</section>

<section class="deep" id="yandeng">
  <main>
    <div class="shead rv"><span class="sno">火部</span><h2>烟灯</h2><span class="en">一份提前七十四年的成瘾记录</span></div>
    <div class="lampwrap rv">
      <svg viewBox="0 0 420 220" class="lampsvg" aria-hidden="true">
        <g class="part p-ding dim">
          <ellipse cx="76" cy="178" rx="40" ry="12" fill="none" stroke="#9b8a68" stroke-width="2"/>
          <path d="M50,176 q4,-26 26,-26 q22,0 26,26" fill="none" stroke="#9b8a68" stroke-width="2"/>
          <text class="slabel" x="60" y="204">铜铛</text>
        </g>
        <g class="part p-tong dim">
          <rect x="150" y="96" width="180" height="26" rx="13" fill="none" stroke="#b0a284" stroke-width="2"/>
          <line x1="170" y1="102" x2="170" y2="116" stroke="#b0a284" stroke-width="1" opacity=".6"/>
          <line x1="192" y1="102" x2="192" y2="116" stroke="#b0a284" stroke-width="1" opacity=".6"/>
          <line x1="214" y1="102" x2="214" y2="116" stroke="#b0a284" stroke-width="1" opacity=".6"/>
          <line x1="236" y1="102" x2="236" y2="116" stroke="#b0a284" stroke-width="1" opacity=".6"/>
          <line x1="258" y1="102" x2="258" y2="116" stroke="#b0a284" stroke-width="1" opacity=".6"/>
          <circle cx="268" cy="109" r="4.5" fill="#121210" stroke="#b0a284" stroke-width="1.6"/>
          <text class="slabel" x="176" y="142">竹筒 · 中实棕丝</text>
        </g>
        <g class="part p-hulu dim">
          <circle cx="356" cy="109" r="13" fill="none" stroke="#c9a06a" stroke-width="2"/>
          <circle cx="356" cy="88" r="8" fill="none" stroke="#c9a06a" stroke-width="2"/>
          <text class="slabel" x="336" y="142">黄泥葫芦</text>
        </g>
        <g class="part p-deng dim">
          <path class="lframe" d="M196,196 h74" stroke="#b0a284" stroke-width="2" fill="none"/>
          <path d="M206,196 q6,-16 27,-16 q21,0 27,16" fill="none" stroke="#b0a284" stroke-width="2"/>
          <path class="flame2" d="M233,176 q7,-16 14,0 q-7,12 -14,0z" fill="#e0aa5a"/>
          <text class="slabel" x="216" y="214">灯</text>
        </g>
      </svg>
      <div class="lampbox s1" id="lampbox">
        <div class="lsteps">
          <button class="lstep on" data-s="1">煮烟</button>
          <button class="lstep" data-s="2">具器</button>
          <button class="lstep" data-s="3">燃灯聚吸</button>
          <button class="lstep" data-s="4">刻不能离</button>
          <button class="lstep" data-s="5">破家丧身</button>
        </div>
        <div class="lquotes">
          <div class="lq" data-s="1"><q>@@yp_1@@。</q><span data-who="引台海使槎录"></span></div>
          <div class="lq" data-s="2"><q>@@yp_5@@</q>，嵌入筒首。<span data-who="引海东扎记"></span></div>
          <div class="lq" data-s="3"><q>@@yp_4@@。</q><span data-who="引海东扎记"></span></div>
          <div class="lq" data-s="4"><q>@@yp_2@@。</q><q>@@yp_3@@。</q><span data-who="引台海使槎录"></span></div>
          <div class="lq" data-s="5"><q>@@yp_6@@。</q><span data-who="引海东扎记"></span></div>
        </div>
        <p class="ywarn">火部收药，收的是灯火炊烟，也收了这一条。它几乎是一份成瘾说明书：怎么煮，怎么吸，吸了怎样，断了怎样，末了怎样。写下此条时，<b>距虎门销烟还有七十四年</b>。</p>
        <div class="yline"><span class="now">乾隆乙酉（1765）著录烟害</span><span>一八三九 虎门销烟</span></div>
      </div>
    </div>
  </main>
</section>

<section class="paper" id="shierz">
  <main>
    <div class="shead rv"><span class="sno">书后</span><h2>十二种存二</h2><span class="en">利济一百卷的下落</span></div>
    <p class="rv" style="font-size:15px;color:#55524a;max-width:52em;margin-bottom:26px">晚年他把平生著述编为利济十二种，通计一百卷。这年他刚得一弟，父亲以治海患筑塘之功名其堂曰利济，兄弟俩的乳名也得了这两个字；药圃开在自家园林里，两人季季寝食其中。到嘉庆末年，十二种传钞本只剩两种。</p>
    <div class="spines rv">
      <div class="spine dead"><q>医林集腋</q><span class="vol">十六卷</span></div>
      <div class="spine dead"><q>养素园传信方</q><span class="vol">六卷</span></div>
      <div class="spine dead"><q>祝由录验</q><span class="vol">四卷</span></div>
      <div class="spine dead"><q>囊露集</q><span class="vol">四卷</span></div>
      <div class="spine dead"><q>本草话</q><span class="vol">三十二卷</span></div>
      <div class="spine live" data-panel="p-sy" role="button" tabindex="0"><q>串雅</q><span class="vol">八卷</span></div>
      <div class="spine dead"><q>花药小名录</q><span class="vol">四卷</span></div>
      <div class="spine dead"><q>升降秘要</q><span class="vol">二卷</span></div>
      <div class="spine dead"><q>摄生闲览</q><span class="vol">四卷</span></div>
      <div class="spine dead"><q>药性元解</q><span class="vol">四卷</span></div>
      <div class="spine dead"><q>奇药备考</q><span class="vol">六卷</span></div>
      <div class="spine live" data-panel="p-sy2" role="button" tabindex="0"><q>本草纲目拾遗</q><span class="vol">十卷</span></div>
    </div>
    <div class="ppanes rv">
      <div class="ppane on" id="p-sy2">
        <h3>粘条殆满</h3>
        <p>同治甲子（1864）张应昌作跋：他借到的稿本是先生亲辑而未誊清的本子，初稿纸短，后来增补的条目全靠粘条贴上去，又不注次序，传钞本因此错乱。他按体例重新排比校正，此书才可读。</p>
        <q class="qt">@@ba_1@@</q>
        <p>两年多后乱起杭州，连家原稿亡失，串雅也佚了，这一部因为随身携带而独存。</p>
        <q class="qt">@@ba_2@@</q>
      </div>
      <div class="ppane" id="p-sy">
        <h3>串亦曰雅</h3>
        <p>十二种里的另一种幸存者，记走方医的顶串诸术。总序里说，友人宗子柏云行医游历八年归来，把历游方术倾囊相授，与自家园圃所集验方合编成书；串而曰雅，是不肯把它当江湖俗技看。此书本系列已另有导读。</p>
      </div>
    </div>
    <div class="xucard rv">
      <h3>药圃旧事</h3>
      <p>利济之名的来历，与那座让兄弟俩把书读进泥土里的园子。</p>
      <q class="qt">@@lj_1@@。</q>
      <q class="qt" data-who="利济十二种总序">@@lj_2@@</q>，<q class="qt" data-who="利济十二种总序">@@lj_3@@</q>。
    </div>
  </main>
</section>

<section class="alt" id="choujian">
  <main>
    <div class="shead rv"><span class="sno">目录</span><h2>十八部抽检</h2><span class="en">奇物俯拾即是</span></div>
    <div class="chips rv">
      <span class="chip">水部</span><span class="chip">火部</span><span class="chip">土部</span><span class="chip">金部</span><span class="chip">石部</span><span class="chip">草部</span><span class="chip">木部</span><span class="chip">藤部</span><span class="chip">花部</span><span class="chip">果部</span><span class="chip">诸谷部</span><span class="chip">诸蔬部</span><span class="chip">器用部</span><span class="chip">禽部</span><span class="chip">兽部</span><span class="chip">鳞部</span><span class="chip">介部</span><span class="chip">虫部</span>
    </div>
    <div class="drawrow rv">
      <button class="drawbtn" id="drawbtn">抽一叶</button>
      <p class="drawnote">自八味奇物中抽取一叶，再看一眼他记了什么</p>
    </div>
    <div id="drawbox" class="rv"></div>
    <div id="qbank">
      <div class="bq" data-name="春水"><q>@@cs_1@@</q></div>
      <div class="bq" data-name="天孙水"><q>@@ts_1@@</q></div>
      <div class="bq" data-name="荷叶上露"><q>@@hd_1@@。</q></div>
      <div class="bq" data-name="鸡神水"><q>@@js_1@@</q>，<q>@@js_2@@</q>。</div>
      <div class="bq" data-name="葛仙米"><q>@@gx_1@@</q></div>
      <div class="bq" data-name="鹧鸪菜"><q>@@zg_1@@。</q></div>
      <div class="bq" data-name="胖大海"><q>@@pd_1@@。</q><q>@@pd_2@@</q>，壳中有仁两瓣。</div>
      <div class="bq" data-name="藏香"><q>@@zx_1@@。</q></div>
    </div>
  </main>
</section>

<section class="fin" id="fin">
  <main>
    <div class="shead rv"><span class="sno">收梢</span><h2>账不能停</h2></div>
    <div class="cols rv">
      <div class="fseal">恕轩</div>
      <div class="fcol">纲目既行百七十年，</div>
      <div class="fcol">物类新故相续，账不能停；</div>
      <div class="fcol">十二种存其二，粘条与传钞</div>
      <div class="fcol">拼回一部书，也算利济有后。</div>
    </div>
    <p class="end">拾 遗 十 卷 · 终</p>
  </main>
</section>

<footer>
  <p>文本来源：殆知阁古代文献简体库〈<q>本草纲目拾遗</q>〉医藏库本　<b>github.com/robertsong/daizhige-daodu</b></p>
  <p>引文经脚本自库本锚点切片生成、去标点归一逐字比对通过；白话行文与库本六字窗反扫零撞。</p>
  <p>本书为乾隆间医家著述：鸦片烟条所记烟馆群吸诸语系当日闻见照录；鸡神水、天孙水、藏香杀邪等涉民俗信仰与传闻，照录存照，不代今人立论；所记番、倭、洋诸称谓皆时代用语。</p>
</footer>

<script>
(function(){
  var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('on');io.unobserve(e.target);}});},{threshold:.15});
  document.querySelectorAll('.rv').forEach(function(el){io.observe(el);});

  document.querySelectorAll('.slip').forEach(function(s){
    var t=function(){s.classList.toggle('down');};
    s.addEventListener('click',t);
    s.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();t();}});
  });

  document.getElementById('sealbtn').addEventListener('click',function(){
    document.getElementById('xuseal').classList.add('on');
    this.textContent='已钤';
  });

  var eb=document.getElementById('etchbtn');
  eb.addEventListener('click',function(){
    var c=document.getElementById('etchcard');
    c.classList.toggle('live');
    eb.textContent=c.classList.contains('live')?'复蜡':'渍之';
  });

  var sb=document.getElementById('stillbtn');
  sb.addEventListener('click',function(){
    var c=document.getElementById('stillcard');
    c.classList.toggle('live');
    sb.textContent=c.classList.contains('live')?'熄火':'蒸之';
  });

  document.querySelectorAll('.gtab').forEach(function(t){
    t.addEventListener('click',function(){
      document.querySelectorAll('.gtab').forEach(function(x){x.classList.remove('on');});
      t.classList.add('on');
      document.getElementById('gpane').dataset.tab=t.dataset.tab;
    });
  });

  var lampbox=document.getElementById('lampbox');
  document.querySelectorAll('.lstep').forEach(function(b){
    b.addEventListener('click',function(){
      document.querySelectorAll('.lstep').forEach(function(x){x.classList.remove('on');});
      b.classList.add('on');
      lampbox.className='lampbox s'+b.dataset.s+(b.dataset.s==='5'?' end':'');
    });
  });

  document.querySelectorAll('.spine.live').forEach(function(sp){
    sp.addEventListener('click',function(){
      document.querySelectorAll('.ppane').forEach(function(p){p.classList.toggle('on',p.id===sp.dataset.panel);});
      document.querySelectorAll('.spine').forEach(function(x){x.classList.remove('sel');});
      sp.classList.add('sel');
    });
  });

  var bank=Array.prototype.slice.call(document.querySelectorAll('#qbank .bq'));
  document.getElementById('drawbtn').addEventListener('click',function(){
    var it=bank[Math.floor(Math.random()*bank.length)];
    var box=document.getElementById('drawbox');
    box.innerHTML='<div class="dname">'+it.getAttribute('data-name')+'</div>'+it.innerHTML;
    box.classList.add('on');
  });
})();
</script>
</body>
</html>
'''

html = TPL
for k, v in Q.items():
    html = html.replace('@@' + k + '@@', v)
assert '@@' not in html, 'unresolved token'

# ---- 核验一：每个 q 元素与库本归一比对 ----
def norm(t):
    t = re.sub(r'\s+', '', t)
    return ''.join(ch for ch in t if not unicodedata.category(ch).startswith(('P', 'S', 'C')))

src_n = norm(text)
qs = re.findall(r'<q[^>]*>(.*?)</q>', html, flags=re.S)
bad = [q for q in qs if norm(q) not in src_n]
assert not bad, '引文核验失败: ' + repr(bad[:2])

# ---- 核验二：白话反扫（q 之外不得有库本六字窗）----
body = re.sub(r'<style.*?</style>', '', html, flags=re.S)
body = re.sub(r'<script.*?</script>', '', body, flags=re.S)
prose = re.sub(r'<q[^>]*>.*?</q>', '\x00', body, flags=re.S)
prose = re.sub(r'<[^>]+>', '', prose)
title_m = re.search(r'<title>(.*?)</title>', html, flags=re.S).group(1)
prose_n = norm(re.sub(r'\x00', '\n', prose) + '\n' + title_m)
hits = []
i = 0
while i + 6 <= len(prose_n):
    w = prose_n[i:i + 6]
    if w in src_n:
        hits.append((i, w))
        i += 6
    else:
        i += 1
if hits:
    for i, w in hits[:10]:
        print('反扫撞窗@%d: %s ... 上下文: %s' % (i, w, prose_n[max(0, i - 12):i + 12]))
    sys.exit('白话反扫未通过，撞窗 %d 处' % len(hits))

open(OUT, 'w', encoding='utf-8').write(html)
print('OK 写出 %s' % OUT)
print('q 元素 %d 个，引文核验通过；白话反扫六字窗零撞' % len(qs))
print('库本去空白字数 %d' % len(re.sub(r'\s+', '', text)))
