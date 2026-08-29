#!/usr/bin/env python3
"""核验 yilin-gaicuo.html 引文与殆知阁库内《医林改错》逐字一致，并查排版规则。"""
import re, sys

SRC = "/home/robertsong/workspace/claude/daizhige-simplified/医藏/医林改错.txt"
PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/yilin-gaicuo.html"

# 库本讹字归一：赃→脏，已→巳，着→著，限→眼
VARIANTS = str.maketrans({"赃": "脏", "已": "巳", "着": "著", "限": "眼"})

def norm(s):
    return re.sub(r"[^一-鿿]", "", s).translate(VARIANTS)

raw = open(SRC, encoding="utf-8").read()
text = norm(raw)
fail = 0

def check(q, where):
    global fail
    ok = norm(q) in text
    print(("PASS" if ok else "FAIL"), where, q[:24] + ("…" if len(q) > 24 else ""))
    fail += 0 if ok else 1

MANUAL = [
    # 开场
    ("著书不明脏腑，岂不是痴人说梦；治病不明脏腑，何异于盲子夜行。", "开场 忏悔语"),
    # 其一
    ("治国良相，世代皆有；著书良医，无一全人。", "其一 良相良医"),
    ("夫业医诊病，当先明脏腑。", "其一 规矩"),
    ("看小肠化食，水自阑门出一节，真是千古笑谈。", "其一 千古笑谈"),
    # 其二 年表
    ("十年之久，念不少忘。", "年表 动念"),
    ("十死八九", "年表 瘟疫"),
    ("彼处乡风，更不深埋，意在犬食", "年表 乡风"),
    ("破腹露脏之儿，日有百余", "年表 义冢"),
    ("古人所以错论脏腑，皆由未尝亲见。", "年表 想通"),
    ("十人之内，看全不过三人。连视十日，大约看全不下三十余人", "年表 连视十日"),
    ("膈膜已破，仍未得见", "年表 崇文门"),
    ("自思一箦未成，不能终止", "年表 张格尔"),
    ("于膈膜一事，知之最悉", "年表 恒敬"),
    ("闻言喜出望外，即拜叩而问之", "年表 拜问"),
    ("余将亲见诸脏腑显隐之形，绘于其后。计四十二件。", "年表 刻书"),
    # 膈膜分界
    ("惟胸中隔膜一片，其薄如纸，最关紧要。", "膈膜 cap"),
    # 其三 对账
    ("灵机记性，不在心在脑", "对对 灵机"),
    ("小儿无记性者，脑髓未满；高年无记性者，脑髓渐空。", "对对 记性"),
    ("肺外皮实无透窍，亦无行气之二十四孔。", "对对 肺无孔"),
    ("两目系如线，长于脑，所见之物归于脑。", "对对 目系"),
    ("人身膈膜是上下界物。", "对对 膈膜界"),
    ("舌后白片，名曰会厌，乃遮盖左右气门。", "对对 会厌"),
    ("试看杀羊者，割其颈项不刺心，心内亦无血。", "错错 心无血"),
    ("卫总管，行气之府，其中无血。", "错错 气管"),
    ("肝体坚实，非肠、胃、膀胱可比，绝不能藏血。", "错错 肝"),
    ("元气即火，火即元气，此火乃人生命之源。", "错错 元气"),
    ("以无凭之谈，作欺人之事，利己不过虚名，损人却属实祸。窃财犹谓之盗，偷名岂不为贼！", "夹账 偷名"),
    # 其四 方
    ("余著《医林改错》一书，非治病全书，乃记脏腑之书也", "其四 自认"),
    ("示人以规矩", "其四 规矩"),
    ("身外凉，心里热，故名灯笼病，内有血瘀。认为虚热，愈补愈瘀；认为实火，愈凉愈凝。", "其四 灯笼病"),
    ("江西巡抚阿霖公，年七十四，夜卧露胸可睡，盖一层布压则不能睡，已经七年。召余诊之，此方五付全愈。", "其四 胸不任物"),
    ("一女二十二岁，夜卧令仆妇坐于胸，方睡，已经二年，余亦用此方，三付而愈，设一齐问病源，何以答之？", "其四 胸任重物"),
    ("补阳还五赤芍芎，归尾通经佐地龙，四两黄耆为主药，血中瘀滞用桃红。", "其四 方歌"),
    # 其五 未病三十四兆
    ("偶尔一阵头晕", "兆 01"), ("头无故一阵发沉", "兆 02"),
    ("耳内无故一阵风响", "兆 03"), ("耳内无故一阵蝉呜", "兆 04"),
    ("下眼皮长跳动", "兆 05"), ("一支眼渐渐小", "兆 06"),
    ("无故一阵眼睛发直", "兆 07"), ("眼前长见旋风", "兆 08"),
    ("长向鼻中攒冷气", "兆 09"), ("上嘴唇一阵跳动", "兆 10"),
    ("上下嘴唇相凑发紧", "兆 11"), ("睡卧口流涎沫", "兆 12"),
    ("平素聪明忽然无记性", "兆 13"), ("忽然说话少头无尾", "兆 14"),
    ("无故一阵气喘", "兆 15"), ("一手长战", "兆 16"),
    ("两手长战", "兆 17"), ("手无名指每日有一时屈而不伸", "兆 18"),
    ("手大指无故自动", "兆 19"), ("胳膊无故发麻", "兆 20"),
    ("腿无故发麻", "兆 21"), ("肌肉无故跳动", "兆 22"),
    ("手指甲缝一阵阵出冷气", "兆 23"), ("脚指甲缝一阵阵出冷气", "兆 24"),
    ("两腿膝缝出冷气", "兆 25"), ("脚孤拐骨一阵发软", "兆 26"),
    ("腿无故抽筋", "兆 27"), ("脚指无故抽筋", "兆 28"),
    ("行走两腿如拌蒜", "兆 29"), ("心口一阵气堵", "兆 30"),
    ("心口一阵发空气不接", "兆 31"), ("心口一阵发忙", "兆 32"),
    ("头项无故一阵发直", "兆 33"), ("睡卧自觉身子沉", "兆 34"),
    ("皆是元气渐亏之症。因不痛不痒，无寒无热，无碍饮食起居，人最易于疏忽。", "其五 尾句"),
    # 其六 收束
    ("余著《医林改错》一书，非治病全书，乃记脏腑之书也。其中当尚有不实不尽之处，后人倘遇机会，亲见脏腑，精察增补，抑又幸矣！", "其六 自序"),
    ("直翻千百年旧案，正其谬误，决其瑕疵，为希世之宝也", "其六 张序"),
    ("其所以能绘诸形者，则由于亲见。其所以得亲见者，则由于稻地镇之一游也。", "其六 知非子"),
]
for q, where in MANUAL:
    check(q, where)

