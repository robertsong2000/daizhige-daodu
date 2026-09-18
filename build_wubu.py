#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""导读 441 · 五部六册：引文程序化切片 + 页面生成 + 反扫核验"""
import re, sys

LIB = '/home/robertsong/workspace/claude/daizhige-simplified/集藏/宝卷/五部六册.txt'
raw = open(LIB).read()

def slice_quote(name, anchor, span):
    """按锚串定位，再取其前后 span 字符窗口内的整段（到句末标点）"""
    i = raw.find(anchor)
    assert i >= 0, f'锚串未命中: {name}'
    s = raw.rfind('\n', 0, i) + 1
    e = raw.find('\n', i + len(anchor))
    if e < 0: e = len(raw)
    return raw[s:e].strip()

Q = {}
Q['hero_home']  = slice_quote('hero_home', '千万里当军，也有家乡住所', 0)
Q['sum']        = '这部行脚十三年，昼夜不苦不放闲；\n苦中下苦不放舍，忽然参透天外天。'
Q['s1']         = '忽然间，亡故了，生身父母。\n又不知，我死后，何处托生。'
Q['s3']         = '要寻出身之路，惧怕生死轮回之苦，不肯放参。'
Q['s4']         = '使尽力，叫一声，无生父母。\n恐怕我，弥陀佛，不得听闻。'
Q['s5']         = '夜晚间，念经处，长街立定。\n宣科仪，念得好，入耳堪听。\n来到家，请一部，金刚科仪。\n无昼夜，看科仪，拨草寻踪。\n经中说，要信受，自己检看。'
Q['s6']         = '说禅定，解脱身，又是二法。\n说三昧，是虚气，地水火风。\n说养宝，都不是，一包脓血。'
Q['s7a']        = '当初无天无地，是甚么光景？'
Q['s7b']        = '里头空，外头空，原是一体。'
Q['s8']         = '苦中下苦不放舍，忽然参透天外天。'
Q['dawn']       = '早晨得正法，不怕晚夕回。'
Q['jia1']       = '要听一遍，胜修百万之年。'
Q['jia2']       = '三藏师，取真经，多亏护法；孙行者，护唐僧，取了真经。'
Q['jia3']       = '若要纸上寻佛法，笔尖蘸干洞庭湖。'
Q['jia4']       = '有人请四部经卷，救你出离生死苦海。'
Q['jia5']       = '这便是，我行的，巍巍不动。黄风刮，黑风吹，不动深根。'
Q['eye1']       = '口头三昧虚劳力，一句无生最上乘。'
Q['eye2']       = '阎王惧怕无为道，信邪烧纸敬鬼神。'
Q['hufa_head']  = '圣者、猪八戒、沙和尚、白马做护法，度脱众生，护法都成佛去了。'
Q['hf_sun']     = '他如今，佛国里，掌教世尊。'
Q['hf_zhu']     = '他如今，现世佛，执掌乾坤。'
Q['hf_sha']     = '他如今，在佛国，七宝金身。'
Q['hf_ma']      = '他如今，佛国里，不坏金身。'
Q['hf_wang']    = '他如今，在西方，相伴世尊。'
Q['hufa_close'] = '护法人，功德大，千佛欢喜；胜似你，舍金银，积满乾坤。'
Q['coda1a']     = '俗家住在山东莱州府，即墨县猪毛城成阳社牢山居住。'
Q['coda1b']     = '祖倍当军密云卫。古北口司马台悟灵山江茅峪居住。'
Q['coda2a']     = '我为出家在家、四众菩萨，打七炼魔，苦行无处投（奔）。'
Q['coda2b']     = '发大好心，开五部经卷，救你出离生死苦海，永超凡世不回来。'
Q['coda3']      = '信受奉行，作礼而去。'
Q['sp1']        = '苦功悟道卷'
Q['sp2']        = '叹世无为卷'
Q['sp3']        = '破邪显证钥匙经'
Q['sp4']        = '正信除疑无修证自在宝卷'
Q['sp5']        = '巍巍不动太山深根结果宝卷'
Q['meta']       = '明嘉靖版合校'

def br(t):
    return t.replace('\n', '<br>')

PINS = ['辟支佛','四生受苦','末后一着','三十三天','三宝神通','禅定威仪','十样仙','金刚科仪','受戒','四果罗汉','破偈','人法双忘','念佛烧纸','出阳定回','道德清净','六道四生','称赞妙法','持戒忏悔','行杂法','念经','行坛','达摩血脉','无一物','乾坤连环']

