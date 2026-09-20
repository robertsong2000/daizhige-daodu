#!/usr/bin/env python3
"""贫士传导读页构建：引文逐条 assert 在库本原文中，生僻字以□存照。"""
import re, sys

LIB = "/home/robertsong/workspace/claude/daizhige-simplified/史藏/传记/贫士传.txt"
OUT = "/home/robertsong/workspace/claude/daizhige-daodu/pinshizhuan.html"

raw = open(LIB, encoding="utf-8").read()
lib = re.sub(r"[ \t　]+", "", raw)

def safe(s):
    """ext-A 与 ext-B+ 僻字以□存照"""
    out = []
    for c in s:
        o = ord(c)
        out.append("□" if (0x3400 <= o <= 0x4DBF or o >= 0x20000) else c)
    return "".join(out)

# ---- 条目与赞 ----
ents = []
for l in lib.split("\n"):
    l = l.strip()
    m = re.match(r"^([^\s：]{2,10})：(.+)$", l)
    if m and not l.startswith("贫士传"):
        ents.append((m.group(1), m.group(2)))
assert len(ents) == 70, len(ents)
zans = []
for n, b in ents:
    assert "/" in b, n
    z = b.split("/")[-1]
    zans.append((n, z))

# ---- 引文（手打，必须逐字在库本） ----
QU = {
"d1": "吾子皮相之士何足语姓字也",
"d2": "捉衿而肘见纳履而踵决",
"d3": "斜而有余不如正而不足也",
"d4": "闵仲叔岂以口腹累安邑耶",
"d5": "吾农家安知吕处士",
"y1": "马迁之纪货殖但刺淫奢扬雄之赋逐贫未融嗟抑",
"y2": "癸巳之春青阳卧疾乃就榻上徐为编摩姬周迄今凡得七十五人列为二卷",
"y3": "使天下皆贫士之心焉则揖让成而雍皞登矣讵可易视之哉",
"b0": "回尝箪食瓢饮处于陋巷人不堪其忧回也不改其乐孔子贤之",
"b1": "宪居以环堵茨以生草蓬户不完桑木为枢而瓮牖二室褐以为塞上漏下湿匡坐而弦歌",
"b2": "先生病矣",
"b3": "宪闻无财之谓贫学道不能之谓病若宪贫也非病也",
"b4": "子贡逡巡而退有愧色",
"m1": "吾五月披裘而负薪岂取遗金者哉季子知其为贤者请问姓字公曰吾子皮相之士何足语姓字也",
"m2a": "我东海之波臣也君岂有斗升之水活我哉",
"m2b": "君乃言此曾不如早索我于枯鱼之肆",
"m3a": "予惟不食嗟来之食以至于斯也从而谢焉终不食而死",
"m3b": "其嗟也可去其谢也可食",
"m4a": "吾欲省烦耳今更作烦耶受而弗食",
"m4b": "仲叔怪问知之乃叹曰闵仲叔岂以口腹累安邑耶遂去客沛以寿终",
"m5a": "覆头则足见覆足则头见",
"m5b": "甘天下之澹味安天下之卑位不戚戚于贫贱不欣欣于富贵求仁得仁求义得义其斯可谥为康也已",
"m6a": "徽之哂焉乃出侮之徽之口占以答无不精美",
"m6b": "不义之货我何庸取",
"m6c": "忽米桶内有人乃徽之妻也以天寒无衣坐为障耳",
"m7": "吾思僧不易为生龟脱筒亦难堪忍祠部已付酒家偿负矣",
"h1": "储儋石而一磬悬学贯天人御三冬而四壁立岂但执瓢之回悬鹑之宪而已乎",
"h2": "食力者先民处世之务求己者元圣训人之方",
"c1": "贫者士之常也",
"c2": "死者命之终也",
"c3": "居常待终当何忧乎",
"c4": "或皆不免于襁褓而吾行年九十矣是三乐也",
}
for k, v in QU.items():
    assert v in lib, f"quote {k} 不在库本: {v[:20]}"

# ---- 赞墙 ----
chips_up, chips_dn, qbank = [], [], []
dn = False
for i, (n, z) in enumerate(zans):
    if n == "扈累":
        dn = True
    tag = ""
    if n in ("仲尼三弟子", "春秋三子"): tag = "·三人"
    elif n in ("徐氏父子", "吴蔡二隐"): tag = "·二人"
    itag = "<i>" + tag + "</i>" if tag else ""
    chip = '<button class="chip" data-i="' + str(i) + '" type="button">' + safe(n) + itag + "</button>"
    (chips_up if not dn else chips_dn).append(chip)
    qbank.append('<q class="bk" id="bk' + str(i) + '">' + safe(z) + "</q>")

def q(k):
    return f"<q>{QU[k]}</q>"

T = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>贫士传 · 殆知阁导读</title>
<style>
:root{
  --ink:#191917; --ink2:#141413; --paper:#e8e4dc; --paper2:#dfdacd;
  --gold:#c9963f; --gold2:#8a6a33; --dim:#8f8a7f; --warm:#f4d9a6;
}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{background:var(--ink);color:var(--paper);font-family:"Songti SC","STSong","NSimSun","SimSun",serif;line-height:1.75;overflow-x:hidden}
.mono{font-family:ui-monospace,Menlo,Consolas,monospace}
q{quotes:none}
a{color:inherit}
.fp{opacity:0;transform:translateY(22px);transition:opacity .7s ease,transform .7s ease}
.fp.on{opacity:1;transform:none}
section{position:relative}
.wrap{max-width:1080px;margin:0 auto;padding:0 22px}

