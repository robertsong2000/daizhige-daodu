# -*- coding: utf-8 -*-
"""勿庵历算书记 导读页构建（引文切片 + 页面拼装）"""
import re, json, html

SRC = "daizhige-simplified/子藏/算法/勿庵历算书记.txt"
OUT = "daizhige-daodu/wuan-lisuan-shuji.html"
lines = open(SRC).read().split("\n")
FULL = "\n".join(lines)

def slice_q(ln, a, b):
    s = lines[ln-1]
    i = s.find(a)
    assert i >= 0, f"start anchor miss L{ln}: {a[:12]}"
    j = s.find(b, i)
    assert j >= 0, f"end anchor miss L{ln}: {b[:12]}"
    return s[i:j+len(b)]

# ---- 引文切片（程序化，零誊写） ----
Q = {}
Q["q1"]  = slice_q(22, "顺治辛丑", "学歴之志")
Q["q2"]  = slice_q(26, "授时歴集古法之大成", "大率多因古术")
Q["q3"]  = slice_q(26, "不读耶律文正之庚午元歴", "岁实消长")
Q["q4"]  = slice_q(26, "非一行之大衍歴", "天自为天")
Q["q5"]  = slice_q(26, "然非洛下闳谢姓等肇启其端", "无自而生其智矣")
Q["q6"]  = slice_q(43, "余出所携歴草通轨补之", "不易也")
Q["q7"]  = slice_q(79, "先生既门庭若水", "得稿三十余篇")
Q["q8"]  = slice_q(80, "壬午夏安溪公以抚臣扈防行河", "进呈此书钦防")
Q["q9"]  = slice_q(81, "御笔亲加评阅", "恭纪中")
Q["q10"] = slice_q(53, "据史立成之算", "令人起敬也")
Q["q11"] = slice_q(59, "和仲于此事甚勤", "恨仲弟未之见")
Q["q12"] = slice_q(59, "而亦久为古人矣", "而亦久为古人矣")
Q["q13"] = slice_q(63, "回歴即西法之旧率", "有根源")
Q["q14"] = slice_q(65, "书首小序曰", "所能及也")
Q["q15"] = slice_q(173, "算数作于隶首", "中西两家之法")
Q["q16"] = slice_q(173, "各有本末而理实同归", "各有本末而理实同归")
Q["q17"] = slice_q(184, "对数之竒尤在开方", "俄顷可得")
Q["q18"] = slice_q(186, "穆先生曰表有十万", "以法通之")
Q["q19"] = slice_q(194, "九章之第八曰方程", "或已尠矣")
Q["q20"] = slice_q(209, "天学初函内有几何原本六卷", "任此者耳")
Q["q21"] = slice_q(215, "竒技淫巧古人所禁", "民生日用")
Q["q22"] = slice_q(235, "生平得力于友朋之益", "别为一卷")
Q["q23"] = slice_q(237, "今有笔算", "天下习用")
Q["q24"] = slice_q(239, "初学莫易于笔算", "虽童子可知矣")
Q["q25"] = slice_q(129, "自周官有挈壶氏", "明天启间尚存")
Q["q26"] = slice_q(127, "然无以处隂雨之际", "无裨实用")
Q["q27"] = slice_q(127, "以节晨昏", "为用亦大矣")
Q["q28"] = slice_q(125, "在璇玑玉衡以齐七政", "能定歴者也")
Q["q29"] = slice_q(30, "总而计之约有九家", "欧逻巴歴也")
Q["q30"] = slice_q(30, "愚故曰西法原非一种", "知其故矣")
Q["q31"] = slice_q(118, "地既浑圆", "纬度则然")
Q["q32"] = slice_q(29, "通歴书之理而自辟门庭", "后来居上")
Q["q33"] = slice_q(49, "有西域人与耶律文正王", "作歴托始是年也")
Q["q34"] = slice_q(49, "故推演上元庚午冬至朔旦七曜齐元", "谓之西征庚午元歴")
Q["q35"] = slice_q(39, "大意言明用大统实即授时", "以补其未备")
Q["q36"] = slice_q(89, "歴法可騐者莫如交食", "莫如交食")
Q["q37"] = slice_q(167, "余方羁燕不相値也", "余方羁燕不相値也")

for k, v in Q.items():
    for ch in v:
        assert not (0xE000 <= ord(ch) <= 0xF8FF), f"PUA in {k}"
print("quotes:", len(Q))

