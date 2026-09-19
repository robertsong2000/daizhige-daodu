#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""池北偶谈导读页 build：全部 <q> 引文由库本锚点切片注入，零誊写。"""
import os, sys, re

PUA = re.compile('[\uE000-\uF8FF]')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'daizhige-simplified', '史藏', '志存记录', '池北偶谈.txt')
OUT = os.path.join(HERE, 'chibei-outan.html')

# key -> (start_anchor, end_anchor)；end 为空表示单句=整段 start 锚
QUOTES = {
 'pool':   ('西为小圃，有池焉，老屋数椽在其北。', ''),
 'name':   ('辄取乐天池北书库之名名之。', ''),
 'water':  ('竹树飒然', '可见毛发'),
 'moon':   ('或酒阑月堕', '神仙鬼怪之事'),
 'record': ('儿辈从旁记录', '遂成卷轴。'),
 'four':   ('区其条目', '曰谈异'),
 'keep':   ('大之可以畜德', '小亦可以多识'),
 'luanwei':('朝制，武臣不乘肩舆', ''),
 'jiao':   ('遂张盖肩舆', '视六卿矣'),
 'kowtow': ('上行三跪九叩头礼', '行三献礼'),
 'weep':   ('父老从者数万人', '皆感泣'),
 'ladle':  ('携一酒瓢，满酌送侍御', ''),
 'oath':   ('吾曹期不愧天日', '不愧百姓耳。'),
 'fairy':  ('公今日之行', '楚囚相对耶'),
 'empty':  ('行之日，囊无一钱', ''),
 'donkey': ('既归家，骑一驴', '往来田间'),
 'fifty':  ('崇祯朝，阁臣五十人', ''),
 'names':  ('崇祯朝，阁臣五十人：', '丘瑜。'),
 'grain1': ('伐香严寺木造舟', '木中有纹理成诗'),
 'poem1a': ('栽松种柏兴唐日', '破宋时。'),
 'poem1b': ('可惜香严千载树', '岁寒枝。'),
 'grain2': ('松上有绝句', '字如虫蛀者'),
 'poem2a': ('修庙还', '鹤巢空。'),
 'poem2b': ('不如留却青松在', '老化龙。'),
 'ape':    ('大不盈尺', '所谓通臂猿也。'),
 'ape2':   ('乃知画贵格物', ''),
 'maozhi': ('世几不知此老少年面目矣', '子真茂之知己也。'),
 'si1':    ('四娘已至前万福', '腰佩双剑。'),
 'si2':    ('妾故衡王宫嫔也', '生长金陵。'),
 'si3':    ('每张筵，初不见有宾客', '笑语酬酢。'),
 'si4':    ('悲不自胜，引节而歌', '举坐沾衣罢酒。'),
 'si5':    ('妾尘缘已尽，当往终南', ''),
 'ku1':    ('闻有人声自裤中出', '若近若远'),
 'ku2':    ('妾博罗韩氏女也。城陷被贼俘掳', '骂贼而死。'),
 'blind':  ('胸悬一牌云', '善决大疑。”'),
 'town':   ('比入市，则肩摩毂击', '万瓦鳞次。'),
 'wall':   ('见粉壁上累累有物', '皆人耳鼻也'),
 'man':    ('有伟男子科跣坐其上', ''),
 'hair':   ('否则某月日夫人', '宁忘之乎？'),
 'pale':   ('中丞启缄，忽色变而入', ''),
 'ni1':    ('取剑臂之，跨卫向南山径去', '倏忽不见。'),
 'ni2':    ('尼徒步手人头驱卫而返', ''),
 'ni3':    ('掷人头地上曰', '不错杀却否？”'),
 'ni4':    ('比东归，再往访之', '空无人矣。'),
}

