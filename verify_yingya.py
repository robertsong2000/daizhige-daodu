#!/usr/bin/env python3
"""核验 yingya-shenglan.html 引文与殆知阁库内《瀛涯胜览》逐字一致，并查排版规则。"""
import re, sys

SRC = "/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/瀛涯胜览.txt"
PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/yingya-shenglan.html"

def norm(s):
    return re.sub(r"[^一-鿿]", "", s)

raw = open(SRC, encoding="utf-8").read()
text = norm(raw)
fail = 0

def check(q, where):
    global fail
    ok = norm(q) in text
    print(("PASS" if ok else "FAIL"), where, q[:20] + ("…" if len(q) > 20 else ""))
    fail += 0 if ok else 1

# 首查：写稿时逐字取材的引文底稿（含 blockquote 与正文/诗签内引句）
MANUAL = [
    ("余以通译番书，亦被使末，随其所至，鲸波浩渺，不知其几于万里，历涉诸邦，其天时气候、地理人物、目击而身履之。", "自序 通事"),
    ("然奉命而往者，吾不知几千万人，而尽厥事称厥旨者，舍吾山阴宗道马公其谁乎？", "马敬序"),
    ("第愧愚昧，一介微氓，叨陪使节，与斯胜览，诚千载之奇遇也。", "自序 奇遇"),
    ("但直笔书其事", "自序 直笔"),
    ("如人有争讼难明之事，官不能决者，则令争讼二人骑水牛赴过其潭。理亏者鳄鱼出而食之；理直者虽过十次，亦不被食。最可奇也。", "占城 鳄鱼潭"),
    ("番人甚爱其头，或有触其头者，如中国杀人之恨。", "占城 爱头"),
    ("男子腰插不剌头一把，三岁小儿至百岁老人皆有此刀，皆是兔毫雪花上等镔铁为之。", "爪哇 不剌头"),
    ("其国风土无日不杀人，甚可畏也。", "爪哇 无日不杀人"),
    ("至永乐五年，朝廷差太监郑和等统领西洋大宝船到此处。有施进卿者，亦广东人也，来报陈祖义凶横等情，被太监郑和生擒陈祖义等，回朝伏诛，就赐施进卿冠带，归旧港为大头目，以主其地。本人死，位不传子，是其女施二姐为王，一切赏罪黜陟皆从其制。", "旧港 施二姐"),
    ("其王之妻与众誓曰：「有能报夫死之雠，复全其地者，吾愿妻之，共主国事。」言讫，本处有一渔翁，奋志而言：「我能报之。」", "苏门答剌 渔翁"),
    ("其牙人则言某月某日于众手中拍一掌已定，或贵或贱，再不悔改。", "古里 击掌"),
    ("彼之算法无算盘，只以两手、两脚幷二十指计算，毫厘无差，甚异于常。", "古里 二十指"),
    ("若手烂溃，其事不枉，即加以刑，若手如旧不损，则释之，头目人等以鼓乐礼送此人回家，诸亲邻友馈礼相贺，饮酒作乐以相庆，此事最为奇异。", "古里 油锅"),
    ("常言宝石乃是佛祖眼泪结成。", "锡兰 宝石"),
    ("每有大雨冲出土，流下沙中，寻拾则有", "锡兰 拾宝"),
    ("麒麟前二足高九尺余，后两足约高六尺，头抬颈长一丈六尺。首昂后低，人莫能骑。", "阿丹 麒麟"),
    ("食粟、豆、面饼", "阿丹 麒麟食性"),
    ("到天堂礼拜寺，其堂番名恺阿白。外周垣城，其城有四百六十六门，门之两傍皆用白玉石为柱。", "天方 恺阿白"),
    ("夜放一空碗，盛至天明，其露水有三分在碗。", "天方 露水"),
    ("下番之人取其水藏于船边，海中倘遇飓风，即以此水洒之，风浪顿息。", "天方 渗渗井"),
    ("就选差通事等七人，赍带麝香、磁器等物，附本国船只到彼。往回一年，买到各色奇货异宝，麒麟、狮子、驼鸡等物，幷画天堂圆真本回京。", "天方 通事七人"),
    ("舟人矫首混西东，惟指星辰定南北。", "纪行诗 星辰"),
    ("际天极地皆王臣", "纪行诗 句"),
    ("圣明一统混华夏", "纪行诗 句"),
    ("使节勤劳恐迟暮", "纪行诗 句"),
    ("时值南风指归路。舟行巨浪若游龙，回首遐荒隔烟雾。", "纪行诗 归路"),
    ("此序仅见国朝典故本", "库本 马敬序注"),
    ("国朝典故本及吴本并阙", "库本 后序注"),
    ("承前", "库本 拼接痕"),
]
for q, where in MANUAL:
    check(q, where)

# 复查：页面所有 blockquote.q 逐块回验
html = open(PAGE, encoding="utf-8").read()
blocks = re.findall(r'<blockquote class="q"[^>]*>(.*?)</blockquote>', html, flags=re.S)
print(f"\n页面引文块 {len(blocks)} 个（blockquote.q）：")
for b in blocks:
    body = re.sub(r"<span.*?</span>", "", b, flags=re.S)
    body = re.sub(r"<em>(.*?)</em>", r"\1", body, flags=re.S)
    body = re.sub(r"<[^>]+>", "", body).strip()
    check(body, "页面块")

# 数字核对：库内实测字符数（含标点空白）
nchars = len(raw)
print(f"\n库内总字符数：{nchars}，其中汉字 {len(text)}")
ok = nchars == 22552
print(("PASS" if ok else "FAIL"), "页面声称实测字符数 22,552")
fail += 0 if ok else 1

# 排版规则
for i, line in enumerate(html.split("\n"), 1):
    if "—" in line or "–" in line:
        print("FAIL 排版：出现长划线，行", i, line.strip()[:40]); fail += 1
    if line.count("·") > 1:
        print("FAIL 排版：一行多个·，行", i, line.strip()[:40]); fail += 1

for k in ["殆知阁", "核验", "局限", "mulu.html"]:
    if k not in html:
        print("FAIL 页面缺少：", k); fail += 1

print("\n结果：", "全部通过" if fail == 0 else f"{fail} 处失败")
sys.exit(1 if fail else 0)