entries = json.load(open("daizhige-daodu/.wuan_entries.json"))
# 重点条白话（防撞：均改写，不整抄库本窗）
EXT = {
 21:"三十岁上下，他从同乡倪竹冠先生那里初学官历，带着两个弟弟一起推步，订讹补缺写成二卷去见老师，得到一句首肯。多年后自记，就是在这时立下了终身之志。",
 23:"嫌通行历经简古，他借到家中旧藏的一部二十一史，读出郭守敬当年的精细，为初学者绘图作注。",
 25:"贯穿全书的源流总谱，四库提要几乎整段抄引。他自述志向：兼采古术与西术，只对天求证，不敢拿己见定高低。",
 32:"从《春秋》记南至算起，把各家历法的岁实摆在一起对账，替郭守敬古大今小的消长法翻案。",
 38:"进京修志前寄给施闰章的大纲几条：明代的历实为授时之续，回历沿用已久当备录，西法改宪之功亦不可抹。",
 42:"明史馆的历志骨架出自他手。黄宗羲的稿本他摘出五十多处疑误；为补授时表缺页，抱着错漏满纸的写本亲手重算，篝灯两月。",
 45:"郭守敬原著散亡，只余历草，传写多误。他订正并拈出精义，还替中西两种起算次序说了句公道话：剖析浑体求出句股，理无二致。",
 48:"耶律楚材与西域人赌月蚀获胜，作历托始于庚午年，推为受命之符；他顺手纠正《元史》里把太祖庚辰误写成太宗的错。",
 51:"立成之算王恂草创、郭守敬终成，监本却只刻王恂之名。他读出的不是疏漏，而是古人让善的深意。",
 54:"朋友潘天成初学历苦于布算，他专写一册入门式相授，自评殊便初学。",
 56:"三弟尔素多年的算稿，替他录成一册，旧法因而有据。",
 58:"与仲弟和仲共成。和仲勤勉能助而早卒，十余年后得通轨校验相合，人已不在；连誊清立成的从弟，也早已作古。",
 62:"回回历以太阴年布立成、太阳年取距算，巧藏根数，连在钦天监当差的回回子孙也说不出所以然。他的结论：泰西之学以回历为旧率，后出转精，须知其根源。",
 64:"为明初译出的西域星占书作注。最推重书首小序那句老实话：算法有失验之时，不可以一次不验就废掉此理。",
 66:"把回回星表三十杂星对证中方星名，是中西星名的第一次对表。",
 70:"从周髀里读出里差之法，认定西人经纬度之说由此自出。",
 74:"地圆之后，经纬一度约合二百五十里，纬圈愈远愈狭，附各省与蒙古东西南北之差。",
 78:"李光地出题，要一本望而辄解的入门书。他在中街寓邸动笔，李光地下朝就问今日成何论，脱稿亲手点定，数月得三十余篇。壬午年进呈，皇帝亲笔加了圈点。",
 82:"历法可验者莫如交食。他把散逸的蒙求细草重辑订补，日食月食各成一卷。",
 88:"附说两卷，其中一卷刻行于世。",
 94:"交食管见，交食方位自出手眼的简法。",
 98:"太阳日差的加减有两处根子，他主张分列两表各算其用。",
 101:"荧惑一星最难算，他专讲地谷立法的根由所在，刻成以正历书之误。",
 104:"上三星轨迹绕日成圆象，为岁轮旧说补出图形。",
 108:"月能掩日、日远而月近，道理本自浅显。他替太阴测影辨误，存古人景符取窍之法。",
 111:"浑盖一器，拿盖天的道理干浑天的活。他疑心这类器制是周髀一脉西传的痕迹。",
 117:"又名义作里差捷法，讲地圆与经纬换算，是给行海人写的小册子。",
 124:"一部测天仪器小史，命题只有一句：治历的根本全在测验。",
 126:"西器收机牙于径寸：小者聊供玩好，大者按更节晨昏，为用亦大。",
 128:"上起周官挈壶氏，下及宋铜壶滴漏、莲华漏、田家水漏、四刻沙漏，替阴雨天留一套计时底账。",
 130:"三卷晷式，集历代之大成。",
 156:"为穆氏的一部西历书作订注：对数之表与历书迥别而得数无二，异与同他都替后贤标出。",
 158:"为薛凤祚天学会通订注，正其剞劂多讹。",
 162:"为王锡阐遗书作注。他评王氏立议精到，用了一个后来居上的考语。",
 166:"钞存揭暄的一册谈天之书。揭先生翩然来访时他正羁留京师，两人竟未谋面。",
 172:"算数见于周官，本属圣门六艺；利玛窦以来别为两家，各有所长，而理实同归。",
 174:"筹算之法创于作历书时，简明得多，旧法难比。",
 176:"笔算易横为直，定位一端尤便文人之用，一生两稿。",
 178:"比例规解即西人尺算，他借得残本钞补订正，与矩算同为度算。",
 181:"对数是穆尼阁亲授。十万之表西来失散仅存一万，他以法通之补足全表；开方到三乘方以上要熬上半天，对数一查立得。",
 188:"西人之三角，犹古人之句股。平三角广为五卷，书版由李光地刻于保定任上，乙酉年南巡时呈到了御前。",
 193:"九章第八章久成绝学，存例多臆说。他重立其旨，令明算者复能举其名。",
 195:"几何是西算的根。书里由浅入深、最会打比方，他摘其要以为测量之用。",
 197:"量天离不开句股。在他看来，三角是句股的精微处，八线表是句股的立成。",
 200:"算学初无古今。他辑九章遗义立此存古，警告踵事生新者勿轻古率为疏。",
 204:"从一次幂到九次幂的相生旧图，他补出用途，续编自此始。",
 206:"算家旧有分田之法，他推广之，聊存以见数法无所不通。",
 208:"几何原本只译到六卷。他从历书拾出未译之理，自补棱体诸说。",
 210:"西镜录不知出自谁手，然有定位之法，为踵事加精之证，他为之订注。",
 212:"重学之表讹误尤甚，他借《仪象志》逐数对勘，其数稍真。",
 214:"那四个字古人是禁的，但他认抽水起重诸机械于民间日用大有好处，替它们翻了案。",
 216:"读薛氏书另得两法，是在旧传诸法之外的收获。",
 218:"弧度求法莫良于三角，他补测量全义举例之缺正其错谬。",
 220:"以加减代乘除，他存疑了几十年才理出头绪；有远道写信来商榷的，也附在卷尾，替对方留名。",
 224:"借土方之法量天度，用平面管圆面，用方体测圆体。",
 226:"几何书里不讲句股，道理却就是句股。译书时未会通遂分途径，他以句股释其难通者。",
 230:"日出入的方位与时刻各查一表，按里差以弧三角布算。",
 232:"历书圆周率列到二十位，真正入算却仍取旧率，他详辨乘除之际的取舍。",
 234:"一言之惠不敢忘。他把友朋关于算学的片语录成一卷，取名丽泽。",
 236:"珠盘实起于元末明初，古人持筹。三页纸的计算器考古。",
 238:"初学快船：笔算三日可了，乘除定位理顺之后，童子亦可入门。",
}