# 复查：页面所有 blockquote.q 与 span.qv 逐块回验
html = open(PAGE, encoding="utf-8").read()
blocks = re.findall(r'<blockquote class="q">(.*?)</blockquote>', html, flags=re.S)
spans = re.findall(r'<span class="qv">(.*?)</span>', html, flags=re.S)
print(f"\n页面引文：blockquote.q {len(blocks)} 个，span.qv {len(spans)} 个")
for b in blocks + spans:
    b = re.sub(r'<span class="src">.*?</span>', "", b, flags=re.S)
    body = re.sub(r"<[^>]+>", "", b).strip()
    check(body, "页面回验")

# 三十四兆条目数核对
omen = re.findall(r"<li>([^<]+)</li>", html)
omen = [o for o in omen if "一阵" in o or "发" in o or "无故" in o or "无记性" in o or "拌蒜" in o or "腿" in o]
n_li = len(re.findall(r'<ol class="omen">.*?</ol>', html, flags=re.S))
seg = re.search(r'<ol class="omen">(.*?)</ol>', html, flags=re.S).group(1)
cnt = len(re.findall(r"<li>", seg))
print(f"\n未病之兆清单条目：{cnt}（页面声称三十四条）")
ok = cnt == 34
print(("PASS" if ok else "FAIL"), "条目数 34")
fail += 0 if ok else 1

# 症目三十九条核对：本库文本通窍14 + 血府19 + 膈下6
def seg_titles(a, b):
    s = raw[raw.index(a):raw.index(b)]
    return len(re.findall(r"^　　([^\s　][^　]{0,14})$", s, flags=re.M))
n1 = seg_titles("通窍活血汤所治症目", "通窍活血汤\n")
n2 = seg_titles("血府逐瘀汤所治症目", "血府逐瘀汤\n")
n3 = seg_titles("隔下逐瘀汤所治症目", "隔下逐瘀汤\n")
print(f"症目实测：通窍 {n1} + 血府 {n2} + 膈下 {n3} = {n1+n2+n3}（页面声称三十九条）")
ok = n1 + n2 + n3 == 39
print(("PASS" if ok else "FAIL"), "症目 39")
fail += 0 if ok else 1

# 数字核对：库内实测字符数
nchars = len(raw)
print(f"\n库内总字符数：{nchars}，其中汉字 {len(text)}")
ok = nchars == 30767
print(("PASS" if ok else "FAIL"), "页面声称实测字符数 30,767")
fail += 0 if ok else 1

# 排版规则
for i, line in enumerate(html.split("\n"), 1):
    if "—" in line or "–" in line:
        print("FAIL 排版：出现长划线，行", i, line.strip()[:40]); fail += 1
    if line.count("·") > 1:
        print("FAIL 排版：一行多个·，行", i, line.strip()[:40]); fail += 1

for k in ["殆知阁", "逐字核对", "局限", "mulu.html"]:
    if k not in html:
        print("FAIL 页面缺少：", k); fail += 1

print("\n结果：", "全部通过" if fail == 0 else f"{fail} 处失败")
sys.exit(1 if fail else 0)
