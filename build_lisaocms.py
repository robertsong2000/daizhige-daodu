# -*- coding: utf-8 -*-
"""build 离骚草木疏 导读页：品芳史馆壳（石青）"""
import sys, io
SRC = "/home/robertsong/workspace/claude/daizhige-simplified/诗藏/楚辞/离骚草木疏.txt"
OUT = "/home/robertsong/workspace/claude/daizhige-daodu/lisao-caomushu.html"

text = io.open(SRC, encoding="utf-8").read()

Q = {
 "q1":  "荪芙蓉以下凡四十有四种犹青史忠义独行之有全传也",
 "q2":  "薋菉葹之类十一种傅着巻末犹佞幸奸臣传也",
 "q2b": "犹佞幸奸臣传也",
 "q2c": "犹青史忠义独行之有全传也",
 "q3a": "彼既不能流芳后世",
 "q3b": "姑使之遗臭万载",
 "q4":  "每正冠敛衽如见其人",
 "q5":  "竭忠尽节凛然有国士之风",
 "q6":  "凡芳草嘉木一经品题者谓皆可敬也",
 "q7":  "班固讥三闾怨恨怀王是未知离骚之近于诗而诗之可以怨也",
 "q8":  "峡中储毒以药人兰花为第一",
 "q9":  "乃知甚美必有甚恶",
 "q10": "兰为国香人固服媚之又当爱而知其恶也",
 "q11": "离骚以兰为不可恃亦不为无说",
 "q12": "兰似君子蕙似士",
 "q13": "一干一华而香有余者兰也一干五七华而香不足者蕙也",
 "q14": "秋英不比春英落",
 "q15": "然以为飘零满地金则过矣",
 "q16": "落英云者谓始华之时",
 "q17": "菊花堕其水中水为变居民食甘谷水无不寿考",
 "q18": "菊性介烈不与百卉盛衰须霜降乃发",
 "q19": "其天性髙洁如此宜其通仙灵也",
 "q20": "朝歌之山有莽草焉可以毒鱼",
 "q21": "三闾所称草木多出于山海经此为莽草无疑",
 "q22": "王逸不见山海经以意言之",
 "q23": "人用捣以和米内水中鱼吞即浮出",
 "q24": "后皇嘉植橘徕服兮受命不迁生南国兮",
 "q25": "橘逾淮北为枳地气使然",
 "q26": "橘生江北为枳水土异也",
 "q27": "建安郡有橘冬月于木上覆裹之至明年春夏色变青黒味绝美",
 "q28": "药有君臣佐使而此为君离骚又以为君喻良有以也",
 "q29": "白芷一物而离骚异其名者四曰芷曰芳曰茝曰药",
 "q30": "生下湿地者曰泥菖夏菖生溪水中者曰水菖生石上者为石菖蒲",
 "q31": "以视陆玑之疏毛诗罗愿之翼尔雅可以方轨并驾",
 "q32": "泽畔行吟主于侈其博赡非以写其哀怨是亦好奇之过矣",
 "q33": "三闾未识孤妍离骚遗恨千年",
 "q34": "与君为新婚免丝附女萝",
 "q35": "浴兰兮沐芳",
 "q36": "扈江离与辟芷兮",
 "q37": "岂惟纫夫蕙茝",
 "q38": "辛夷楣兮药房",
 "q39": "兰生深山丛薄之中不为无人而不芳",
 "q40": "荼始苦而终甘荠则初食便甘",
 "q41": "余处幽篁兮终不见天",
 "q42": "一名羊负来者中国无此从外国羊毛中来",
 "q43": "军家铸鐡作之以布散路",
 "q44": "草冬生不死者楚人名曰宿莽",
 "q45": "离骚之文多本山海经",
 "q46": "岁在庆元丁已四月三日",
 "q47": "比以离骚草木疏见属刋于罗田县庠",
 "q48": "旧板散佚流传颇罕写本仅存亦可谓艺林之珍笈矣",
 "q49": "此本为影宋旧钞末有庆元庚申方灿跋",
 "q50": "仁杰少喜读离骚文今老矣犹时时手之",
 "q51": "多识于鸟兽草木之名",
 "q52": "荃香草以喻君也",
 "q53": "岭南地暖百卉造作无时而菊独后开",
 "q54": "訾医师以昌阳引年欲进其狶苓",
 "q55": "夕揽洲之宿莽",
}
for k, v in Q.items():
    assert v in text, "quote not in src: %s => %s" % (k, v)