LI_ORDER = ["发轫","通考","史志","交食","行度","测器","参商"]
SU_ORDER = ["通算","几何","古算","器用"]
GRPCNT = {}
for e in entries:
    if e["kind"] != "at":
        GRPCNT[e["grp"]] = GRPCNT.get(e["grp"], 0) + 1

CN = {"发轫":"六","通考":"十一","史志":"七","交食":"六","行度":"九","测器":"十九","参商":"四",
      "通算":"七","几何":"十二","古算":"四","器用":"三"}

def esc(s): return html.escape(s, quote=False)

def state_chip(e):
    st = e["st"]
    if "进呈" in st: return "进呈"
    for tag,chip in [("魏茘彤刻","魏刻"),("魏荔彤刻","魏刻"),("已刻","已刻"),("巳刻","已刻"),("巳刻","已刻"),("刻","刻")]:
        if tag in st: return chip
    return ""

def sign_html(e, idx):
    t = esc(e["title"])
    chip = state_chip(e)
    dot = "at" if e["kind"]=="at" else ("on" if chip else "")
    ext = ""
    if e["ln"] in EXT:
        ext = f'<p class="dtx">{esc(EXT[e["ln"]])}</p>'
    sol = esc(e["sol"][:60]) if not ext and e["sol"] else ""
    stline = ""
    if e["kind"]=="at":
        stline = f'<p class="dtx dim">原自为帙，{esc(ATTACH_TXT[e["ln"]])}。</p>'
    elif e["st"]:
        stline = f'<p class="dtx dim">刊藏记：<q>{esc(e["st"])}</q>。</p>'
    if e["ln"]==42:
        ext += '<div class="dqq"><span>篝灯两月之幕见下节</span></div>'
    return (f'<div class="sg {dot}" id="sg{e["ln"]}" data-ln="{e["ln"]}">'
            f'<span class="sdot"></span>'
            f'<span class="sname"><q>{t}</q></span>'
            f'<span class="sno">{esc(CN_N[e["ln"]])}</span>'
            f'<span class="schip">{chip}</span>'
            f'</div><div class="det" id="det{e["ln"]}">{ext}{stline}{f"<p class='dtx src'><q>{sol}</q></p>" if sol else ""}</div>')

CN_N = {}
for i,e in enumerate(entries,1):
    CN_N[e["ln"]] = str(i) if e["kind"]!="at" else "附"

ATTACH_TXT = {90:"今收入前卷",93:"今收入交食蒙求订补",228:"并入前条"}

def group_block(title, order, kind):
    out = [f'<div class="zh"><div class="zhhead"><span class="zhname">{title}</span>'
           f'<span class="zhcnt">{ " · ".join([]) }</span></div><div class="zhsigs">']
    return out

# 组装帙墙
walls = []
for title, order in [("历学之簿", LI_ORDER), ("算学之簿", SU_ORDER)]:
    walls.append(f'<div class="book"><h3 class="bh">{title}</h3>')
    for g in (LI_ORDER if title.startswith("历") else SU_ORDER):
        es = [e for e in entries if e["kind"]!="at" and e["grp"]==g]
        walls.append(f'<div class="zhu"><div class="zhhead"><span class="zhname">{g}</span>'
                     f'<span class="zhcnt">{CN[g]}签</span></div>')
        for e in es:
            walls.append(sign_html(e, 0))
        walls.append('</div>')
    at = [e for e in entries if e["kind"]=="at"]
    if title.startswith("历"):
        walls.append('<div class="zhu"><div class="zhhead"><span class="zhname">附存</span>'
                     '<span class="zhcnt">三签</span></div>')
        for e in at:
            walls.append(sign_html(e, 0))
        walls.append('</div>')
    walls.append('</div>')
SIGNS = "".join(walls)