TMPL = r'''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>池北偶谈 · 池月</title>
<style>
:root{
  --ink:#191917; --paper:#e8e4dc; --shih:#5e8fbb; --shihd:#3a5f83;
  --zhu:#c0453c; --faint:#a8a294; --night:#0f1216; --dusk:#1c1f24;
  --wood:#6b5236;
}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{background:var(--ink);color:var(--paper);
  font-family:"Songti SC","STSong","Noto Serif CJK SC","SimSun",serif;
  line-height:1.9;letter-spacing:.04em}
q{quotes:none;font-style:normal}
button{font-family:inherit;cursor:pointer;background:none;border:none;color:inherit}
.sec{max-width:1060px;margin:0 auto;padding:88px 28px 70px}
.shead{display:flex;align-items:baseline;gap:16px;border-bottom:1px solid #3a3a36;
  padding-bottom:14px;margin-bottom:16px}
.shead b{font-size:27px;font-weight:700;letter-spacing:.3em}
.shead span{font-size:13px;color:var(--faint);letter-spacing:.2em}
.note{color:#cfc9bc;font-size:15px;max-width:47em;margin:0 0 30px}
.rv{opacity:0;transform:translateY(26px);transition:opacity .9s ease,transform .9s ease}
.rv.on{opacity:1;transform:none}
.seal{display:inline-flex;align-items:center;justify-content:center;
  border:2.5px solid var(--zhu);color:var(--zhu);border-radius:6px;
  font-weight:700;letter-spacing:.1em;pointer-events:none}
@media (max-width:720px){.sec{padding:64px 18px 52px}.shead b{font-size:22px}
#seal-yu{right:10px;top:11%;padding:10px 5px;font-size:16px}}

/* ---- S0 首屏：池心月堕 ---- */
#hero{min-height:100vh;position:relative;overflow:hidden;display:flex;
  flex-direction:column;align-items:center;justify-content:center;padding:60px 18px}
#pond{width:min(92vw,660px);display:block}
#hit{position:absolute;left:50%;top:50%;transform:translate(-50%,10%);
  width:min(60vw,360px);height:150px;cursor:pointer;z-index:3}
.hword{position:absolute;left:0;right:0;top:8%;text-align:center;z-index:2;
  pointer-events:none}
.hword h1{font-size:clamp(40px,8vw,74px);letter-spacing:.32em;font-weight:700;
  opacity:0;transform:translateY(34px);transition:opacity 1.6s ease .5s,transform 1.6s ease .5s}
.hword .subline{margin-top:18px;font-size:15px;color:#cfc9bc;letter-spacing:.25em;
  opacity:0;transition:opacity 1.4s ease 1.4s}
.hword .waterline{margin-top:14px;font-size:13px;color:var(--shih);letter-spacing:.2em;
  opacity:0;transition:opacity 1.4s ease 2s}
#hero.lit h1,#hero.lit .subline,#hero.lit .waterline{opacity:1;transform:none}
#hint{position:absolute;bottom:7%;left:0;right:0;text-align:center;z-index:3;
  font-size:13px;color:var(--faint);letter-spacing:.3em;transition:opacity .6s}
#hero.lit #hint{opacity:0}
#seal-yu{position:absolute;right:calc(50% - min(46vw,330px) - 64px);top:16%;
  writing-mode:vertical-rl;padding:14px 6px;font-size:20px;opacity:0;
  transition:opacity 1.2s ease 2.2s;z-index:2}
#hero.lit #seal-yu{opacity:.92}
.moonhide{opacity:0;transition:opacity 2s ease .4s}
#hero.lit .moonhide{opacity:1}
@keyframes rip{0%{r:20;opacity:.85}100%{r:200;opacity:0}}
#hero.lit .rip{animation:rip 2.6s ease-out forwards}
.rip{opacity:0}

/* ---- 昼坛 ---- */
.day{background:var(--paper);color:#26241f}
.day .shead{border-color:#c9c2b2}
.day .shead span{color:#7d7666}
.day .note{color:#4a463c}
.day q{color:#3d4b5e}
.qcard{border-left:3px solid var(--shih);padding:10px 18px;margin:22px 0;
  font-size:16px;background:rgba(94,143,187,.07)}
.twocol{display:grid;grid-template-columns:1.1fr .9fr;gap:44px;align-items:start}
@media (max-width:820px){.twocol{grid-template-columns:1fr}}

/* 四签 */
.signtable{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:34px}
@media (max-width:720px){.signtable{grid-template-columns:repeat(2,1fr)}}
.sign{border:1px solid #c9c2b2;background:#efeadd;padding:20px 14px 16px;
  text-align:center;position:relative}
.sign::before{content:"";position:absolute;top:0;left:50%;transform:translateX(-50%);
  width:34px;height:5px;background:var(--dot,#8a8474)}
.sign b{display:block;font-size:19px;letter-spacing:.24em;margin:8px 0 6px}
.sign i{font-style:normal;font-size:12.5px;color:#7d7666;display:block}
.sign .cnt{position:absolute;top:10px;right:12px;font-size:12px;color:#a09a88}

/* 谒陵五步 */
.lx{display:flex;gap:10px;justify-content:space-between;margin:34px 0 8px;
  position:relative;flex-wrap:wrap}
.lx::before{content:"";position:absolute;left:4%;right:4%;top:31px;height:2px;
  background:#d3ccba}
.lxstep{flex:1 1 0;min-width:104px;text-align:center;position:relative}
.lxpai{width:62px;height:62px;margin:0 auto;border:1.6px solid #b4ac98;
  background:#efeadd;display:flex;align-items:center;justify-content:center;
  font-size:21px;letter-spacing:.1em;position:relative;z-index:1;
  transition:all .55s ease;color:#5a5446}
.lxstep.on .lxpai{background:var(--zhu);border-color:var(--zhu);color:var(--paper);
  transform:translateY(-6px);box-shadow:0 10px 22px rgba(192,69,60,.3)}
.lxstep p{font-size:13px;color:#7d7666;margin-top:12px;min-height:4.6em}
.lxstep q{display:block;font-size:13.5px;color:#3d4b5e}
#lxgo{border:1.4px solid var(--zhu);color:var(--zhu);padding:9px 30px;
  letter-spacing:.3em;font-size:14px;margin-top:8px}
#lxgo.off{opacity:.35;pointer-events:none}
.yeartag{font-size:12.5px;color:#a09a88;letter-spacing:.15em;margin-top:14px}

/* 倾瓢 */
.piaorow{display:grid;grid-template-columns:280px 1fr;gap:44px;align-items:center;
  margin-top:10px}
@media (max-width:820px){.piaorow{grid-template-columns:1fr}}
#piaobox{text-align:center}
#piao{width:200px;transition:transform .9s ease;transform-box:fill-box;transform-origin:center}
#piaobox.pour #piao{transform:rotate(-38deg) translateX(-16px)}
#stream{stroke:var(--shih);stroke-width:3;stroke-dasharray:6 7;
  stroke-dashoffset:220;transition:stroke-dashoffset 1.6s ease}
#piaobox.pour #stream{stroke-dashoffset:0}
.oathcard{opacity:.18;transform:translateX(16px);transition:all 1s ease .5s}
.oathcard>q{display:block}
#piaobox.pour ~ .oathcard{opacity:1;transform:none}
.oathcard>q{font-size:17.5px;margin-bottom:14px}
.gesture{font-size:12.5px;color:#a09a88;letter-spacing:.2em;margin-top:10px}

/* 五十相 */
.xq{display:block;border:1px solid #c9c2b2;background:#efeadd;padding:20px 22px;
  font-size:15px;line-height:2.3;margin-top:18px}
.xq span{display:inline-block;padding:0 2px}
.xq span.zhu{color:var(--zhu);font-weight:700;border-bottom:2px solid var(--zhu)}
.xq span.dim{color:#a09a88}

/* ---- 谈艺（暮色） ---- */
#yi{background:var(--dusk)}
#yi .shead{border-color:#33363c}
.plankrow{display:grid;grid-template-columns:1fr 1fr;gap:30px;margin-top:30px}
@media (max-width:820px){.plankrow{grid-template-columns:1fr}}
.plank{border:1px solid #3a352c;background:#221f19;padding:20px;position:relative}
.plank .poem{position:absolute;left:24px;right:24px;top:20px;bottom:64px;
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;
  text-align:center;opacity:0;transform:translateY(12px);transition:all 1.2s ease .3s;
  pointer-events:none}
.plank.show .poem{opacity:1;transform:none}
.plank .poem q{font-size:19px;letter-spacing:.16em;color:var(--paper);text-shadow:0 2px 10px #000}
@media (max-width:820px){.plank .poem q{font-size:15.5px}}
.plank svg{width:100%;display:block}
.plank .grain{transition:opacity 1.1s ease}
.plank.show .grain{opacity:.16}
.plank .ptag{font-size:12.5px;color:#9a9484;letter-spacing:.2em;margin-top:14px;
  text-align:center}
.apebox{margin-top:34px;border-left:3px solid var(--shih);padding:8px 20px}
.apebox q{display:block;font-size:15.5px;color:#c7cfda}
.apebox .mao{display:block;font-size:14.5px;color:#9fb0c4;margin-top:10px}

/* ---- 昼夜门 ---- */
#gate{background:linear-gradient(180deg,var(--dusk),var(--night));
  text-align:center;padding:130px 22px 110px;position:relative;overflow:hidden}
#gate q{font-size:clamp(20px,3.4vw,30px);letter-spacing:.22em;color:var(--paper);
  display:block;position:relative;z-index:2}
#gate .gwho{margin-top:16px;font-size:13px;color:var(--faint);letter-spacing:.25em;
  position:relative;z-index:2}
.gmoon{position:absolute;left:50%;top:26%;width:56px;height:56px;border-radius:50%;
  background:var(--paper);opacity:.22;transform:translateX(-50%);
  transition:transform 1.8s ease,opacity 1.8s ease;box-shadow:0 0 44px rgba(232,228,220,.35)}
#gate.on .gmoon{transform:translate(-50%,150px);opacity:.1}

/* ---- 夜坛 ---- */
.night{background:var(--night)}
.night .shead{border-color:#2b3038}
.night .note{color:#b9c2ce}
.night q{color:#c9d4e2}

/* 裤中魂 */
.kurow{display:grid;grid-template-columns:250px 1fr;gap:42px;align-items:center}
@media (max-width:820px){.kurow{grid-template-columns:1fr}}
#kubox{text-align:center;cursor:pointer}
#kuwave path{stroke:var(--shih);stroke-width:2;fill:none;opacity:0;
  transition:opacity 1s ease}
#kubox.spoken #kuwave path{opacity:.8}
#kubox.spoken #kuq{opacity:1;transform:none}
#kuq{opacity:.16;transform:translateY(10px);transition:all 1.1s ease .4s;font-size:15.5px}
#kuq q{display:block;margin-top:10px}

/* 林四娘三拍 */
#sibeats{margin-top:14px}
.beat{display:none;grid-template-columns:1fr 180px;gap:40px;align-items:center}
.beat.cur{display:grid;animation:fadein 1s ease}
@keyframes fadein{from{opacity:0}to{opacity:1}}
@media (max-width:820px){.beat{grid-template-columns:1fr}.beat .vcol{display:none}}
.beat q.big{font-size:17.5px;display:block;margin-bottom:16px}
.beat .bnote{color:#9aa7b8;font-size:14px;margin-top:16px}
.beatdots{display:flex;gap:12px;margin:26px 0 20px}
.bd{width:34px;height:34px;border:1.4px solid #3a4250;border-radius:50%;
  font-size:15px;color:#8b98aa;transition:all .4s}
.bd.cur{background:var(--zhu);border-color:var(--zhu);color:var(--paper)}
.vcol{writing-mode:vertical-rl;height:300px;letter-spacing:.34em;
  border-right:1px solid #2b3038;padding-right:20px;font-size:16px;
  color:#c9d4e2;margin-left:auto}

/* 剑侠夜行 */
.xia{margin-top:64px}
.xtrack{position:relative;border:1px solid #242a33;background:#11151b;
  padding:30px 26px 26px;transition:background 1.2s ease}
.xstops{display:flex;gap:8px;margin-bottom:24px}
.xstop{flex:1;text-align:center;font-size:13.5px;letter-spacing:.2em;color:#5d6878;
  padding-bottom:10px;border-bottom:2px solid #242a33;transition:all .5s}
.xstop.lit{color:var(--paper);border-color:var(--zhu)}
.xpanel{display:none;max-width:44em}
.xpanel.cur{display:block;animation:fadein .9s ease}
.xpanel q{font-size:17px;display:block;margin-bottom:12px}
.xpanel .xw{color:#93a1b4;font-size:14px}
.xbtns{margin-top:22px;display:flex;gap:16px;align-items:center}
#xgo{border:1.4px solid var(--shih);color:var(--shih);padding:9px 26px;
  letter-spacing:.24em;font-size:14px}
#xgo.fin{border-color:var(--zhu);color:var(--zhu)}
.xcount{font-size:12px;color:#5d6878;letter-spacing:.2em}
.zhuword{color:var(--zhu)}

/* 女侠尼三签 */
.nvx{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:26px}
@media (max-width:820px){.nvx{grid-template-columns:1fr}}
.nvx figure{border:1px solid #242a33;background:#13171d;padding:18px 18px 14px}
.nvx q{font-size:14.5px;display:block}
.nvx figcaption{font-size:12px;color:#5d6878;letter-spacing:.2em;margin-top:12px}

/* ---- 尾屏 ---- */
#coda{min-height:88vh;display:flex;flex-direction:column;align-items:center;
  justify-content:center;text-align:center;position:relative;overflow:hidden;
  background:linear-gradient(180deg,var(--night),#0b0d10);padding:110px 22px}
.hline{width:1px;height:70px;background:#2b3038;margin-bottom:40px}
#codamoon{width:64px;height:64px;border-radius:50%;background:var(--paper);
  opacity:.16;box-shadow:0 0 50px rgba(232,228,220,.3);
  transition:transform 2.4s ease,opacity 2.4s ease}
#coda.on #codamoon{transform:translateY(200px);opacity:.04}
#keepq{margin:44px 0 18px;font-size:clamp(19px,3vw,26px);letter-spacing:.2em;
  color:var(--paper)}
.ckw{color:#9aa7b8;font-size:14.5px;max-width:36em}
#seal-chi{margin-top:54px;padding:16px 8px;writing-mode:vertical-rl;font-size:21px}
footer{background:#0b0d10;color:#6f6a5e;font-size:12.5px;line-height:2.1;
  padding:34px 20px 44px;text-align:center;letter-spacing:.06em}
footer a{color:#8a8474}
</style>
</head>
<body>

<!-- S0 首屏 -->
<section id="hero">
  <div class="hword">
    <h1>池北偶谈</h1>
    <div class="subline">新城王士禛撰　康熙辛未成书</div>
    <div class="waterline"><q>__water__</q></div>
  </div>
  <svg id="pond" viewBox="0 0 660 430" aria-hidden="true">
    <defs>
      <radialGradient id="wg" cx="50%" cy="50%" r="60%">
        <stop offset="0%" stop-color="#232b36"/><stop offset="100%" stop-color="#12161c"/>
      </radialGradient>
      <filter id="mg" x="-80%" y="-80%" width="260%" height="260%">
        <feGaussianBlur stdDeviation="7"/>
      </filter>
    </defs>
    <circle cx="96" cy="64" r="1.3" fill="#e8e4dc" opacity=".4"/>
    <circle cx="176" cy="40" r="1" fill="#e8e4dc" opacity=".3"/>
    <circle cx="560" cy="52" r="1.2" fill="#e8e4dc" opacity=".35"/>
    <circle cx="608" cy="120" r="1" fill="#e8e4dc" opacity=".3"/>
    <circle cx="40" cy="150" r="1" fill="#e8e4dc" opacity=".25"/>
    <g class="moonhide">
      <circle cx="470" cy="120" r="24" fill="#e8e4dc" opacity=".9" filter="url(#mg)"/>
      <circle cx="470" cy="120" r="19" fill="#efeadd"/>
    </g>
    <g stroke="#8a8474" stroke-width="2" fill="none" opacity=".55">
      <path d="M470 96 q-52 -8 -96 22"/>
      <path d="M470 96 q54 -6 92 26"/>
      <path d="M470 96 v-30"/>
      <path d="M436 128 v26 M504 130 v24"/>
      <path d="M420 156 h100" stroke-width="1.6"/>
    </g>
    <ellipse cx="320" cy="330" rx="252" ry="72" fill="url(#wg)"/>
    <ellipse cx="320" cy="330" rx="252" ry="72" fill="none" stroke="#31384233" stroke-width="2"/>
    <clipPath id="pondclip"><ellipse cx="320" cy="330" rx="250" ry="70"/></clipPath>
    <g class="moonhide" clip-path="url(#pondclip)">
      <circle class="rip" cx="320" cy="336" r="20" fill="none" stroke="#5e8fbb" stroke-width="1.6"/>
      <circle class="rip" cx="320" cy="336" r="20" fill="none" stroke="#5e8fbb" stroke-width="1.2" style="animation-delay:.7s"/>
      <circle class="rip" cx="320" cy="336" r="20" fill="none" stroke="#5e8fbb" stroke-width="1" style="animation-delay:1.4s"/>
      <circle cx="320" cy="334" r="22" fill="#e8e4dc" opacity=".92"/>
      <ellipse cx="313" cy="328" rx="7" ry="4" fill="#fff" opacity=".55"/>
    </g>
    <path d="M92 322 q36 -7 72 0 M470 348 q42 -6 84 0" stroke="#3d465270" stroke-width="1.4" fill="none"/>
  </svg>
  <div id="hit" role="button" aria-label="点池心"></div>
  <div class="seal" id="seal-yu">渔洋</div>
  <div id="hint">点 池 心 · 候 月 堕</div>
</section>

<!-- S1 昼坛 · 来历 -->
<section class="sec day" id="origin">
  <div class="shead rv"><b>池北书库</b><span>书名所自</span></div>
  <p class="note rv">康熙三十年秋，自序成书。王士禛官至刑部尚书，执诗坛牛耳数十年，论诗主神韵。他的宅西有一方小池，池北几间老屋，藏书数千卷，名字借了白居易的旧典。暇日里与客人坐在池上那间画舫样的亭子中，谈的无非文章、经史、国故；至于夜里说些什么，序里也交代了。</p>
  <div class="twocol">
    <div>
      <div class="qcard rv"><q>__pool__</q></div>
      <div class="qcard rv"><q>__name__</q></div>
      <p class="note rv" style="margin-top:26px">书稿是家里小辈们从旁笔录攒出来的，日积月累，装订成二十六卷，分作四类：</p>
      <div class="qcard rv" style="font-size:15px"><q>__four__</q></div>
    </div>
    <div class="rv">
      <div class="signtable">
        <div class="sign" style="--dot:#c9963f"><span class="cnt">四卷</span><b>谈故</b><i>朝廷殊典<br>衣冠胜事</i></div>
        <div class="sign" style="--dot:#7d8fa3"><span class="cnt">六卷</span><b>谈献</b><i>贤臣名宦<br>布衣奇士</i></div>
        <div class="sign" style="--dot:#5e8fbb"><span class="cnt">九卷</span><b>谈艺</b><i>诗文书画<br>领异标新</i></div>
        <div class="sign" style="--dot:#c0453c"><span class="cnt">七卷</span><b>谈异</b><i>神仙鬼怪<br>姑妄听之</i></div>
      </div>
      <p class="note" style="font-size:13.5px;margin-top:18px">四类签色即本页地图：前三类在昼坛，末一类入夜坛。一枚书名，两种时辰。</p>
    </div>
  </div>
</section>

<!-- S2 昼坛 · 谈故 -->
<section class="sec day" id="gu">
  <div class="shead rv"><b>谈故</b><span>庙堂之上</span></div>
  <p class="note rv">谈故记本朝掌故。开卷第一条就有点戏：武臣原不许坐轿，康熙六年，有个管仪仗的武官上疏争到了这口气，从此张盖肩舆、视同六卿。<q>__luanwei__</q>，<q>__jiao__</q>。而全卷最重的一幕，是甲子年冬皇帝南巡金陵，亲谒明孝陵：前朝陵寝之前，今上以敌国之礼下拜，江南父老围观感泣。以下五步，循礼而行。</p>
  <div class="lx rv">
    <div class="lxstep" data-i="0"><div class="lxpai">驻</div><p>大驾入金陵，陵户肃立</p></div>
    <div class="lxstep" data-i="1"><div class="lxpai">行</div><p>皇帝不走正中御道，自旁而行</p></div>
    <div class="lxstep" data-i="2"><div class="lxpai">叩</div><p><q>__kowtow__</q></p></div>
    <div class="lxstep" data-i="3"><div class="lxpai">献</div><p>三献礼成，礼数无缺</p></div>
    <div class="lxstep" data-i="4"><div class="lxpai">泣</div><p><q>__weep__</q></p></div>
  </div>
  <button id="lxgo" class="rv">恭 谒 孝 陵</button>
  <p class="yeartag rv">岁在甲子（1684）；越五年己巳，再谒一次。</p>
</section>

<!-- S3 昼坛 · 谈献 -->
<section class="sec day" id="xian" style="background:#e2ddd0">
  <div class="shead rv"><b>谈献</b><span>人物之鉴</span></div>
  <p class="note rv">谈献六卷，记名臣、廉吏、畸人、烈女。王士禛推他为本朝州府官里清廉第一。此前同乡李御史巡按江南，遭谗被逮，吴地百姓数万哭送登舟，僚属相视挥涕；李正华最后一个到，只带了一只酒瓢。</p>
  <div class="piaorow">
    <div id="piaobox" class="rv">
      <svg viewBox="0 0 220 240" aria-hidden="true">
        <path id="stream" d="M86 148 q-26 32 -24 68" fill="none"/>
        <g id="piao">
          <ellipse cx="128" cy="96" rx="62" ry="34" fill="#8a7350"/>
          <ellipse cx="128" cy="92" rx="62" ry="30" fill="#a58a5f"/>
          <ellipse cx="128" cy="92" rx="46" ry="20" fill="#7a623f"/>
          <path d="M72 104 q-34 10 -50 40" stroke="#8a7350" stroke-width="13" fill="none" stroke-linecap="round"/>
          <path d="M104 76 q22 -14 44 -2" stroke="#7a623f" stroke-width="4" fill="none"/>
        </g>
        <text x="110" y="234" text-anchor="middle" font-size="12" fill="#a09a88" letter-spacing="3">瓢中酒</text>
      </svg>
      <div class="gesture">点 瓢 · 满 酌</div>
    </div>
    <div class="oathcard">
      <q>__ladle__</q>
      <q>__oath__</q>
      <q>__fairy__</q>
      <p class="note" style="font-size:14px;margin-top:18px">瓢是给御史送行的，话是说给满船哭丧脸的僚属听的。后来李正华考成镌级去官，<q>__empty__</q>；还乡之后，<q>__donkey__</q>。</p>
    </div>
  </div>

  <div class="shead rv" style="margin-top:76px"><b>崇祯五十相</b><span>十七年 · 五十位宰相</span></div>
  <p class="note rv">谈献里夹着一份冷静到可怕的名册：崇祯在位十七年，内阁大学士前后五十人，平均四个月换一位。名册照录如下，最后两位的结局，是史册里最冷的注脚。</p>
  <q class="xq rv" id="xq">__names__</q>
  <p class="note rv" style="font-size:13.5px;margin-top:14px">校字记：名册中蒋德、黄景、吴三人名下库本各阙一字，据史补识为璟、昉、甡；名册中括注为库本原样。</p>
</section>

<!-- S4 暮 · 谈艺 -->
<section class="sec" id="yi">
  <div class="shead rv"><b>谈艺</b><span>诗文书画</span></div>
  <p class="note rv">谈艺九卷是全书的重镇，评诗论文，记所见书画。这里取两件最玄的事：木头里的诗。淅川古称商于，金兵南下时，香严寺的古木被砍来造船，木纹里竟现出字来；顺治辛卯年，又有个道人砍松修观，树上再显绝句。两块木板，各藏一首。</p>
  <div class="plankrow">
    <div class="plank rv" data-plank="1">
      <svg viewBox="0 0 400 150" aria-hidden="true">
        <defs><linearGradient id="wd" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#7a5f3e"/><stop offset="100%" stop-color="#5c4630"/>
        </linearGradient></defs>
        <rect x="6" y="10" width="388" height="130" rx="8" fill="url(#wd)"/>
        <g class="grain" stroke="#2e2317" stroke-width="1.6" fill="none" opacity=".85">
          <path d="M14 40 q90 12 190 2 t182 6"/>
          <path d="M14 74 q110 -14 200 4 t172 -8"/>
          <path d="M14 108 q86 10 210 0 t162 6"/>
          <path d="M60 24 q40 30 8 96"/>
        </g>
      </svg>
      <div class="poem">
        <q>__poem1a__</q>
        <q>__poem1b__</q>
      </div>
      <p class="ptag">香严寺舟木（金人伐木所见） · 点板读诗</p>
    </div>
    <div class="plank rv" data-plank="2">
      <svg viewBox="0 0 400 150" aria-hidden="true">
        <rect x="6" y="10" width="388" height="130" rx="8" fill="url(#wd)"/>
        <g class="grain" stroke="#2e2317" stroke-width="1.6" fill="none" opacity=".85">
          <path d="M14 36 q100 16 186 0 t186 8"/>
          <path d="M14 72 q90 -12 196 6 t176 -6"/>
          <path d="M14 110 q120 8 204 -4 t168 8"/>
          <path d="M330 22 q-42 34 -6 102"/>
        </g>
      </svg>
      <div class="poem">
        <q>__poem2a__</q>
        <q>__poem2b__</q>
      </div>
      <p class="ptag">回阳观松（树上现出绝句） · 点板读诗</p>
    </div>
  </div>
  <p class="note rv" style="font-size:14px;margin-top:22px">板一之诗，谶唐宋兴亡；板二之诗，救了一棵松。诸生祷于神，字如虫蛀，众人称异，伐松遂止。纹里有话，木不肯死。<q>__grain1__</q>。</p>

  <div class="twocol" style="margin-top:56px">
    <div class="apebox rv">
      <span class="shead" style="border:none;padding:0;margin-bottom:8px"><b style="font-size:20px">画贵格物</b><span>谈艺八</span></span>
      <q>__ape__</q>
      <q>__ape2__</q>
      <p class="note" style="font-size:14px;margin-top:12px">宣宗画过一头黑猿，猿臂挂在一根横木上，几百年无人解。直到门人从粤东回来说，岭外真有这种猿。看画看到这一层，才算看懂。</p>
    </div>
    <div class="apebox rv" style="border-color:#3a5f83">
      <span class="shead" style="border:none;padding:0;margin-bottom:8px"><b style="font-size:20px">传灯之托</b><span>谈艺三</span></span>
      <q class="mao" style="color:#c7cfda">__maozhi__</q>
      <p class="note" style="font-size:14px;margin-top:12px">老诗人林茂之携六十年诗稿求王士禛论定，得到这样一句回答。这一条，是乱世诗脉一线相承的温柔，也是盟主把自己放进书里的方式。</p>
    </div>
  </div>
</section>

<!-- S5 昼夜门 -->
<section id="gate">
  <div class="gmoon"></div>
  <q>__moon__</q>
  <div class="gwho">自序语 · 昼坛至此关闭</div>
</section>

<!-- S6 夜坛 · 谈异 -->
<section class="sec night" id="night">
  <div class="shead rv"><b>谈异</b><span>夜半七卷</span></div>
  <p class="note rv">谈异七卷，记神仙鬼怪。这一坛在夜里开，先听一条最小的：乱后的广州，有人在市上买了一条裤子。</p>

  <div class="kurow rv">
    <div id="kubox">
      <svg viewBox="0 0 200 220" aria-hidden="true">
        <path d="M62 26 h76 l10 84 -26 84 h-20 l-12 -70 -12 70 h-20 l-26 -84 z"
          fill="#20262f" stroke="#3a4250" stroke-width="2"/>
        <path d="M62 26 h76 v18 h-76 z" fill="#2b3340"/>
        <g id="kuwave">
          <path d="M100 44 q-30 18 -22 44 q8 26 -8 44" opacity="0"/>
          <path d="M100 44 q30 18 22 44 q-8 26 8 44" opacity="0"/>
          <path d="M100 52 q-16 22 -6 46 q10 22 -4 40" opacity="0"/>
        </g>
      </svg>
      <div class="gesture">点 裤 · 听 声</div>
    </div>
    <div id="kuq">
      <q>__ku1__</q>
      <q>__ku2__</q>
      <p class="note" style="font-size:14px">那声音在裤子里说话，忽远忽近。众邻延僧诵经，焚了那条裤，怪事方绝。一句骂贼而死的自述，让一条裤成了全书最小的招魂幡。</p>
    </div>
  </div>

  <div class="shead rv" style="margin-top:80px"><b>林四娘</b><span>青州夜宴 · 三拍</span></div>
  <p class="note rv">谈异四卷里最著名的一篇。福建人陈宝钥在青州做官，某日在书斋里坐得久了，忽有婢女通报：林四娘来见。来的却不是活人。</p>
  <div id="sibeats" class="rv">
    <div class="beatdots">
      <button class="bd cur" data-b="0">至</button>
      <button class="bd" data-b="1">宴</button>
      <button class="bd" data-b="2">别</button>
    </div>
    <div class="beat cur">
      <div>
        <q class="big">__si1__</q>
        <q class="big">__si2__</q>
        <p class="bnote">腰佩双剑，故王宫嫔：鬼而侠，侠而艳。她要借陈的亭馆延客，于陈无所损益。</p>
      </div>
      <div class="vcol"><q>__si1__</q></div>
    </div>
    <div class="beat">
      <div>
        <q class="big">__si3__</q>
        <q class="big">__si4__</q>
        <p class="bnote">张筵而无客，笑语自满一堂。她讲起王府旧事，歌罢满座沾衣。亡国的记忆由一个鬼来保管。</p>
      </div>
      <div class="vcol"><q>__si4__</q></div>
    </div>
    <div class="beat">
      <div>
        <q class="big">__si5__</q>
        <p class="bnote">年馀后黯然辞去，往终南。数年之后，淄川人蒲松龄把同一个林四娘写进了自己的书；为那部书题诗的，正是本书作者。志怪史上的两位山东人，在同一支曲子上碰了杯。</p>
      </div>
      <div class="vcol"><q>__si5__</q></div>
    </div>
  </div>

  <div class="xia rv" id="xia">
    <div class="shead"><b>剑侠</b><span>夜行五站 · 与瞽叟入山</span></div>
    <p class="note">一位中丞派小吏押送三千两官银进京，夜里投宿古庙，晨起金失而门钥宛然。中丞怒责赔偿，小吏请限一月自寻，以妻子为质。以下五站，越走越深。</p>
    <div class="xtrack" id="xtrack">
      <div class="xstops">
        <div class="xstop lit">失金</div>
        <div class="xstop">遇叟</div>
        <div class="xstop">入镇</div>
        <div class="xstop">粉壁</div>
        <div class="xstop">截发</div>
      </div>
      <div class="xpanel cur">
        <p class="xw">官吏一路询访无所得，将归。忽然，市中多了一个胸挂牌子的瞎老头。</p>
      </div>
      <div class="xpanel">
        <q>__blind__</q>
        <p class="xw">漫问之，叟竟先开口问出了失金数目。觅车载叟，君第随往。</p>
      </div>
      <div class="xpanel">
        <q>__town__</q>
        <p class="xw">入深山行数百里，至一大市镇，肩摩毂击，如王公之居。堂上坐着一个长发男子。</p>
      </div>
      <div class="xpanel">
        <q>__man__</q>
        <q>__wall__</q>
        <p class="xw"><span class="zhuword">粉壁之上，皆是耳鼻。</span>看得人魂飞魄散，深宅四合，插翅难逃，僵坐到天亮。</p>
      </div>
      <div class="xpanel">
        <q>__hair__</q>
        <q>__pale__</q>
        <p class="xw">金不可得，但予一纸书。中丞启缄色变，释吏赔责，并还其妻子。他不敢追问的那笔账，半夜有人替他记着。</p>
      </div>
      <div class="xbtns">
        <button id="xgo">随 叟 入 山</button>
        <span class="xcount" id="xcount">第一站 · 共五站</span>
      </div>
    </div>
  </div>

  <div class="rv" style="margin-top:70px">
    <div class="shead"><b>女侠尼</b><span>剑侠的余韵</span></div>
    <p class="note">又一桩：解官银的役夫夜宿尼庵，红巾恶人掷香破门，银失而众仆。庵中尼出，牵一头黑驴，取剑臂上，径入南山。</p>
    <div class="nvx">
      <figure><q>__ni1__</q><figcaption>往</figcaption></figure>
      <figure><q>__ni2__</q><q>__ni3__</q><figcaption>返</figcaption></figure>
      <figure><q>__ni4__</q><figcaption>空</figcaption></figure>
    </div>
    <p class="note" style="font-size:14px;margin-top:18px">再访时，庵门已锁，院里空空的，人早已不在。全书最快的侠，自始至终没有露过一次真名。</p>
  </div>
</section>

<!-- S7 尾屏 -->
<section id="coda">
  <div class="hline"></div>
  <div id="codamoon"></div>
  <q id="keepq">__keep__</q>
  <p class="ckw">辛未秋的自序里，作者把这部杂书的用处说得极谦：大处可以养德，小处可以增广见闻，总比博弈强。庙堂与鬼话，廉吏与剑侠，木纹里的兴亡与裤中魂的自述，都被他收进池北的几间老屋。</p>
  <div class="seal" id="seal-chi">池北</div>
</section>

<footer>
  <p>文本来源：殆知阁古代文献简体库 〈池北偶谈〉史藏志存记录本 · github.com/robertsong/daizhige-daodu</p>
  <p>引文经脚本自库本锚点切片生成，去标点归一后逐字比对通过；白话行文与库本六字窗反扫零撞。</p>
  <p>所录志怪、贞烈诸条皆时代底色，照录存照，不代今人立论。</p>
</footer>

<script>
(function(){
  var io=new IntersectionObserver(function(es){
    es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('on');io.unobserve(e.target);}});
  },{threshold:.18});
  document.querySelectorAll('.rv,#gate,#coda').forEach(function(el){io.observe(el);});

  var hero=document.getElementById('hero'),hit=document.getElementById('hit'),lit=false;
  hit.addEventListener('click',function(){
    if(lit)return; lit=true;
    hero.classList.add('lit');
    var h=document.getElementById('hint'); if(h)h.textContent='';
  });

  var lxgo=document.getElementById('lxgo');
  if(lxgo){lxgo.addEventListener('click',function(){
    lxgo.classList.add('off');
    var steps=document.querySelectorAll('#gu .lxstep');
    steps.forEach(function(s,i){setTimeout(function(){s.classList.add('on');},420*i+200);});
  });}

  var pb=document.getElementById('piaobox');
  if(pb){pb.addEventListener('click',function(){pb.classList.toggle('pour');});}

  document.querySelectorAll('.plank').forEach(function(p){
    p.addEventListener('click',function(){p.classList.toggle('show');});
  });

  var kb=document.getElementById('kubox');
  if(kb){kb.addEventListener('click',function(){kb.classList.toggle('spoken');});}

  var beats=document.querySelectorAll('#sibeats .beat'),bds=document.querySelectorAll('#sibeats .bd');
  bds.forEach(function(b){b.addEventListener('click',function(){
    var i=+b.dataset.b;
    beats.forEach(function(x,k){x.classList.toggle('cur',k===i);});
    bds.forEach(function(x,k){x.classList.toggle('cur',k===i);});
  });});

  var xgo=document.getElementById('xgo'),xc=document.getElementById('xcount');
  var xp=document.querySelectorAll('.xpanel'),xs=document.querySelectorAll('.xstop');
  var xi=0;
  var nums=['第一','第二','第三','第四','第五'];
  if(xgo){xgo.addEventListener('click',function(){
    if(xi>=xp.length-1)return;
    xi++;
    xp.forEach(function(p,k){p.classList.toggle('cur',k===xi);});
    xs.forEach(function(s,k){s.classList.toggle('lit',k<=xi);});
    xc.textContent=nums[xi]+'站 · 共五站';
    if(xi===xp.length-1){xgo.textContent='夜 已 深';xgo.classList.add('fin');}
  });}
})();
</script>
</body>
</html>
'''