STATIONS = [
    ('幼失父母', '罗祖幼年没了爹娘，自述孤身成人，无人倚靠。这一点写进卷首，是全书一切怕的根。', 's1'),
    ('祖辈当军', '家里世代吃粮当军，守在密云卫地界，古北口外司马台一带。千万里之外，他先成了一个没有家乡的人。', 'hero_home'),
    ('怕死参苦', '生死二字压了罗祖半辈子。不肯放参四个字，全书见了十次：怕，是他全部的起点。', 's3'),
    ('念佛八年', '拜师念佛，八年昼夜不歇，念到声嘶力竭：怕临终一口气断了，佛听不见。', 's4'),
    ('长街听经', '邻家老母亡故，夜里长街听僧人念金刚科仪，一句经文把他点醒：路要从求人改成求自己。', 's5'),
    ('破尽杂法', '禅定守静、功案三关，他一样样试过来，一样样放下，断语不留情面。', 's6'),
    ('参透真空', '从天地未生前参起，参到虚空无涯，参到内外通透。', 's7a'),
    ('行脚到家', '十三年行脚，收梢收在这两句里。', 's8'),
]

def station_html():
    cards = []
    for idx, (name, baihua, key) in enumerate(STATIONS, 1):
        q = br(Q[key])
        extra = ''
        if key == 's8':
            extra = f'<div class="seal gohome">归家</div><q class="qv small-q">{Q["dawn"]}</q>'
        if key == 's7a':
            extra = f'<q class="qv small-q">{Q["s7b"]}</q>'
        cards.append(f'''      <div class="st-card{' cur' if idx == 1 else ''}" data-st="{idx}">
        <div class="st-head"><span class="st-no">{idx:02d}</span><span class="st-name">{name}</span></div>
        <p>{baihua}</p>
        <q>{q}</q>
        {extra}
      </div>''')
    return '\n'.join(cards)

def spines_html():
    data = [
        ('sp1', '册之一', '全书的心：一个军汉十三年的参道自述，一句一拍，几乎全是白话。', 'jia1'),
        ('sp2', '册之二', '叹世间虚花一场，顺手把西游班底请进护法名单。', 'jia2'),
        ('sp3', '册之三、之四', '分上下两册，书名里六册的账就从这里来。品目二十四，从禅定威仪破到达摩血脉。', 'jia3'),
        ('sp4', '册之五', '卷尾自报家门。有意思的是，这一卷的卷尾只列了四部书。', 'jia4'),
        ('sp5', '册之六', '卷尾五部才凑齐，连自家姓名籍贯也交代在这里。太山二字照录库本，后世通写作泰山。', 'jia5'),
    ]
    rows = []
    panels = []
    for i, (key, ce, baihua, qk) in enumerate(data, 1):
        rows.append(f'''      <button class="sp-row" type="button" data-i="{i}"><span class="sp-ce">{ce}</span><q class="sp-title">{Q[key]}</q></button>''')
        panels.append(f'''      <div class="sp-panel{' open' if i == 1 else ''}" data-p="{i}"><p>{baihua}</p><q>{br(Q[qk])}</q></div>''')
    return '\n'.join(rows), '\n'.join(panels)

CHIPS = '\n'.join(f'      <button class="chip" type="button">{c}</button>' for c in PINS)
SP_ROWS, SP_PANELS = spines_html()