# ---- 页面 ----
CSS = """
:root{--bg:#191917;--bg2:#1e1e1b;--paper:#e8e4dc;--paper2:#dcd6ca;--ink:#26251f;
--dim:#8f8b80;--acc:#5f9270;--accd:#3f6b4e;--zhu:#c0453c;}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--paper);font-family:"Songti SC","STSong","SimSun","Noto Serif CJK SC",serif;line-height:1.9}
.wrap{max-width:1080px;margin:0 auto;padding:0 22px}
a{color:var(--acc)}
q{quotes:none}
.mono{font-family:"SF Mono",Menlo,Consolas,monospace}
/* hero */
.hero{position:relative;min-height:92vh;display:flex;align-items:center;justify-content:center;overflow:hidden}
.arm{position:absolute;inset:0;opacity:.9}
.arm svg{width:100%;height:100%}
.arm{left:24vw}
@media (max-width:820px){.arm{left:0}}
.hcol{position:relative;z-index:3;display:flex;gap:26px;align-items:flex-start}
.hcol .vtitle{writing-mode:vertical-rl;text-orientation:upright;font-size:64px;letter-spacing:14px;
 color:var(--paper);height:max-content}
.hcol .vsub2{writing-mode:vertical-rl;text-orientation:upright;font-size:15px;color:var(--dim);letter-spacing:6px;height:max-content;margin-top:8px}
.seal{width:38px;height:120px;background:var(--zhu);color:#f5efe4;display:flex;align-items:center;justify-content:center;
 writing-mode:vertical-rl;text-orientation:upright;font-size:15px;letter-spacing:6px;border-radius:6px;box-shadow:0 0 0 2px rgba(192,69,60,.25)}
.kick{position:absolute;top:26px;left:0;right:0;text-align:center;color:var(--dim);font-size:13px;letter-spacing:3px;z-index:3}
.hint{position:absolute;bottom:24px;left:0;right:0;text-align:center;color:var(--dim);font-size:13px;z-index:3}
.hint button{margin-left:14px;background:none;border:1px solid var(--acc);color:var(--acc);padding:7px 20px;
 font-family:inherit;font-size:14px;letter-spacing:4px;cursor:pointer;border-radius:3px}
.hint button:hover{background:rgba(95,146,112,.12)}
/* 起算牌 */
.qipai{display:none;margin:0 auto 60px;max-width:640px;border:1px solid var(--accd);background:var(--bg2);padding:26px 30px;border-radius:4px}
.qipai.show{display:block}
.qipai .lab{color:var(--acc);font-size:13px;letter-spacing:3px;margin-bottom:10px}
.qipai q{color:var(--paper);font-size:16px}
/* 簿墙 */
.sec{padding:64px 0}
.sechead{margin-bottom:30px}
.sechead .sk{color:var(--acc);font-size:13px;letter-spacing:3px}
.sechead h2{font-size:26px;font-weight:normal;margin-top:6px;letter-spacing:2px}
.sechead p{color:var(--dim);font-size:14px;margin-top:10px;max-width:720px}
.book{border:1px solid #2c2b25;border-radius:6px;background:var(--bg2);padding:22px;margin-bottom:26px}
.bh{font-weight:normal;font-size:19px;letter-spacing:3px;color:var(--paper);border-bottom:1px solid #2c2b25;padding-bottom:12px;margin-bottom:6px}
.zhu{margin-top:16px}
.zhhead{display:flex;align-items:baseline;gap:12px;margin-bottom:8px}
.zhname{color:var(--acc);font-size:15px;letter-spacing:3px}
.zhcnt{color:var(--dim);font-size:12px}
.sg{display:flex;align-items:center;gap:10px;padding:7px 10px;border-bottom:1px dashed #2c2b25;cursor:pointer;border-radius:3px}
.sg:hover{background:rgba(95,146,112,.07)}
.sdot{width:8px;height:8px;border-radius:50%;border:1px solid var(--acc);flex:none}
.sg.on .sdot{background:var(--zhu);border-color:var(--zhu)}
.sg.at{opacity:.62}
.sg.at .sdot{border-color:var(--dim)}
.sname{font-size:14px;color:var(--paper)}
.sname q{color:#d8d3c7}
.sno{margin-left:auto;color:var(--dim);font-size:11px;flex:none}
.schip{flex:none;font-size:11px;color:var(--zhu);border:1px solid rgba(192,69,60,.4);border-radius:2px;padding:0 5px;display:none}
.sg.on .schip{display:inline-block}
.det{display:none;padding:12px 14px 14px 28px;border-bottom:1px solid #2c2b25;background:rgba(95,146,112,.05)}
.det.show{display:block}
.dtx{font-size:14px;color:#c9c4b8}
.dtx.dim,.src{color:var(--dim);font-size:13px}
.dqq{margin-top:6px;color:var(--dim);font-size:12px}
/* 幕 */
.stage{display:grid;grid-template-columns:1fr 1fr;gap:30px;align-items:center}
@media (max-width:820px){.stage{grid-template-columns:1fr}}
.note{color:var(--dim);font-size:14px;margin-top:12px}
.bigq{margin-top:16px;padding:14px 18px;background:var(--paper);color:var(--ink);border-radius:4px;font-size:15px;line-height:2}
.bigq q{color:var(--ink)}
.act{margin-top:16px;display:flex;gap:12px;flex-wrap:wrap}
.act button{background:none;border:1px solid var(--acc);color:var(--acc);padding:8px 18px;font-family:inherit;
 font-size:14px;letter-spacing:3px;cursor:pointer;border-radius:3px}
.act button:hover{background:rgba(95,146,112,.12)}
.act button:disabled{opacity:.4;cursor:default}
/* 篝灯 */
.dengbox{position:relative;height:320px;border:1px solid #2c2b25;border-radius:6px;background:var(--bg2);overflow:hidden}
.moon{position:absolute;top:34px;right:44px;width:64px;height:64px;border-radius:50%;background:#cfc9ba;overflow:hidden}
.moon i{position:absolute;top:0;width:64px;height:64px;border-radius:50%;background:var(--bg2);transition:transform .35s}
.lamp{position:absolute;bottom:20px;left:44px}
.flame{transform-origin:50% 90%;animation:fl 1.6s ease-in-out infinite alternate}
@keyframes fl{from{transform:scaleY(.86)}to{transform:scaleY(1.1)}}
.mslog{position:absolute;bottom:18px;right:20px;color:var(--dim);font-size:12px;letter-spacing:2px}
/* 让善 */
.pair{display:flex;gap:22px;justify-content:center;padding:30px 0}
.pcard{width:120px;height:190px;perspective:600px;cursor:pointer}
.pinner{position:relative;width:100%;height:100%;transition:transform .7s;transform-style:preserve-3d}
.pcard.flip .pinner{transform:rotateY(180deg)}
.pface{position:absolute;inset:0;backface-visibility:hidden;border-radius:6px;display:flex;align-items:center;justify-content:center;
 writing-mode:vertical-rl;text-orientation:upright;letter-spacing:8px;font-size:24px}
.pfront{background:#2a2a24;color:var(--paper);border:1px solid #3a3931}
.pback{background:var(--zhu);color:#f5efe4;transform:rotateY(180deg);font-size:18px;letter-spacing:5px}
.rangseal{display:none;text-align:center;margin-top:14px}
.rangseal.show{display:block}
.rangseal .seal2{display:inline-flex;width:74px;height:74px;border:2px solid var(--zhu);color:var(--zhu);border-radius:8px;
 align-items:center;justify-content:center;writing-mode:vertical-rl;letter-spacing:4px;font-size:20px}
/* 九家环 */
.jiubox{display:grid;grid-template-columns:1fr 300px;gap:20px;align-items:center}
@media (max-width:820px){.jiubox{grid-template-columns:1fr}}
.jiuinfo{border:1px solid #2c2b25;border-radius:6px;background:var(--bg2);padding:20px;min-height:180px}
.jiuinfo .who{color:var(--acc);letter-spacing:2px;font-size:15px}
.jiuinfo .what{color:var(--paper);font-size:17px;margin-top:8px;letter-spacing:2px}
.jiuinfo p{color:var(--dim);font-size:13px;margin-top:10px}
.jg{cursor:pointer}
.jg circle{transition:.25s}
.jg:hover circle,.jg.hit circle{r:9}
.jg.hit circle{fill:var(--zhu);stroke:var(--zhu)}
.leg{display:flex;gap:18px;color:var(--dim);font-size:12px;margin-top:10px}
.leg i{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:5px}
/* 对数 */
.bars{border:1px solid #2c2b25;border-radius:6px;background:var(--bg2);padding:24px}
.bar{margin-bottom:18px}
.bar .blab{display:flex;justify-content:space-between;color:var(--dim);font-size:13px;letter-spacing:2px;margin-bottom:6px}
.track{height:14px;background:#262620;border-radius:7px;overflow:hidden}
.fill{height:100%;width:0;border-radius:7px}
.fill.gu{background:#6e6a5e}
.fill.xin{background:var(--acc)}
.flag{display:none;margin-top:6px;color:var(--acc);font-size:14px;letter-spacing:3px}
.flag.show{display:block}
/* 进呈舟 */
.boatbox{position:relative;border:1px solid #2c2b25;border-radius:6px;background:var(--bg2);height:300px;overflow:hidden}
.boatbox .cheng{position:absolute;top:20px;left:0;right:0;text-align:center}
.cheng .seal3{display:none;width:70px;height:70px;border:2px solid var(--zhu);color:var(--zhu);border-radius:8px;
 writing-mode:vertical-rl;letter-spacing:3px;font-size:16px;align-items:center;justify-content:center;margin:0 auto}
.cheng.hit .seal3{display:inline-flex;animation:drop .6s}
@keyframes drop{from{transform:translateY(-24px);opacity:0}to{transform:none;opacity:1}}
.wave{position:absolute;bottom:0;left:0;right:0;height:90px}
/* 尾屏 */
.colophon{padding:80px 0 40px;display:flex;gap:40px;justify-content:center;align-items:flex-start}
.vlog{writing-mode:vertical-rl;text-orientation:upright;letter-spacing:10px;font-size:19px;color:#cfc9ba;height:max-content}
.vlog.small{font-size:13px;color:var(--dim);letter-spacing:6px}
.endseal{display:flex;flex-direction:row;gap:14px;align-items:flex-start}
footer{border-top:1px solid #34302a;padding:34px 0 44px;font-size:13px;color:var(--dim);line-height:2}
footer a{color:var(--acc)}
footer p{margin-bottom:8px}
.rv{opacity:0;transform:translateY(18px);transition:.8s}
.rv.in{opacity:1;transform:none}
"""