CHIPS = [
 (1, [("荪荃","君者的菖蒲"),("芙蓉","莲的谱系"),("菊","落英公案"),("芝","一年三开"),("兰","国香之下有毒"),("石兰","山侧之兰"),
      ("蕙","一干多花"),("芷芳","一名四变"),("茝药","被认错的白芷"),("杜蘅","马蹄香"),("蘼芜","川芎之苗"),("杜若","芳洲之礼"),
      ("芰","菱的本名"),("蘦","先凋的甘草")]),
 (2, [("荼","苦菜还是茶"),("薜茘","缘木之藤"),("女萝","菟丝旧案"),("菌","非蕈乃是桂"),("茹","柴胡别名"),("紫","紫草所染"),
      ("华","芦苇青时"),("苽","雕胡之米"),("莼","水葵之羹"),("苹","大萍非花"),("蒿","皤皤白蒿"),("苴","蘘荷解蛊"),
      ("蒌","蒌蒿可羹"),("薠","似莎之草"),("胡","大小蒜辨"),("绳","蛇床别名"),("芭","蕉皮织布"),("藑茅","卜用之茅"),
      ("掲车","香草出彭城"),("留夷","芍药之疑")]),
 (3, [("橘","受命不迁"),("桂","木犀之憾"),("椒","似贤之戒"),("松","五鬣之名"),("柏","庙前古柏"),("辛夷","木笔迎春"),
      ("木兰","鲁班兰舟"),("莽","毒鱼之案"),("楸","望都之木"),("黄棘","盟约之名")]),
 (4, [("薋","蒺藜满道"),("菉","王刍贱草"),("葹","苍耳粘衣"),("艾","滥服之叶"),("茅","香草之变"),("萧","祭脂之蒿"),
      ("葛","钩吻之亲"),("萹","路旁杂菜"),("荠","甘而易生"),("榝","假椒充佩"),("篁","蔽天之竹")]),
]
assert sum(len(c) for _, c in CHIPS) == 55
assert len(CHIPS[3][1]) == 11 and sum(len(c) for j, c in CHIPS[:3]) == 44

def chips_html():
    out = []
    for juan, items in CHIPS:
        cls = "q4" if juan == 4 else ""
        tags = "".join('<button class="chip %s" data-t="%s"><q>%s</q></button>' % (cls, t, n) for n, t in items)
        out.append(tags)
    return out

C1, C2, C3, C4 = chips_html()

