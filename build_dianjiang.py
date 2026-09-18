#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成导读 385：光宣诗坛点将录（聚义厅点将壳）+ 内嵌核验。"""
import re, sys, random
from html import escape

LIB = 'daizhige-simplified/诗藏/诗话/光宣诗坛点将录.txt'
OUT = 'daizhige-daodu/guangxuan-dianjianglu.html'
T = open(LIB, encoding='utf-8').read()

def cut(s, e):
    i = T.find(s)
    assert i >= 0, 'start not found: ' + s
    j = T.find(e, i)
    assert j >= 0, 'end not found: ' + e
    return T[i:j + len(e)]

Q = {}
Q['qianli'] = cut('昔瓶水斋主人', '之作。')
Q['caodongfu'] = cut('并世诗人', '突过乾嘉。')
Q['yizhouye'] = cut('竭一昼夜之力', '纲罗斯册矣。')
Q['bainian'] = cut('百年之间', '略系于此。')
Q['bieshi'] = cut('别有事在', '非无谓而作也。')
Q['gengyi'] = cut('故于校稿时', '实乖余本旨。')
Q['dazhu'] = cut('日走四马路书坊', '一时纸贵。')
Q['zhongban'] = cut('中者半，不中者半', '不中者半')
Q['xiangqi'] = cut('似我者拙', '学我者死。')
Q['yuansiliang'] = cut('湘绮为湖湘派领袖', '百世莫易矣。')
Q['sanli1'] = cut('见一善', '阅世高谈辟户牖。')
Q['sanli2'] = cut('撑肠万卷饥犹餍', '西江一脉此传薪。')
Q['zheng1'] = cut('慷慨北京卢俊义', '收取此山奇货去。')
Q['zheng2'] = cut('吁嗟乎！日暮途远终为虏', '惜哉此子巧言语。')
Q['zheng3'] = cut('盖以自托殷顽', '于民族为不孝。')
Q['zheng4'] = cut('孔子不以人废言', '兹仍旧录。')
Q['linxu1'] = cut('断头旭', '百夫之特。')
Q['linxu2'] = cut('戊戌参与新政', '政变诛，年二十四。')
Q['shuijun'] = cut('按四寨水军头领', '词家属之。')
Q['wpy'] = cut('铁骑突出刀枪鸣', '秋月白。')
Q['zm'] = cut('六百年来', '梦窗神髓者也')
Q['kangzan'] = cut('维新百日', '视此镌。')
Q['siyin'] = cut('此四家，埋名而不隐姓', '不必人人尽喻也。')
Q['lehe'] = cut('衣冠而优孟', '者也。')
Q['shiqian'] = cut('一半儿乞相一半儿偷', '一半儿偷。')
Q['duan'] = cut('好一把贱骨头', '贱骨头。')
Q['pan'] = cut('粉墨登场一曲新', '艳说英伦迹已陈。')
Q['shijing'] = cut('昨夜梦洞庭', '使我松间醒。')
Q['fang'] = cut('尝制二印', '不讳也。')
Q['niao'] = cut('鸟是众生', '乃无可依耳。')
Q['reunion'] = cut('及癸酉秋间', '寓俞大维家。')
Q['mu10'] = cut('子今来甚佳', '今可见矣！')
Q['huanwei'] = cut('吾向不知', '欢慰平生。')
Q['xusijiang'] = cut('汪先生今之许子将也', '惜某未见其人也。')
Q['nianyajiazi'] = cut('余年家子耳', '余年家子耳')
Q['mengxiang'] = cut('王梦湘不可漏', '王梦湘不可漏')
Q['ningshang'] = cut('宁偿一士丧千金', '漫谓遗珠负王叟')
Q['kang1'] = cut('汪撰《光宣诗坛点将录》', '何谓之摹拟也？')
Q['kang2'] = cut('某生平经史学问', '窥其隐欤？')
Q['shangmoni'] = cut('康南海但以', '三字致憾。')
Q['shiyi'] = cut('陈石遗以天罡自命', '大为不乐。')
Q['wei'] = cut('言近代诗派者', '必不可废也。')
Q['zyy'] = cut('不为无益之事', '安能悦有涯之生？')
Q['luokuan'] = cut('甲申十一月', '覃家小湾方湖')

# ---------- 座次解析 ----------
GROUPS = ['诗坛旧头领一员','诗坛都头领二员','掌管诗坛机密军师二员','一同参赞诗坛军务头领一员',
 '掌管钱粮头领二员','马军五虎将五员','马军大骠骑兼先锋使八员','马军小彪将兼远探出哨头领一十六员',
 '步军头领一十员','步军将校一十七员','四寨水军头领八员','四店打听声息邀接来宾头领八员',
 '总探声息头领一员','军中走报机密步军头领四员','守护中军马军骁将二员','守护中军步军骁将二员',
 '专管行刑刽子手二员','专管三军内探事马军头领二员','掌管监造诸事头领一十六员','额外头领附录']