HTML_TOP = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>勿庵历算书记 · 殆知阁导读第四百五十八篇</title>
<style>__CSS__</style>
</head>
<body>

<div class="hero">
  <div class="arm">__ARM__</div>
  <div class="kick">殆知阁古代文献 · 子藏算法</div>
  <div class="hcol">
    <div class="vtitle">勿庵</div>
    <div class="seal">数无中西</div>
    <div class="vtitle" style="font-size:44px;letter-spacing:10px;margin-top:6px">历算书记</div>
    <div class="vsub2">清 宣城 梅文鼎</div>
  </div>
  <div class="hint">一部写给自己也写给朝廷的学术总目，八十八签，各有一段自疏<button id="qisuan" type="button">起 算</button></div>
</div>

<div class="wrap">
<div class="qipai" id="qipai">
  <div class="lab">起算 · 顺治辛丑</div>
  <q>__Q1__</q>
  <p class="note">开篇第一条只是一册跟着老师啃出来的作业，可八十年历算生涯，就是从这枚签上起算的。</p>
</div>
"""

HTML_MID1 = """
<section class="sec" id="bu">
  <div class="sechead rv">
    <div class="sk">簿 墙</div>
    <h2>两簿十一帙，八十八签</h2>
    <p>历学一簿六十二签分七帙，算学一簿二十六签分四帙；另附存三签，是后来并入他册的短篇。朱点者已刻行世，空点者稿藏于家。点签可展。</p>
  </div>