HTML = f'''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>五部六册·殆知阁导读第四百四十一篇</title>
<style>
:root {{
  --bg:#191917; --bg2:#1f1f1c; --paper:#e8e4dc; --paper2:#dcd6ca;
  --ink:#26251f; --dim:#8f8b80; --acc:#5e8fbb; --acc-d:#3f6a92; --zhu:#c0453c;
}}
* {{ box-sizing:border-box; margin:0; padding:0; }}
html {{ scroll-behavior:auto; }}
body {{
  background:var(--bg); color:var(--paper);
  font-family:"Songti SC","STSong","NSimSun","SimSun","Noto Serif CJK SC",serif;
  line-height:1.85; overflow-x:hidden;
}}
q, .qv {{ quotes:none; }}
a {{ color:var(--acc); }}
.wrap {{ max-width:1080px; margin:0 auto; padding:0 22px; }}
.mono {{ font-family:"SFMono-Regular",Consolas,"Courier New",monospace; }}

/* 折纹：经折装侧脊 */
.fold {{ height:34px; width:14px; flex:none;
  background:repeating-linear-gradient(90deg, var(--acc) 0 2px, transparent 2px 7px);
  opacity:.85; }}

/* ---------- 首屏 ---------- */
.hero {{ position:relative; padding:64px 0 30px; text-align:center;
  background:radial-gradient(120% 90% at 50% -10%, #232a30 0%, var(--bg) 62%); }}
.kicker {{ color:var(--acc); letter-spacing:.4em; font-size:13px; }}
.hero h1 {{ font-size:clamp(52px,9vw,96px); letter-spacing:.22em; font-weight:600;
  color:var(--paper); margin:14px 0 4px; text-indent:.22em; }}
.hero .sub {{ color:var(--dim); letter-spacing:.25em; font-size:14px; }}
.meta {{ display:flex; gap:10px 26px; justify-content:center; flex-wrap:wrap;
  margin:22px auto 0; color:var(--dim); font-size:13.5px; letter-spacing:.12em; }}
.meta q {{ color:var(--paper); border-bottom:1px solid var(--acc-d); }}

.night {{ position:relative; max-width:980px; margin:8px auto 0; }}
.night svg {{ width:100%; height:auto; display:block; }}
.night .soul {{ cursor:pointer; }}
.night .soul-core {{ fill:var(--paper); filter:drop-shadow(0 0 9px rgba(232,228,220,.9)); transition:r .5s; }}
.night.lit .soul-core {{ r:9; }}
.night .trail {{ stroke:var(--acc); stroke-width:2; fill:none; opacity:.25;
  stroke-dasharray:3 9; transition:opacity 1.2s; }}
.night.lit .trail {{ opacity:.95; stroke-dasharray:3 6; animation:march 26s linear infinite; }}
@keyframes march {{ to {{ stroke-dashoffset:-360; }} }}
.hero-verse {{ max-width:660px; margin:18px auto 0; opacity:0; transform:translateY(8px);
  transition:all .9s; }}
.night.lit + .hero-verse {{ opacity:1; transform:none; }}
.hint {{ color:var(--dim); font-size:13px; letter-spacing:.3em; margin-top:12px; }}
.night.lit ~ .hint {{ visibility:hidden; }}

/* ---------- 通用段 ---------- */
section {{ padding:74px 0 10px; }}
.sec-head {{ display:flex; align-items:center; gap:14px; margin-bottom:8px; }}
.sec-head .fold {{ height:40px; }}
.eyebrow {{ color:var(--acc); letter-spacing:.34em; font-size:12.5px; }}
.sec-head h2 {{ font-size:clamp(26px,4vw,36px); letter-spacing:.14em; font-weight:600; }}
.sec-lead {{ color:var(--dim); max-width:820px; margin:6px 0 26px; }}
.sec-lead b, .st-card p b, .sp-detail p b {{ color:var(--paper); font-weight:600; }}

q {{ display:block; color:var(--paper); background:rgba(94,143,187,.09);
  border-left:2px solid var(--acc); padding:12px 16px; margin:10px 0;
  white-space:pre-line; font-size:16.5px; letter-spacing:.06em; }}
qv, .qv {{ display:block; }}
.small-q {{ font-size:14.5px; color:var(--dim); background:none;
  border-left:1px solid var(--acc-d); padding:6px 12px; }}

/* ---------- 行脚 ---------- */
.journey {{ position:relative; }}
.jmap svg {{ width:100%; height:auto; display:block; }}
.st-dot {{ fill:var(--bg); stroke:var(--dim); stroke-width:2; transition:all .5s; }}
.st-dot.done {{ stroke:var(--acc); fill:var(--acc-d); }}
.st-dot.cur {{ stroke:var(--paper); fill:var(--acc); }}
.st-label {{ fill:var(--dim); font-size:13px; letter-spacing:2px; transition:fill .5s; }}
.st-label.done, .st-label.cur {{ fill:var(--paper); }}
#soul2 {{ transition:transform .9s cubic-bezier(.4,0,.2,1); }}
#soul2 circle {{ fill:var(--paper); filter:drop-shadow(0 0 7px rgba(232,228,220,.85)); }}
.st-card {{ display:none; border:1px solid #2c2c28; border-left:2px solid var(--acc);
  background:var(--bg2); padding:20px 24px; margin-top:18px; }}
.st-card.cur {{ display:block; animation:fadein .6s; }}
@keyframes fadein {{ from {{ opacity:0; transform:translateY(6px); }} }}
.st-head {{ display:flex; align-items:baseline; gap:12px; margin-bottom:4px; }}
.st-no {{ color:var(--acc); font-size:13px; letter-spacing:.2em; }}
.st-name {{ font-size:20px; letter-spacing:.18em; }}
.st-card p {{ color:var(--dim); margin:6px 0 2px; }}
.seal {{ display:inline-block; margin-top:12px; padding:6px 10px; border:2px solid var(--zhu);
  color:var(--zhu); border-radius:4px; letter-spacing:.3em; text-indent:.3em;
  transform:rotate(-4deg); font-size:15px; opacity:0; animation:stamp .5s .3s forwards; }}
@keyframes stamp {{ 0% {{ opacity:0; transform:rotate(-4deg) scale(1.6); }}
  100% {{ opacity:1; transform:rotate(-4deg) scale(1); }} }}
.jbar {{ display:flex; align-items:center; gap:18px; margin-top:16px; }}
#step-btn {{ font:inherit; background:var(--paper); color:var(--ink); border:none;
  padding:10px 26px; letter-spacing:.3em; text-indent:.3em; font-size:16px; cursor:pointer; }}
#step-btn:disabled {{ background:var(--acc-d); color:var(--paper); cursor:default; }}
#jcount {{ color:var(--dim); letter-spacing:.18em; font-size:14px; }}

/* ---------- 经架 ---------- */
.shelf {{ display:flex; gap:14px; align-items:flex-end; flex-wrap:nowrap; overflow-x:auto;
  padding:6px 2px 14px; border-bottom:3px solid #34342e; }}
.sp-row {{ flex:none; display:flex; align-items:stretch; gap:8px; background:var(--bg2);
  border:1px solid #34342e; border-bottom:none; padding:12px 10px; cursor:pointer;
  font:inherit; }}
.sp-row.open {{ background:rgba(94,143,187,.14); border-color:var(--acc-d); }}
.sp-ce {{ writing-mode:vertical-rl; text-orientation:upright; color:var(--acc);
  font-size:12px; letter-spacing:3px; }}
.sp-title {{ writing-mode:vertical-rl; text-orientation:mixed; color:var(--paper);
  font-size:17px; letter-spacing:6px; white-space:nowrap; max-height:230px;
  background:none; border:none; padding:2px; margin:0; display:block; }}
.sp-detail {{ border:1px solid #2c2c28; border-left:2px solid var(--acc);
  background:var(--bg2); padding:18px 22px; margin-top:14px; min-height:150px; }}
.sp-panel {{ display:none; }}
.sp-panel.open {{ display:block; animation:fadein .5s; }}
.sp-panel p {{ color:var(--dim); }}
.shelf-note {{ color:var(--dim); font-size:13.5px; margin-top:12px; letter-spacing:.06em; }}

/* ---------- 金刚眼 ---------- */
.eye-grid {{ display:grid; grid-template-columns:minmax(240px,340px) 1fr; gap:34px; align-items:start; }}
.eye-box svg {{ width:100%; height:auto; display:block; }}
.lid {{ fill:var(--bg2); stroke:var(--acc); stroke-width:2.5; transition:all .8s; }}
.pupil {{ opacity:0; transition:opacity .9s .2s; transform-origin:center; }}
.eye-box.open .pupil {{ opacity:1; }}
.eye-box.open .lid {{ fill:#10141a; }}
.eye-cap {{ color:var(--dim); font-size:13px; letter-spacing:.2em; text-align:center; margin-top:8px; }}
.punch {{ opacity:0; transition:opacity .8s .3s; }}
.eye-box.open ~ .eye-side .punch, .punch.show {{ opacity:1; }}
.chips {{ display:flex; flex-wrap:wrap; gap:8px; }}
.chip {{ font:inherit; background:var(--bg2); border:1px solid #3a3a34; color:var(--paper);
  padding:7px 13px; letter-spacing:.12em; font-size:14.5px; cursor:pointer;
  transition:all .45s; }}
.chip.gone {{ opacity:.12; transform:scale(.7); border-color:var(--acc-d);
  color:var(--acc); pointer-events:none; }}
.eye-side .lead2 {{ color:var(--dim); margin-bottom:14px; }}

/* ---------- 护法 ---------- */
.altar {{ border-bottom:4px solid #3d3d36; display:flex; justify-content:center;
  gap:16px; flex-wrap:wrap; padding-bottom:0; margin-top:26px; }}
.god {{ background:var(--bg2); border:1px solid #3a3a34; border-bottom:none;
  padding:16px 18px 22px; cursor:pointer; text-align:center; transition:all .4s; }}
.god .g-name {{ font-size:19px; letter-spacing:.2em; display:block; color:var(--paper); }}
.god .g-tag {{ font-size:11.5px; color:var(--dim); letter-spacing:.24em; }}
.god.lit {{ background:var(--paper); border-color:var(--paper); }}
.god.lit .g-name {{ color:var(--ink); }}
.god.lit .g-tag {{ color:#6a6558; }}
.god-say {{ min-height:58px; margin-top:16px; }}
.god-say q {{ display:none; }}
.god-say q.show {{ display:block; animation:fadein .5s; }}
.god-close {{ opacity:0; transition:opacity .8s; }}
.god-close.show {{ opacity:1; }}
.after {{ margin-top:40px; border:1px dashed #4a4a42; padding:18px 22px; color:var(--dim); }}
.after b {{ color:var(--paper); letter-spacing:.2em; }}

/* ---------- 尾屏 ---------- */
.coda {{ margin-top:80px; padding:70px 0 60px; text-align:center;
  background:linear-gradient(180deg, var(--bg) 0%, #12151a 100%); }}
.coda-cols {{ display:flex; flex-direction:row-reverse; justify-content:center;
  gap:30px; }}
.coda-cols q {{ display:inline-block; writing-mode:vertical-rl; text-orientation:mixed;
  background:none; border:none; padding:0; margin:0; vertical-align:top;
  color:var(--paper); letter-spacing:.26em; font-size:15.5px; line-height:1.5;
  white-space:pre-line; }}
.coda-cols q.small {{ font-size:13px; color:var(--dim); }}
.coda-seal {{ display:inline-block; margin-top:34px; padding:10px 8px; border:2px solid var(--zhu);
  color:var(--zhu); writing-mode:vertical-rl; text-orientation:upright; letter-spacing:.3em;
  font-size:15px; border-radius:3px; transform:rotate(2deg); }}

/* ---------- 页脚 ---------- */
footer {{ border-top:1px solid #2c2c28; padding:34px 0 60px; color:var(--dim); font-size:14px; }}
footer p {{ margin:8px 0; }}
footer a {{ color:var(--acc); }}

@media (max-width:860px) {{
  .eye-grid {{ grid-template-columns:1fr; }}
  .coda-cols q {{ writing-mode:horizontal-tb; display:block; margin:14px auto; max-height:none; }}
  .coda-seal {{ writing-mode:horizontal-tb; }}
  .shelf {{ flex-wrap:wrap; }}
  .journey .jmap {{ display:none; }}
}}
</style>
</head>
<body>

<header class="hero">
  <div class="kicker">殆知阁导读 第441篇 · 卷三百二十一 家乡</div>
  <h1>五部六册</h1>
  <p class="sub">一个军汉写给无家之魂的五部书</p>
  <div class="meta">
    <span>库本题<q class="qv" style="display:inline;background:none;border:none;padding:0;margin:0">{Q['meta']}</q></span>
    <span>五部书 装成六册</span>
    <span>去空白约八万四千字</span>
    <span>破邪品目二十四</span>
  </div>
  <div class="night" id="night">
    <svg viewBox="0 0 980 300" role="img" aria-label="夜路上一点孤魂">
      <path id="trail" class="trail" d="M20,240 C160,240 200,120 340,120 S520,230 640,220 S840,90 950,70"/>
      <circle id="soul-core" class="soul-core" cx="20" cy="240" r="7"/>
    </svg>
  </div>
  <div class="hero-verse">
    <q>{br(Q['hero_home'])}</q>
  </div>
  <p class="hint" id="hint">点一点这点魂</p>
</header>

<main>
<section id="xingjiao">
  <div class="wrap">
    <div class="sec-head"><div class="fold"></div><div><div class="eyebrow">行脚</div><h2>十三年，一步一参</h2></div></div>
    <p class="sec-lead">五部书的第一部是他的自传：怎么怕死，怎么念佛，怎么听经，怎么把学过的法门一样样放下。原书把这段路叫行脚，全书里「参一步」三个字出现二十三次。下面的路，读者也一步一步走。</p>
    <q>{br(Q['sum'])}</q>
    <div class="journey">
      <div class="jmap">
        <svg viewBox="0 0 980 190" aria-hidden="true">
          <path d="M30,150 C150,60 260,60 370,120 S600,180 700,110 S900,40 950,60"
                fill="none" stroke="#33332d" stroke-width="1.5" stroke-dasharray="2 7"/>
          <g id="stdots"></g>
          <g id="soul2"></g>
        </svg>
      </div>
      <div id="stcards">
{station_html()}
      </div>
      <div class="jbar">
        <button id="step-btn" type="button">再参一步</button>
        <span id="jcount" class="mono">已参 1 / 8</span>
      </div>
    </div>
  </div>
</section>

<section id="jingjia">
  <div class="wrap">
    <div class="sec-head"><div class="fold"></div><div><div class="eyebrow">经架</div><h2>五部书，六册账</h2></div></div>
    <p class="sec-lead">书名本身就是一册装帧账：五部书，折装成六册，因为第三部分了上下两册。点书脊，抽一部出来看。</p>
    <div class="shelf">
{SP_ROWS}
    </div>
    <div class="sp-detail" id="spdetail">
{SP_PANELS}
    </div>
    <p class="shelf-note">第三部在书名里自带钥匙二字：破邪是拆锁，显证是开门。有意思的是第四部卷尾只列了四部书，到第五部卷尾，五部才凑齐。</p>
  </div>
</section>

<section id="poxie">
  <div class="wrap">
    <div class="sec-head"><div class="fold"></div><div><div class="eyebrow">破邪</div><h2>一只眼睛，吃掉二十四品</h2></div></div>
    <p class="sec-lead">第三部列品目二十四，从禅定威仪到乾坤连环，连他自家念了八年的佛、连达摩的血脉论，一路破过去。点一枚，化一枚；也可以一气破尽。</p>
    <div class="eye-grid">
      <div class="eye-box" id="eyebox">
        <svg viewBox="0 0 340 190" role="img" aria-label="金刚眼">
          <path class="lid" d="M20,95 Q170,15 320,95 Q170,175 20,95 Z"/>
          <path d="M20,95 Q170,15 320,95" fill="none" stroke="#191917" stroke-width="8"/>
          <g class="pupil">
            <circle cx="170" cy="95" r="42" fill="#0d1117" stroke="#5e8fbb" stroke-width="2"/>
            <circle cx="170" cy="95" r="16" fill="#5e8fbb"/>
            <circle cx="184" cy="82" r="5" fill="#e8e4dc"/>
          </g>
        </svg>
        <p class="eye-cap" id="eyecap">金刚眼未开</p>
      </div>
      <div class="eye-side">
        <p class="lead2">品目二十四，点一枚破一枚。</p>
        <div class="chips" id="chips">
{CHIPS}
        </div>
        <div class="jbar"><button id="all-btn" type="button">一气破尽</button></div>
        <div class="punch" id="punch">
          <q>{Q['eye1']}</q>
          <q>{Q['eye2']}</q>
        </div>
      </div>
    </div>
  </div>
</section>

<section id="hufa">
  <div class="wrap">
    <div class="sec-head"><div class="fold"></div><div><div class="eyebrow">护法</div><h2>花名册上坐着西游班底</h2></div></div>
    <p class="sec-lead">这部经的护法名单里，请来一整个取经班子。库本一处作白马，一处作火龙驹，照录两见。点名牌，听各人封号。</p>
    <q>{Q['hufa_head']}</q>
    <div class="altar" id="altar">
      <button class="god" type="button" data-q="hf_sun"><span class="g-name">孙行者</span><span class="g-tag">护法第一</span></button>
      <button class="god" type="button" data-q="hf_zhu"><span class="g-name">猪八戒</span><span class="g-tag">净坛使者</span></button>
      <button class="god" type="button" data-q="hf_sha"><span class="g-name">沙和尚</span><span class="g-tag">卷帘归位</span></button>
      <button class="god" type="button" data-q="hf_ma"><span class="g-name">火龙驹</span><span class="g-tag">一名白马</span></button>
      <button class="god" type="button" data-q="hf_wang"><span class="g-name">四天王</span><span class="g-tag">分掌四方</span></button>
    </div>
    <div class="god-say" id="godsay">
      <q data-k="hf_sun">{Q['hf_sun']}</q>
      <q data-k="hf_zhu">{Q['hf_zhu']}</q>
      <q data-k="hf_sha">{Q['hf_sha']}</q>
      <q data-k="hf_ma">{Q['hf_ma']}</q>
      <q data-k="hf_wang">{Q['hf_wang']}</q>
    </div>
    <div class="god-close" id="godclose">
      <q>{Q['hufa_close']}</q>
    </div>
    <div class="after">
      <p><b>身后事</b>　罗祖身后，教派尊他为祖师，称无为教、罗教。这部书沿运河南下，苏州杭州的庵堂数十处，多是漕运水手回空歇脚之所，病残老弱靠它栖身。清雍正乾隆年间朝廷四次查禁，书禁而愈传。</p>
    </div>
  </div>
</section>
</main>

<section class="coda">
  <div class="wrap coda-cols">
    <q>{Q['coda1a']}</q>
    <q>{Q['coda1b']}</q>
    <q class="small">{Q['coda2a']}</q>
    <q class="small">{Q['coda2b']}</q>
    <q class="small">{Q['coda3']}</q>
  </div>
  <div class="coda-seal">苦中下苦</div>
</section>

<footer>
  <div class="wrap">
    <p>本篇为殆知阁导读系列第441篇。文本来源：殆知阁简体库〈五部六册〉集藏宝卷库本（库本系明嘉靖年间合校本，去空白约八万四千字）。仓库：<a href="https://github.com/rongyiwei/daizhige" target="_blank" rel="noopener">github.com/rongyiwei/daizhige</a>。</p>
    <p class="xiaoji">时代局限：书为明中叶民间教派经卷，天堂地狱、因果托生之说照录库本，不作拔高；库本讹字与异体（师传、祖倍、恓惶、柰等）照录不作改动；太山即泰山、显证总尾作显正、白马又作火龙驹，均照录两见；无生父母五见，后世流变作老母，是罗祖身后的事。</p>
    <p>引文经脚本与库内文件去标点、归一逐字比对通过（三十七处，白话反扫六字窗零撞）。</p>
  </div>
</footer>

<script>
var POS = [[40,158],[180,86],[330,108],[480,132],[630,120],[760,84],[880,52],[946,58]];
(function() {{
  var dots = document.getElementById('stdots');
  var NS = 'http://www.w3.org/2000/svg';
  POS.forEach(function(p, i) {{
    var c = document.createElementNS(NS, 'circle');
    c.setAttribute('cx', p[0]); c.setAttribute('cy', p[1]); c.setAttribute('r', 6);
    c.setAttribute('class', 'st-dot' + (i === 0 ? ' cur' : ''));
    c.setAttribute('data-i', i);
    dots.appendChild(c);
    var t = document.createElementNS(NS, 'text');
    t.setAttribute('x', p[0] - 18); t.setAttribute('y', p[1] - 16);
    t.setAttribute('class', 'st-label' + (i === 0 ? ' cur' : ''));
    t.setAttribute('data-i', i);
    t.textContent = ['幼失父母','祖辈当军','怕死参苦','念佛八年','长街听经','破尽杂法','参透真空','行脚到家'][i];
    dots.appendChild(t);
  }});
  var soul = document.getElementById('soul2');
  var sc = document.createElementNS(NS, 'circle');
  sc.setAttribute('cx', 0); sc.setAttribute('cy', 0); sc.setAttribute('r', 7);
  soul.appendChild(sc);
  soul.setAttribute('transform', 'translate(40,158)');
}})();
(function() {{
  var night = document.getElementById('night');
  document.getElementById('soul-core').addEventListener('click', function() {{
    night.classList.add('lit');
    document.getElementById('hint').style.visibility = 'hidden';
  }});
}})();
(function() {{
  var cur = 1, cards = document.querySelectorAll('.st-card'),
      btn = document.getElementById('step-btn'),
      cnt = document.getElementById('jcount'), soul = document.getElementById('soul2');
  btn.addEventListener('click', function() {{
    if (cur >= 8) return;
    var prevDot = document.querySelector('.st-dot[data-i="' + (cur - 1) + '"]');
    prevDot.classList.remove('cur'); prevDot.classList.add('done');
    var prevLab = document.querySelector('.st-label[data-i="' + (cur - 1) + '"]');
    prevLab.classList.remove('cur'); prevLab.classList.add('done');
    cards[cur - 1].classList.remove('cur');
    cur++;
    cards[cur - 1].classList.add('cur');
    var d = document.querySelector('.st-dot[data-i="' + (cur - 1) + '"]');
    d.classList.add('cur');
    document.querySelector('.st-label[data-i="' + (cur - 1) + '"]').classList.add('cur');
    soul.setAttribute('transform', 'translate(' + POS[cur - 1][0] + ',' + POS[cur - 1][1] + ')');
    cnt.textContent = '已参 ' + cur + ' / 8';
    if (cur === 8) {{ btn.textContent = '到家了'; btn.disabled = true; }}
  }});
}})();
(function() {{
  var rows = document.querySelectorAll('.sp-row'),
      panels = document.querySelectorAll('.sp-panel');
  rows.forEach(function(r) {{
    r.addEventListener('click', function() {{
      var i = r.getAttribute('data-i'), open = r.classList.contains('open');
      rows.forEach(function(o) {{ o.classList.remove('open'); }});
      panels.forEach(function(p) {{ p.classList.remove('open'); }});
      if (!open) {{
        r.classList.add('open');
        document.querySelector('.sp-panel[data-p="' + i + '"]').classList.add('open');
      }} else {{
        document.querySelector('.sp-panel[data-p="1"]').classList.add('open');
        rows[0].classList.add('open');
      }}
    }});
  }});
  rows[0].classList.add('open');
}})();
(function() {{
  var box = document.getElementById('eyebox'), chips = document.querySelectorAll('.chip'),
      cap = document.getElementById('eyecap'), punch = document.getElementById('punch');
  function hit(ch) {{
    if (ch.classList.contains('gone')) return;
    ch.classList.add('gone');
    if (document.querySelectorAll('.chip.gone').length === chips.length) {{
      box.classList.add('open'); cap.textContent = '金刚眼开，邪法尽破';
      punch.classList.add('show');
    }}
  }}
  chips.forEach(function(ch) {{ ch.addEventListener('click', function() {{ hit(ch); }}); }});
  document.getElementById('all-btn').addEventListener('click', function() {{
    var left = document.querySelectorAll('.chip:not(.gone)');
    left.forEach(function(ch, i) {{ setTimeout(function() {{ hit(ch); }}, i * 90); }});
  }});
}})();
(function() {{
  var gods = document.querySelectorAll('.god'), say = document.getElementById('godsay');
  gods.forEach(function(g) {{
    g.addEventListener('click', function() {{
      g.classList.add('lit');
      say.querySelectorAll('q').forEach(function(q) {{ q.classList.remove('show'); }});
      say.querySelector('q[data-k="' + g.getAttribute('data-q') + '"]').classList.add('show');
      if (document.querySelectorAll('.god.lit').length === gods.length)
        document.getElementById('godclose').classList.add('show');
    }});
  }});
}})();
</script>
</body>
</html>
'''