IDX = [T.find(g) for g in GROUPS]
assert all(a < b for a, b in zip(IDX, IDX[1:])), 'group order broken'
IDX.append(T.find('○光宣诗坛点将录定本跋'))
SEAT_RE = re.compile(r'^(托塔天王\S*|[天地].星\S*)[ 　]+(.+)$')
EXTRA_SEAT = re.compile(r'^(教头王进|黄面佛黄文煜|铁棒栾廷玉)　+(.+)$')

wall = []   # (header, subchips, seats raw list)
for gi in range(len(GROUPS)):
    seg = T[IDX[gi]:IDX[gi+1]]
    lines = [l.strip() for l in seg.split('\n') if l.strip()]
    seats, subs = [], []
    prev_sub = False
    for l in lines[1:]:
        m = SEAT_RE.match(l) or EXTRA_SEAT.match(l)
        if m:
            seats.append(l); prev_sub = False
        elif l.endswith('一员') and GROUPS[gi].startswith('掌管监造'):
            subs.append(l); prev_sub = True
        elif prev_sub and len(l) < 25:
            seats.append(l); prev_sub = False
    wall.append((GROUPS[gi], subs, seats))
N_SEATS = sum(len(s) for _, _, s in wall)
CN_NUM = '〇一二三四五六七八九'
def cn(n):
    return ''.join(CN_NUM[int(d)] for d in str(n))

def seat_html(raw, cls='seat'):
    parts = [p for p in re.split(r'[ 　]+', raw) if p]
    head = parts[0]
    star = head[:4] if head.startswith('托塔天王') else head[:3]
    nick = head[len(star):]
    out = '<span class="%s qv"><b>%s</b><i>%s</i>' % (cls, escape(star), escape(nick))
    for p in parts[1:]:
        pm = re.match(r'^(（附[^）]*）|（?一作.*)$', p)
        if pm:
            out += '<u>%s</u>' % escape(p)
        else:
            nm = re.match(r'^(.*?)(（附[^）]*）|（?一作.*)$', p)
            if nm and nm.group(2):
                out += '<em>%s</em><u>%s</u>' % (escape(nm.group(1)), escape(nm.group(2)))
            else:
                out += '<em>%s</em>' % escape(p)
    return out + '</span>'

def qblock(key, cls='q'):
    return '<span class="%s">%s</span>' % (cls, escape(Q[key]))

# 妙配数据 (seat raw 前缀 -> 理由)
MIAOPEI = [
 ('地满星玉旖竿孟康', '严复', '孟康管造船。严复是福州船政学堂第一届学生，上舰实习过，后来把海那边的书一本本译回来。'),
 ('地巧星玉臂匠金大坚', '吴俊卿', '金大坚专刻印信。吴昌硕刻了一辈子印，祖师爷的活儿找对了人。'),
 ('地辅星轰天雷凌振', '梁启超', '凌振放炮，任公办报。一支笔当炮用，响遍天下。'),
 ('地文星圣手书生萧让', '顾印愚', '行文走檄的书记官，交给真会写字的手。'),
 ('地正星铁面孔目裴宣', '胡思敬', '铁面孔目掌功过簿。他当御史时，真的参过硬骨头。'),
 ('地慧星一丈青扈三娘', '吴芝瑛', '榜上罕见的女手。书法家，葬过秋瑾，配一丈青绰号毫不委屈。'),
]
def miao_raw(prefix):
    for _, subs, seats in wall:
        for s in seats:
            if s.startswith(prefix):
                return s
    raise KeyError(prefix)

random.seed(385)
stars_pos = []
for i in range(N_SEATS):
    ang = random.uniform(0, 6.2832)
    rad = 120 + (i % 5) * 26 + random.uniform(0, 18)
    stars_pos.append((200 + rad*1.25*__import__('math').cos(ang), 200 + rad*__import__('math').sin(ang)))
stars_html = ''.join('<i style="left:%.1f%%;top:%.1f%%;--d:%.2fs"></i>' % (x/4.6, y/4.6, 0.06+i*0.018) for i,(x,y) in enumerate(stars_pos))

# 空椅
BLANKS = [('地乐星铁叫子乐和', '惮□□', 'lehe'), ('地贼星鼓上蚤时迁', '林□□', 'shiqian'),
          ('地狗星金毛犬段景住', '沈□□', 'duan'), ('地耗星白日鼠白胜', '潘□□', 'pan')]
def blank_raw(head):
    for _, _, seats in wall:
        for s in seats:
            if s.startswith(head):
                return s
    raise KeyError(head)

HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>殆知阁导读 · 第三八五篇</title>
<style>
:root{--ink:#191917;--ink2:#20201e;--paper:#e8e4dc;--paper2:#ddd7cb;--stone:#5e8fbb;--stone2:#3f6c96;
--cinnabar:#c0453c;--dim:#8b877e;--faint:#55534d;
--serif:"Songti SC","STSong","Noto Serif CJK SC","Source Han Serif SC","SimSun",serif}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{background:var(--ink);color:var(--paper);font-family:var(--serif);line-height:1.75}
b{font-weight:700}
.q,.qv{color:var(--paper)}
.q{background:linear-gradient(180deg,transparent 62%,rgba(94,143,187,.22) 62%)}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
/* hero */
.hero{min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;position:relative;overflow:hidden;padding:56px 20px}
.kicker{letter-spacing:.35em;font-size:13px;color:var(--dim);margin-bottom:34px}
.stage{position:relative;width:min(760px,92vw);aspect-ratio:1.45;max-height:62vh}
.gongwrap{position:absolute;left:50%;top:50%;transform:translate(-50%,-52%);width:min(320px,58vw)}
.gong{width:100%;display:block;cursor:pointer;background:none;border:none;color:var(--paper)}
.gong svg{display:block;width:100%;height:auto}
.gong .ring{transition:transform .5s}
.gong:hover .ring{transform:scale(1.02)}
.gong:focus-visible{outline:2px solid var(--stone);outline-offset:6px;border-radius:50%}
.dots i{position:absolute;width:6px;height:6px;border-radius:50%;background:var(--stone);opacity:.13;transform:scale(.7);transition:opacity .6s,transform .6s;transition-delay:var(--d)}
.hero.lit .dots i{opacity:.95;transform:scale(1.15)}
.hero.lit .dots i:nth-child(3n){background:#7fa8cf}
.vtitle{position:absolute;right:2%;top:50%;transform:translateY(-50%);writing-mode:vertical-rl;height:max-content;font-size:clamp(38px,6vw,58px);letter-spacing:.18em;font-weight:700;opacity:.28;transition:opacity 1.2s .2s,transform 1.2s .2s;transform:translateY(-46%)}
.hero.lit .vtitle{opacity:1;transform:translateY(-50%)}
.vtitle .qv{text-orientation:upright;display:inline-block}
.seal{position:absolute;right:calc(2% - 74px);bottom:8%;width:64px;height:64px;background:var(--cinnabar);color:var(--paper);display:grid;grid-template-columns:1fr 1fr;place-items:center;font-size:24px;line-height:1;border-radius:6px;box-shadow:0 0 0 2px rgba(232,228,220,.15);opacity:0;transform:scale(1.7) rotate(-8deg);transition:all .45s cubic-bezier(.2,1.4,.4,1) 1.6s}
.seal span{display:block}
.seal .s1{grid-area:1/2}.seal .s2{grid-area:2/2}.seal .s3{grid-area:1/1}.seal .s4{grid-area:2/1}
.hero.lit .seal{opacity:1;transform:scale(1) rotate(-3deg)}
.taphint{margin-top:30px;font-size:14px;color:var(--dim);letter-spacing:.3em}
.hero-sub{max-width:560px;margin-top:26px;font-size:15px;color:#c9c4b8;text-align:center}
/* spine */
.spine{position:fixed;right:18px;top:50%;transform:translateY(-50%);z-index:40;display:flex;flex-direction:column;gap:10px}
.spine a{writing-mode:vertical-rl;text-decoration:none;color:var(--faint);font-size:13px;letter-spacing:.22em;padding:10px 3px;border-right:2px solid transparent;transition:color .3s,border-color .3s}
.spine a.on{color:var(--stone);border-right-color:var(--stone)}
@media(max-width:1100px){.spine{display:none}}
/* panels */
section{position:relative}
.wrap{max-width:980px;margin:0 auto;padding:90px 24px}
h2.sec{font-size:clamp(24px,3.4vw,34px);letter-spacing:.14em;margin-bottom:10px}
.sec-note{color:var(--dim);font-size:14px;margin-bottom:46px}
/* S1 三折 */
.folds{display:grid;grid-template-columns:repeat(3,1fr);gap:0;background:var(--paper);color:#2b2925;border-radius:4px;overflow:hidden;box-shadow:0 18px 50px rgba(0,0,0,.5)}
.fold{padding:38px 30px 42px;position:relative}
.fold+.fold{border-left:1px dashed #b8b0a0}
.fold:nth-child(2){background:#efeae1}
.fold:nth-child(3){background:#e6e0d4}
.fold h3{font-size:20px;letter-spacing:.1em;margin-bottom:6px;color:#1e1c1a}
.fold .yr{font-size:12px;letter-spacing:.3em;color:#8a6f3f;margin-bottom:16px}
.fold p{font-size:14.5px;margin-bottom:18px;color:#3a372f}
.fold .q{background:linear-gradient(180deg,transparent 60%,rgba(94,143,187,.25) 60%);color:#23211d;display:block;margin:12px 0;padding:2px 0;font-size:15px}
.fold .src{display:block;font-size:12px;color:#8a7f68}
@media(max-width:900px){.folds{grid-template-columns:1fr}.fold+.fold{border-left:0;border-top:1px dashed #b8b0a0}}
/* S2 聚义厅 */
.juyi{background:var(--ink2)}
.hall{display:flex;flex-direction:column;gap:44px}
.band{border:1px solid #34332f;border-radius:6px;overflow:hidden}
.band-h{display:flex;align-items:baseline;gap:14px;padding:14px 20px;background:#232320;border-bottom:1px solid #34332f}
.band-h .qv{font-size:16px;letter-spacing:.08em;color:var(--stone)}
.band-h small{color:var(--dim);font-size:12px;letter-spacing:.2em}
.band-b{padding:20px}
.subchip{display:inline-block;margin:4px 6px 4px 0;padding:3px 10px;font-size:12px;color:#a89d84;border:1px dashed #4a453c;border-radius:20px}
.subchip.qv{color:#a89d84}
.seats{display:flex;flex-wrap:wrap;gap:8px}
.seat{display:inline-flex;align-items:baseline;gap:6px;padding:7px 12px;border:1px solid #3c3f46;border-radius:3px;background:#232529;font-size:14px;transition:border-color .25s,background .25s;cursor:default}
.seat:hover{border-color:var(--stone);background:#2a2d33}
.seat b{color:var(--stone);font-size:12.5px;letter-spacing:.05em}
.seat i{font-style:normal;color:#d8d3c7}
.seat em{font-style:normal;font-weight:700;color:var(--paper)}
.seat u{text-decoration:none;color:var(--dim);font-size:12px}
.bigcard{border:1px solid #3c4b5c;background:linear-gradient(160deg,#232830,#1f232a);border-radius:6px;padding:26px 28px;margin-bottom:18px;position:relative}
.bigcard:before{content:"";position:absolute;inset:6px;border:1px solid rgba(94,143,187,.18);border-radius:4px;pointer-events:none}
.bigcard .who{display:flex;flex-wrap:wrap;align-items:baseline;gap:10px;margin-bottom:14px}
.bigcard .who .qv{font-size:15px;color:var(--stone)}
.bigcard .who .qv em{font-size:21px;color:var(--paper)}
.bigcard .cap{font-size:14px;color:#b3ac9e;margin-bottom:12px}
.bigcard .q{display:block;margin:10px 0;padding:3px 0;font-size:16.5px}
.bigcard .src{display:block;font-size:12px;color:var(--dim);margin-bottom:6px}
.panh{font-size:15px;color:var(--cinnabar);border-left:3px solid var(--cinnabar);padding:2px 0 2px 12px;margin:14px 0 4px;letter-spacing:.06em}
/* S3 空椅 */
.kongyi{background:var(--paper);color:#2b2925}
.kongyi h2.sec{color:#1e1c1a}
.kongyi .sec-note{color:#7d7361}
.kongyi .q,.kongyi .qv{color:#23211d}
.kongyi .q{background:linear-gradient(180deg,transparent 60%,rgba(94,143,187,.28) 60%)}
.chairs{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:36px}
@media(max-width:900px){.chairs{grid-template-columns:repeat(2,1fr)}}
.flip{perspective:900px;min-height:230px}
.flip .inner{position:relative;width:100%;height:100%;min-height:230px;transform-style:preserve-3d;transition:transform .7s cubic-bezier(.3,.9,.3,1)}
.flip.on .inner{transform:rotateY(180deg)}
.face{position:absolute;inset:0;backface-visibility:hidden;border:1px dashed var(--cinnabar);border-radius:6px;background:#f2eee5;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;padding:20px;text-align:center}
.face.back{transform:rotateY(180deg);background:#ece6d9;border-style:solid;border-color:#c9bfa9}
.face .qv{font-size:16px;letter-spacing:.06em}
.face .seat b{color:#8a6f3f}
.face .qm{font-size:30px;color:#b8ad95;font-family:var(--serif)}
.face .hint{font-size:12px;color:#a2937a;letter-spacing:.25em}
.face .q{font-size:15px;display:block}
.siyn{margin-top:34px;font-size:15px;border-top:1px dashed #b8b0a0;padding-top:22px}
/* S4 反响 */
.fanyin{background:var(--ink)}
.notes{display:grid;grid-template-columns:repeat(2,1fr);gap:22px}
@media(max-width:900px){.notes{grid-template-columns:1fr}}
.note{background:var(--paper);color:#2b2925;border-radius:3px;padding:26px 26px 30px;box-shadow:0 14px 34px rgba(0,0,0,.45);position:relative}
.note:nth-child(odd){transform:rotate(-.5deg)}
.note:nth-child(even){transform:rotate(.5deg)}
.note:before{content:"";position:absolute;top:-9px;left:50%;transform:translateX(-50%);width:16px;height:16px;border-radius:50%;background:var(--cinnabar);box-shadow:0 2px 5px rgba(0,0,0,.4)}
.note h3{font-size:18px;letter-spacing:.1em;margin-bottom:12px;color:#1e1c1a}
.note p{font-size:14.5px;margin-bottom:12px;color:#3a372f}
.note .q{display:block;font-size:15px;margin:8px 0;padding:2px 0;background:linear-gradient(180deg,transparent 60%,rgba(94,143,187,.25) 60%);color:#23211d}
.note .src{display:block;font-size:12px;color:#8a7f68;margin-bottom:6px}
/* S5 妙配 */
.miaopei{background:var(--ink2)}
.tiles{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
@media(max-width:900px){.tiles{grid-template-columns:1fr}}
.tile{perspective:900px;min-height:210px}
.tile .inner{position:relative;width:100%;height:100%;min-height:210px;transform-style:preserve-3d;transition:transform .7s cubic-bezier(.3,.9,.3,1)}
.tile.on .inner{transform:rotateY(180deg)}
.tface{position:absolute;inset:0;backface-visibility:hidden;border-radius:6px;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:12px;padding:22px;text-align:center}
.tface.front{background:#262a31;border:1px solid #3c4b5c}
.tface.front .qv{font-size:17px;color:#cfd8e2}
.tface.front .qv b{color:var(--stone)}
.tface.front .hint{font-size:12px;color:var(--dim);letter-spacing:.25em}
.tface.back{transform:rotateY(180deg);background:var(--paper);color:#2b2925;border:1px solid #c9bfa9}
.tface.back .qv{font-size:16px;color:#23211d;font-weight:700}
.tface.back p{font-size:14px;color:#3a372f}
button.flipbtn{all:unset;cursor:pointer;display:block;width:100%}
button.flipbtn:focus-visible .face,button.flipbtn:focus-visible .tface{outline:2px solid var(--stone);outline-offset:4px}
/* S6 尾屏 */
.tail{background:#131312;min-height:82vh;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden}
.tailwrap{display:flex;gap:clamp(30px,7vw,90px);align-items:flex-start;padding:80px 24px}
.vcol{writing-mode:vertical-rl;height:max-content;display:inline-block}
.vcol .q{font-size:clamp(19px,2.6vw,26px);letter-spacing:.3em;line-height:2.1}
.vcol.small .q{font-size:15px;color:var(--dim);letter-spacing:.24em}
.tseal{width:52px;height:52px;background:var(--cinnabar);color:var(--paper);display:flex;align-items:center;justify-content:center;font-size:22px;letter-spacing:.1em;border-radius:5px;writing-mode:vertical-rl;margin-top:18px}
/* footer */
footer{background:#111110;padding:44px 24px 56px;font-size:13px;color:var(--dim)}
footer .fin{max-width:980px;margin:0 auto;display:flex;flex-direction:column;gap:8px}
footer a{color:#7f96ad}
footer .warm{color:#a2977f}
/* reveal */
.rv{opacity:0;transform:translateY(26px);transition:opacity .8s ease,transform .8s ease}
.rv.in{opacity:1;transform:none}
@media(max-width:640px){.wrap{padding:64px 18px}.hero-sub{font-size:14px}.seal{right:auto;left:2%;bottom:0;width:54px;height:54px;font-size:20px}}
</style>
</head>
<body>

<header class="hero" id="top">
  <p class="kicker">第三八五篇 · 诗藏诗话</p>
  <div class="stage">
    <div class="dots" aria-hidden="true">__STARS__</div>
    <button class="gong" id="gong" aria-label="敲锣开榜">
      <svg viewBox="0 0 400 400" aria-hidden="true">
        <defs>
          <radialGradient id="gm" cx="42%" cy="36%" r="75%">
            <stop offset="0%" stop-color="#3a4c60"/><stop offset="55%" stop-color="#2b3a4a"/><stop offset="100%" stop-color="#1c2631"/>
          </radialGradient>
        </defs>
        <g class="ring">
          <line x1="118" y1="42" x2="282" y2="42" stroke="#4a4a44" stroke-width="4"/>
          <line x1="200" y1="42" x2="200" y2="88" stroke="#4a4a44" stroke-width="2.5"/>
          <circle cx="200" cy="200" r="118" fill="none" stroke="#5e8fbb" stroke-width="5" opacity=".55"/>
          <circle cx="200" cy="200" r="104" fill="url(#gm)" stroke="#8fb4d6" stroke-width="2.5"/>
          <circle cx="200" cy="200" r="26" fill="none" stroke="#8fb4d6" stroke-width="2" opacity=".8"/>
          <circle cx="200" cy="200" r="9" fill="#5e8fbb"/>
        </g>
      </svg>
    </button>
    <h1 class="vtitle"><span class="qv">光宣诗坛点将录</span></h1>
    <div class="seal" aria-hidden="true"><span class="s1">诗</span><span class="s2">坛</span><span class="s3">点</span><span class="s4">将</span></div>
  </div>
  <p class="taphint">敲锣 · 开榜</p>
  <p class="hero-sub">一九一九年南昌，两位诗人闲谈间定了件小事：把光绪宣统两朝一百多位诗人，照梁山泊一百单八将的规矩排座次。榜出之后，上榜名士一半叫好一半叫屈，榜首本人亲手校订过这份榜，另有四把椅子，直到今天没有名字。</p>
</header>

<nav class="spine" aria-label="章节">
  <a href="#top" class="on">开榜</a>
  <a href="#yuanqi">缘起</a>
  <a href="#juyi">聚义厅</a>
  <a href="#kongyi">空椅</a>
  <a href="#fanyin">反响</a>
  <a href="#miaopei">妙配</a>
  <a href="#wei">收梢</a>
</nav>

<section id="yuanqi">
  <div class="wrap rv">
    <h2 class="sec">缘起 · 一榜三折</h2>
    <p class="sec-note">一份榜单写了二十六年，从南昌寓所的闲谈，到重庆山湾里的定本。</p>
    <div class="folds">
      <div class="fold">
        <p class="yr">己未 · 南昌</p>
        <h3>一昼夜草成</h3>
        <p>南昌寓所里，汪国垣和曹东敷朝夕论文。曹东敷撺掇他续旧例给并世诗人排座次，他一夜加一个白天写完初稿，同寓诸君抚掌叫绝。</p>
        <span class="q">__Q_qianli__</span>
        <span class="q">__Q_caodongfu__</span>
        <span class="src">曹东敷语</span>
        <span class="q">__Q_yizhouye__</span>
      </div>
      <div class="fold">
        <p class="yr">乙丑 · 北京</p>
        <h3>一本周刊带走</h3>
        <p>章士钊在京城的一座会馆里遇着他，当场把稿子拿走，刊上《甲寅》周刊。校稿时章行严擅自做了删改，作者多年后还记着这笔账。</p>
        <span class="q">__Q_gengyi__</span>
        <p>分期连载未完，沪上名流天天去书坊问出刊日期，赌谁坐哪把交椅。</p>
        <span class="q">__Q_dazhu__</span>
        <span class="q">__Q_zhongban__</span>
      </div>
      <div class="fold">
        <p class="yr">甲申 · 重庆</p>
        <h3>二十年补赞</h3>
        <p>避寇重庆，翻出箧藏原稿重定，逐人补写赞语。他把这次补写说得很重，说榜单背后另有寄托。</p>
        <span class="q">__Q_bainian__</span>
        <span class="q">__Q_bieshi__</span>
      </div>
    </div>
  </div>
</section>

<section class="juyi" id="juyi">
  <div class="wrap">
    <h2 class="sec rv">聚义厅 · 座次全榜</h2>
    <p class="sec-note rv">__NSEATS__席，二十级职司，一座梁山泊规模的诗坛。小牌是座次，大牌有赞语，全部照录库本。</p>
    <div class="hall">
__WALL__
    </div>
  </div>
</section>

<section class="kongyi" id="kongyi">
  <div class="wrap rv">
    <h2 class="sec">空椅 · 四个没有名字的座位</h2>
    <p class="sec-note">全榜只有四席，有星号有绰号有赞语，唯独名字空着。点开看作者给的四句谜面。</p>
    <div class="chairs">
__BLANKS__
    </div>
    <p class="siyn">库本作「惮」，而他自己的按语说「恽、沈二赞」，首字疑当作恽，照录待考。</p>
  </div>
</section>

<section class="fanyin" id="fanyin">
  <div class="wrap rv">
    <h2 class="sec">反响 · 上榜的人不答应</h2>
    <p class="sec-note">榜上人物大多健在，于是这份榜单的后续，全在别人的反应里。</p>
    <div class="notes">
      <div class="note">
        <h3>榜首自阅</h3>
        <p>一九三三年秋，袁伯揆到金陵探望陈散原。散原忽然记起什么，叫人把楼上客人请了下来。</p>
        <span class="q">__Q_reunion__</span>
        <span class="q">__Q_mu10__</span>
        <span class="q">__Q_huanwei__</span>
        <p>同年九月，这位榜首已经先要了副本，一页页从头审到尾，只嫌漏收一人。</p>
        <span class="q">__Q_mengxiang__</span>
        <span class="q">__Q_ningshang__</span>
        <span class="src">程穆庵赠诗</span>
      </div>
      <div class="note">
        <h3>康南海上门</h3>
        <p>南昌百花洲宴席上，康有为端着粤音当面发难：夸你一句，再讨个说法。</p>
        <span class="q">__Q_kang1__</span>
        <span class="q">__Q_kang2__</span>
        <p>翻了半天杂志，最后认下一条：写诗的事，汪辟疆看准了。</p>
        <span class="q">__Q_shangmoni__</span>
      </div>
      <div class="note">
        <h3>陈石遗不乐</h3>
        <p>陈衍自认为该坐天罡，榜上给了他地煞头一把，门户之内，座次是天大的事。</p>
        <span class="q">__Q_shiyi__</span>
      </div>
      <div class="note">
        <h3>许子将再见</h3>
        <p>袁伯揆在沪杭间逢人夸榜，只恨不识作者。见到本人，才知是散原的年家子。</p>
        <span class="q">__Q_xusijiang__</span>
        <span class="q">__Q_nianyajiazi__</span>
        <span class="src">散原答袁伯揆</span>
      </div>
    </div>
  </div>
</section>

<section class="miaopei" id="miaopei">
  <div class="wrap rv">
    <h2 class="sec">妙配 · 职司里的暗号</h2>
    <p class="sec-note">点将录的趣味一半在比拟：水浒的职司不是乱派的，六块牌翻过来看底。</p>
    <div class="tiles">
__TILES__
    </div>
  </div>
</section>

<section class="tail" id="wei">
  <div class="tailwrap">
    <div class="vcol small"><span class="q">__Q_zyy__</span></div>
    <div class="vcol"><span class="q">__Q_wei__</span></div>
    <div class="vcol small"><span class="q">__Q_luokuan__</span><span class="tseal">方湖</span></div>
  </div>
</section>

<footer>
  <div class="fin">
    <p>文本来源：殆知阁简体库 · 诗藏部《<span class="qv">光宣诗坛点将录</span>》，页面为殆知阁导读系列第三八五篇。代码与全部篇目见 <a href="https://github.com/robertsong/daizhige-daodu" rel="noopener">daizhige-daodu</a>。</p>
    <p>引文经脚本与库内文件去标点、异体归一逐字比对通过（__NQ__处），正文白话反扫六字窗零撞。</p>
    <p class="warm">提醒：本书是民国人给民国前后诗家排的座次，月旦人物自带那个时代的门户之见与党派眼光，连「附逆」的判词也是当时的写法，阅读请自带过滤器。</p>
  </div>
</footer>

<script>
(function(){
  var hero=document.querySelector('.hero');
  var gong=document.getElementById('gong');
  var done=false;
  gong.addEventListener('click',function(e){
    if(done){hero.classList.remove('lit');done=false;return;}
    if(e.target.closest('.vtitle'))return;
    hero.classList.add('lit');done=true;
  });
  var io=new IntersectionObserver(function(es){
    es.forEach(function(en){if(en.isIntersecting)en.target.classList.add('in');});
  },{threshold:.12});
  document.querySelectorAll('.rv').forEach(function(el){io.observe(el);});
  document.querySelectorAll('.flip,.tile').forEach(function(f){
    var b=f.querySelector('.flipbtn');
    b.addEventListener('click',function(){f.classList.toggle('on');});
  });
  var links=[].slice.call(document.querySelectorAll('.spine a'));
  var secs=links.map(function(a){return document.querySelector(a.getAttribute('href'));});
  var so=new IntersectionObserver(function(es){
    es.forEach(function(en){
      if(en.isIntersecting){
        links.forEach(function(a){a.classList.toggle('on',a.getAttribute('href')==='#'+en.target.id);});
      }
    });
  },{rootMargin:'-40% 0px -55% 0px'});
  secs.forEach(function(s){if(s)so.observe(s);});
})();
</script>
</body>
</html>
"""

# ---- 组装墙 ----
FEAT = {0:'wangkaiyun',1:'tou',5:'linxu',10:'shuijun',12:'kang',16:'fang',19:'shijing'}
def feat_card(kind, header, seats):
    if kind=='wangkaiyun':
        return ('<div class="bigcard"><div class="who">%s</div>'
                '<p class="cap">旧头领之位留给前一辈盟主，如晁盖之在天王殿，受香火，不问事。</p>'
                '<span class="q">%s</span><span class="src">湘绮自道</span>'
                '<span class="q">%s</span><span class="src">袁思亮语</span></div>'
                % (seat_html(seats[0]), escape(Q['xiangqi']), escape(Q['yuansiliang'])))
    if kind=='tou':
        return ('<div class="bigcard"><div class="who">%s</div>'
                '<span class="q">%s</span><span class="src">赞</span>'
                '<span class="q">%s</span></div>'
                '<div class="bigcard"><div class="who">%s</div>'
                '<p class="cap">第二把交椅坐了后来附逆的人。作者不肯抹名，也不肯轻轻放过，赞语之后另加一整段判词。</p>'
                '<span class="q">%s</span><span class="src">旗上语</span>'
                '<span class="q">%s</span>'
                '<p class="panh">判词</p>'
                '<span class="q">%s</span>'
                '<span class="q">%s</span></div>'
                % (seat_html(seats[0]), escape(Q['sanli1']), escape(Q['sanli2']),
                   seat_html(seats[1]), escape(Q['zheng1']), escape(Q['zheng2']),
                   escape(Q['zheng3']), escape(Q['zheng4'])))
    if kind=='linxu':
        rest=''.join(seat_html(s) for s in seats if '林旭' not in s)
        return ('<div class="bigcard"><div class="who">%s</div>'
                '<span class="q">%s</span><span class="src">赞</span>'
                '<span class="q">%s</span></div><div class="seats">%s</div>'
                % (seat_html(next(s for s in seats if '林旭' in s)), escape(Q['linxu1']),
                   escape(Q['linxu2']), rest))
    if kind=='shuijun':
        return ('<span class="q">%s</span>' % escape(Q['shuijun']) +
                '<div class="bigcard"><div class="who">%s</div>'
                '<span class="q">%s</span></div>'
                '<div class="bigcard"><div class="who">%s</div>'
                '<span class="q">%s</span><span class="src">半塘老人评</span></div>'
                '<div class="seats">%s</div>'
                % (seat_html(seats[0]), escape(Q['wpy']),
                   seat_html(seats[1]), escape(Q['zm']),
                   ''.join(seat_html(s) for s in seats[2:])))
    if kind=='kang':
        return ('<div class="bigcard"><div class="who">%s</div>'
                '<span class="q">%s</span><span class="src">赞</span></div>'
                % (seat_html(seats[0]), escape(Q['kangzan'])))
    if kind=='fang':
        return ('<div class="bigcard"><div class="who">%s%s</div>'
                '<span class="q">%s</span>'
                '<p class="cap">大方在天津制过两方印，真篆刻，真不讳。寒云问他何以自处，他拿陶诗答，答得听的人绝倒。</p>'
                '<span class="q">%s</span><span class="src">大方答寒云</span></div>'
                % (seat_html(seats[0]), seat_html(seats[1]), escape(Q['fang']), escape(Q['niao'])))
    if kind=='shijing':
        rest=''.join(seat_html(s) for s in seats if '释敬安' not in s)
        return ('<div class="bigcard"><div class="who">%s</div>'
                '<p class="cap">八指头陀的梦，君山是茶叶，煮的是月亮。</p>'
                '<span class="q">%s</span><span class="src">梦洞庭</span></div>'
                '<div class="seats">%s</div>'
                % (seat_html(next(s for s in seats if '释敬安' in s)), escape(Q['shijing']), rest))
    return ''

blocks=[]
for gi,(header,subs,seats) in enumerate(wall):
    seat_str=''.join(seat_html(s) for s in seats)
    chips=''.join('<span class="subchip qv">%s</span>' % escape(s) for s in subs)
    if gi in FEAT:
        body=feat_card(FEAT[gi], header, seats)
        blocks.append('<div class="band"><div class="band-h"><span class="qv">%s</span><small>%s席</small></div><div class="band-b">%s%s</div></div>'
                      % (escape(header), len(seats), chips, body))
    else:
        blocks.append('<div class="band"><div class="band-h"><span class="qv">%s</span><small>%d席</small></div><div class="band-b"><div class="seats">%s</div></div></div>'
                      % (escape(header), len(seats), seat_str))

tiles=''
for pref, poet, why in MIAOPEI:
    raw=miao_raw(pref)
    tiles+=('<div class="tile"><button class="flipbtn" aria-expanded="false"><div class="inner">'
            '<div class="tface front"><span class="qv">%s</span><span class="hint">翻牌见底</span></div>'
            '<div class="tface back"><span class="qv">%s</span><p>%s</p></div>'
            '</div></button></div>' % (escape(raw), escape(poet), escape(why)))

blanks=''
for head, shown, key in BLANKS:
    raw=blank_raw(head)
    blanks+=('<div class="flip"><button class="flipbtn" aria-expanded="false"><div class="inner">'
             '<div class="face front"><span class="qm">□</span><span class="qv">%s</span><span class="hint">点开看谜面</span></div>'
             '<div class="face back"><span class="q">%s</span></div>'
             '</div></button></div>'
             % (escape(raw), escape(Q[key])))

def fill(h):
    for k,v in Q.items():
        h=h.replace('__Q_%s__'%k, escape(v))
    h=h.replace('__STARS__', stars_html)
    h=h.replace('__WALL__', '\n'.join(blocks))
    h=h.replace('__TILES__', tiles)
    h=h.replace('__BLANKS__', blanks)
    h=h.replace('__NSEATS__', cn(N_SEATS))
    h=h.replace('__NQ__', str(len(Q)+N_SEATS+len(MIAOPEI)+len(BLANKS)+2))
    return h

html=fill(HTML)
open(OUT,'w',encoding='utf-8').write(html)

# ================= 核验 =================
def norm(s):
    return ''.join(ch for ch in s if ch.isalnum())
LIBN=norm(T)
fails=[]
for k,v in Q.items():
    if norm(v) not in LIBN: fails.append('quote '+k)
for _,_,seats in wall:
    for s in seats:
        if norm(s) not in LIBN: fails.append('seat '+s[:18])
for pref,_,_ in MIAOPEI:
    if norm(miao_raw(pref)) not in LIBN: fails.append('miao '+pref)
for head,_,_ in BLANKS:
    if norm(blank_raw(head)) not in LIBN: fails.append('blank '+head)

# 反扫：块边界切分 + 栈式引文通道
from html.parser import HTMLParser
QTOK={'q','qv','qi','qn','vq'}
BLOCK={'p','div','section','h1','h2','h3','h4','li','tr','blockquote','footer','header','td','th','br','title','small','span','em','b','i','u','button','a','nav','main','article','aside'}
class Sweep(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[]; self.chunks=[]; self.buf=[]
    def flush(self):
        if self.buf:
            self.chunks.append(''.join(self.buf)); self.buf=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs) if attrs else {}
        cls=(d.get('class') or '')
        qd=any(t in cls.split() for t in QTOK)
        self.stack.append((tag,qd))
        if tag in BLOCK: self.flush()
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:
                del self.stack[i:]; break
        if tag in BLOCK: self.flush()
    def handle_data(self,data):
        if not any(q for _,q in self.stack): self.buf.append(data)
sw=Sweep(); sw.feed(html)
hits=[]
for ch in sw.chunks:
    n=norm(ch)
    for i in range(len(n)-5):
        if n[i:i+6] in LIBN:
            hits.append((n[max(0,i-6):i+10], ch[:40]))
            i+=5
            break
print('seats:',N_SEATS,'quotes:',len(Q),'qtotal:',len(Q)+N_SEATS+len(MIAOPEI)+len(BLANKS)+2)
if fails:
    print('VERIFY FAIL:'); [print(' -',f) for f in fails]
if hits:
    print('ANTISCAN HITS:', len(hits)); [print(' -',h) for h in hits[:20]]
if not fails and not hits:
    print('ALL PASS')