__SIGNS__
</section>
"""

HTML_MID2 = """
<section class="sec" id="deng">
  <div class="sechead rv">
    <div class="sk">幕 一</div>
    <h2>篝灯两月</h2>
    <p>明史馆的历志稿到他手里时，授时表缺页、写本错漏相连。没有可抄的本子，只能亲手重算。灯下两轮月圆月缺，才算理顺一卷。</p>
  </div>
  <div class="stage rv">
    <div class="dengbox">
      <div class="moon"><i id="mshade"></i></div>
      <svg class="lamp" width="120" height="150" viewBox="0 0 120 150">
        <ellipse cx="60" cy="140" rx="46" ry="7" fill="#111009"/>
        <rect x="38" y="96" width="44" height="40" fill="#3a382e"/>
        <path d="M30 96 Q60 66 90 96 Z" fill="#4a463a"/>
        <path d="M52 30 Q60 14 68 30 Q74 44 60 56 Q46 44 52 30 Z" fill="#e8b25a">
          <animate attributeName="opacity" values="1;.72;1" dur="1.2s" repeatCount="indefinite"/>
        </path>
        <rect x="57" y="56" width="6" height="12" fill="#6e6a5e"/>
      </svg>
      <div class="mslog" id="mslog">月相未动</div>
    </div>
    <div>
      <div class="act"><button id="lightbtn" type="button">挑 灯</button></div>
      <div class="bigq" id="dengq" hidden><q>__Q6__</q></div>
      <p class="note">黄宗羲的稿本他先摘出五十多处疑误；轮到补表，谁也靠不上，只有算。</p>
    </div>
  </div>
</section>

<section class="sec" id="rang">
  <div class="sechead rv">
    <div class="sk">幕 二</div>
    <h2>让 善</h2>
    <p>大统历立成，王恂草创而郭守敬终成。元代监本只刻了王恂的名字。别人抢着认领的事，这里反过来。两块牌都翻开，看他读出了什么。</p>
  </div>
  <div class="rv">
    <div class="pair">
      <div class="pcard" id="pc1"><div class="pinner">
        <div class="pface pfront">王 恂</div><div class="pface pback">创 始 之 美</div></div></div>
      <div class="pcard" id="pc2"><div class="pinner">
        <div class="pface pfront">郭守敬</div><div class="pface pback">终 事 之 勤</div></div></div>
    </div>
    <div class="rangseal" id="rangseal">
      <div class="bigq" style="max-width:640px;margin:0 auto"><q>__Q10__</q></div>
      <div class="seal2" style="margin-top:16px">让善</div>
    </div>
  </div>
</section>

<section class="sec" id="jiu">
  <div class="sechead rv">
    <div class="sk">幕 三</div>
    <h2>西法九家</h2>
    <p>在他眼里，所谓西法从来不是一块铁板：唐有九执，元有万年，明有回历与融合之作，是为旧法；利玛窦以来四家，是为新法。九点环上点一家，亮一家。</p>
  </div>
  <div class="jiubox rv">
    <svg id="jiuvg" viewBox="0 0 420 420" style="width:100%;max-width:460px;margin:0 auto;display:block">
      <circle cx="210" cy="210" r="150" fill="none" stroke="#2c2b25" stroke-width="1.5"/>
      <circle cx="210" cy="210" r="112" fill="none" stroke="#26251f" stroke-width="1" stroke-dasharray="3 6"/>
      <text x="210" y="205" text-anchor="middle" fill="#8f8b80" font-size="13" letter-spacing="4">西法九家</text>
      <text x="210" y="226" text-anchor="middle" fill="#4a463c" font-size="11">旧五 · 新四</text>
    </svg>
    <div>
      <div class="jiuinfo" id="jiuinfo">
        <div class="who">点环上任一家</div>
        <div class="what">旧法五家，新法四家</div>
        <p>他的断语是：西法多门，愈晚愈精。</p>
      </div>
      <div class="leg"><span><i style="background:#5f9270"></i>旧法五</span><span><i style="background:#c0453c"></i>新法四</span></div>
    </div>
  </div>
  <div class="bigq rv" style="margin-top:22px"><q>__Q29__</q></div>
</section>

<section class="sec" id="ds">
  <div class="sechead rv">
    <div class="sk">幕 四</div>
    <h2>俄 顷</h2>
    <p>对数表随穆尼阁东来，途中失散只剩一万；他以法补足十万。这册《比例数解》记下他第一次见到「开方神器」时的新旧对照。</p>
  </div>
  <div class="stage rv">
    <div class="bars">
      <div class="bar"><div class="blab"><span>古法开方</span><span id="gut">未布算</span></div>
        <div class="track"><div class="fill gu" id="guf"></div></div></div>
      <div class="bar"><div class="blab"><span>用对数</span><span id="xint">未查表</span></div>
        <div class="track"><div class="fill xin" id="xinf"></div></div></div>
      <div class="flag" id="ejq">俄 顷 可 得</div>
    </div>
    <div>
      <div class="act"><button id="gubtn" type="button">布 古 算</button><button id="xinbtn" type="button">查 对 数</button></div>
      <div class="bigq"><q>__Q17__</q><p class="note" style="margin-top:10px">穆尼阁的一句话他也记下了：</p><q>__Q18__</q></div>
    </div>
  </div>
</section>

