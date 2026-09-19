#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build shiyou-tanji.html: quotes sliced verbatim from 库本, zero retyping."""
import sys

SRC_PATH = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/师友谈记.txt'
OUT_PATH = '/home/robertsong/workspace/claude/daizhige-daodu/shiyou-tanji.html'
PIANO = '\U000230C1'  # 𣃁

lines = open(SRC_PATH, encoding='utf-8').read().split('\n')

# id: (line_no(1-based), start_anchor, end_anchor, end_inclusive)
QUOTES = {
 'zhizi':      (18, '知之者不如好之者', '不如乐之者', True),
 'fanchunfu':  (21, '范淳夫讲书', '无一冗字', True),
 'fengshan':   (21, '为人臣凡有劝人主', '佞臣也', True),
 'weiwang':    (42, '所谓讳恶者危亡之言', '不绝于耳', True),
 'xianshu':    (22, '献书公车者三', '闻罢', True),
 'ruzi':       (22, '如子之才', '时曳裾也', True),
 'wenming':    (22, '士人当使王公', '识面少', True),
 'ning':       (22, '寜使王公', '其不去', True),
 'peiwei':     (22, '廌以此言如佩韦', '如佩韦', False),
 'shenqi':     (3,  '知其交由神契', '势利相攀', True),
 'fuji':       (19, '伏其几而袭其裳', '岂为孔子', True),
 'maomao':     (19, '学其书而戴其帽', '未是蘓公', True),
 'youwenzhang':(19, '吾之文章', '不可及也', True),
 'zizhan':     (19, '汝不见吾头上', '子瞻乎', True),
 'weigui':     (20, '吾非畏鬼人', '也', True),
 'fudun':      (20, '祸福天也', '其如予何', True),
 'ganshang':   (20, '感尚书', '去也', True),
 'yuanshou':   (26, '凡小赋如人之元首', '乃其眉', True),
 'yijun':      (30, '当取一君二民', '之义', True),
 'jinqi':      (29, '与其无缝而陋', '有缝而佳', True),
 'lianju':     (31, '惟贵链句之功', '鬬新', True),
 'tianqu':     (35, '观少防之说', '填歌曲尔', True),
 'haowenzhang':(35, '作赋何用好文章', '偶俪而已', True),
 'gongqing':   (36, '一时公卿', '交口推服', True),
 'zhankai':    (38, '凡比常例展二十日', '盖始于此', True),
 'peiyang':    (39, '蘓轼之才', '培养之', True),
 'caogao':     (40, '凡三次起草', '涂注', True),
 'weigui2':    (56, '惟五更可以勾当', '自家事', True),
 'zijiashi':   (56, '所谓自家事', '将得去者', True),
 'jingren':    (56, '景仁虽不学佛', '逹佛理', True),
 'an4ti':      (57, '吾初睡时', '无一不稳', True),
 'jiehui':     (57, '天下之理能戒', '能慧', True),
 'ximian':     (44, '一日两洗面', '浴焉', True),
 'jianci':     (44, '一曰俭二曰慈', '二曰慈', True),
 'jingcu':     (49, '叶温叟将谓', '精确也', True),
 'cuzu':       (49, '觕音麄', '或作粗', True),
 'wushui':     (51, '城中无水', '吮睛饮血者', True),
 'bingsi':     (51, '当与兵死', '兵死', True),
 'baoping':    (53, '但怪土犯寳瓶', '瓶耳', True),
 'husun':      (54, '以孙莘老为大胡孙', '小胡孙学士', True),
 'shaoyao':    (59, '芍药善堕胎', '为之赠', True),
 'yangsheng':  (59, '知养生然后', '进学矣', True),
 'su':         (60, '惟粟性坚', '待匮尔', True),
 'yu':         (60, '即用大甑蒸之', '取食之', True),
 'huanglong':  (52, '梦一金色黄龙', '数畦', True),
 'su7':        (61, '明日蘓七君', '吾甚畏之', True),
 'diaoben':    (46, '初眉山集有雕本', '忘寐', True),
 'yuan':       (46, '縁吾读眉山集', '致之也', True),
 'zhongcheng': (65, '中丞职当肃政', '不闻', True),
 'tanhe':      (65, '恐累二圣', '弹劾以闻', True),
 'gaidai':     (65, '东坡不惟文章', '逺甚', True),
 'sanjun':     (66, '三君为主司', '兹可罚也', True),
 'wenqian':    (66, '先生昔知举', '之罚均也', True),
 'wenzhangren':(66, '文章之任', '其道不坠', True),
 'fushou':     (66, '异时文章盟主', '付授也', True),
 'liaoliao':   (3,  '寥寥数简之书', '岂偶然哉', True),
 'fan_poem':   (23, '穿云', '愿时供', True),
 'li_poem':    (23, '节藏泥滓', '诳蛟龙', True),
 'qin_poem':   (23, '楚山春笋', '鼎烹龙', True),
}

def extract(key):
    ln, start, end, incl = QUOTES[key]
    text = lines[ln - 1]
    i = text.find(start)
    assert i >= 0, f'{key}: start not found in line {ln}'
    assert text.find(start, i + 1) < 0, f'{key}: start anchor not unique in line {ln}'
    j = text.find(end, i)
    assert j >= 0, f'{key}: end not found in line {ln}'
    if not incl:
        seg = text[i:j]
    else:
        seg = text[i:j + len(end)]
    seg = seg.replace(PIANO, '□')
    assert '□' not in seg or key.endswith('_poem'), f'{key}: unexpected PUA square'
    return seg

Q = {k: extract(k) for k in QUOTES}

