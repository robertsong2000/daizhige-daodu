# -*- coding: utf-8 -*-
# 医贯 · 走马灯壳 · 竹青
# 引文全部由库本锚点切片生成,禁止手抄
import re, sys

SRC = '/home/robertsong/workspace/claude/daizhige-simplified/医藏/医贯.txt'
OUT = '/home/robertsong/workspace/claude/daizhige-daodu/yiguan.html'

src = open(SRC, encoding='utf-8').read()

# (token, start_anchor, end_anchor or None for single-anchor slice)
QUOTES = [
    ('Q_XU',      '医巫闾子医贯序', None),
    ('Q_XIAN',    '仙炼之为丹', '一以贯之也'),
    ('Q_TAO',     '盖有逃名之意焉', '藏诸山以俟其人'),
    ('Q_MEN',     '造化以阳为生之根', '人生以火为生之门'),
    ('Q_GUAN',    '心者。君主之官也', '气化则能出矣'),
    ('Q_FEIXIN',  '愚谓人身别有一主非心也', '当云十一官矣'),
    ('Q_ZHU',     '愚谓人身别有一主非心也', None),
    ('Q_DENG',    '譬之元宵之鳌山走马灯', '躯壳未尝不存也'),
    ('Q_ZHUN',    '余所以谆谆必欲明此论者', '加意于火之一字'),
    ('Q_WEIXING', '故曰汝身非汝所有', '是天地之委形也'),
    ('Q_SHUI1',   '命门君主之火', '壮水之主。以镇阳光'),
    ('Q_SHUI2',   '火之不足', '以消阴翳'),
    ('Q_KAN',     '易所谓一阳陷于二阴之中', None),
    ('Q_KAN2',    '内经曰。七节之旁。有小心是也', '是为真君真主'),
    ('Q_LONG1',   '霹雳火也', '得雨而益炽'),
    ('Q_LONG2',   '善治者。以温肾之药', '此至理也'),
    ('Q_LONG3',   '奈何今之治阴虚火衰者', '良可悲哉'),
    ('Q_YU1',     '予谓凡病之起', '抑而不通之义'),
    ('Q_YU2',     '丹溪先生云', '诸病生焉'),
    ('Q_YANG',    '故养生莫先于养火', None),
    # 十二官职守(qv)
    ('Q_DUTY1',  '神明出焉', None), ('Q_DUTY2',  '治节出焉', None),
    ('Q_DUTY3',  '谋虑出焉', None), ('Q_DUTY4',  '决断出焉', None),
    ('Q_DUTY5',  '喜乐出焉', None), ('Q_DUTY6',  '五味出焉', None),
    ('Q_DUTY7',  '变化出焉', None), ('Q_DUTY8',  '化物出焉', None),
    ('Q_DUTY9',  '伎巧出焉', None), ('Q_DUTY10', '水道出焉', None),
    ('Q_DUTY11', '津液藏焉', None),
]

slices = {}
for item in QUOTES:
    tok, a, b = item[0], item[1], item[2]
    nth = item[3] if len(item) > 3 else 0
    n = src.count(a)
    if n <= nth:
        sys.exit(f'anchor occurrence {nth} missing: {tok} x{n}')
    s = src.index(a) if nth == 0 else [m.start() for m in re.finditer(re.escape(a), src)][nth]
    e = (src.index(b, s) + len(b)) if b else (s + len(a))
    sl = re.sub(r'[　\s]+', '', src[s:e])
    if not sl:
        sys.exit(f'empty slice {tok}')
    for ch in sl:
        if '' <= ch <= '':
            sys.exit(f'PUA char in {tok}: {hex(ord(ch))}')
    slices[tok] = sl