<section class="sec" id="cheng">
  <div class="sechead rv">
    <div class="sk">幕 五</div>
    <h2>进 呈</h2>
    <p>壬午年夏，李光地扈从出行河工，把这部《历学疑问》呈了上去。乙酉年南巡，又蒙召对。一介布衣的书，进了皇帝的书箱。</p>
  </div>
  <div class="boatbox rv">
    <div class="cheng" id="chengbox"><span class="seal3">钦蒙进呈</span></div>
    <svg class="wave" viewBox="0 0 800 90" preserveAspectRatio="none">
      <path d="M0 60 Q100 40 200 60 T400 60 T600 60 T800 60 V90 H0 Z" fill="#232f27"/>
      <path d="M0 72 Q100 54 200 72 T400 72 T600 72 T800 72 V90 H0 Z" fill="#2a3a2f"/>
    </svg>
    <svg style="position:absolute;bottom:56px;left:50%;transform:translateX(-50%)" width="220" height="120" viewBox="0 0 220 120" id="boat">
      <path d="M20 86 L200 86 L172 112 L48 112 Z" fill="#4a463a"/>
      <rect x="104" y="20" width="5" height="66" fill="#6e6a5e"/>
      <path d="M110 22 Q168 40 110 80 Z" fill="#d8d3c7" id="sail" style="cursor:pointer"/>
      <path d="M20 86 L200 86" stroke="#111009" stroke-width="2"/>
    </svg>
  </div>
  <div class="bigq rv" id="chengq" hidden style="margin-top:22px"><q>__Q8__</q><br><q>__Q9__</q></div>
</section>
"""

HTML_END = """
<section class="colophon">
  <div class="vlog">八十八签一簿历八十年</div>
  <div class="vlog small">布衣负重器不坠斯文</div>
  <div class="endseal">
    <div class="seal" style="height:64px;width:38px">勿庵</div>
    <div class="seal" style="background:var(--acc);height:64px;width:38px">星簿</div>
  </div>
</section>
</div>

<footer>
  <div class="wrap">
    <p>本篇为殆知阁导读系列第458篇。文本来源：殆知阁简体库〈勿庵历算书记〉子藏算法库本（一卷，八十八种解题并四库提要，约一万九千九百字）。仓库：<a href="https://github.com/rongyiwei/daizhige" target="_blank" rel="noopener">github.com/rongyiwei/daizhige</a>；导读页在 <a href="https://github.com/robertsong2000/daizhige-daodu" target="_blank" rel="noopener">github.com/robertsong2000/daizhige-daodu</a>。</p>
    <p>引文经脚本与库内文件去标点、归一逐字比对通过；白话反扫六字窗零撞。库本「首肻」「扈防」等讹字照录（防字三见分讹点定、钦蒙、扈跸）。</p>
    <p>时代局限：本书成于清初，对帝王知遇与西学教士所传一系的记述皆从当日起笔，历争诸案的是非亦以亲历者口吻落墨；本页照录立此存照，不代表对相关史事与立场的认定。</p>
  </div>
</footer>

<script>
(function () {
  var qs = function (s) { return document.querySelector(s); };
  var qsa = function (s) { return document.querySelectorAll(s); };

  qs('#qisuan').addEventListener('click', function () {
    qs('#qipai').classList.add('show');
    this.disabled = true;
  });

  qsa('.sg').forEach(function (s) {
    s.addEventListener('click', function () {
      qs('#det' + s.getAttribute('data-ln')).classList.toggle('show');
    });
  });

  var phases = ['0%','100%','-25%','-50%','-75%','-100%','-125%','-150%'];
  var step = 0, timer = null;
  qs('#lightbtn').addEventListener('click', function () {
    this.disabled = true;
    timer = setInterval(function () {
      var m = step % 8;
      qs('#mshade').style.transform = 'translateX(' + ([-64,0,-16,-32,-48,-64,-80,-96][m]) + 'px)';
      qs('#mslog').textContent = step < 8 ? '第一月 相' + (m + 1) : '第二月 相' + (m + 1);
      step++;
      if (step > 16) {
        clearInterval(timer);
        qs('#mslog').textContent = '两月既尽';
        qs('#dengq').hidden = false;
      }
    }, 420);
  });

  var flipped = 0;
  qsa('.pcard').forEach(function (c) {
    c.addEventListener('click', function () {
      if (c.classList.contains('flip')) return;
      c.classList.add('flip');
      if (++flipped === 2) qs('#rangseal').classList.add('show');
    });
  });

  var NINE = [
    ['唐 · 瞿昙悉达', '九执历', '西法权舆，唐代已入中土。'],
    ['元 · 扎玛里迪音', '万年历', '西域万年历，元世祖时所进。'],
    ['明 · 马沙亦黑', '回回历', '与大统同用三百年。'],
    ['明 · 陈壤 袁黄', '历法新书', '增天地人三元。'],
    ['明 · 唐顺之与周述学', '历宗通议', '会通回历以入授时。'],
    ['利玛窦 汤若望 南怀仁', '天学初函 崇祯历书 仪象志', '新法正宗，时宪历所本。'],
    ['穆尼阁 薛凤祚', '天步真原 天学会通', '对数东来之桥。'],
    ['王锡阐（寅旭）', '晓庵新法', '自辟门庭，其考语是精到。'],
    ['揭暄 方中通', '写天新语 揭方问答', '多西书所未发。']
  ];
  var svg = qs('#jiuvg');
  var NS = 'http://www.w3.org/2000/svg';
  NINE.forEach(function (n, i) {
    var ang = -90 + i * 40;
    var rad = ang * Math.PI / 180;
    var x = 210 + 150 * Math.cos(rad), y = 210 + 150 * Math.sin(rad);
    var g = document.createElementNS(NS, 'g');
    g.setAttribute('class', 'jg'); g.setAttribute('data-i', i);
    var c = document.createElementNS(NS, 'circle');
    c.setAttribute('cx', x); c.setAttribute('cy', y); c.setAttribute('r', 7);
    c.setAttribute('fill', i < 5 ? '#5f9270' : '#c0453c'); c.setAttribute('stroke', '#191917'); c.setAttribute('stroke-width', 2);
    var t = document.createElementNS(NS, 'text');
    t.setAttribute('x', x); t.setAttribute('y', y - 14);
    t.setAttribute('text-anchor', 'middle'); t.setAttribute('fill', '#8f8b80'); t.setAttribute('font-size', 11);
    t.textContent = ['一','二','三','四','五','六','七','八','九'][i];
    g.appendChild(c); g.appendChild(t); svg.appendChild(g);
    g.addEventListener('click', function () {
      qsa('.jg').forEach(function (o) { o.classList.remove('hit'); });
      g.classList.add('hit');
      qs('#jiuinfo .who').textContent = n[0];
      qs('#jiuinfo .what').textContent = n[1];
      qs('#jiuinfo p').textContent = n[2];
    });
  });

  var gu = qs('#gubtn');
  gu.addEventListener('click', function () {
    this.disabled = true;
    var p = 0, t0 = Date.now();
    var iv = setInterval(function () {
      p += 1.4;
      qs('#guf').style.width = Math.min(p, 34) + '%';
      qs('#gut').textContent = '积晷 ' + Math.round((Date.now() - t0) / 100) / 10 + ' 刻';
      if (p >= 34) { clearInterval(iv); qs('#gut').textContent = '三乘方以上 · 未竟'; }
    }, 90);
  });
  qs('#xinbtn').addEventListener('click', function () {
    this.disabled = true;
    qs('#xinf').style.transition = 'width .3s'; qs('#xinf').style.width = '100%';
    qs('#xint').textContent = '已得'; qs('#ejq').classList.add('show');
  });

  qs('#sail').addEventListener('click', function () {
    qs('#chengbox').classList.add('hit');
    qs('#chengq').hidden = false;
  });

  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { threshold: 0.12 });
  qsa('.rv').forEach(function (el) { io.observe(el); });
})();
</script>