/* ---------- hero 蓬户巷 ---------- */
#hero{min-height:100vh;display:flex;flex-direction:column;overflow:hidden}
#hero .top{display:flex;justify-content:space-between;align-items:flex-start;padding:20px 26px 0}
.vseal{background:var(--gold);color:#1c150a;font-size:13px;letter-spacing:2px;padding:7px 10px;border-radius:3px;font-weight:700}
.kick{color:var(--dim);font-size:13px;letter-spacing:3px}
#hero .main{flex:1;display:flex;justify-content:flex-end;padding:12px 6vw 0 0}
.hgroup{writing-mode:vertical-rl;text-orientation:upright;height:min(52vh,430px)}
.hgroup h1{font-size:min(15vw,96px);font-weight:700;letter-spacing:.12em;color:var(--paper);line-height:1}
.hgroup h1 b{color:var(--gold)}
.hgroup .vs{display:inline-block;color:var(--dim);font-size:14px;letter-spacing:.35em;border-right:1px solid #333;padding-right:14px;margin-top:6px}
.moon{position:absolute;top:9vh;right:37vw;width:74px;height:74px;border-radius:50%;
  background:radial-gradient(circle at 38% 34%,#efe9da,#b8b2a2 70%);opacity:.32;filter:blur(1px)}
.hint{color:var(--gold);font-size:13px;letter-spacing:2px;text-align:center;padding-bottom:6px}
/* 巷 */
.lane{position:relative;height:350px;perspective:900px;
  background:linear-gradient(#191917 0%,#1c1b19 78%,#22201c 79%,#191917 100%)}
.lane:before{content:"";position:absolute;left:0;right:0;bottom:0;height:64px;
  border-top:1px solid #3a352c;background:linear-gradient(#211f1b,#191917)}
.snow{position:absolute;inset:0;pointer-events:none;opacity:.5;
  background-image:radial-gradient(1.6px 1.6px at 20px 30px,#e8e4dc 45%,transparent 50%),
  radial-gradient(1.2px 1.2px at 120px 90px,#e8e4dc 45%,transparent 50%),
  radial-gradient(1.4px 1.4px at 210px 50px,#e8e4dc 45%,transparent 50%),
  radial-gradient(1px 1px at 300px 120px,#e8e4dc 45%,transparent 50%);
  background-size:340px 170px;animation:snowfall 14s linear infinite}
@keyframes snowfall{from{background-position:0 0}to{background-position:0 170px}}
.laneflex{position:absolute;inset:0;display:flex;justify-content:center;align-items:flex-end;gap:4.5vw;padding-bottom:64px}
.door{position:relative;width:104px;height:210px;background:none;border:none;cursor:pointer;font-family:inherit;color:inherit}
.door:nth-child(2){height:186px;width:96px}
.door:nth-child(3){height:224px;width:112px}
.door:nth-child(4){height:176px;width:92px}
.door:nth-child(5){height:198px;width:100px}
.door .frame{position:absolute;inset:0;border:1px solid #4a4438;border-bottom:none;background:#201e1a;
  box-shadow:inset 0 -30px 50px #000}
.door .leaf{position:absolute;inset:4px;z-index:3;transform-origin:left center;transition:transform .8s cubic-bezier(.6,0,.3,1);
  background:repeating-linear-gradient(90deg,#2b2822 0 24px,#26241f 24px 26px);border:1px solid #4a4438}
.door .leaf b{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);writing-mode:vertical-rl;
  text-orientation:upright;letter-spacing:8px;font-size:14px;color:var(--gold2);font-weight:400}
.door .knob{position:absolute;right:12px;top:52%;width:7px;height:7px;border-radius:50%;background:#5a5244}
.door .room{position:absolute;inset:4px;z-index:2;display:flex;align-items:center;justify-content:center;
  background:radial-gradient(ellipse at 50% 72%,#3d3428,#1c1a16 75%);opacity:0;transition:opacity .8s}
.door .slip{position:absolute;bottom:calc(100% + 14px);left:50%;transform:translateX(-50%) translateY(8px);
  width:230px;background:var(--paper);color:#26241f;padding:12px 14px 10px;font-size:13.5px;line-height:1.8;
  opacity:0;pointer-events:none;transition:opacity .5s,transform .5s;box-shadow:0 8px 24px #000a;text-align:left}
.door .slip:after{content:"";position:absolute;top:-7px;left:50%;transform:translateX(-50%) rotate(45deg);width:12px;height:12px;background:var(--paper)}
.door .slip i{display:block;font-style:normal;color:var(--gold2);font-size:12px;letter-spacing:2px;margin-top:4px}
.door.open .leaf{transform:rotateY(-76deg)}
.door.open .room{opacity:1}
.door.open .slip{opacity:1;transform:translateX(-50%) translateY(0)}
.door.open .leaf b{opacity:0}
.plac{position:absolute;top:calc(100% + 12px);left:50%;transform:translateX(-50%);font-size:12.5px;color:var(--dim);letter-spacing:3px;white-space:nowrap}

/* ---------- 通用段头 ---------- */
.shead{display:flex;align-items:baseline;gap:16px;margin-bottom:8px}
.shead .no{color:var(--gold);font-size:13px;letter-spacing:3px;white-space:nowrap}
.shead h2{font-size:clamp(22px,3.4vw,30px);font-weight:700;letter-spacing:2px}
.slead{color:#b9b3a6;max-width:720px;font-size:15px;margin-bottom:26px}
.pq{background:var(--paper);color:#28251f;padding:20px 24px;font-size:16px;line-height:2;border-radius:2px;position:relative}
.pq:before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--gold)}
.pq small{display:block;color:var(--gold2);font-size:12px;letter-spacing:2px;margin-top:8px}
.note{color:#a09a8d;font-size:13.5px;margin-top:10px}

/* ---------- 榻上三问 ---------- */
#yuan{padding:96px 0 90px}
.qa{border-top:1px solid #2c2a25;padding:26px 0;cursor:pointer}
.qa:last-child{border-bottom:1px solid #2c2a25}
.qa .qm{display:flex;align-items:baseline;gap:14px}
.qa .qm b{color:var(--gold);font-size:19px;font-weight:700;letter-spacing:1px}
.qa .qm span{color:var(--dim);font-size:13px;letter-spacing:2px}
.qa .ans{max-height:0;overflow:hidden;transition:max-height .7s ease}
.qa.open .ans{max-height:420px}
.qa.open .qm b{color:var(--paper)}
.qa .ans .pq{margin:18px 0 0 0}
.qa .plus{float:right;color:var(--gold);font-size:18px;transition:transform .4s}
.qa.open .plus{transform:rotate(45deg)}

/* ---------- 贫病之辨 ---------- */
#bian{background:var(--ink2);border-top:1px solid #26241f;border-bottom:1px solid #26241f;padding:96px 0}
#bian .duo{display:grid;grid-template-columns:1fr 1fr;gap:26px;margin:34px 0}
.card{background:#1e1c18;border:1px solid #35322a;border-radius:3px;padding:22px}
.card h3{color:var(--gold);font-size:15px;letter-spacing:3px;margin-bottom:12px}
.stagebox{position:relative;height:190px;margin:10px 0 6px}
/* 子贡车马 */
.zig .cart{position:absolute;left:12%;bottom:26px;width:120px;height:46px;border:2px solid var(--gold);border-radius:4px;
  transition:transform 1s ease;box-shadow:0 10px 18px #0008}
.zig .cart:before,.zig .cart:after{content:"";position:absolute;bottom:-14px;width:26px;height:26px;border-radius:50%;
  border:2px solid #6b6350;background:#191917}
.zig .cart:before{left:10px}
.zig .cart:after{right:10px}
.zig .canopy{position:absolute;left:calc(12% + 26px);bottom:70px;width:0;height:0;border-left:34px solid transparent;border-right:34px solid transparent;border-bottom:26px solid var(--gold2)}
.zig.retreat .cart{transform:translateX(-120px) rotate(-4deg);opacity:.35}
/* 原宪环堵 */
.yx .hut{position:absolute;right:14%;bottom:26px;width:130px;height:96px}
.yx .roof{position:absolute;top:0;left:-8px;right:-8px;height:40px;clip-path:polygon(50% 0,100% 100%,0 100%);background:repeating-linear-gradient(90deg,#3a362c 0 7px,#2e2b22 7px 9px)}
.yx .body{position:absolute;top:40px;left:8px;right:8px;bottom:0;border:2px solid #4a4438;border-top:none}
.yx .body:before{content:"";position:absolute;left:50%;top:0;width:22px;height:52px;transform:translateX(-50%);border:1px dashed #55503f;border-top:none}
.yx .qin{position:absolute;right:-34px;bottom:8px;width:44px;height:12px;border:1px solid var(--gold2);border-radius:6px}
.yx .drip i{position:absolute;width:2px;height:8px;background:#5e7c8a;animation:drip 1.6s linear infinite}
.yx .drip i:nth-child(1){left:24px;top:46px}
.yx .drip i:nth-child(2){left:96px;top:46px;animation-delay:.8s}
@keyframes drip{0%{opacity:0;transform:translateY(0)}30%{opacity:1}100%{opacity:0;transform:translateY(26px)}}
.steplabel{min-height:52px;color:#cfc9bc;font-size:15px}
#bian .flow{margin-top:8px}
.bstep{display:none;margin-top:14px}
.bstep.show{display:block;animation:fadeup .6s ease}
@keyframes fadeup{from{opacity:0;transform:translateY(12px)}to{opacity:1}}
#zgo{background:none;border:1px solid var(--gold);color:var(--gold);padding:9px 22px;font-size:14px;letter-spacing:3px;cursor:pointer;font-family:inherit;border-radius:2px}
#zgo:hover{background:var(--gold);color:#1c150a}
.bigq{font-size:clamp(17px,2.4vw,21px);line-height:2.1}

/* ---------- 七幕 ---------- */
#mu{padding:96px 0}
.rail{display:flex;align-items:flex-start;gap:22px;overflow-x:auto;scroll-snap-type:x mandatory;padding:8px 22px 26px;-webkit-overflow-scrolling:touch}
.ms{flex:0 0 min(400px,84vw);scroll-snap-align:center;background:#1e1c18;border:1px solid #35322a;border-radius:3px;
  padding:20px 22px;cursor:pointer;user-select:none}
.ms .mt{display:flex;justify-content:space-between;align-items:baseline;border-bottom:1px solid #2c2a25;padding-bottom:10px;margin-bottom:8px}
.ms .mt b{font-size:16.5px;letter-spacing:2px}
.ms .mt span{color:var(--dim);font-size:12px;letter-spacing:2px}
.ms .box{position:relative;height:150px;margin:6px 0}
.ms .ph{opacity:0;transform:translateY(10px);transition:opacity .55s,transform .55s}
.ms[data-step="1"] .p1,.ms[data-step="2"] .p1,.ms[data-step="2"] .p2,.ms[data-step="3"] .p1,.ms[data-step="3"] .p2,.ms[data-step="3"] .p3{opacity:1;transform:none}
.ms .ph .pq{padding:12px 14px;font-size:13.8px;line-height:1.9}
.ms .ph .pq:before{width:3px}
.ms .cap{color:#a09a8d;font-size:13px;min-height:44px}
.ms .ph .cap{margin-top:8px;color:#b9b3a6}
.ms .tip{position:absolute;right:0;top:2px;color:#5f5a4e;font-size:12px;letter-spacing:2px}
/* 场景小件 */
.road{position:absolute;left:0;right:0;bottom:22px;height:3px;background:#3a352c}
.nug{position:absolute;left:34%;bottom:26px;width:26px;height:18px;border-radius:45% 55% 50% 50%;background:radial-gradient(circle at 35% 30%,#f0d79a,var(--gold) 75%);transition:transform .8s,opacity .8s;box-shadow:0 0 14px #c9963f55}
.ms[data-step="1"] .nug{transform:translate(60px,-8px) scale(.5);opacity:0}
.wood{position:absolute;right:16%;bottom:26px;width:20px;height:56px;background:repeating-linear-gradient(#4a4032 0 4px,#3a3226 4px 6px);border-radius:2px}
.rut{position:absolute;left:8%;right:8%;bottom:30px;height:16px;border-bottom:2px solid #3f3a30;border-top:2px solid #3f3a30;border-radius:50%}
.fsh{position:absolute;left:44%;bottom:32px;width:44px;height:20px;background:#5e7c8a;border-radius:60% 40% 50% 50%/60% 60% 40% 40%;transition:transform .5s}
.fsh:before{content:"";position:absolute;right:-12px;top:2px;border-left:14px solid #5e7c8a;border-top:8px solid transparent;border-bottom:8px solid transparent}
.fsh:after{content:"";position:absolute;left:8px;top:5px;width:5px;height:5px;border-radius:50%;background:#191917}
.ms[data-step="2"] .fsh{transform:translateX(-26px) rotate(-8deg)}
.bowl{position:absolute;left:42%;bottom:30px;width:52px;height:24px;background:#3d3930;border-radius:0 0 26px 26px;border-top:3px solid var(--gold2)}
.bowl:before{content:"";position:absolute;left:50%;top:-12px;transform:translateX(-50%);width:18px;height:10px;border-radius:50%;background:#4a4438}
.garlic{position:absolute;left:16%;bottom:28px;width:22px;height:24px;background:#cfc5ae;border-radius:50% 50% 40% 40%}
.liver{position:absolute;right:18%;bottom:28px;width:34px;height:20px;background:#7a3f38;border-radius:60% 40% 55% 45%/60% 55% 45% 40%}
.quilt{position:absolute;left:50%;bottom:34px;transform:translateX(-50%);width:88px;height:34px;background:repeating-linear-gradient(90deg,#4f4a3d 0 12px,#453f33 12px 14px);border-radius:6px;transition:transform .6s}
.fig{position:absolute;left:50%;bottom:34px;transform:translateX(-50%);width:36px;height:52px}
.fig:before{content:"";position:absolute;top:-20px;left:50%;transform:translateX(-50%);width:20px;height:20px;border-radius:50%;background:#5a5546}
.fig:after{content:"";position:absolute;inset:0;background:#514c3f;border-radius:10px 10px 4px 4px}
.ms[data-step="1"] .quilt{transform:translateX(-50%) translateY(-6px)}
.ms[data-step="2"] .quilt{transform:translateX(-50%) translateY(-14px)}
.snowg{position:absolute;inset:0;background-image:radial-gradient(1.4px 1.4px at 30px 20px,#e8e4dc44 45%,transparent 50%),radial-gradient(1.2px 1.2px at 90px 60px,#e8e4dc44 45%,transparent 50%);background-size:120px 90px}
.hdoor{position:absolute;left:34%;bottom:26px;width:44px;height:74px;border:2px solid #4a4438;border-bottom:none}
.hdoor:before{content:"";position:absolute;inset:3px;background:#26241f}
.bucket{position:absolute;right:22%;bottom:26px;width:34px;height:30px;border:2px solid #4a4438;border-top:none;border-radius:0 0 8px 8px}
.ms[data-step="3"] .bucket{border-color:var(--gold2)}
.stepper-hint:after{content:"点卡推进";color:#5f5a4e;font-size:11.5px;letter-spacing:2px;position:absolute;right:0;bottom:-2px}

/* ---------- 贫士谱 ---------- */
#pu{background:var(--ink2);border-top:1px solid #26241f;padding:90px 0 96px}
.rdr{display:flex;align-items:baseline;gap:14px;background:#1a1916;border:1px dashed #454033;border-radius:3px;padding:16px 20px;min-height:96px;margin:26px 0}
.rdr b{color:var(--gold);letter-spacing:3px;white-space:nowrap;font-size:15px}
.rdr q{font-size:15.5px;line-height:2;color:var(--paper)}
.rdr q span{display:inline-block;margin:0 6px 4px 0;letter-spacing:2px}
.wall{display:flex;flex-wrap:wrap;gap:9px;margin-bottom:26px}
.wname{color:var(--gold);font-size:13px;letter-spacing:3px;margin:22px 0 12px;border-left:3px solid var(--gold);padding-left:10px}
.chip{background:#23211c;border:1px solid #38342a;color:#cfc9bc;font-family:inherit;font-size:14px;padding:6px 13px;border-radius:2px;cursor:pointer;letter-spacing:1px;transition:all .25s}
.chip:hover{border-color:var(--gold);color:var(--paper)}
.chip.act{background:var(--gold);color:#1c150a;border-color:var(--gold)}
.chip i{font-style:normal;color:var(--gold2);font-size:11px;margin-left:2px}
.chip.act i{color:#1c150a}
.qbank{position:absolute;left:-9999px;top:0;visibility:hidden}

/* ---------- 后序 ---------- */
#hou{padding:100px 0}
.acct{max-width:640px;margin:30px auto 0;background:var(--paper);color:#28251f;padding:34px 36px 30px;transform:rotate(-1.2deg);
  box-shadow:0 16px 40px #0009;position:relative}
.acct:before{content:"";position:absolute;top:14px;left:0;right:0;height:10px;
  background:radial-gradient(circle 4px at 20px 5px,var(--ink) 98%,transparent),radial-gradient(circle 4px at 80px 5px,var(--ink) 98%,transparent),
  radial-gradient(circle 4px at 140px 5px,var(--ink) 98%,transparent),radial-gradient(circle 4px at 200px 5px,var(--ink) 98%,transparent),
  radial-gradient(circle 4px at 260px 5px,var(--ink) 98%,transparent),radial-gradient(circle 4px at 320px 5px,var(--ink) 98%,transparent),
  radial-gradient(circle 4px at 380px 5px,var(--ink) 98%,transparent),radial-gradient(circle 4px at 440px 5px,var(--ink) 98%,transparent)}
.acct .ah{color:var(--gold2);font-size:12px;letter-spacing:3px;margin-bottom:14px}
.acct q{font-size:16.5px;line-height:2.15;display:block}
.acct .verdict{margin-top:16px;padding-top:12px;border-top:1px dashed #b7b0a0;font-size:14px;color:#5c564a}
.acct .red{position:absolute;right:-14px;top:46%;background:#a5402f;color:#f4ede0;font-size:12.5px;letter-spacing:3px;padding:9px 8px;writing-mode:vertical-rl;border-radius:2px;transform:rotate(2deg)}

/* ---------- 尾屏 ---------- */
#coda{min-height:78vh;display:flex;align-items:center;justify-content:center;padding:80px 0}
.codaflex{display:flex;align-items:center;gap:9vw;flex-wrap:wrap;justify-content:center}
.vq3{writing-mode:vertical-rl;text-orientation:upright;height:min(46vh,360px)}
.vq3 .col{display:inline-block;font-size:clamp(19px,3vw,27px);letter-spacing:.35em;color:var(--paper);line-height:1;margin-left:30px}
.vq3 .col small{display:block;font-size:12px;color:var(--dim);letter-spacing:4px;margin-top:14px}
.seal4{writing-mode:vertical-rl;text-orientation:upright;background:#a5402f;color:#f2e7d4;font-size:19px;letter-spacing:7px;
  padding:15px 9px;border-radius:3px;box-shadow:0 6px 18px #0007;transform:rotate(2deg)}
.coda-side{max-width:340px;color:#a8a295;font-size:14.5px}
.coda-side .pq{margin:14px 0;padding:14px 16px;font-size:14px}

/* ---------- 页脚 ---------- */
footer{border-top:1px solid #2c2a25;padding:34px 0 46px;color:#7d786d;font-size:12.8px;line-height:2}
footer a{color:#a3834b;text-decoration:none}

@media (max-width:760px){
  #hero .main{justify-content:center;padding:26px 0 34px;flex:none}
  .hgroup{height:auto;writing-mode:horizontal-tb;text-orientation:mixed;flex-direction:column;align-items:center;gap:6px;text-align:center}
  .hgroup h1{font-size:52px;letter-spacing:.18em}
  .hgroup .vs{border-right:none;border-bottom:1px solid #333;padding:0 0 8px;letter-spacing:.3em}
  .moon{right:8vw;top:6vh;width:52px;height:52px}
  .lane{height:300px}
  .laneflex{gap:3vw;padding-bottom:58px}
  .door{width:64px!important;height:130px!important}
  .door .slip{width:172px;font-size:12px}
  .door .leaf b{font-size:11px;letter-spacing:3px}
  .plac{font-size:10.5px;letter-spacing:1px}
  #bian .duo{grid-template-columns:1fr}
  .rail{padding:8px 14px 22px}
  .acct{padding:26px 20px 22px}
  .codaflex{gap:40px}
  .vq3{height:300px;gap:16px}
}
</style>
</head>
<body>

<!-- 首屏 蓬户巷 -->
<section id="hero">
  <div class="top">
    <span class="vseal">肆百贰拾肆</span>
    <span class="kick">明 ｜ 黄姬水 ｜ 清贫类传</span>
  </div>
  <i class="moon" aria-hidden="true"></i>
  <div class="main">
    <div class="hgroup">
      <h1>贫<b>士</b>传</h1>
      <div class="vs">一条住着穷读书人的巷子</div>
    </div>
  </div>
  <p class="hint">巷上有五扇门，点开门里的人</p>
  <div class="lane">
    <i class="snow" aria-hidden="true"></i>
    <div class="laneflex">
      <button class="door fp" type="button">
        <span class="slip"><q>@Qd1@</q><i>披裘公 · 春秋</i></span>
        <span class="room"></span><span class="frame"></span>
        <span class="leaf"><b>负薪</b><span class="knob"></span></span>
        <span class="plac">披裘公</span>
      </button>
      <button class="door fp" type="button">
        <span class="slip"><q>@Qd2@</q><i>原宪 · 孔门</i></span>
        <span class="room"></span><span class="frame"></span>
        <span class="leaf"><b>弦歌</b><span class="knob"></span></span>
        <span class="plac">原宪</span>
      </button>
      <button class="door fp" type="button">
        <span class="slip"><q>@Qd3@</q><i>黔娄妻 · 春秋</i></span>
        <span class="room"></span><span class="frame"></span>
        <span class="leaf"><b>正被</b><span class="knob"></span></span>
        <span class="plac">黔娄先生</span>
      </button>
      <button class="door fp" type="button">
        <span class="slip"><q>@Qd4@</q><i>闵贡 · 东汉</i></span>
        <span class="room"></span><span class="frame"></span>
        <span class="leaf"><b>辞肝</b><span class="knob"></span></span>
        <span class="plac">闵贡</span>
      </button>
      <button class="door fp" type="button">
        <span class="slip"><q>@Qd5@</q><i>吕徽之 · 宋末</i></span>
        <span class="room"></span><span class="frame"></span>
        <span class="leaf"><b>桶雪</b><span class="knob"></span></span>
        <span class="plac">吕徽之</span>
      </button>
    </div>
  </div>
</section>

<!-- 榻上三问 -->
<section id="yuan">
  <div class="wrap">
    <div class="shead fp"><span class="no">卷首 ｜ 缘起</span><h2>榻上三问</h2></div>
    <p class="slead fp">嘉靖十二年（1533）春天，吴郡人黄姬水病在床上。他没写养病的诗，而是动手给自古以来的穷读书人编一本传记。动笔之前，这本书先要过三问。点开每一问。</p>
    <div class="qa fp" type="button">
      <div class="qm"><span class="plus">＋</span><b>一问</b><span>写发财的书很多，为什么偏要写穷的？</span></div>
      <div class="ans">
        <div class="pq"><q>@Qy1@</q><small>库本自序</small></div>
        <p class="note">司马迁给货殖立传，他读出的意思是通篇在刺奢侈；扬雄写过逐贫的赋，也只是自嘲。穷读书人一直没人正经立传，这是他要补的空。</p>
      </div>
    </div>
    <div class="qa fp">
      <div class="qm"><span class="plus">＋</span><b>二问</b><span>这书是怎么写出来的？</span></div>
      <div class="ans">
        <div class="pq"><q>@Qy2@</q><small>库本自序</small></div>
        <p class="note">库本自序只给了一句：春天卧病，就在榻上慢慢编。从周代数到本朝，自序说得了七十五人；今本七十条传目，几条合传折算是七十六人，两个数字就这么并存。</p>
      </div>
    </div>
    <div class="qa fp">
      <div class="qm"><span class="plus">＋</span><b>三问</b><span>给穷人立传，图什么？</span></div>
      <div class="ans">
        <div class="pq"><q>@Qy3@</q><small>库本自序</small></div>
        <p class="note">他把话说得很大：人人存一点贫士之心，天下就太平了。这句与其说是论断，不如说是他给自己这本书壮胆。</p>
      </div>
    </div>
  </div>
</section>

<!-- 贫病之辨 -->
<section id="bian">
  <div class="wrap">
    <div class="shead fp"><span class="no">卷上 ｜ 书眼</span><h2>贫与病，是两件事</h2></div>
    <p class="slead fp">全书的分量压在孔门一节。同门先例是颜回：</p>
    <div class="pq fp" style="max-width:720px"><q>@Qb0@</q><small>仲尼三弟子 · 颜回</small></div>
    <div class="duo">
      <div class="card fp">
        <h3>原宪的房</h3>
        <div class="stagebox yx">
          <div class="hut"><i class="roof"></i><i class="body"></i><i class="qin"></i></div>
          <div class="drip"><i></i><i></i></div>
        </div>
        <div class="pq"><q>@Qb1@</q></div>
        <p class="note">墙是草堆的，门枢是桑木条，窗是一只破瓮。漏着雨，他端坐弹琴。</p>
      </div>
      <div class="card fp">
        <h3>子贡的车</h3>
        <div class="stagebox zig" id="zig">
          <i class="canopy"></i>
          <i class="cart"></i>
        </div>
        <div class="steplabel" id="zlabel">盛服轩车，来看老同学。</div>
        <div class="flow">
          <div class="bstep" id="bs1"><div class="pq"><q>@Qb2@</q><small>子贡曰</small></div><p class="note">一句问候，把穷当成了病。</p></div>
          <div class="bstep" id="bs2"><div class="pq bigq"><q>@Qb3@</q><small>原宪应</small></div><p class="note">没钱叫贫，学不会道才叫病。两个字，他拆得清清楚楚。</p></div>
          <div class="bstep" id="bs3"><div class="pq"><q>@Qb4@</q></div><p class="note">车马很体面地退了出去。</p></div>
        </div>
        <button id="zgo" type="button" style="margin-top:14px">子贡驾到</button>
      </div>
    </div>
  </div>
</section>

<!-- 七幕 -->
<section id="mu">
  <div class="wrap">
    <div class="shead fp"><span class="no">名场面 ｜ 七幕</span><h2>穷法各不相同</h2></div>
    <p class="slead fp">七十条传里挑七段，一段一个穷法。点卡片推进。</p>
  </div>
  <div class="rail">
    <div class="ms fp" data-max="1">
      <div class="mt"><b>第一幕 ｜ 拾金</b><span>披裘公 · 春秋</span></div>
      <div class="box">
        <span class="tip" aria-hidden="true">点卡推进</span>
        <i class="road"></i><i class="nug"></i><i class="wood"></i>
      </div>
      <p class="cap">延陵季子看见路上有金子，喊那个五月披裘打柴的人来拿。</p>
      <div class="ph p1"><div class="pq"><q>@Qm1@</q></div><p class="cap">人家扔下镰刀回敬他一句：你是看脸皮看人的。季子再抬头，人已经不见了。</p></div>
    </div>
    <div class="ms fp" data-max="2">
      <div class="mt"><b>第二幕 ｜ 涸辙</b><span>庄周 · 战国</span></div>
      <div class="box">
        <span class="tip" aria-hidden="true">点卡推进</span>
        <i class="rut"></i><i class="fsh"></i>
      </div>
      <p class="cap">家里断粮，庄子上门借粟。监河侯许了个大愿：等封邑租金一到，借你三百金。</p>
      <div class="ph p1"><div class="pq"><q>@Qm2a@</q></div></div>
      <div class="ph p2"><div class="pq"><q>@Qm2b@</q></div><p class="cap">远水救不了车辙里的鱼。故事讲完，粟没借到，寓言留了下来。</p></div>
    </div>
    <div class="ms fp" data-max="2">
      <div class="mt"><b>第三幕 ｜ 嗟来</b><span>齐饿者 · 战国</span></div>
      <div class="box">
        <span class="tip" aria-hidden="true">点卡推进</span>
        <i class="bowl"></i>
      </div>
      <p class="cap">齐国大饥，黔敖在路边备了饭等人来吃。有人蒙着脸晃晃悠悠走过来，他端着碗喊：喂，来吃。</p>
      <div class="ph p1"><div class="pq"><q>@Qm3a@</q></div></div>
      <div class="ph p2"><div class="pq"><q>@Qm3b@</q></div><p class="cap">曾子补记留了个余地：喊得轻慢，可以走；道了歉，其实可以吃。传主没等到这个余地。</p></div>
    </div>
    <div class="ms fp" data-max="2">
      <div class="mt"><b>第四幕 ｜ 辞肝</b><span>闵贡 · 东汉</span></div>
      <div class="box">
        <span class="tip" aria-hidden="true">点卡推进</span>
        <i class="garlic"></i><i class="liver"></i>
      </div>
      <p class="cap">闵贡旅居安邑，年迈多病，买不起肉，每天只买一片猪肝，有时屠户还不肯卖。县令听说了，吩咐按时供给。</p>
      <div class="ph p1"><div class="pq"><q>@Qm4a@</q></div><p class="cap">老友周党送一头生蒜，说省得天天买菜。他收下，没吃。</p></div>
      <div class="ph p2"><div class="pq"><q>@Qm4b@</q></div><p class="cap">特供一到，他反倒搬了家：不能为口腹连累一座县城。</p></div>
    </div>
    <div class="ms fp" data-max="3">
      <div class="mt"><b>第五幕 ｜ 正被</b><span>黔娄先生 · 春秋</span></div>
      <div class="box">
        <span class="tip" aria-hidden="true">点卡推进</span>
        <i class="fig"></i><i class="quilt"></i>
      </div>
      <p class="cap">黔娄死时被子太短，曾子说，斜过来拉一拉就都盖上了。</p>
      <div class="ph p1"><div class="pq"><q>@Qm5a@</q></div></div>
      <div class="ph p2"><div class="pq"><q>@Qd3@</q></div><p class="cap">妻子一句话定案：斜过来有多余，不如正着不够。</p></div>
      <div class="ph p3"><div class="pq"><q>@Qm5b@</q></div><p class="cap">于是定谥一个康字。曾子叹：这样的人，才有这样的妻子。</p></div>
    </div>
    <div class="ms fp" data-max="3">
      <div class="mt"><b>第六幕 ｜ 桶雪</b><span>吕徽之 · 宋末</span></div>
      <div class="box">
        <span class="tip" aria-hidden="true">点卡推进</span>
        <i class="snowg"></i><i class="hdoor"></i><i class="bucket"></i>
      </div>
      <p class="cap">大雪天，吕徽之到富人家换谷子，门房没人搭理。堂上公子们正凑不齐咏雪的诗。</p>
      <div class="ph p1"><div class="pq"><q>@Qm6a@</q></div><p class="cap">被人轻慢，他随口把诗接完了。</p></div>
      <div class="ph p2"><div class="pq"><q>@Qm6b@</q></div><p class="cap">公子们认出这位就是想见而见不到的吕处士，送谷子赔礼，他不要。</p></div>
      <div class="ph p3"><div class="pq"><q>@Qm6c@</q></div><p class="cap">访客循迹找到他家：草屋四壁，米桶里坐着人，是他妻子，天冷无衣，坐在桶里挡寒。</p></div>
    </div>
    <div class="ms fp" data-max="1">
      <div class="mt"><b>第七幕 ｜ 僧牒</b><span>俞澹 · 北宋</span></div>
      <div class="box">
        <span class="tip" aria-hidden="true">点卡推进</span>
        <i class="stupa" style="position:absolute;left:44%;bottom:30px;width:34px;height:44px;border:2px solid #4a4438;border-radius:3px"></i>
        <i class="stupa2" style="position:absolute;left:49%;bottom:52px;width:12px;height:12px;background:#4a4438;border-radius:50%"></i>
      </div>
      <p class="cap">俞澹穷得没房子，住在山上。王安石欣赏他，出钱给他捐了个僧人度牒，约好日子剃度。</p>
      <div class="ph p1"><div class="pq"><q>@Qm7@</q></div><p class="cap">到了日子人没来。他的解释：当和尚不容易，像活龟脱壳；度牒已经付给酒家抵债了。</p></div>
    </div>
  </div>
</section>

<!-- 贫士谱 -->
<section id="pu">
  <div class="wrap">
    <div class="shead fp"><span class="no">谱牒 ｜ 全目</span><h2>贫士谱</h2></div>
    <p class="slead fp">七十条传目，从春秋的披裘公数到明初的邢量，每人传末系一首四言赞。点名字，读他的赞。带角标的几条是合传，传主不止一人。</p>
    <div class="rdr fp"><b id="rdname">谱 ｜ 待点</b><q id="rdq"></q></div>
    <div class="wname fp">上卷 · 先秦两汉</div>
    <div class="wall">@WALLUP@</div>
    <div class="wname fp">下卷 · 三国至明</div>
    <div class="wall">@WALLDN@</div>
    <div class="qbank">@QBANK@</div>
  </div>
</section>

<!-- 后序 -->
<section id="hou">
  <div class="wrap">
    <div class="shead fp"><span class="no">卷尾 ｜ 后序一勺</span><h2>替穷读书人算总账</h2></div>
    <div class="acct fp">
      <div class="ah">库本后序</div>
      <q>@Qh1@</q>
      <div class="verdict">米没几石，屋里空得像挂着一面磬；学问通天，熬过三个冬天，还是四面白墙。这样的不止颜回和原宪。</div>
      <q style="margin-top:14px;font-size:15px">@Qh2@</q>
      <div class="verdict">后序的落点也不是哭穷：自食其力，凡事求己，是古训里的正路。</div>
      <span class="red">总账</span>
    </div>
  </div>
</section>

<!-- 尾屏 -->
<section id="coda">
  <div class="codaflex">
    <div class="vq3 fp">
      <div class="col"><q>@Qc1@</q></div>
      <div class="col"><q>@Qc2@</q></div>
      <div class="col"><q>@Qc3@</q><small>荣启期</small></div>
    </div>
    <div class="coda-side fp">
      <p>七十六个人，没有谁靠这本书脱了贫；这本书也没打算帮谁脱贫。它只是把一种活法收进档案。底色是荣启期答孔子的那句：</p>
      <div class="pq"><q>@Qc4@</q><small>荣启期 · 三乐</small></div>
      <p>行年九十，披裘带索，鼓琴而歌。贫是他的日常，他没打算讨价还价。</p>
    </div>
    <span class="seal4 fp">居常待终</span>
  </div>
</section>

<footer>
  <div class="wrap">
    文本来源：殆知阁简体库〈贫士传〉（史藏 ｜ 传记），仓库：<a href="https://github.com/robertsong/daizhige" target="_blank" rel="noopener">daizhige-daodu</a>。<br>
    引文均经脚本自库本切片、去标点归一逐字比对；白话部分经六字窗反扫核验。本页为古籍导读。<br>
    校字记：自序称得七十五人，今本七十条传目按合传折算七十六人，两数并存；僻字残字（沈□之□、可□钺我、供□粥、贫□困乏等）页面以方框存照、相关切片避开；披裘条「视之下膑」膑字费解照录不引；披袭公赞「秘名口口」缺字存照；「譔」为「撰」之异体照录。<br>
    时代局限：饿死不食、辞征全节、以贫显德的价值观与妇女坐米桶挡寒的记录都是古代语境，照录不代今论；书中斥富户贪残的立场是明代士人话头，请以今日眼光辨之。
  </div>
</footer>

<script>
(function(){
  var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('on');io.unobserve(e.target);}});},{threshold:.1});
  document.querySelectorAll('.fp').forEach(function(el){io.observe(el);});
  document.querySelectorAll('.door').forEach(function(d){d.addEventListener('click',function(){d.classList.toggle('open');});});
  document.querySelectorAll('.qa').forEach(function(qa){qa.addEventListener('click',function(){qa.classList.toggle('open');});});
  var n=0,btn=document.getElementById('zgo');
  btn.addEventListener('click',function(){
    n++;
    if(n===1){document.getElementById('bs1').classList.add('show');document.getElementById('zlabel').textContent='到了门前，开口第一句。';}
    if(n===2){document.getElementById('bs2').classList.add('show');document.getElementById('zlabel').textContent='这一问，问错了字。';}
    if(n===3){document.getElementById('bs3').classList.add('show');document.getElementById('zig').classList.add('retreat');document.getElementById('zlabel').textContent='车马退出巷口。';btn.textContent='再看一遍';}
    if(n===4){n=0;['bs1','bs2','bs3'].forEach(function(i){document.getElementById(i).classList.remove('show');});document.getElementById('zig').classList.remove('retreat');document.getElementById('zlabel').textContent='盛服轩车，来看老同学。';btn.textContent='子贡驾到';}
  });
  document.querySelectorAll('.ms').forEach(function(c){
    c.addEventListener('click',function(){
      var max=+c.dataset.max||1,cur=+(c.dataset.step||0);
      c.dataset.step=cur>=max?0:cur+1;
    });
    c.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();c.click();}});
  });
  var rdn=document.getElementById('rdname'),rdq=document.getElementById('rdq');
  document.querySelectorAll('.chip').forEach(function(ch){
    ch.addEventListener('click',function(){
      var q=document.getElementById('bk'+ch.dataset.i);
      if(!q){return;}
      document.querySelectorAll('.chip.act').forEach(function(x){x.classList.remove('act');});
      ch.classList.add('act');
      rdn.textContent='赞 ｜ '+ch.textContent;
      rdq.innerHTML='';
      var t=q.textContent,arr=t.match(/.{1,4}/g)||[];
      arr.forEach(function(s){var sp=document.createElement('span');sp.textContent=s;rdq.appendChild(sp);});
    });
  });
})();
</script>
</body>
</html>
"""

for k, v in QU.items():
    T = T.replace("@Q" + k + "@", safe(v))
T = T.replace("@WALLUP@", "".join(chips_up)).replace("@WALLDN@", "".join(chips_dn)).replace("@QBANK@", "".join(qbank))
open(OUT, "w", encoding="utf-8").write(T)
print("written", OUT, len(T), "chars;", len(ents), "entries; q total:", len(QU) + len(qbank))