TPL = r'''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>医贯导读 · 殆知阁</title>
<style>
  :root{
    --ink:#191917; --ink2:#201f1d; --paper:#e8e4dc;
    --dim:#a39e93; --faint:#6e6a61;
    --zhu:#5f9270; --hair:rgba(232,228,220,.13);
    --fire1:#e8b454; --fire2:#d07a34; --fire3:#c0453c;
  }
  *{margin:0;padding:0;box-sizing:border-box}
  html{scroll-behavior:smooth}
  body{background:var(--ink);color:var(--paper);
    font-family:"Songti SC","Noto Serif CJK SC","Source Han Serif SC","SimSun",serif;
    line-height:1.9; -webkit-font-smoothing:antialiased}
  .wrap{max-width:1060px;margin:0 auto;padding:0 24px}
  q{quotes:none}
  q::before,q::after{content:none}
  .qv{color:var(--zhu);font-size:.92em}
  a{color:var(--zhu)}

  /* ---------- hero ---------- */
  .hero{min-height:96vh;display:flex;flex-direction:column;align-items:center;
    justify-content:center;padding:56px 18px 30px;position:relative;
    background:radial-gradient(ellipse 70% 46% at 50% 44%, rgba(95,146,112,.10), rgba(95,146,112,0) 70%),
               radial-gradient(ellipse 40% 26% at 50% 40%, rgba(232,180,84,.07), rgba(0,0,0,0) 70%)}
  .kicker{letter-spacing:.42em;font-size:13px;color:var(--dim);margin-bottom:6px}
  .lamp-stage{width:min(500px,88vw);margin:6px 0 2px}
  .lamp-stage svg{width:100%;height:auto;display:block}
  #wheel{transform-box:fill-box;transform-origin:center;
    animation:wspin var(--spin,8s) linear infinite}
  @keyframes wspin{to{transform:rotate(360deg)}}
  body.lamp-hi{--spin:2.2s}
  body.lamp-lo{--spin:8s}
  body.lamp-off #wheel{animation-play-state:paused}
  .flamein{transform-box:fill-box;transform-origin:50% 100%;
    animation:flick 2.6s ease-in-out infinite;transition:transform 1.4s ease,opacity 1.4s ease}
  @keyframes flick{0%,100%{transform:scaleY(1) scaleX(1)}38%{transform:scaleY(1.14) scaleX(.94)}70%{transform:scaleY(.94) scaleX(1.05)}}
  body.lamp-hi .flamein{transform:scaleY(1.34)}
  body.lamp-off .flamein{animation:none;transform:scaleY(.14);opacity:.28}
  #glow{transition:opacity 1.4s ease}
  body.lamp-hi #glow{opacity:1}
  body.lamp-lo #glow{opacity:.62}
  body.lamp-off #glow{opacity:.07}
  .panel-p{transition:opacity 1s ease}
  body.lamp-off .panel-p{opacity:.34}
  .dial{display:flex;gap:14px;margin:16px 0 6px}
  .dial button{background:none;border:1px solid var(--hair);color:var(--dim);
    font:inherit;font-size:15px;letter-spacing:.28em;padding:8px 22px 8px 26px;
    cursor:pointer;transition:.3s;border-radius:2px}
  .dial button:hover{border-color:var(--zhu);color:var(--paper)}
  .dial button.act{border-color:var(--zhu);color:var(--paper);
    background:rgba(95,146,112,.16)}
  .dial-cap{font-size:12.5px;color:var(--faint);letter-spacing:.2em}
  .still-note{display:none;margin-top:12px;color:var(--dim);font-size:14.5px;letter-spacing:.14em}
  body.lamp-off .still-note{display:block}
  .hero-t{margin-top:26px;text-align:center}
  .hero-t h1{font-size:52px;font-weight:600;letter-spacing:.5em;text-indent:.5em}
  .hero-t .who{color:var(--dim);font-size:16px;letter-spacing:.3em;margin-top:4px}
  .hero-t .one{color:var(--faint);font-size:14px;margin-top:16px;max-width:620px}
  .scrolldn{position:absolute;bottom:18px;color:var(--faint);font-size:12px;letter-spacing:.4em}

  /* ---------- sections ---------- */
  section{padding:96px 0}
  section.alt{background:var(--ink2)}
  .shead{display:flex;align-items:baseline;gap:20px;margin-bottom:40px}
  .sno{font-size:15px;color:var(--zhu);border:1px solid rgba(95,146,112,.45);
    padding:3px 12px;letter-spacing:.3em;white-space:nowrap;border-radius:2px}
  .shead h2{font-size:27px;font-weight:600;letter-spacing:.22em}
  .shead .en{color:var(--faint);font-size:13px;letter-spacing:.24em;margin-left:auto;white-space:nowrap}
  .prose{max-width:760px;color:#cfcabf;font-size:16.5px}
  .prose p{margin:0 0 18px}
  .q{display:block;background:rgba(95,146,112,.07);border-left:3px solid var(--zhu);
    padding:22px 28px;margin:30px 0;color:var(--paper);font-size:19px;line-height:2.15;
    letter-spacing:.06em;border-radius:0 3px 3px 0}
  .q[data-who]::after{content:attr(data-who);display:block;margin-top:12px;
    font-size:13px;color:var(--dim);letter-spacing:.18em}
  .cap{color:var(--dim);font-size:14px;letter-spacing:.14em}

  /* s1 */
  .tri{display:flex;gap:26px;align-items:stretch;margin:34px 0 6px;flex-wrap:wrap}
  .tri .node{flex:1;min-width:150px;border:1px solid var(--hair);padding:22px 20px;text-align:center;border-radius:3px}
  .tri .node b{display:block;font-size:30px;font-weight:600;letter-spacing:.2em}
  .tri .node span{color:var(--dim);font-size:13.5px;letter-spacing:.12em}
  .tri .join{align-self:center;color:var(--zhu);font-size:24px;padding:0 2px}
  .origin{margin:26px 0 0;border:1px dashed rgba(95,146,112,.5);padding:18px 24px;
    display:inline-block;border-radius:3px;font-size:15px;color:#cfcabf}
  .origin .qv{font-size:17px;letter-spacing:.1em}

  /* s2 十二官 */
  .guan-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:30px 0 20px}
  .guan{background:none;border:1px solid var(--hair);border-radius:3px;padding:16px 10px 13px;
    text-align:center;cursor:pointer;font:inherit;color:var(--paper);transition:.25s}
  .guan:hover{border-color:rgba(95,146,112,.6)}
  .guan.act{border-color:var(--zhu);background:rgba(95,146,112,.13)}
  .guan .gn{display:block;font-size:26px;font-weight:600;letter-spacing:.1em}
  .guan .du{display:block;color:var(--dim);font-size:13.5px;margin-top:6px;letter-spacing:.06em}
  .guan.zhu{border-style:dashed;border-color:rgba(95,146,112,.75)}
  .guan.zhu .gn{color:var(--zhu)}
  .gp{border:1px solid var(--hair);border-radius:3px;padding:24px 30px;min-height:104px;position:relative}
  .gd{display:none}
  .gd.act{display:block}
  .gd .gg{font-size:21px;font-weight:600;letter-spacing:.14em}
  .gd .gg small{color:var(--dim);font-size:14px;font-weight:400;margin-left:12px;letter-spacing:.1em}
  .gd .qv{display:block;margin-top:8px;font-size:16.5px}
  .gd q{display:block;margin-top:8px;color:var(--paper);font-size:16.5px;
    border-left:3px solid var(--zhu);padding-left:14px;line-height:2}

  /* s4 split */
  .split{display:grid;grid-template-columns:300px 1fr;gap:52px;align-items:center}
  .split svg{width:100%;height:auto}
  .pills{display:flex;gap:20px;flex-wrap:wrap;margin:26px 0 0}
  .pill{flex:1;min-width:240px;border:1px solid var(--hair);border-radius:3px;padding:20px 24px}
  .pill b{display:block;color:var(--zhu);letter-spacing:.24em;font-size:16px;margin-bottom:10px}
  .pill .q{margin:0;padding:14px 0 0;border:none;background:none;font-size:16px;line-height:2}

  /* s5 龙雷 */
  .stage{border:1px solid var(--hair);border-radius:4px;padding:14px 14px 6px;margin:26px 0 8px;
    background:linear-gradient(180deg, rgba(95,146,112,.05), rgba(0,0,0,0))}
  .stage svg{width:100%;height:auto;display:block}
  .stg-btns{display:flex;gap:14px;margin:14px 0 4px;flex-wrap:wrap}
  .stg-btns button{background:none;border:1px solid var(--hair);color:var(--dim);font:inherit;
    font-size:14.5px;letter-spacing:.22em;padding:8px 20px;cursor:pointer;transition:.3s;border-radius:2px}
  .stg-btns button:hover{border-color:var(--zhu);color:var(--paper)}
  .drop{opacity:0;transform-box:fill-box}
  body.raining .drop{animation:fall 1s linear infinite}
  @keyframes fall{0%{transform:translateY(0);opacity:.85}100%{transform:translateY(96px);opacity:0}}
  .f5{transform-box:fill-box;transform-origin:50% 100%;transition:transform 1.3s ease}
  body.raining .f5{transform:scale(1.45)}
  body.guiding .f5{transform:translateY(30px) scale(.72)}
  #g5{transition:opacity 1.3s ease;transform-box:fill-box;transform-origin:center}
  body.raining #g5{opacity:1}
  body.guiding #g5{opacity:.4}
  .trough{opacity:0;transition:opacity 1.3s ease}
  body.guiding .trough{opacity:1}
  .note5{display:none;margin:10px 4px 8px;color:var(--dim);font-size:14.5px;letter-spacing:.1em}
  body.raining .n-rain{display:block}
  body.guiding .n-gui{display:block}

  /* s6 郁 */
  .wu{display:flex;gap:16px;margin:32px 0 10px;flex-wrap:wrap}
  .wu .w{flex:1;min-width:110px;text-align:center;border:1px solid var(--hair);border-radius:3px;padding:22px 8px 18px}
  .wu b{display:block;font-size:42px;font-weight:600;color:var(--zhu)}
  .wu span{display:block;color:var(--dim);font-size:13px;margin-top:10px;letter-spacing:.14em}

  /* outro */
  .outro{padding:130px 0 90px;text-align:center;position:relative}
  .outro .big{font-size:30px;letter-spacing:.3em;line-height:2.2;margin:26px 0 34px}
  .outro .big .qv{font-size:inherit}
  .seal{display:inline-block;border:2px solid rgba(95,146,112,.8);color:var(--zhu);
    padding:14px 10px;font-size:19px;letter-spacing:.28em;writing-mode:vertical-rl;
    border-radius:2px;margin-top:44px}

  footer{border-top:1px solid var(--hair);padding:44px 0 60px;color:var(--faint);
    font-size:13.5px;line-height:2.1}
  footer a{color:var(--dim)}
  footer .qv{color:var(--zhu)}

  @media (max-width:760px){
    .hero-t h1{font-size:40px}
    .guan-grid{grid-template-columns:repeat(3,1fr)}
    .split{grid-template-columns:1fr;gap:26px}
    .shead .en{display:none}
    section{padding:70px 0}
  }
</style>
</head>
<body class="lamp-lo">

<header class="hero">
  <div class="kicker">殆知阁导读　第528篇　竹青 · 医藏</div>
  <div class="lamp-stage">
    <svg viewBox="0 0 520 480" aria-label="走马灯">
      <defs>
        <radialGradient id="gGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#e8b454" stop-opacity=".34"/>
          <stop offset="55%" stop-color="#d07a34" stop-opacity=".12"/>
          <stop offset="100%" stop-color="#d07a34" stop-opacity="0"/>
        </radialGradient>
        <linearGradient id="gFl" x1="0" y1="1" x2="0" y2="0">
          <stop offset="0%" stop-color="#c0453c"/>
          <stop offset="55%" stop-color="#d07a34"/>
          <stop offset="100%" stop-color="#e8b454"/>
        </linearGradient>
      </defs>
      <line x1="260" y1="0" x2="260" y2="42" stroke="rgba(232,228,220,.25)" stroke-width="1.4"/>
      <path d="M198 42 L322 42 L300 70 L220 70 Z" fill="#232620" stroke="rgba(95,146,112,.5)" stroke-width="1.4"/>
      <ellipse id="glow" cx="260" cy="205" rx="185" ry="130" fill="url(#gGlow)"/>
      <g id="wheel">
        <g transform="rotate(0 260 190)">
          <path class="panel-p" d="M206 46 Q260 34 314 46 L292 122 L228 122 Z" fill="rgba(232,228,220,.09)" stroke="rgba(95,146,112,.55)" stroke-width="1.3"/>
          <circle cx="234" cy="60" r="2" fill="rgba(95,146,112,.8)"/>
          <circle cx="286" cy="60" r="2" fill="rgba(95,146,112,.8)"/>
          <g fill="rgba(232,228,220,.72)">
            <circle cx="243" cy="72" r="6"/>
            <path d="M243 79 q-9 5 -11 19 l7 3 q3 -11 8 -13 z"/>
          </g>
          <text x="276" y="88" font-size="13" fill="rgba(163,158,147,.8)" letter-spacing="1">拜</text>
        </g>
        <g transform="rotate(60 260 190)">
          <path class="panel-p" d="M206 46 Q260 34 314 46 L292 122 L228 122 Z" fill="rgba(232,228,220,.09)" stroke="rgba(95,146,112,.55)" stroke-width="1.3"/>
          <circle cx="234" cy="60" r="2" fill="rgba(95,146,112,.8)"/>
          <circle cx="286" cy="60" r="2" fill="rgba(95,146,112,.8)"/>
          <g fill="rgba(232,228,220,.72)">
            <circle cx="252" cy="70" r="6"/>
            <path d="M252 77 q-14 2 -19 16 l6 4 q6 -10 13 -11 z"/>
            <path d="M252 77 q14 4 16 18 l-7 3 q-4 -10 -11 -13 z"/>
          </g>
          <text x="270" y="88" font-size="13" fill="rgba(163,158,147,.8)" letter-spacing="1">舞</text>
        </g>
        <g transform="rotate(120 260 190)">
          <path class="panel-p" d="M206 46 Q260 34 314 46 L292 122 L228 122 Z" fill="rgba(232,228,220,.09)" stroke="rgba(95,146,112,.55)" stroke-width="1.3"/>
          <circle cx="234" cy="60" r="2" fill="rgba(95,146,112,.8)"/>
          <circle cx="286" cy="60" r="2" fill="rgba(95,146,112,.8)"/>
          <path d="M238 82 q10 -14 26 -8 q-8 2 -11 9 q-9 1 -15 -1 z" fill="rgba(232,228,220,.72)"/>
          <text x="272" y="88" font-size="13" fill="rgba(163,158,147,.8)" letter-spacing="1">飞</text>
        </g>
        <g transform="rotate(180 260 190)">
          <path class="panel-p" d="M206 46 Q260 34 314 46 L292 122 L228 122 Z" fill="rgba(232,228,220,.09)" stroke="rgba(95,146,112,.55)" stroke-width="1.3"/>
          <circle cx="234" cy="60" r="2" fill="rgba(95,146,112,.8)"/>
          <circle cx="286" cy="60" r="2" fill="rgba(95,146,112,.8)"/>
          <g fill="rgba(232,228,220,.72)">
            <ellipse cx="248" cy="82" rx="13" ry="6.5"/>
            <path d="M258 78 l7 -8 4 2 -5 9 z"/>
            <path d="M238 87 l-3 9 4 0 3 -8 z M250 88 l-1 9 4 0 1 -9 z"/>
          </g>
          <text x="274" y="88" font-size="13" fill="rgba(163,158,147,.8)" letter-spacing="1">走</text>
        </g>
        <g transform="rotate(240 260 190)">
          <path class="panel-p" d="M206 46 Q260 34 314 46 L292 122 L228 122 Z" fill="rgba(232,228,220,.09)" stroke="rgba(95,146,112,.55)" stroke-width="1.3"/>
          <circle cx="234" cy="60" r="2" fill="rgba(95,146,112,.8)"/>
          <circle cx="286" cy="60" r="2" fill="rgba(95,146,112,.8)"/>
          <g fill="rgba(232,228,220,.72)">
            <circle cx="243" cy="72" r="6"/>
            <path d="M243 79 q-9 5 -11 19 l7 3 q3 -11 8 -13 z"/>
          </g>
          <text x="276" y="88" font-size="13" fill="rgba(163,158,147,.8)" letter-spacing="1">拜</text>
        </g>
        <g transform="rotate(300 260 190)">
          <path class="panel-p" d="M206 46 Q260 34 314 46 L292 122 L228 122 Z" fill="rgba(232,228,220,.09)" stroke="rgba(95,146,112,.55)" stroke-width="1.3"/>
          <circle cx="234" cy="60" r="2" fill="rgba(95,146,112,.8)"/>
          <circle cx="286" cy="60" r="2" fill="rgba(95,146,112,.8)"/>
          <g fill="rgba(232,228,220,.72)">
            <circle cx="252" cy="70" r="6"/>
            <path d="M252 77 q-14 2 -19 16 l6 4 q6 -10 13 -11 z"/>
            <path d="M252 77 q14 4 16 18 l-7 3 q-4 -10 -11 -13 z"/>
          </g>
          <text x="270" y="88" font-size="13" fill="rgba(163,158,147,.8)" letter-spacing="1">舞</text>
        </g>
        <circle cx="260" cy="190" r="7" fill="none" stroke="rgba(95,146,112,.8)" stroke-width="1.6"/>
        <circle cx="260" cy="190" r="2.4" fill="rgba(95,146,112,.9)"/>
      </g>
      <g class="flamein">
        <path d="M260 300 C246 282 251 262 260 244 C269 262 274 282 260 300 Z" fill="url(#gFl)"/>
        <path d="M260 296 C254 286 256 274 260 264 C264 274 266 286 260 296 Z" fill="rgba(250,236,198,.9)"/>
      </g>
      <rect x="250" y="302" width="20" height="26" rx="2" fill="#232620" stroke="rgba(201,150,63,.45)" stroke-width="1.2"/>
      <path d="M212 346 L308 346 L292 372 L228 372 Z" fill="#1d1f19" stroke="rgba(95,146,112,.5)" stroke-width="1.4"/>
      <path d="M244 372 L276 372 L272 402 L248 402 Z" fill="#1d1f19" stroke="rgba(95,146,112,.4)" stroke-width="1.2"/>
      <ellipse cx="260" cy="408" rx="74" ry="12" fill="#232620" stroke="rgba(95,146,112,.55)" stroke-width="1.4"/>
    </svg>
  </div>
  <div class="dial" role="group" aria-label="火候">
    <button type="button" data-k="hi">旺</button>
    <button type="button" data-k="lo" class="act" aria-pressed="true">微</button>
    <button type="button" data-k="off">熄</button>
  </div>
  <div class="dial-cap">拨一档火候,看轮转快慢</div>
  <p class="still-note">轮停了。灯影未散,壳还在。</p>
  <div class="hero-t">
    <h1>医　贯</h1>
    <div class="who">赵献可 撰</div>
    <p class="one">一部讲「人身之主不在心,在一团火」的医论。作者借一盏走马灯立说:灯里拜舞飞走的诸影,全靠中间一点火。本书导读把整部书做成这盏灯。</p>
  </div>
  <div class="scrolldn">向下看灯</div>
</header>

<main>
<section>
  <div class="wrap">
    <div class="shead"><span class="sno">屏一</span><h2>丹灯德,一贯之</h2><span class="en">书名从哪里来</span></div>
    <div class="prose">
      <p>作者署了一个奇怪的别号,把自己藏了起来。序是别人代写的,里面把书名的来历说得很坦白:修仙的人炼丹,参禅的人传灯,读书人明德,求的其实是同一样东西。医书讲的道理和它们一贯,所以叫「医贯」。</p>
      <span class="origin">库本卷首题:<qv>@@Q_XU@@</qv></span>
      <q class="q" data-who="库本卷首序">@@Q_XIAN@@</q>
      <p>真正有趣的是落款。他不用本名,自称「医巫闾子」。医巫闾是一座山的名字,在今天的辽宁北镇。</p>
      <q class="q" data-who="库本卷首序">@@Q_TAO@@</q>
      <p>把真名藏进别号,把写成的书藏进山里,等一个识货的人。这盏灯,他自己没有挂在闹市。</p>
    </div>
  </div>
</section>

<section class="alt">
  <div class="wrap">
    <div class="shead"><span class="sno">屏二</span><h2>十二官与一位不在场的君</h2><span class="en">满朝有官,君在何处</span></div>
    <div class="prose">
      <p>开卷第一论引《内经》把人身比作朝廷,五脏六腑各授官职,像一幅满朝文武的点卯图。点一点下面这些官,看各自的职守。</p>
      <q class="q" data-who="卷之一 · 内经十二官论">@@Q_GUAN@@</q>
      <div class="guan-grid" role="group" aria-label="十二官">
        <button type="button" class="guan" data-i="0"><span class="gn">心</span><span class="du">君主之官</span></button>
        <button type="button" class="guan" data-i="1"><span class="gn">肺</span><span class="du">相传之官</span></button>
        <button type="button" class="guan" data-i="2"><span class="gn">肝</span><span class="du">将军之官</span></button>
        <button type="button" class="guan" data-i="3"><span class="gn">胆</span><span class="du">中正之官</span></button>
        <button type="button" class="guan" data-i="4"><span class="gn">膻中</span><span class="du">臣使之官</span></button>
        <button type="button" class="guan" data-i="5"><span class="gn">脾胃</span><span class="du">仓廪之官</span></button>
        <button type="button" class="guan" data-i="6"><span class="gn">大肠</span><span class="du">传道之官</span></button>
        <button type="button" class="guan" data-i="7"><span class="gn">小肠</span><span class="du">受盛之官</span></button>
        <button type="button" class="guan" data-i="8"><span class="gn">肾</span><span class="du">作强之官</span></button>
        <button type="button" class="guan" data-i="9"><span class="gn">三焦</span><span class="du">决渎之官</span></button>
        <button type="button" class="guan" data-i="10"><span class="gn">膀胱</span><span class="du">州都之官</span></button>
        <button type="button" class="guan zhu" data-i="11"><span class="gn">主</span><span class="du">何在</span></button>
      </div>
      <div class="gp" aria-live="polite">
        <div class="gd act" data-g="welcome"><span class="gg">点卯已毕<small>还差一位</small></span><span class="qv">十一位官员都已到齐。经文说这是十二官,那么第十二位、真正的君主,在哪里?</span></div>
        <div class="gd" data-g="0"><span class="gg">心<small>君主之官</small></span><qv class="qv">@@Q_DUTY1@@</qv><span class="cap" style="display:block;margin-top:8px">历代注家都把心当作这位君主。赵献可说:且慢。</span></div>
        <div class="gd" data-g="1"><span class="gg">肺<small>相传之官</small></span><qv class="qv">@@Q_DUTY2@@</qv></div>
        <div class="gd" data-g="2"><span class="gg">肝<small>将军之官</small></span><qv class="qv">@@Q_DUTY3@@</qv></div>
        <div class="gd" data-g="3"><span class="gg">胆<small>中正之官</small></span><qv class="qv">@@Q_DUTY4@@</qv></div>
        <div class="gd" data-g="4"><span class="gg">膻中<small>臣使之官</small></span><qv class="qv">@@Q_DUTY5@@</qv></div>
        <div class="gd" data-g="5"><span class="gg">脾胃<small>仓廪之官</small></span><qv class="qv">@@Q_DUTY6@@</qv></div>
        <div class="gd" data-g="6"><span class="gg">大肠<small>传道之官</small></span><qv class="qv">@@Q_DUTY7@@</qv></div>
        <div class="gd" data-g="7"><span class="gg">小肠<small>受盛之官</small></span><qv class="qv">@@Q_DUTY8@@</qv></div>
        <div class="gd" data-g="8"><span class="gg">肾<small>作强之官</small></span><qv class="qv">@@Q_DUTY9@@</qv></div>
        <div class="gd" data-g="9"><span class="gg">三焦<small>决渎之官</small></span><qv class="qv">@@Q_DUTY10@@</qv></div>
        <div class="gd" data-g="10"><span class="gg">膀胱<small>州都之官</small></span><qv class="qv">@@Q_DUTY11@@</qv><span class="cap" style="display:block;margin-top:8px">此处库本另有<qv>气化则能出矣</qv>一句,见上引原文。</span></div>
        <div class="gd" data-g="11"><span class="gg">主<small>别有一物</small></span><q>@@Q_ZHU@@</q></div>
      </div>
      <p style="margin-top:26px">他的论证几乎是个逻辑玩笑:经文明明数出十二个官,又说这个主一旦不明,十二官都危险。如果心就是那个主,它自己也在十二官之数,经文就该说十一官危才对。多出来的那一位,才是真君。</p>
      <q class="q" data-who="卷之一 · 内经十二官论">@@Q_FEIXIN@@</q>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="shead"><span class="sno">屏三</span><h2>鳌山走马</h2><span class="en">全书的比喻核心</span></div>
    <div class="prose">
      <p>真君无形无相,怎么让人看见?他抬出了元宵节的走马灯。首屏那盏灯,拨到「熄」再看这一段,滋味最准。</p>
      <q class="q" data-who="卷之一 · 内经十二官论">@@Q_DENG@@</q>
      <p>灯是身体,火是那个主。火旺,影子转得快;火微,影子转得慢;火一熄,影子一个不少地留在原地。他把这层意思叮嘱得几乎苦口。</p>
      <q class="q" data-who="卷之一 · 内经十二官论">@@Q_ZHUN@@</q>
      <p>说到最沉处,他借了一句庄子:这具身子本来就不属于你,是天地临时借你的形。</p>
      <q class="q" data-who="卷之一 · 内经十二官论,语本庄子">@@Q_WEIXING@@</q>
    </div>
  </div>
</section>

<section class="alt">
  <div class="wrap">
    <div class="shead"><span class="sno">屏四</span><h2>水中之火</h2><span class="en">坎卦里的那一点阳</span></div>
    <div class="split">
      <svg viewBox="0 0 300 360" aria-label="坎卦示意">
        <g fill="none" stroke="rgba(163,158,147,.5)" stroke-width="1">
          <line x1="40" y1="20" x2="40" y2="340" stroke-dasharray="2 6"/>
          <line x1="260" y1="20" x2="260" y2="340" stroke-dasharray="2 6"/>
        </g>
        <g>
          <rect x="96" y="56" width="108" height="18" fill="rgba(232,228,220,.16)" stroke="rgba(232,228,220,.3)"/>
          <rect x="96" y="96" width="108" height="18" fill="#5f9270"/>
          <rect x="96" y="136" width="108" height="18" fill="rgba(232,228,220,.16)" stroke="rgba(232,228,220,.3)"/>
        </g>
        <text x="150" y="196" font-size="17" fill="rgba(232,228,220,.75)" text-anchor="middle" letter-spacing="6">坎</text>
        <circle cx="150" cy="248" r="26" fill="none" stroke="rgba(95,146,112,.7)" stroke-width="1.6" stroke-dasharray="4 5"/>
        <circle cx="150" cy="248" r="7" fill="#5f9270"/>
        <text x="150" y="306" font-size="15" fill="rgba(163,158,147,.85)" text-anchor="middle" letter-spacing="4">命门</text>
        <text x="150" y="336" font-size="12.5" fill="rgba(110,106,97,.9)" text-anchor="middle" letter-spacing="3">两水之间,一点真阳</text>
      </svg>
      <div class="prose">
        <p>这位真君住在哪里?他取了《易》的坎卦:两个阴爻中间夹一个阳爻,像两片水护着一点火。位置就在两肾之间。</p>
        <q class="q" data-who="卷之一 · 内经十二官论">@@Q_KAN@@</q>
        <q class="q" data-who="卷之一 · 内经十二官论">@@Q_KAN2@@</q>
        <p>所以这本书的全部治法,归结起来只有两句话:火显得太旺,别去打它,是水不够了,添水;火显得太弱,别去烤它,在水里添火。书末两卷各给了一粒代表丸药:滋水的六味丸,益火的八味丸。</p>
        <div class="pills">
          <div class="pill"><b>火旺者 · 添水配火</b><q>@@Q_SHUI1@@</q></div>
          <div class="pill"><b>火弱者 · 水中补火</b><q>@@Q_SHUI2@@</q></div>
        </div>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="shead"><span class="sno">屏五</span><h2>龙雷之火</h2><span class="en">一场越浇越旺的火</span></div>
    <div class="prose">
      <p>有人会问:既是火,水难道浇不灭?他把火分了类:炉灶里的火,一瓢水就灭;可雷雨天的霹雳火,偏偏雨越大烧得越旺。肾里的火就是后一种。点一场雨试试。</p>
      <div class="stage">
        <svg viewBox="0 0 520 300" aria-label="龙雷之火演示">
          <g fill="rgba(95,146,112,.30)">
            <path d="M96 66 q10 -26 40 -22 q10 -20 38 -14 q26 -12 44 8 q24 -2 26 20 q2 16 -16 18 l-116 0 q-18 -2 -16 -10 z"/>
          </g>
          <g stroke="#7fae8e" stroke-width="2" stroke-linecap="round">
            <line class="drop" x1="110" y1="84" x2="106" y2="98" style="animation-delay:0s"/>
            <line class="drop" x1="146" y1="88" x2="142" y2="102" style="animation-delay:.3s"/>
            <line class="drop" x1="182" y1="82" x2="178" y2="96" style="animation-delay:.6s"/>
            <line class="drop" x1="214" y1="90" x2="210" y2="104" style="animation-delay:.15s"/>
            <line class="drop" x1="128" y1="96" x2="124" y2="110" style="animation-delay:.45s"/>
            <line class="drop" x1="168" y1="98" x2="164" y2="112" style="animation-delay:.75s"/>
            <line class="drop" x1="200" y1="70" x2="196" y2="84" style="animation-delay:.9s"/>
            <line class="drop" x1="136" y1="70" x2="132" y2="84" style="animation-delay:.2s"/>
          </g>
          <ellipse id="g5" cx="392" cy="212" rx="120" ry="72" fill="url(#gGlow)" opacity=".62"/>
          <g class="f5">
            <path d="M392 232 C372 208 379 182 392 156 C405 182 412 208 392 232 Z" fill="url(#gFl)"/>
            <path d="M392 226 C384 212 386 196 392 182 C398 196 400 212 392 226 Z" fill="rgba(250,236,198,.9)"/>
          </g>
          <path d="M330 258 q16 -12 32 0 q16 12 32 0 q16 -12 32 0 q16 12 32 0" fill="none" stroke="rgba(95,146,112,.85)" stroke-width="2.4" class="trough"/>
          <text x="86" y="46" font-size="13" fill="rgba(163,158,147,.8)" letter-spacing="3">雨云</text>
          <text x="452" y="286" font-size="13" fill="rgba(163,158,147,.8)" letter-spacing="2">命门之火</text>
        </svg>
      </div>
      <div class="stg-btns">
        <button type="button" id="btnRain">降一场雨</button>
        <button type="button" id="btnGui">引火归原</button>
      </div>
      <p class="note5 n-rain">雨下大了,火反而更旺。浇,是浇不灭的。</p>
      <p class="note5 n-gui">火退回水里,安安稳稳地烧。他说这才是治法。</p>
      <q class="q" data-who="卷之四 · 相火龙雷论">@@Q_LONG1@@</q>
      <p>正治的法子,不是灭火,是把它送回家。</p>
      <q class="q" data-who="卷之四 · 相火龙雷论">@@Q_LONG2@@</q>
      <p>而他真正要怼的,是当时流行的另一派:一见「上火」,不问青红皂白,先开两味苦寒药。</p>
      <q class="q" data-who="卷之四 · 相火龙雷论">@@Q_LONG3@@</q>
    </div>
  </div>
</section>

<section class="alt">
  <div class="wrap">
    <div class="shead"><span class="sno">屏六</span><h2>百病从「不通」开始</h2><span class="en">郁病论摘影</span></div>
    <div class="prose">
      <p>卷二留了一篇专论:许多病,起点不是邪气,是「郁」,抑而不通。《内经》给五种郁各配了一个字的对治,他把这五个字排成一面小小的墙。</p>
      <q class="q" data-who="卷之二 · 郁病论">@@Q_YU1@@</q>
      <div class="wu">
        <div class="w"><b>达</b><span>木郁 · 疏它</span></div>
        <div class="w"><b>发</b><span>火郁 · 散它</span></div>
        <div class="w"><b>夺</b><span>土郁 · 通它</span></div>
        <div class="w"><b>泄</b><span>金郁 · 利它</span></div>
        <div class="w"><b>折</b><span>水郁 · 制它</span></div>
      </div>
      <p>他还引了同时代前面的金元大家朱丹溪作呼应:气血通畅,百病不生;一处怫郁,诸病就跟着来了。</p>
      <q class="q" data-who="卷之二 · 郁病论">@@Q_YU2@@</q>
    </div>
  </div>
</section>

<section class="outro">
  <div class="wrap">
    <p class="cap">全书的落脚处,其实只有一句</p>
    <p class="big"><qv>@@Q_MEN@@</qv>。而人这盏灯,要紧的是别让火灭。</p>
    <q class="q" style="display:inline-block;max-width:640px">@@Q_YANG@@</q>
    <p class="cap" style="max-width:560px;margin:30px auto 0">书成之后,他没有声张,把灯藏进了山里。三百年间,温补一派奉此书为门径;今天再看,它更像一封写给「功能比器官更要紧」这句话的旧信。</p>
    <div class="seal">医巫闾子</div>
  </div>
</section>
</main>

<footer>
  <div class="wrap">
    文本来源:殆知阁古代文献简体库(医藏,<qv>医贯</qv>),明赵献可撰,去空白约七万八千字,凡六卷:玄元肤论、主客辨疑、绛雪丹书、先天要论上下、后天要论。仓库:<a href="https://github.com/robertsong2000/daizhige-daodu" target="_blank" rel="noopener"><b>daizhige-daodu</b></a><br>
    本篇引文经脚本与库内文件去标点、归一后逐字比对通过;库本「的以」「相根据」等形依原文照录不归一,私用区缺字处引文一律避开。<br>
    时代局限提醒:本书以阴阳五行与命门相火立论,属前现代身体观;所载丸散汤方与治法为历史文献记录,不可替代现代诊疗,切勿仿用;对寒凉攻下诸派的门户之评,亦存当日之争,照录立此存照,不代今人立论。
  </div>
</footer>

<script>
(function(){
  var body = document.body;
  var dial = document.querySelectorAll('.dial button');
  dial.forEach(function(b){
    b.addEventListener('click', function(){
      dial.forEach(function(x){x.classList.remove('act');x.removeAttribute('aria-pressed');});
      b.classList.add('act'); b.setAttribute('aria-pressed','true');
      body.className = 'lamp-' + b.getAttribute('data-k');
    });
  });
  var cards = document.querySelectorAll('.guan');
  var gds = document.querySelectorAll('.gd');
  cards.forEach(function(c){
    c.addEventListener('click', function(){
      cards.forEach(function(x){x.classList.remove('act');});
      c.classList.add('act');
      gds.forEach(function(g){g.classList.remove('act');});
      var g = document.querySelector('.gd[data-g="' + c.getAttribute('data-i') + '"]');
      if (g) { g.classList.add('act'); }
    });
  });
  var bR = document.getElementById('btnRain'), bG = document.getElementById('btnGui');
  bR.addEventListener('click', function(){ body.classList.toggle('raining'); body.classList.remove('guiding'); });
  bG.addEventListener('click', function(){ body.classList.toggle('guiding'); body.classList.remove('raining'); });
})();
</script>
</body>
</html>
'''

html = TPL
for tok, sl in slices.items():
    html = html.replace('@@' + tok + '@@', sl)
left = re.findall(r'@@Q_[A-Z0-9]+@@', html)
if left:
    sys.exit('unreplaced tokens: %s' % left)

# self checks
if '—' in html or '–' in html:
    sys.exit('dash found')
for ln in html.split('\n'):
    if ln.count('·') > 1:
        sys.exit('multi · in line: ' + ln.strip()[:80])
open(OUT, 'w', encoding='utf-8').write(html)
print('written', OUT, len(html), 'bytes,', len(slices), 'slices')