</body>
</html>
"""

# 浑仪 SVG
ARM = """<svg viewBox="0 0 1200 800" preserveAspectRatio="xMidYMid slice">
 <defs>
  <radialGradient id="gg" cx="50%" cy="42%" r="60%">
    <stop offset="0%" stop-color="#232823"/><stop offset="100%" stop-color="#191917"/>
  </radialGradient>
 </defs>
 <rect width="1200" height="800" fill="url(#gg)"/>
 <g id="stars"></g>
 <g transform="translate(600,392)">
   <g style="animation:none">
     <circle r="218" fill="none" stroke="#3f6b4e" stroke-width="2" stroke-dasharray="30 6 2 6" opacity=".9"/>
     <circle r="188" fill="none" stroke="#5f9270" stroke-width="1.4" opacity=".55"/>
   </g>
   <g class="ringy">
     <circle r="158" fill="none" stroke="#5f9270" stroke-width="2.4" stroke-dasharray="90 14 30 14" opacity=".8"/>
   </g>
   <g class="ringx">
     <circle r="124" fill="none" stroke="#c9963f" stroke-width="1.6" stroke-dasharray="46 10 8 10" opacity=".6"/>
   </g>
   <circle r="58" fill="#1e1e1b" stroke="#5f9270" stroke-width="2"/>
   <circle r="52" fill="none" stroke="#2c2b25" stroke-width="1"/>
   <path d="M-120 190 L-40 64 M120 190 L40 64" stroke="#34302a" stroke-width="7" fill="none"/>
   <path d="M-140 196 L140 196" stroke="#34302a" stroke-width="8"/>
 </g>
</svg>"""

STARS_JS = ""  # 星点静态生成
def stars_svg():
    import random
    random.seed(458)
    out = []
    for _ in range(90):
        x, y = random.randint(0, 1200), random.randint(0, 800)
        r = random.choice([0.8, 1.1, 1.4, 2.0])
        o = random.choice([0.25, 0.4, 0.6, 0.85])
        out.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#cfc9ba" opacity="{o}"/>')
    # 环上一颗亮星
    out.append('<circle cx="758" cy="300" r="3.4" fill="#5f9270"/>')
    out.append('<circle cx="758" cy="300" r="9" fill="none" stroke="#5f9270" opacity=".4"/>')
    return "".join(out)

CSS += """
.ringy{transform-origin:600px 392px;animation:spin 70s linear infinite}
.ringx{transform-origin:600px 392px;animation:spinr 48s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes spinr{to{transform:rotate(-360deg)}}
@media (prefers-reduced-motion:reduce){.ringy,.ringx,.flame{animation:none}}
"""

page = (HTML_TOP.replace("__CSS__", CSS)
        .replace("__ARM__", ARM.replace('<g id="stars"></g>', '<g id="stars">' + stars_svg() + '</g>'))
        .replace("__Q1__", esc(Q["q1"]))
        + HTML_MID1.replace("__SIGNS__", SIGNS)
        + (HTML_MID2.replace("__Q6__", esc(Q["q6"]))
                     .replace("__Q10__", esc(Q["q10"]))
                     .replace("__Q29__", esc(Q["q29"]))
                     .replace("__Q17__", esc(Q["q17"]))
                     .replace("__Q18__", esc(Q["q18"]))
                     .replace("__Q8__", esc(Q["q8"]))
                     .replace("__Q9__", esc(Q["q9"])))
        + HTML_END)

open(OUT, "w").write(page)
json.dump(Q, open("daizhige-daodu/.wuan_quotes.json", "w"), ensure_ascii=False, indent=1)
print("page written:", OUT, len(page), "bytes")