HTML = u"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>离骚草木疏</title>
<style>
:root{--bg:#191917;--panel:#1f1e1b;--panel2:#22211d;--paper:#e8e4dc;--ink:#26241f;--c:#5e8fbb;--cd:#3d5a75;--dim:#8b887f;--zhu:#a0423f;--line:#33312c}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--paper);font-family:"Songti SC","STSong","Noto Serif CJK SC","Source Han Serif SC","SimSun",serif;line-height:1.85}
q{quotes:none}
.hintro q,.note q,.kv .v q,.bub q,.tw q,.tw p q,.xu p q,.verdict .v q,.st p q{border-bottom:1px dashed var(--cd);color:#ddd8cd}
.xu p q{border-bottom-color:#b3a88f;color:#3a372f}
a{color:inherit}
.wrap{max-width:1060px;margin:0 auto;padding:0 26px}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.kicker{font-size:12px;letter-spacing:.4em;color:var(--dim)}
.sec{padding:88px 0 10px}
.sec h2{font-size:14px;font-weight:normal;letter-spacing:.55em;color:var(--c);margin:0 0 8px}
.sec .lead{color:var(--dim);font-size:14px;margin:6px 0 26px;max-width:46em}
q{font-style:normal}
.qq{display:block;margin:12px 0;padding:2px 0 2px 14px;border-left:2px solid var(--cd);color:#ddd8cd;font-size:15px;line-height:2}
.qq.big{font-size:17px;border-left-color:var(--c)}
.note{color:var(--dim);font-size:13.5px}
.hero{min-height:94vh;display:grid;grid-template-columns:150px auto 1fr;gap:34px;align-items:stretch;padding-top:52px}
.htitle{writing-mode:vertical-rl;font-size:clamp(58px,8.4vw,92px);letter-spacing:.16em;line-height:1.14;margin:0;height:100%;max-height:74vh;color:var(--paper)}
.hside{writing-mode:vertical-rl;justify-self:start;display:flex;flex-direction:column;gap:16px;align-items:center;padding-top:8px}
.hseal{writing-mode:vertical-rl;background:var(--c);color:#141410;padding:16px 8px;font-size:15px;letter-spacing:.34em}
.hsub{writing-mode:vertical-rl;color:var(--dim);font-size:13px;letter-spacing:.3em}
.hmain{display:flex;flex-direction:column;gap:30px;justify-content:center}
.hintro{max-width:34em;font-size:15.5px;color:#cfcabf}
.hintro b{color:var(--paper);font-weight:normal;border-bottom:1px solid var(--cd)}
.doors{display:flex;gap:16px}
.door{flex:1;border:1px solid var(--line);background:var(--panel);padding:20px 22px;cursor:pointer;text-align:left;color:var(--paper);font:inherit;transition:border-color .25s,transform .25s}
.door:hover{transform:translateY(-3px)}
.door.fang:hover{border-color:var(--c)}
.door.eq:hover{border-color:var(--dim)}
.door .role{font-size:13px;letter-spacing:.3em;color:var(--dim)}
.door.fang .role{color:var(--c)}
.door .num{display:block;font-size:44px;line-height:1.3;margin:4px 0 2px}
.door.fang .num{color:var(--c)}
.door.eq .num{color:var(--dim)}
.door q{display:block;font-size:12.5px;color:var(--dim);line-height:1.9;margin-top:6px}
.ratio{height:10px;display:flex;margin-top:2px}
.ratio i{display:block;height:100%;width:0;transition:width 1.2s ease .3s}
.ratio .rf{background:var(--c)}
.ratio .re{background:#4a473f}
.rlabels{display:flex;justify-content:space-between;font-size:12.5px;color:var(--dim);margin-top:8px;letter-spacing:.14em}
.rlabels b{color:var(--paper);font-weight:normal}
.juan{border:1px solid var(--line);background:var(--panel);padding:16px 20px;margin-top:14px}
.juan h3{margin:0 0 12px;font-size:12.5px;font-weight:normal;letter-spacing:.32em;color:var(--dim)}
.juan h3 em{font-style:normal;color:var(--c)}
.juan.evil{background:#1b1a17;border-color:#2d2b26}
.juan.evil h3 em{color:var(--dim)}
.juan.flash{outline:1px solid var(--zhu)}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chip{background:var(--panel2);border:1px solid #35332d;color:var(--paper);padding:6px 13px;font:inherit;font-size:15px;cursor:pointer;transition:border-color .2s,color .2s}
.chip:hover,.chip:focus{border-color:var(--c);color:var(--c);outline:none}
.chip.q4{background:transparent;border-style:dashed;color:var(--dim)}
.chip.q4:hover,.chip.q4:focus{color:var(--paper);border-color:var(--dim)}
#chipnote{min-height:26px;margin-top:14px;font-size:13.5px;color:var(--dim)}
#chipnote b{color:var(--paper);font-weight:normal}
.cases{display:grid;grid-template-columns:repeat(12,1fr);gap:16px}
.case{border:1px solid var(--line);background:var(--panel);padding:24px;position:relative}
.case .tag{position:absolute;top:20px;right:22px;font-size:11px;letter-spacing:.22em;color:var(--dim)}
.case h3{margin:0 0 4px;font-size:21px;font-weight:normal}
.case .sub{color:var(--dim);font-size:13px;margin:0 0 14px}
.s7{grid-column:span 7}.s5{grid-column:span 5}
.bub{border:1px solid var(--line);padding:12px 16px;font-size:14px;line-height:2;margin-top:10px;color:#cfcabf}
.bub .who{display:block;font-size:12px;letter-spacing:.26em;color:var(--dim);margin-bottom:2px}
.bub.cut{border-left:2px solid var(--zhu)}
.verdict{display:flex;gap:16px;align-items:flex-start;margin-top:16px}
.vseal2{flex:none;width:52px;height:52px;background:var(--zhu);color:#efe9db;display:flex;align-items:center;justify-content:center;font-size:22px;transform:rotate(-6deg)}
.kv{display:flex;gap:14px;margin-top:12px}
.kv .k{flex:none;font-size:11px;letter-spacing:.3em;color:var(--zhu);padding-top:6px;width:3.2em}
.kv .v{font-size:14px;line-height:2;color:#d5d0c5}
.kv .k.dim{color:var(--dim)}
.tw{display:flex;gap:14px;margin-top:6px}
.tw>div{flex:1;border:1px solid var(--line);padding:14px 16px}
.tw h4{margin:0 0 6px;font-size:14px;letter-spacing:.2em;color:var(--c);font-weight:normal}
.kws{display:flex;gap:14px;margin-top:8px}
.kw{flex:1;border:1px solid var(--line);background:var(--panel);padding:16px 18px}
.kw h4{margin:0;font-size:19px;font-weight:normal}
.kw .hab{display:inline-block;margin-top:8px;font-size:11px;letter-spacing:.2em;color:var(--c);border:1px solid var(--cd);padding:2px 8px}
.kw p{margin:10px 0 0;font-size:13px;color:var(--dim)}
.names{display:flex;gap:8px;margin-top:10px}
.nm{background:var(--panel2);border:1px solid #35332d;color:var(--paper);font:inherit;font-size:20px;padding:8px 22px;cursor:pointer;transition:background .2s,color .2s}
.nm.on{background:var(--c);border-color:var(--c);color:#141410}
.zp{border:1px solid var(--line);background:var(--panel);margin-top:12px;padding:16px 20px}
.zp .pane{display:none}
.zp .pane.show{display:block}
.zp q{display:block;font-size:16px;color:#ddd8cd;line-height:2}
.xu{background:var(--paper);color:var(--ink);margin-top:88px;padding:74px 0 66px}
.xu .kicker{color:#7d7466}
.xu h2{font-size:14px;font-weight:normal;letter-spacing:.55em;color:var(--zhu);margin:0 0 26px}
.xgrid{display:grid;grid-template-columns:auto 1fr;gap:48px}
.vrow{display:flex;flex-direction:row-reverse;gap:30px}
.vq{writing-mode:vertical-rl;height:16.5em;font-size:23px;letter-spacing:.3em;line-height:1;padding:10px 6px;border-right:1px solid #cdc5b4;color:#2c2a24;margin:0}
.xu p{max-width:40em;font-size:15px;line-height:2.1;margin:0 0 14px}
.xu .qq{color:#3a372f;border-left-color:var(--zhu);font-size:15px}
.cou{display:flex;flex-direction:row-reverse;justify-content:flex-start;gap:26px;margin:26px 0 8px}
.cl{writing-mode:vertical-rl;height:11.5em;font-size:21px;letter-spacing:.26em;color:#2c2a24;padding:8px 4px;margin:0;border-right:1px solid #cdc5b4}
.cseal{writing-mode:vertical-rl;background:var(--zhu);color:#efe9db;padding:12px 7px;font-size:15px;letter-spacing:.3em;align-self:flex-start;margin-top:6px}
.tl{display:flex;margin-top:20px}
.st{flex:1;border-top:2px solid var(--line);padding:18px 16px 0;position:relative}
.st::before{content:"";position:absolute;top:-5px;left:16px;width:8px;height:8px;border-radius:50%;background:var(--c)}
.st .yr{font-size:11px;letter-spacing:.24em;color:var(--dim)}
.st h4{margin:6px 0 6px;font-size:16px;font-weight:normal}
.st p{margin:0 0 8px;font-size:13px;color:var(--dim);line-height:1.95}
.st q{font-size:12.5px;color:#c9c4b9;line-height:1.95;display:block}
footer{border-top:1px solid var(--line);margin-top:90px;padding:30px 0 44px}
footer .wrap{font-size:12.5px;color:var(--dim);line-height:2.1}
footer a{color:var(--c);text-decoration:none}
@media (max-width:760px){
 .hero{grid-template-columns:1fr;min-height:0}
 .htitle{writing-mode:horizontal-tb;height:auto;max-height:none;font-size:52px;letter-spacing:.1em}
 .hside{writing-mode:horizontal-tb;flex-direction:row;padding-top:0}
 .hseal{writing-mode:horizontal-tb;padding:8px 14px}
 .hsub{writing-mode:horizontal-tb;letter-spacing:.2em}
 .s7,.s5{grid-column:span 12}
 .kws,.tw,.tl{flex-direction:column}
 .st{border-top:none;border-left:2px solid var(--line);padding:0 0 18px 16px}
 .st::before{top:4px;left:-5px}
 .xgrid{grid-template-columns:1fr}
 .vrow{justify-content:center}
 .vq{height:15.5em;font-size:19px}
 .cou{justify-content:center}
}
</style>
</head>
<body>

<header class="wrap hero">
  <div class="hside">
    <div class="hseal">宋 吴仁杰 撰</div>
    <div class="hsub">楚辞类 · 诗藏</div>
  </div>
  <h1 class="htitle">离骚草木疏</h1>
  <div class="hmain">
    <div class="kicker">殆知阁导读 卷四百二十一 · 品芳</div>
    <p class="hintro">一部给香草立传的书。庆元丁巳，国子学录吴仁杰把屈原笔下的草木一一请出来考订身世，自道篇末安排：<q>@@q1@@</q>，<q>@@q2@@</q>。芳草与恶草各立门墙，一部草木版的名臣传与奸臣传，就此开馆。</p>
    <div class="doors">
      <button class="door fang" id="doorfang">
        <span class="role">忠义之传</span>
        <span class="num">四十四</span>
        <q>@@q2c@@</q>
      </button>
      <button class="door eq" id="doorevil">
        <span class="role">佞幸之传</span>
        <span class="num">十有一</span>
        <q>@@q2b@@</q>
      </button>
    </div>
    <div>
      <div class="ratio" id="ratio"><i class="rf" id="rf"></i><i class="re" id="re"></i></div>
      <div class="rlabels"><span>芳册 <b>四十四种</b></span><span>臭册 <b>十一种</b></span></div>
    </div>
  </div>
</header>

<section class="sec wrap" id="qiang">
  <h2>品芳墙 · 五十五签</h2>
  <p class="lead">五十五签，即全书五十五个草目：前三卷四十四签是芳册，卷四十一签单独成坊。悬停任何一签，看它在这一卷里扮什么角色。</p>
  <div class="juan"><h3><em>卷一</em> 芳册 · 十四签</h3><div class="chips">@@C1@@</div></div>
  <div class="juan"><h3><em>卷二</em> 芳册 · 二十签</h3><div class="chips">@@C2@@</div></div>
  <div class="juan"><h3><em>卷三</em> 芳册 · 十签</h3><div class="chips">@@C3@@</div></div>
  <div class="juan evil" id="eviljuan"><h3><em>卷四</em> 佞幸坊（傅着巻末） · 十一签</h3><div class="chips">@@C4@@</div></div>
  <p id="chipnote">　</p>
</section>

<section class="sec wrap" id="chang">
  <h2>名场面 · 四则</h2>
  <p class="lead">考据在这本书里从不干瘪：有毒物档案，有三方对辩，有翻案定谳，还有一杯喝了长寿的菊花水。</p>
  <div class="cases">
    <article class="case s7">
      <span class="tag mono">卷一 · 兰</span>
      <h3>爱而知其恶</h3>
      <p class="sub">国香被告发：兰美丽到可以杀人</p>
      <q class="qq">@@q8@@</q>
      <p style="font-size:14px;color:#cfcabf;margin:8px 0">蜀中士人亲见醉渴者误喝了瓶里泡的兰花水，吐利之后才醒；峡谷里下毒，兰花排第一。吴仁杰从这句传闻里读出的不是惊悚，而是一条读骚的原则：</p>
      <q class="qq big">@@q10@@</q>
      <q class="qq">@@q9@@</q>
      <p class="note">所以〈离骚〉里那句 兰不可恃，在他看来并非苛评：<q>@@q11@@</q>。给偶像作谱的人写下这一笔，是全书最硬的一根骨头。</p>
    </article>
    <article class="case s5">
      <span class="tag mono">卷一 · 菊</span>
      <h3>落英之辩</h3>
      <p class="sub">一朵菊花，吵了近千年</p>
      <div class="bub"><span class="who">王荆公</span>《残菊》写秋菊落瓣，满地如金；有人质疑，他自辩取的是〈离骚〉落英本意。</div>
      <div class="bub"><span class="who">苏东坡</span>驳：<q>@@q14@@</q>，谁见秋菊落瓣？说 <q>@@q15@@</q></div>
      <div class="bub cut"><span class="who">吴仁杰 断</span>两位都急了。落，古义为始：<q>@@q16@@</q>。屈原吃的不是地上的花瓣，是刚开的头一茬。</div>
    </article>
    <article class="case s5">
      <span class="tag mono">卷三 · 莽</span>
      <h3>宿莽翻案</h3>
      <p class="sub">屈原水边的常青草，其实有毒</p>
      <div class="kv"><span class="k dim">旧注</span><div class="v">王逸：经冬不死的就是宿莽。<q>@@q44@@</q>，想当然耳。</div></div>
      <div class="kv"><span class="k dim">证据</span><div class="v">《山海经》：<q>@@q20@@</q>。捣烂拌米投水，鱼吃了就浮头：<q>@@q23@@</q></div></div>
      <div class="verdict">
        <span class="vseal2">断</span>
        <div class="v" style="font-size:14px;line-height:2">莽草即宿莽，芳草清誉就此改判毒物。<q>@@q21@@</q>，<q>@@q22@@</q>。</div>
      </div>
    </article>
    <article class="case s7">
      <span class="tag mono">卷一 · 菊</span>
      <h3>菊的两副面孔</h3>
      <p class="sub">南阳的长寿水，岭南的冬至花</p>
      <div class="tw">
        <div>
          <h4>甘谷水</h4>
          <p style="font-size:13.5px;color:#cfcabf;margin:0 0 6px">南阳郦县有甘谷，谷上遍生甘菊，落花坠水，水就变了性子；谷边居民长年喝这水，无不高寿。王畅、刘寛们到南阳做官，官做到司空、太尉，县里月月还得送四十斛甘谷水进府。</p>
          <q>@@q17@@</q>
        </div>
        <div>
          <h4>岭南霜</h4>
          <p style="font-size:13.5px;color:#cfcabf;margin:0 0 6px">中原重阳菊开，岭南却要等到冬至前后。吴仁杰说这正是菊的脾气：<q>@@q18@@</q>；天暖不发，非微霜不可，所以他赞叹：<q>@@q19@@</q></p>
          <q>@@q53@@</q>
        </div>
      </div>
    </article>
  </div>
</section>

<section class="sec wrap" id="bian">
  <h2>辨名考 · 两桩</h2>
  <p class="lead">全书一半篇幅在打名字官司：同一种草，几个名字；同一个名字，几种草。考据的刀光都藏在名实之间。</p>
  <div class="kws">
    <div class="kw"><h4>泥菖</h4><span class="hab">生下湿地</span><p>根肥大，气味臭，俗称臭蒲。叶虽有剑脊，仁杰问：要它何用。</p></div>
    <div class="kw"><h4>水菖</h4><span class="hab">生溪水中</span><p>一名白昌，根色正白，即溪荪。陈藏器把它与昌阳混为一谈。</p></div>
    <div class="kw"><h4>石菖蒲</h4><span class="hab">生石上</span><p>长在石上，根硬节密，闻着辛香。一寸九节，开紫花的最善，服食家的上品。</p></div>
  </div>
  <q class="qq">@@q30@@</q>
  <p class="note">名头最乱的一株草：荪、荃，还有菖蒲、昌阳与溪荪，王逸说它香草喻君，沈存中说兰荪即菖蒲，韩愈被讥 <q>@@q54@@</q>。仁杰排比诸家，只认一寸就有九节、开紫花的那一种，并断曰：<q>@@q28@@</q> 又引王逸原注 <q>@@q52@@</q>，君草的名分就此坐实。</p>

  <div style="margin-top:54px">
    <h3 style="font-weight:normal;font-size:15px;letter-spacing:.3em;color:var(--dim);margin:0 0 4px">白芷一名四变</h3>
    <q class="qq" style="font-size:14px">@@q29@@</q>
    <div class="names">
      <button class="nm on" data-k="zhi">芷</button>
      <button class="nm" data-k="fang">芳</button>
      <button class="nm" data-k="chai">茝</button>
      <button class="nm" data-k="yao">药</button>
    </div>
    <div class="zp">
      <div class="pane show" data-p="zhi"><q>@@q36@@</q><p class="note" style="margin:6px 0 0">起手第一句，扈江离配辟芷，以被服众善自喻。</p></div>
      <div class="pane" data-p="fang"><q>@@q35@@</q><p class="note" style="margin:6px 0 0">浴兰沐芳，连沐浴都用它。</p></div>
      <div class="pane" data-p="chai"><q>@@q37@@</q><p class="note" style="margin:6px 0 0">岂止纫个蕙茝，声调里的不服气。</p></div>
      <div class="pane" data-p="yao"><q>@@q38@@</q><p class="note" style="margin:6px 0 0">辛夷做门楣，白芷当房间，香到建筑上。</p></div>
    </div>
  </div>

  <div style="margin-top:54px">
    <h3 style="font-weight:normal;font-size:15px;letter-spacing:.3em;color:var(--dim);margin:0 0 4px">兰蕙之别 · 一干几花</h3>
    <q class="qq big">@@q13@@</q>
    <p class="note">黄庭坚立的这条标准沿用至今；他还说 <q>@@q12@@</q>，替屈原的 九畹兰、百亩蕙 算出兰贵蕙贱。仁杰补了地亩账：畹三十亩、畦五十亩，兰田合计二百七十亩，蕙才百亩，贵的不嫌多，贱的何必多。又录山谷句 <q>@@q39@@</q>，抄在书里，像抄给自己的座右铭。</p>
    <p class="note">另有女萝菟丝一案：古诗 <q>@@q34@@</q>，尔雅、本草、《神农本草经》各执一词，一物五名千年缠讼，吴仁杰判决：松上者为真女萝，附草而生的是菟丝，两物也。顺带记下橘的倔强：<q>@@q24@@</q>，<q>@@q25@@</q>；建安果农早在冬天给橘树裹衣防冻，来年春夏果子青黑转味绝美：<q>@@q27@@</q>，千年前的反季栽培记录。</p>
  </div>
</section>

<section class="xu" id="xu">
  <div class="wrap">
    <h2>后序 · 自道</h2>
    <div class="xgrid">
      <div class="vrow">
        <q class="vq">@@q5@@</q>
        <q class="vq">@@q4@@</q>
      </div>
      <div>
        <p><q>@@q50@@</q>。他自陈不是爱它文辞漂亮：屈原竭忠尽节的样子写进了草木，他每次正一正衣冠，都像当面见到了那个人。</p>
        <p>于是他做了一件前人没做过的事：<q>@@q6@@</q>。芳草与嘉木一经屈原品题，就该有传记；恶草也得有名有姓地钉在卷末。全书体例被他一语道破：</p>
        <q class="qq">@@q1@@</q>
        <q class="qq">@@q2@@</q>
        <div class="cou">
          <q class="cl">@@q3a@@</q>
          <q class="cl">@@q3b@@</q>
          <span class="cseal">品芳</span>
        </div>
        <p>这话是对着当年的士人说的。落款 <q>@@q46@@</q>，自署通直郎、国子录，河南人吴仁杰：庆元党禁正炽的年头，一部忠奸之辨的草木书。他不点名地替屈原挡了两支冷箭：班固讥屈原怨怼，他答 <q>@@q7@@</q>；刘勰笑鸩鸟为媒迂怪，他搬出《山海经》说鸩有二种，骚人的怪语皆有出处，不过 <q>@@q51@@</q> 的功夫做到底。</p>
      </div>
    </div>
  </div>
</section>

<section class="sec wrap" id="ke">
  <h2>刊刻行旅 · 四站</h2>
  <p class="lead">从罗田县学的书版到四库馆的影宋钞，这册小书走了六百多年。</p>
  <div class="tl">
    <div class="st">
      <span class="yr mono">庆元丁巳 · 1197</span>
      <h4>书成自序</h4>
      <p>四月三日自序于卷末，署衔国子录，自陈少喜离骚、老而手之不辍。</p>
      <q>@@q46@@</q>
    </div>
    <div class="st">
      <span class="yr mono">庆元庚申 · 1220</span>
      <h4>罗田刊版</h4>
      <p>中秋，河南方灿作跋，把这册书刻进罗田县学的学宫，供后进取径。</p>
      <q>@@q47@@</q>
    </div>
    <div class="st">
      <span class="yr mono">宋元明 · 数百年</span>
      <h4>旧板散佚</h4>
      <p>县学书版不寿，全书靠一部影写宋钞流传，海内孤本一线。</p>
      <q>@@q49@@</q>
    </div>
    <div class="st">
      <span class="yr mono">清乾隆间 · 1781</span>
      <h4>入四库</h4>
      <p>二月，馆臣提要：既赞其富，又嫌其执，两句话都留在了卷首。</p>
      <q>@@q31@@</q>
      <q>@@q32@@</q>
    </div>
  </div>
  <p class="note" style="margin-top:26px">馆臣那句「好奇之过」并非全然苛责：把草木都推给大荒之外，确乎淹没了泽畔行吟的哀怨；但正是这份 <q>@@q45@@</q> 的执拗，替后世留住了一份南宋人的博物账本。另记两处存照：提要说他疏二十五篇，后序又自云二十篇，两数自相龃龉；后序落款作「丁已」，当为「丁巳」，库本如此，照录不改。</p>
</section>

<footer>
  <div class="wrap">
    文本来源：殆知阁简体库〈离骚草木疏〉（诗藏 · 楚辞），仓库：<a href="https://github.com/robertsong/daizhige" target="_blank" rel="noopener">daizhige-daodu</a>。<br>
    引文均经脚本自库本切片、去标点归一逐字比对；白话部分经六字窗反扫核验。库本异体字（呉巻髙扵隠歴等）照录或归一存照。<br>
    本页为古籍导读：香草美人、忠奸二元是那个时代的语言；毒鱼、毒人诸方记载仅作文献存录，切勿效仿；兰花水致吐利等说法属古人见闻，无科学依据。
  </div>
</footer>

<script>
(function(){
  var rf=document.getElementById('rf'),re=document.getElementById('re');
  requestAnimationFrame(function(){requestAnimationFrame(function(){
    rf.style.width=(44/55*100)+'%';re.style.width=(11/55*100)+'%';});});
  function go(id,focusEvil){
    return function(){document.getElementById('qiang').scrollIntoView();
      if(focusEvil){var j=document.getElementById('eviljuan');j.classList.add('flash');
        setTimeout(function(){j.classList.remove('flash');},1600);}};
  }
  document.getElementById('doorfang').addEventListener('click',go('qiang',false));
  document.getElementById('doorevil').addEventListener('click',go('qiang',true));
  var note=document.getElementById('chipnote');
  document.querySelectorAll('.chip').forEach(function(c){
    function show(){var n=c.querySelector('q').textContent;
      note.innerHTML='<b>'+n+'</b> · '+c.getAttribute('data-t');}
    c.addEventListener('mouseenter',show);c.addEventListener('focus',show);
  });
  var nms=document.querySelectorAll('.nm'),panes=document.querySelectorAll('.zp .pane');
  nms.forEach(function(n){n.addEventListener('click',function(){
    nms.forEach(function(m){m.classList.remove('on');});n.classList.add('on');
    var k=n.getAttribute('data-k');
    panes.forEach(function(p){p.classList.toggle('show',p.getAttribute('data-p')===k);});});});
})();
</script>
</body>
</html>
"""

out = HTML
for k, v in Q.items():
    out = out.replace("@@%s@@" % k, v)
out = out.replace("@@C1@@", C1).replace("@@C2@@", C2).replace("@@C3@@", C3).replace("@@C4@@", C4)
assert "@@" not in out, "unresolved token"
assert "—" not in out and "–" not in out, "long dash"
io.open(OUT, "w", encoding="utf-8").write(out)
print("built", OUT, len(out), "bytes,", text and len([1 for _ in CHIPS]), "juan groups")