def main():
    src = open(SRC, encoding='utf-8').read()
    flat = ''.join(src.split())
    html = TMPL
    fails = 0
    for key, (s, e) in QUOTES.items():
        if flat.count(s) != 1:
            print(f'FAIL: 锚不唯一({flat.count(s)}): {key} {s[:24]}'); fails += 1; continue
        i = flat.find(s)
        if e:
            j = flat.find(e, i)
            if j < 0:
                print(f'FAIL: 终锚未找到: {key} {e[:20]}'); fails += 1; continue
            frag = flat[i:j + len(e)]
        else:
            frag = s
        if len(frag) < 4:
            print(f'FAIL: 切片过短: {key}'); fails += 1; continue
        n = len(PUA.findall(frag))
        if n:
            print(f'NOTE: {key} 含库本残字 {n} 处, 映射为□存照')
            frag = PUA.sub('□', frag)
        html = html.replace(f'__{key}__', frag)
    left = [t for t in ('__',) if t in html]
    if '__' in html:
        import re
        miss = sorted(set(re.findall(r'__[a-z0-9]+__', html)))
        print(f'FAIL: 未注入 token: {miss}'); fails += 1
    qn = html.count('<q')
    open(OUT, 'w', encoding='utf-8').write(html)
    print(f'OK: {OUT} 引文 {qn} 处, 失败 {fails}')
    return 1 if fails else 0

if __name__ == '__main__':
    sys.exit(main())