TPL = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>导读第__N__篇：苏门记言簿</title>
<style>
  :root{
    --ink:#191917; --ink2:#1f201e; --card:#232422; --card2:#2a2b27;
    --paper:#e8e4dc; --paper2:#dcd6c9; --dim:#a49f92; --faint:#7b766a;
    --acc:#5e8fbb; --acc2:#7fa8cd; --accdim:#3c5a77;
    --seal:#b3502f;
    --line:#37382f;
    --serif:"Songti SC","Noto Serif CJK SC","Source Han Serif SC","STSong",serif;
  }
  *{margin:0;padding:0;box-sizing:border-box}
  html{scroll-behavior:smooth}
  body{background:var(--ink);color:var(--paper);font-family:var(--serif);line-height:2;font-size:16px}
  q{quotes:none}
  .wrap{max-width:1020px;margin:0 auto;padding:0 22px}

  /* ---------- hero : 帽架 ---------- */
  .hero{min-height:96vh;position:relative;display:flex;align-items:center;overflow:hidden;
    background:radial-gradient(900px 460px at 24% 38%,rgba(94,143,187,.08),transparent 62%),
               radial-gradient(700px 420px at 82% 12%,rgba(232,228,220,.035),transparent 60%)}
  .hero .wrap{display:grid;grid-template-columns:1fr 1fr;gap:30px;align-items:center;width:100%}
  .kick{position:absolute;top:34px;left:0;right:0;text-align:center;font-size:13px;letter-spacing:.5em;color:var(--faint)}
  .stage{position:relative;height:480px}
  .stage svg{position:absolute;inset:0;width:100%;height:100%}
  .hatg{transform-origin:150px 172px;transition:transform .5s cubic-bezier(.3,1.6,.4,1)}
  .stage.on .hatg{animation:wear .9s cubic-bezier(.3,1.5,.4,1) both}
  @keyframes wear{0%{transform:translate(0,0) rotate(0)}35%{transform:translate(0,-34px) rotate(-7deg)}
    70%{transform:translate(0,-6px) rotate(4deg)}100%{transform:translate(0,0) rotate(0)}}
  .hint{position:absolute;left:50%;bottom:8px;transform:translateX(-50%);font-size:13px;color:var(--faint);
    letter-spacing:.3em;transition:opacity .6s}
  .stage.on .hint{opacity:0}
  .titlebox{position:relative;height:480px;display:flex;justify-content:center}
  .vtitle{writing-mode:vertical-rl;display:flex;flex-direction:column;align-items:center;justify-content:flex-start;
    height:100%;opacity:0;transform:translateY(26px);transition:opacity 1.1s ease .15s,transform 1.1s ease .15s}
  .stage.on ~ .titlebox .vtitle,.on .titlebox .vtitle{opacity:1;transform:translateY(0)}
  .vtitle h1{font-size:62px;font-weight:600;letter-spacing:.22em;white-space:nowrap;
    height:max-content;text-shadow:0 0 26px rgba(94,143,187,.25)}
  .vsub1{margin-top:26px;writing-mode:vertical-rl;font-size:15px;color:var(--dim);letter-spacing:.32em;white-space:nowrap}
  .vseal{writing-mode:vertical-rl;margin-top:30px;font-size:15px;color:var(--seal);border:2px solid var(--seal);
    border-radius:5px;padding:9px 5px;letter-spacing:.28em;white-space:nowrap;opacity:0;transform:scale(1.5);
    transition:opacity .45s ease .9s,transform .45s ease .9s;background:rgba(179,80,47,.08)}
  .on .vseal{opacity:1;transform:scale(1)}
  .floater{position:absolute;right:6%;top:12%;writing-mode:vertical-rl;font-size:14px;color:var(--accdim);
    letter-spacing:.5em;white-space:nowrap}

  /* ---------- 簿头 ---------- */
  .btt{padding:70px 0 30px}
  .btt p{max-width:760px;color:var(--dim);font-size:16.5px}
  .btt b{color:var(--paper);font-weight:600}

  /* ---------- 席次 ---------- */
  .xiect{display:flex;flex-wrap:wrap;gap:10px;padding:8px 0 60px}
  .xie{border:1px solid var(--line);border-radius:3px;padding:7px 13px;font-size:14px;color:var(--dim);
    background:var(--ink2)}
  .xie b{color:var(--acc2);font-weight:600;margin-right:7px}
  .xie.lead{border-color:var(--accdim);color:var(--paper)}

  /* ---------- 帙 ---------- */
  .zhi{padding:44px 0 18px;border-top:1px solid var(--line)}
  .zhihead{display:flex;align-items:baseline;gap:16px;margin-bottom:8px}
  .zhihead .no{font-size:13px;color:var(--acc);letter-spacing:.3em}
  .zhihead h2{font-size:26px;font-weight:600;letter-spacing:.14em;color:var(--paper)}
  .zhihead .cnt{font-size:13px;color:var(--faint)}
  .zhinote{color:var(--faint);font-size:14.5px;max-width:760px;margin-bottom:24px}

  .cards{display:grid;grid-template-columns:1fr 1fr;gap:16px}
  .tan{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--accdim);
    border-radius:4px;padding:20px 22px 16px}
  .tan .who{display:inline-block;font-size:12.5px;color:var(--acc2);border:1px solid var(--accdim);
    border-radius:2px;padding:2px 9px;letter-spacing:.18em;margin-bottom:10px}
  .tan h3{font-size:17.5px;font-weight:600;letter-spacing:.1em;margin-bottom:10px;color:var(--paper)}
  .tan blockquote{background:var(--ink2);border-radius:3px;padding:12px 14px;margin-bottom:11px}
  .tan blockquote q{display:block;font-size:15.5px;color:var(--acc2);line-height:2}
  .tan blockquote q + q{margin-top:6px}
  .tan .my{font-size:14.5px;color:var(--dim);line-height:1.95}
  .tan.wide{grid-column:1 / -1}
  .tan.dark{border-left-color:var(--seal);background:#25211e}
  .tan.dark blockquote q{color:#d8a58c}
  .tan.dark .who{color:#d8a58c;border-color:#6b4234}

  /* ---------- 定州一盏 ---------- */
  .zhan{background:linear-gradient(180deg,#1d1e1c,#191917);border-top:1px solid var(--line);
    border-bottom:1px solid var(--line);padding:64px 0 58px;margin:34px 0}
  .zhan h2{font-size:27px;letter-spacing:.16em;text-align:center;color:var(--paper);font-weight:600}
  .zhan .lead{max-width:720px;margin:14px auto 34px;text-align:center;color:var(--dim);font-size:15.5px}
  .cuprow{display:flex;justify-content:center;gap:26px;flex-wrap:wrap;margin-bottom:26px}
  .cup{width:150px;cursor:pointer;user-select:none}
  .cup svg{display:block;width:100%;height:auto}
  .cup .liq{transform-box:fill-box;transform-origin:50% 100%;transform:scaleY(0);opacity:0;
    transition:transform .9s cubic-bezier(.2,.8,.3,1),opacity .5s}
  .cup.hit .liq{transform:scaleY(1);opacity:.92}
  .cup .tag{font-size:13.5px;color:var(--faint);text-align:center;letter-spacing:.12em;min-height:2.6em;line-height:1.7}
  .cup.hit .tag{color:var(--paper)}
  .fushou{max-width:720px;margin:0 auto;background:var(--paper);color:var(--ink);border-radius:4px;
    padding:26px 30px;position:relative;opacity:0;transform:translateY(14px);transition:opacity .8s,transform .8s;
    display:none}
  .fushou.show{display:block;opacity:1;transform:translateY(0)}
  .fushou .fx{font-size:12.5px;letter-spacing:.3em;color:var(--accdim);margin-bottom:8px}
  .fushou q{display:block;font-size:16.5px;line-height:2.1;color:#26241f}
  .fushou q + q{margin-top:8px}
  .fushou .my{margin-top:12px;font-size:14.5px;color:#5a564c;line-height:1.95}
  .fushou .seal2{position:absolute;right:18px;bottom:16px;color:var(--seal);border:2px solid var(--seal);
    border-radius:4px;padding:6px 8px;font-size:14px;letter-spacing:.2em;transform:rotate(6deg)}

  /* ---------- 诗笺 ---------- */
  .jianrow{display:flex;justify-content:center;gap:22px;flex-wrap:wrap;padding:6px 0 50px}
  .jian{width:172px;height:270px;background:var(--paper);color:var(--ink);border-radius:3px;cursor:pointer;
    overflow:hidden;position:relative;transition:height .7s ease;box-shadow:0 6px 24px rgba(0,0,0,.45)}
  .jian.open{height:560px}
  .jian .bar{position:absolute;top:0;left:0;right:0;height:30px;background:var(--accdim);
    color:#dfe7ee;font-size:12.5px;letter-spacing:.24em;display:flex;align-items:center;justify-content:center}
  .jian .jv{writing-mode:vertical-rl;padding:46px 12px 14px;height:100%}
  .jian .jv q{display:block;height:100%;font-size:15px;letter-spacing:.2em;color:#26241f;line-height:2.1}
  .jian .tip{position:absolute;bottom:8px;left:0;right:0;text-align:center;font-size:12px;color:#8b867a}
  .jian.open .tip{display:none}
  .jiannote{max-width:720px;margin:0 auto 20px;color:var(--faint);font-size:14px;text-align:center}

  /* ---------- 睡三昧 ---------- */
  .shui{display:grid;grid-template-columns:1fr 1fr;gap:16px;padding-bottom:20px}
  .steps{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}
  .steps button{background:var(--ink2);border:1px solid var(--accdim);color:var(--acc2);font-family:var(--serif);
    font-size:14px;padding:6px 14px;border-radius:2px;cursor:pointer;letter-spacing:.12em}
  .steps button.cur{background:var(--accdim);color:var(--paper)}
  .steptext p{display:none;font-size:14.5px;color:var(--dim)}
  .steptext p.cur{display:block}

  /* ---------- 尾屏 ---------- */
  .coda{margin-top:56px;border-top:1px solid var(--line);padding:64px 0 30px;
    background:linear-gradient(180deg,transparent,rgba(94,143,187,.05))}
  .coda .cwrap{display:flex;justify-content:center;align-items:flex-start;gap:44px;min-height:420px}
  .cv{writing-mode:vertical-rl;height:420px}
  .cv q{display:block;font-size:21px;letter-spacing:.34em;color:var(--acc2);white-space:nowrap;height:max-content}
  .coda .cmy{max-width:300px;color:var(--dim);font-size:14.5px;padding-top:12px}
  .coda .cseal{writing-mode:vertical-rl;font-size:16px;color:var(--seal);border:2px solid var(--seal);border-radius:5px;
    padding:10px 6px;letter-spacing:.26em;white-space:nowrap;align-self:flex-start;margin-top:6px}

  /* ---------- footer ---------- */
  footer{border-top:1px solid var(--line);margin-top:60px;padding:36px 0 60px;font-size:13.5px;color:var(--faint)}
  .ftgrid{display:grid;grid-template-columns:1fr 1fr;gap:10px 34px}
  .ftgrid b{color:var(--dim);font-weight:600}
  footer q{color:var(--dim)}

  @media (max-width:760px){
    .hero .wrap{grid-template-columns:1fr;gap:0}
    .stage{height:400px}
    .titlebox{height:420px}
    .vtitle h1{font-size:46px}
    .cards,.shui{grid-template-columns:1fr}
    .ftgrid{grid-template-columns:1fr}
    .coda .cwrap{flex-wrap:wrap;min-height:0}
    .cv{height:340px}
    .jian.open{height:500px}
    .floater{display:none}
  }
</style>
</head>
<body>

<header class="hero" id="hero">
  <div class="kick">殆知阁古代文献导读 · 第__N__篇</div>
  <div class="wrap">
    <div class="stage" id="stage">
      <svg viewBox="0 0 300 480" aria-hidden="true">
        <ellipse cx="150" cy="428" rx="92" ry="16" fill="#23241f" stroke="#37382f"/>
        <rect x="145" y="168" width="10" height="262" fill="#2e2f29"/>
        <rect x="145" y="168" width="4" height="262" fill="#3c3d35"/>
        <circle cx="150" cy="166" r="9" fill="#23241f" stroke="#4a4b41"/>
        <g class="hatg">
          <path d="M108 76 Q150 58 192 76 L186 160 Q150 172 114 160 Z" fill="#3f5470"/>
          <path d="M112 82 Q126 66 146 62 L143 158 L122 156 Z" fill="#5d7c9e" opacity=".3"/>
          <path d="M114 148 Q150 160 186 148 L186 160 Q150 172 114 160 Z" fill="#22303f"/>
          <path d="M114 156 Q150 168 186 156" fill="none" stroke="#5e8fbb" stroke-width="2" opacity=".5"/>
          <ellipse cx="150" cy="172" rx="102" ry="12" fill="#2e3d52"/>
          <ellipse cx="150" cy="169" rx="102" ry="12" fill="#436082"/>
          <ellipse cx="150" cy="168" rx="88" ry="8" fill="#2e3d52" opacity=".7"/>
        </g>
      </svg>
      <div class="hint">点一下这顶帽子</div>
    </div>
    <div class="titlebox" id="titlebox">
      <div class="vtitle">
        <h1>师友谈记</h1>
        <div class="vsub1">元祐间一册随闻随记的言谈簿</div>
        <div class="vseal">记言</div>
      </div>
      <div class="floater">北宋元祐 · 汴京</div>
    </div>
  </div>
</header>

<main class="wrap">

  <section class="btt">
    <p>这是一本<b>记话的簿子</b>。元祐年间，落第书生李廌跟在一群第一流人物身边，把席上听来的话一条条录下：先生是苏轼，座中还有范祖禹、秦观、晁补之、张耒。谈吐固然满纸珠玉，但真正让这册小书不朽的，是执笔人的身份：一个终生没有考中进士的学生，替当年那场把他弄丢的考试，悄悄留下了一桩悬案。</p>
  </section>

  <section>
    <div class="zhihead"><span class="no">簿前</span><h2>席上次第</h2><span class="cnt">簿中常客</span></div>
    <div class="xiect">
      <span class="xie lead"><b>东坡先生</b>谈主 · 大半簿归他</span>
      <span class="xie"><b>太史公</b>范祖禹 · 经筵讲官</span>
      <span class="xie"><b>秦少游</b>论赋十则</span>
      <span class="xie"><b>晁无咎</b>馆职闲谈</span>
      <span class="xie"><b>张文潜</b>末席翻案人</span>
      <span class="xie"><b>苏仲豫</b>长公迨</span>
      <span class="xie"><b>苏叔党</b>少公过</span>
      <span class="xie"><b>刘贡父</b>谐谑之祖</span>
      <span class="xie lead"><b>李方叔</b>执笔人自己</span>
    </div>
  </section>

  <section class="zhi">
    <div class="zhihead"><span class="no">第一帙</span><h2>讲筵</h2><span class="cnt">四则</span></div>
    <div class="zhinote">经筵是为皇帝开的课堂，李廌把讲官们的课堂艺术记成了档案。</div>
    <div class="cards">
      <article class="tan">
        <span class="who">东坡先生</span>
        <h3>人君之学</h3>
        <blockquote><q>{R:zhizi}</q></blockquote>
        <p class="my">东坡当值经筵回来，转述他劝小皇帝的话：君王读书不为科名，要紧的是从「知道」走到「爱好」，再走到「乐在其中」。全簿第一则，像是给整本书定的调子：读书先得有趣，别的才谈得上。</p>
      </article>
      <article class="tan">
        <span class="who">李廌记范祖禹</span>
        <h3>讲书三昧</h3>
        <blockquote><q>{R:fanchunfu}</q></blockquote>
        <p class="my">他把师范祖禹夸到顶：没有一个废字，义理明白又有文采。范家当晚备讲，要正衣冠、命子弟陪坐预演。这份郑重李廌旁观多年，直到元祐八年二月才获准旁听一次，听到的正是把封禅讲成佞臣考语的那一课。</p>
      </article>
      <article class="tan">
        <span class="who">太史公</span>
        <h3>封禅考语</h3>
        <blockquote><q>{R:fengshan}</q></blockquote>
        <p class="my">讲《礼记》巡狩之礼，讲到汉儒附会的封禅故事，范祖禹当场定性：劝皇帝封禅的，就是佞臣。李廌在后面盖了四个字的私章：此言可为守成的镜子。</p>
      </article>
      <article class="tan">
        <span class="who">太史公</span>
        <h3>讳恶新解</h3>
        <blockquote><q>{R:weiwang}</q></blockquote>
        <p class="my">旧注把「讳恶」讲成避开桀纣亡国之日之类的忌辰。范祖禹嫌这格局太小：真正的忌讳，是该让危险的话在御座边上常备不懈。把一条礼制讲成谏诤的武器，这是讲官的本事。</p>
      </article>
    </div>
  </section>

  <section class="zhi">
    <div class="zhihead"><span class="no">第二帙</span><h2>教我</h2><span class="cnt">四则</span></div>
    <div class="zhinote">簿子里少有的第一人称。李廌写别人多，写自己的这几条，全是他一辈子随身带着的教训。</div>
    <div class="cards">
      <article class="tan wide">
        <span class="who">李廌自述</span>
        <h3>三次碰壁</h3>
        <blockquote><q>{R:xianshu}</q></blockquote>
        <p class="my">年轻时的李廌求进心切：三次向朝廷上书，三次都因言触怒被压下；转而去投谒名公的门路，依然场屋失意。下一则，就是先生开的药方。</p>
      </article>
      <article class="tan">
        <span class="who">东坡先生</span>
        <h3>循分之诲</h3>
        <blockquote><q>{R:ruzi}</q></blockquote>
        <p class="my">凭你的才气不会被埋没，但要守本分、戒躁进，不必总在王公门前曳着衣摆徘徊。李廌记下这一课后，八年没有再登贵人之门；有人主动示好，他也守着这匹夫之志不肯变。</p>
      </article>
      <article class="tan">
        <span class="who">李文正遗言</span>
        <h3>佩韦之戒</h3>
        <blockquote><q>{R:wenming}</q><q>{R:ning}</q><q>{R:peiwei}</q></blockquote>
        <p class="my">让王公听惯你的名声、少见你的人面；宁可他们怪你怎么还不来，不可让他们怪你怎么还不走。性子急的人腰上佩一块柔韧的韦皮提醒自己，李廌说，这句话就是他的韦。</p>
      </article>
      <article class="tan">
        <span class="who">四库馆臣</span>
        <h3>神契之交</h3>
        <blockquote><q>{R:shenqi}</q></blockquote>
        <p class="my">提要替这层师生关系下了判词：等元祐诸人贬的贬、散的散，李廌还记着这些话，可见交情凭的是投契，不是势利。这话也提前替读者回答了一个疑问：一个落第生，凭什么坐在这张席上。</p>
      </article>
    </div>
  </section>

  <section class="zhi">
    <div class="zhihead"><span class="no">第三帙</span><h2>场屋</h2><span class="cnt">四则</span></div>
    <div class="zhinote">簿子里存着一叠科举旧档：这一家的名字是怎么被认出来的，又被怎么弄丢的。</div>
    <div class="cards">
      <article class="tan">
        <span class="who">东坡先生</span>
        <h3>欧公一荐</h3>
        <blockquote><q>{R:gongqing}</q></blockquote>
        <p class="my">东坡的声名起步，一半靠欧阳修那道荐章：表章才递上去，公卿们争相求见，一日之内名动京师。李廌记这一条，像在记一个「被认出」的时刻，那种幸运他后来一辈子没轮到第二次。</p>
      </article>
      <article class="tan">
        <span class="who">东坡先生</span>
        <h3>展限二十日</h3>
        <blockquote><q>{R:zhankai}</q></blockquote>
        <p class="my">嘉祐年间兄弟同赴制举，临试苏辙病倒。韩魏公奏请改期：这样的兄弟少考一人，非国家之福。于是比常例放宽二十日，此后科目试定在九月，成了制度。魏公还派人数着日子问病，等痊愈才开考。</p>
      </article>
      <article class="tan">
        <span class="who">东坡先生</span>
        <h3>培养之策</h3>
        <blockquote><q>{R:peiyang}</q></blockquote>
        <p class="my">制举中程，英宗想立刻授他知制诰，魏公拦住：此才当为天下所用，但要朝廷先养他，让天下士人畏慕仰望，再取而用之，人人无话；骤用反而累了他。后来有人挑拨，东坡答：这正是古人爱人以德的样子。</p>
      </article>
      <article class="tan">
        <span class="who">王丰甫言</span>
        <h3>三次起草</h3>
        <blockquote><q>{R:caogao}</q></blockquote>
        <p class="my">那篇论刑赏的名文，原来打了三遍草稿，连草稿上都留着涂改墨迹。这卷真迹后来被一个靠吐纳方药过活的道人偷走，东坡贬官途中认出了他，失物至今在京城。所谓行云流水，底子是这份涂抹的谨慎。</p>
      </article>
    </div>
  </section>

  <section class="zhan" id="zhan">
    <h2>定州一盏</h2>
    <p class="lead">元祐八年，苏轼出知定州，馆职同僚在惠济为他饯行。酒至半酣，他忽然举杯罚酒。罚的不是旁人，是当年主持省试的三位考官。先生替落第的学生讨了半生的公道。四只杯子，按席上的次序点。</p>
    <div class="cuprow" id="cuprow">
      <div class="cup" data-i="0">
        <svg viewBox="0 0 120 96">
          <path d="M14 18 L106 18 Q104 62 60 66 Q16 62 14 18 Z" fill="#2c2c27" stroke="#4a4b41"/>
          <path class="liq" d="M26 34 L94 34 Q92 56 60 60 Q28 56 26 34 Z" fill="#8a5a2b"/>
          <path d="M14 18 L106 18" stroke="#5e5a4e" stroke-width="2" opacity=".6"/>
          <path d="M30 88 L90 88" stroke="#4a4b41" stroke-width="4"/>
        </svg>
        <div class="tag">欧阳叔弼<br>馆阁校理</div>
      </div>
      <div class="cup" data-i="1">
        <svg viewBox="0 0 120 96">
          <path d="M14 18 L106 18 Q104 62 60 66 Q16 62 14 18 Z" fill="#2c2c27" stroke="#4a4b41"/>
          <path class="liq" d="M26 34 L94 34 Q92 56 60 60 Q28 56 26 34 Z" fill="#8a5a2b"/>
          <path d="M14 18 L106 18" stroke="#5e5a4e" stroke-width="2" opacity=".6"/>
          <path d="M30 88 L90 88" stroke="#4a4b41" stroke-width="4"/>
        </svg>
        <div class="tag">刘伯修<br>馆阁校理</div>
      </div>
      <div class="cup" data-i="2">
        <svg viewBox="0 0 120 96">
          <path d="M14 18 L106 18 Q104 62 60 66 Q16 62 14 18 Z" fill="#2c2c27" stroke="#4a4b41"/>
          <path class="liq" d="M26 34 L94 34 Q92 56 60 60 Q28 56 26 34 Z" fill="#8a5a2b"/>
          <path d="M14 18 L106 18" stroke="#5e5a4e" stroke-width="2" opacity=".6"/>
          <path d="M30 88 L90 88" stroke="#4a4b41" stroke-width="4"/>
        </svg>
        <div class="tag">常希古<br>司业少尹</div>
      </div>
      <div class="cup" data-i="3">
        <svg viewBox="0 0 120 96">
          <path d="M14 18 L106 18 Q104 62 60 66 Q16 62 14 18 Z" fill="#3a2f27" stroke="#6b4234"/>
          <path class="liq" d="M26 34 L94 34 Q92 56 60 60 Q28 56 26 34 Z" fill="#b3502f"/>
          <path d="M14 18 L106 18" stroke="#8a6a56" stroke-width="2" opacity=".6"/>
          <path d="M30 88 L90 88" stroke="#6b4234" stroke-width="4"/>
        </svg>
        <div class="tag">第四盏<br>张文潜举杯</div>
      </div>
    </div>
    <div class="fushou" id="fushou">
      <div class="fx">席上实录</div>
      <q>{R:sanjun}</q>
      <q>{R:wenqian}</q>
      <p class="my">罚完三位主考，末席的张耒当场把杯子举到老师面前：您当年知贡举，也一样把他漏了，罚得，这杯您也躲不掉。满座大笑。笑过之后，东坡说出真正的托付：文章这道统，要有人轮番主盟才不断绝；当年欧公把它交给自己，如今自己交出去。</p>
      <q>{R:wenzhangren}</q>
      <q>{R:fushou}</q>
      <div class="seal2">付授</div>
    </div>
  </section>

  <section class="zhi">
    <div class="zhihead"><span class="no">第四帙</span><h2>赋法</h2><span class="cnt">五则</span></div>
    <div class="zhinote">秦观是当行本色的词人，谈起作赋也像谈倚声填词。师生两人最后合力把这门功课说破了。</div>
    <div class="cards">
      <article class="tan">
        <span class="who">秦少游</span>
        <h3>眉目之喻</h3>
        <blockquote><q>{R:yuanshou}</q></blockquote>
        <p class="my">小赋好比人的脑袋，破题两句是眉毛，贵在有神采：第一眼就要动人，所以最精最切的材料要放在开头。</p>
      </article>
      <article class="tan">
        <span class="who">秦少游</span>
        <h3>一君二民</h3>
        <blockquote><q>{R:yijun}</q></blockquote>
        <p class="my">六字句里最吃紧的两个字当主，其余四个字当客；客要顺从、要成全主，句子才立得住。一句之内也有君民之分，乱了就散架。</p>
      </article>
      <article class="tan">
        <span class="who">秦少游</span>
        <h3>金器之喻</h3>
        <blockquote><q>{R:jinqi}</q></blockquote>
        <p class="my">用典像打金器：浑然无缝却粗陋，不如留缝而精工。比的是手艺高低，不是针脚密不密。</p>
      </article>
      <article class="tan">
        <span class="who">秦少游</span>
        <h3>鬬难鬬巧</h3>
        <blockquote><q>{R:lianju}</q></blockquote>
        <p class="my">赋是手艺活，专门跟难、巧、新较劲。同一件事别人那样写，你偏要写得与众相同处人各不同，才算工。</p>
      </article>
      <article class="tan wide">
        <span class="who">师生对谈</span>
        <h3>填歌曲</h3>
        <blockquote><q>{R:tianqu}</q><q>{R:haowenzhang}</q></blockquote>
        <p class="my">听完全套心法，李廌回敬一句：照这么说，作赋不就是填词么。秦观认账：曲子再好，不合律就不成声；好文章若只靠小巧拼对偶，那算不得文章。只是朝廷拿这格取士，士人拿它没办法罢了。四库馆臣赞这段「不阿所好」，师生俩亲手把看家本领拆穿了。</p>
      </article>
    </div>
  </section>

  <section class="zhi">
    <div class="zhihead"><span class="no">第五帙</span><h2>谑席</h2><span class="cnt">六则</span></div>
    <div class="zhinote">正经人物的玩笑话。元祐诸贤在簿子里最放松的样子，都在这一帙。</div>
    <div class="cards">
      <article class="tan wide">
        <span class="who">东坡先生</span>
        <h3>头上的招牌</h3>
        <blockquote><q>{R:fuji}</q><q>{R:maomao}</q><q>{R:youwenzhang}</q><q>{R:zizhan}</q></blockquote>
        <p class="my">门人作赋打趣：伏几袭裳的未必是孔子，读书戴帽的也不就等于苏公。那时满朝士人流行戴他那种高桶短檐的帽。东坡听了不恼，反讲御前的笑话：有优人自夸文章天下第一，众人问凭什么，答曰没见我头上顶着的字样么。老师拿自己的招牌供人取乐，笑完很久才收回表情。</p>
      </article>
      <article class="tan">
        <span class="who">刘贡父</span>
        <h3>大小胡孙</h3>
        <blockquote><q>{R:husun}</q></blockquote>
        <p class="my">馆里两位孙学士，差役送墨送错了门；有人说按胡子分，可两位都满腮胡；最后只好按身量定绰号：大胡孙、小胡孙。庙堂名宿，在笔记里全成了山里的猴。</p>
      </article>
      <article class="tan">
        <span class="who">苏仲豫记</span>
        <h3>精觕之对</h3>
        <blockquote><q>{R:jingcu}</q><q>{R:cuzu}</q></blockquote>
        <p class="my">提举保甲的官员奏报训练成效，想问各州精粗如何，落笔却把那个粗字当成了考核结论。神宗笑倒，说他还当这字是精确的意思。后一行小字，是库本在字旁留的原注。</p>
      </article>
      <article class="tan">
        <span class="who">苏尚书述</span>
        <h3>土犯宝瓶</h3>
        <blockquote><q>{R:baoping}</q></blockquote>
        <p class="my">石中立新赐银带，骑马摔下来磕伤了带子，众人问星象，他答：我推步不行，只怪土星犯了宝瓶。满朝传为笑谈，连最严肃的礼学家听了也笑。</p>
      </article>
      <article class="tan">
        <span class="who">苏叔党记</span>
        <h3>大洗面</h3>
        <blockquote><q>{R:ximian}</q><q>{R:jianci}</q></blockquote>
        <p class="my">蒲传正家的洗澡分六等：小洗面两人伺候只洗脸，大洗面换三道水洗到肩颈，大澡浴要用五斛热水、八九个人。东坡回他一封信，只劝两个字：俭，慈。</p>
      </article>
      <article class="tan">
        <span class="who">家传</span>
        <h3>茅将军怕苏七君</h3>
        <blockquote><q>{R:su7}</q></blockquote>
        <p class="my">眉州的妖神庙香火极盛，东坡祖父乘醉带二十个村仆砸了神像，庙也拆了，竟毫无灵验。三年后他路遇另一座茅将军庙正要再砸，庙吏连夜得梦：神哭着求饶，说这位苏七君明日要来。众人苦劝，老人这才收手。</p>
      </article>
    </div>
  </section>

  <section class="zhi">
    <div class="zhihead"><span class="no">插曲</span><h2>猫笋三笺</h2><span class="cnt">一场口福的诗案</span></div>
    <div class="zhinote">朋友送来长沙猫笋，李廌拿去孝敬老师；范祖禹回诗相赠，师生与秦观各和一首。点笺读全。</div>
    <div class="jianrow">
      <div class="jian" >
        <div class="bar">太史公 赠</div>
        <div class="jv"><q>{R:fan_poem}</q></div>
        <div class="tip">点开展全</div>
      </div>
      <div class="jian">
        <div class="bar">李廌 和</div>
        <div class="jv"><q>{R:li_poem}</q></div>
        <div class="tip">点开展全</div>
      </div>
      <div class="jian">
        <div class="bar">秦观 和</div>
        <div class="jv"><q>{R:qin_poem}</q></div>
        <div class="tip">点开展全</div>
      </div>
    </div>
    <p class="jiannote">笺上一处空框，是库本原字刻落的缺口，各以方框存照。</p>
  </section>

  <section class="zhi">
    <div class="zhihead"><span class="no">第六帙</span><h2>师法</h2><span class="cnt">两则</span></div>
    <div class="zhinote">两条教育档案：一位老师用一部医书救了一个人，一册讲章毒死了两句诗。</div>
    <div class="cards">
      <article class="tan">
        <span class="who">客话转述</span>
        <h3>一部医书戒浪子</h3>
        <blockquote><q>{R:yangsheng}</q></blockquote>
        <p class="my">番禺富商送子入胡瑗门下，少年挥霍千金还生了病。父亲赶京不骂一句，只领他去见先生。胡瑗取一部黄帝素问递过去：先学会保命，再谈进学。少年读得心惊肉跳，痛悔自新；先生这才换圣贤书教他，三年登第。所谓因材施教，有时是一副猛药。</p>
      </article>
      <article class="tan">
        <span class="who">张文潜</span>
        <h3>芍药拆穿记</h3>
        <blockquote><q>{R:shaoyao}</q></blockquote>
        <p class="my">新学讲《诗经》溱洧一篇，把男女赠芍药讲成了落胎的方子。张耒当场发问：诗里连谁赠谁都没说清，就算女子所赠，与那花的功能何干？刘贡父补刀，满座大笑。张耒的结语很重：这类穿凿泛滥，正是经义取士带来的祸根。</p>
      </article>
    </div>
  </section>

  <section class="zhi">
    <div class="zhihead"><span class="no">第七帙</span><h2>起居</h2><span class="cnt">两则</span></div>
    <div class="zhinote">两位老人的日常：一个教你怎么睡，一个教你临走前该办什么事。</div>
    <div class="shui">
      <article class="tan">
        <span class="who">东坡先生</span>
        <h3>寝寐三昧</h3>
        <blockquote><q>{R:an4ti}</q><q>{R:jiehui}</q></blockquote>
        <div class="steps">
          <button data-s="0">安四体</button><button data-s="1">按摩</button><button data-s="2">听息</button><button data-s="3">五更起</button>
        </div>
        <div class="steptext">
          <p class="cur">上床先把四肢摆到没有一处不稳，有一处不妥都要重摆。</p>
          <p>有倦痛的地方轻轻按摩过，再闭眼。</p>
          <p>听呼吸调匀，此后四肢哪怕发痒也定心不动，以定胜动。</p>
          <p>五更即起，梳洗后照此法小睡片刻：通宵之味，无可比拟。</p>
        </div>
        <p class="my">他叮嘱李廌和李祉：此法可试，别传出去让人知道。收尾那句，把睡觉讲成了戒定慧的功夫。</p>
      </article>
      <article class="tan">
        <span class="who">东坡先生述</span>
        <h3>五更办自家事</h3>
        <blockquote><q>{R:weigui2}</q><q>{R:zijiashi}</q><q>{R:jingren}</q></blockquote>
        <p class="my">一位不曾参禅却深通禅理的老翁，临终置酒对儿孙说：只有五更天办得了自家事。儿孙不解：家中哪件事不是自家事？老人答：我说的自家事，是咽气时带得走的事。东坡托人把这段话捎给退休后纵情声乐的老上司。又记范镇：平生不好佛，临终也不取佛法，可东坡说他其实比谁都通达。</p>
      </article>
    </div>
  </section>

  <section class="zhi">
    <div class="zhihead"><span class="no">第八帙</span><h2>惊坐</h2><span class="cnt">三则</span></div>
    <div class="zhinote">笑谈之外的三件事：一场弹劾，一阵妖风，一座死城。</div>
    <div class="cards">
      <article class="tan dark wide">
        <span class="who">李廌记</span>
        <h3>弹劾中宫</h3>
        <blockquote><q>{R:zhongcheng}</q><q>{R:tanhe}</q><q>{R:gaidai}</q></blockquote>
        <p class="my">南郊大礼，皇后与太夫人的车轿冲撞仪仗，五使之中没人敢出声。御史中丞说涉及中宫不敢言，东坡答：你的职责就是肃正朝仪，不能不上报。随即自己上疏。次日法驾回宫，皇后果然没有按惯例出来迎候。簿子里另有一句总评：东坡不止文章盖世，政事与风节更过人。</p>
      </article>
      <article class="tan dark">
        <span class="who">东坡先生</span>
        <h3>华山之风</h3>
        <blockquote><q>{R:ganshang}</q><q>{R:weigui}</q><q>{R:fudun}</q></blockquote>
        <p class="my">家里闹鬼，他跟鬼讲道理，那鬼合爪一拜道谢而去；路过华山，随行一个士兵被「神」缠上，众人说是岳神发怒。他进庙直接跟山神讲理：一个小卒如虮虱，何足劳神威？祸福在天，你怒你的，我照样走。顶风而行，风越发专追他这一队人马，劝他祷告的他说：神要怒就怒，我的行程不停，能把我怎样。走完这一程，什么事也没有。</p>
      </article>
      <article class="tan dark">
        <span class="who">李廌记</span>
        <h3>永乐之城</h3>
        <blockquote><q>{R:wushui}</q><q>{R:bingsi}</q></blockquote>
        <p class="my">徐禧坚持把永乐城修进死地，被围后城中断水，最后出现人以口相啖的场面。此前有位洪州老妇用三世禄命书替他算命，说他当死于兵，全家大怒要以妖言办她；城破之日，一切应验。李廌记这类事不置评语，惨烈自己会说话。</p>
      </article>
    </div>
  </section>

  <section class="zhi">
    <div class="zhihead"><span class="no">第九帙</span><h2>家传</h2><span class="cnt">三则</span></div>
    <div class="zhinote">关于苏轼祖父与开国传闻的三段，像是簿子里夹着的一叠族谱散页。</div>
    <div class="cards">
      <article class="tan wide">
        <span class="who">东坡先生述</span>
        <h3>祖父的粮仓</h3>
        <blockquote><q>{R:su}</q><q>{R:yu}</q></blockquote>
        <p class="my">东坡祖父不大识字，胸襟却极宽：只种粟，以稻换粟连年囤积，旁人都不解；大饥之年开仓，按族人、姻亲、佃户、乡邻的次序散尽，一乡无人挨饿。又在宅边广种芋魁，荒年蒸满大甑摆在门外任人取食。后来朝廷给儿子封官的告身送到那天，他正大醉，露顶戴小冠，箕踞读罢，连同赐物和剩下的牛肉装进两只布囊，让村童挑着，自己骑驴进城，围观的人没有不笑的，有识之士却称奇。</p>
      </article>
      <article class="tan">
        <span class="who">东坡先生述</span>
        <h3>黄龙食莴苣</h3>
        <blockquote><q>{R:huanglong}</q></blockquote>
        <p class="my">五代末，普安禅院还是道边一座草庵，僧人种菜奉佛，梦见金色黄龙来吃他的莴苣；不久真有一位伟丈夫取菜而食，僧人看他器宇不凡，殷勤供养，临别赠了几枚钱并讨了一句不忘旧情的许诺。那伟丈夫，后来成了宋朝开国的太祖，寺院也便有了皇家敕额。</p>
      </article>
      <article class="tan">
        <span class="who">王丰甫言</span>
        <h3>读眉山集读没了妻子</h3>
        <blockquote><q>{R:diaoben}</q><q>{R:yuan}</q></blockquote>
        <p class="my">越人章元弼娶了位端庄美丽的表妹，自己相貌平平而痴书：新雕的苏轼集一到手，夜里读到忘睡，妻子忍无可忍求去，他真把人送回了娘家，还逢人便讲：只因读眉山集才把妻子读没了。一代文宗在民间的影响如此，寻常读者追星，不过如此。</p>
      </article>
    </div>
  </section>

  <section class="coda">
    <div class="cwrap">
      <div class="cv"><q>{R:liaoliao}</q></div>
      <p class="cmy">那场没考中的考试，没有拦住这本小书。四库馆臣数过的这几行字，替一个失意的名字，在天地间行走了九百年。</p>
      <div class="cseal">席珍</div>
    </div>
  </section>

</main>

<footer>
  <div class="wrap ftgrid">
    <div><b>文本来源</b>：殆知阁古代文献简体库<q>师友谈记</q>（子藏杂家），北宋李廌撰。仓库：github.com/robertsong/daizhige-daodu</div>
    <div><b>引文核验</b>：本页全部引文由脚本自库本切片生成，经去标点、归一逐字比对通过；白话反扫六字窗零撞。</div>
    <div><b>时代局限</b>：华岳神怒、鬼魅应验、茅将军托梦诸条系宋人记闻照录，不代今人采信；元祐党争语境下对新学的讥评、「佞臣」「小人」等贬语均为作者立场；永乐城条记围城惨状照录；妇女境遇（章元弼出妻、乳媪遇祟）反映当时观念。立此存照，不代今人立论。</div>
    <div><b>导读说明</b>：李廌字方叔，「苏门六君子」之一，元祐三年下第、终身布衣，东坡卒后他所作祭文有「名山大川」之句传诵后世，系库外史料；库本提要定为元祐后追记，卷尾校上年月系四库进书原帙。</div>
  </div>
</footer>

<script>
(function(){
  var stage=document.getElementById('stage');
  stage.addEventListener('click',function(){
    if(stage.classList.contains('on'))return;
    stage.classList.add('on');
    document.body.classList.add('on');
  });

  var cups=document.querySelectorAll('.cup');
  var fushou=document.getElementById('fushou');
  var order=0;
  cups.forEach(function(c){
    c.addEventListener('click',function(){
      var i=+c.getAttribute('data-i');
      if(i!==order)return;
      order++;
      c.classList.add('hit');
      if(order===4){
        setTimeout(function(){fushou.classList.add('show');},700);
      }
    });
  });

  document.querySelectorAll('.jian').forEach(function(j){
    j.addEventListener('click',function(){j.classList.toggle('open');});
  });

  var btns=document.querySelectorAll('.steps button');
  var lines=document.querySelectorAll('.steptext p');
  btns.forEach(function(b){
    b.addEventListener('click',function(){
      var s=+b.getAttribute('data-s');
      btns.forEach(function(x){x.classList.remove('cur');});
      lines.forEach(function(x){x.classList.remove('cur');});
      b.classList.add('cur');
      lines[s].classList.add('cur');
    });
  });
})();
</script>
</body>
</html>
'''

N = '466'
html = TPL.replace('__N__', N)
for k, v in Q.items():
    tok = '{R:%s}' % k
    assert tok in html, f'token missing in template: {k}'
    html = html.replace(tok, v)
assert '{R:' not in html, 'unreplaced token remains'

open(OUT_PATH, 'w', encoding='utf-8').write(html)
print('written', OUT_PATH, len(html), 'bytes,', len(Q), 'quotes')
for k in Q:
    print(f'  {k}: {Q[k]}')