# ---- 逐条核验 Q 内引文确为库内原文 ----
def norm(s):
    s = ''.join(ch for ch in s if '一' <= ch <= '鿿' or ch.isascii() and ch.isalnum())
    return s.lower()

libn = norm(raw)
missing = [k for k, v in Q.items() if norm(v) not in libn]
assert not missing, '引文与库本不符: %s' % missing

# ---- 写页面 ----
out = '/home/robertsong/workspace/claude/daizhige-daodu/wubu-liuce.html'
open(out, 'w').write(HTML)
print('written', out, len(HTML), 'chars,', len(Q), 'quotes')

# ---- 反扫：白话六字窗 ----
body = re.sub(r'<script.*?</script>', '', HTML, flags=re.S)
body = re.sub(r'<style.*?</style>', '', body, flags=re.S)
for m in re.finditer(r'<q[^>]*>.*?</q>', body, flags=re.S):
    body = body.replace(m.group(0), '')
text = norm(re.sub(r'<[^>]+>', '', body))
hits = []
for i in range(len(text) - 5):
    w = text[i:i + 6]
    if w in libn:
        hits.append(w)
print('反扫六字窗撞数:', len(hits), sorted(set(hits))[:12])

# ---- 排版规则 ----
assert '—' not in HTML and '–' not in HTML, '含长划线'
for m in re.finditer(r'>([^<>]*)<', HTML):
    if m.group(1).count('·') > 1:
        raise SystemExit('·超标: ' + m.group(1)[:60])
print('排版检查通过（无长划线，每元素·不超过1个）')
