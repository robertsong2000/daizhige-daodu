#!/usr/bin/env python3
"""核验 kaiyuan-zhanjing.html 引文与殆知阁库内《开元占经》逐字一致，并查排版规则。"""
import re, sys

SRC = "/home/robertsong/workspace/claude/daizhige-simplified/易藏/术数/开元占经.txt"
PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/kaiyuan-zhanjing.html"

def norm(s):
    return re.sub(r"[^一-鿿]", "", s)

raw = open(SRC, encoding="utf-8").read()
text = norm(raw)
fail = 0

def check(q, where):
    global fail
    ok = norm(q) in text
    print(("PASS" if ok else "FAIL"), where, q[:24] + ("…" if len(q) > 24 else ""))
    fail += 0 if ok else 1

# 首查：写稿时逐字取材的引文底稿（含页面散引）
MANUAL = [
    # 卷首提要
    ("唐瞿昙悉达撰。", "提要 开篇"),
    ("《国史志》四卷，《崇文目》三卷。", "提要 残卷著录"),
    ("考《玉海》开元六年诏瞿昙悉达译《九执历》，则悉达之为太史监，当在开元初。", "提要 开元六年译九执历"),
    ("此本一百二十卷", "提要 一百二十卷"),
    ("所言占验之法，大抵术家之异学，本不足存。", "提要 术不足存"),
    ("《九执历》不载于《唐志》，他书亦不过标撮大旨。此书所载，全法具著，为近世推步家所不及窥。", "提要 九执历仅存于此"),
    ("如《隋志》所称纬书八十一篇，此书尚存其七八，尤为罕见。", "提要 纬书方舟"),
    ("然则其术可废，其书则有可采也。", "提要 术废书采"),
    ("卷首有万历丁巳张熙识语，谓是书历唐迄明，约数百年，始得之挹元道人。钩沉起滞，非偶然已。", "提要 万历复得"),
    ("自一卷“天占”至一百十卷“星图”，均占天象。自一百十一卷“八谷占”至一百二十卷“龙鱼虫蛇占”，均占物异。", "提要 卷次结构"),
    ("考唐一行以开元九年奉诏创《大衍历》，以开元十六年颁之，其时《麟德历》遂不行，此书仍云见行《麟德历》，知其成于开元十六年以前矣。", "提要 成书年代依据"),
    # 卷一 张衡《灵宪》
    ("其后有冯焉者，羿请无死之药于西王母，姮娥以之奔月。将往，枚筮之于有黄，有黄占之曰：‘吉，翩翩归妹，独将西行，逢天晦芒，毋惊毋恐，后且大昌。’姮娥遂托身于月，是为蟾蜍。", "灵宪 嫦娥奔月"),
    ("夫日譬犹火，月譬犹水，火则外光，水则含景。故月光生于日之所照，魄生于日之所蔽，当日则光盈，就日则光尽也。", "灵宪 月光反射"),
    ("宇之表无极，宙之端无穷。", "灵宪 宇宙无限"),
    # 卷六十五 石氏中官占
    ("摄提六星，夹大角；（入角八度少，去北极五十九度半，在黄帝道内三十二度太。）一名环枢，一名天枢，一名阙丘，一名致法，一名三老，一名天𫓧，一名天狱，一名天楯；一名天武；一名天兵。", "石氏 摄提坐标"),
    ("贯索，贼人之牢；中星实，则囚多；虚、则开出。", "天牢 占辞"),
    ("大角不明，王者失天心，强臣凌主，天下有忧；秦之亡也，摄提不动，而大角亡去。", "大角 秦亡占例"),
    ("三星俱明，天下和平。", "织女 散引"),
    # 卷一百零四 九执历
    ("承前或译为风，或译为蚀神，梵之日呼为罗睺。", "罗睺 蚀神"),
    ("又诸曜则巡宿顺行，其阿修则巡宿逆转，掩蔽日月，以亦交蚀。", "罗睺 逆行掩蔽"),
    ("右天竺算法，用上件九个字，乘除其字，皆一举礼而成。凡数至十，进入前位，每空位处，恒安一点，有间咸记，无由辄错，运算便眼，趁须先及历度。", "天竺算法 九字一点"),
    ("今起明庆二年丁巳岁二月一日，以为历首", "九执历 历元"),
    ("卷一百零四", "卷次 存在"),
]
for q, where in MANUAL:
    check(q, where)

# 复查：页面所有 blockquote.q 逐块回验（省略号按分隔拆段核对）
html = open(PAGE, encoding="utf-8").read()
blocks = re.findall(r'<blockquote class="zhi q"[^>]*>(.*?)</blockquote>', html, flags=re.S)
print(f"\n页面引文块 {len(blocks)} 个（blockquote.zhi.q）：")
for b in blocks:
    body = re.sub(r"<span.*?</span>", "", b, flags=re.S)
    body = re.sub(r"<[^>]+>", "", body).strip()
    segs = [s.strip() for s in body.split("……") if s.strip()]
    for s in segs:
        check(s, "页面块")

# 数字核对：库内实测字符数
nchars = len(raw)
print(f"\n库内总字符数：{nchars}，其中汉字 {len(text)}")
ok = f"{nchars:,}" in html
print(("PASS" if ok else "FAIL"), f"页面声称实测字符数 {nchars:,}")
fail += 0 if ok else 1

# 排版规则
for i, line in enumerate(html.split("\n"), 1):
    if "—" in line or "–" in line:
        print("FAIL 排版：出现长划线，行", i, line.strip()[:40]); fail += 1
    if line.count("·") > 1:
        print("FAIL 排版：一行多个·，行", i, line.strip()[:40]); fail += 1

for k in ["殆知阁", "核验", "时代局限", "mulu.html", "github.com/robertsong2000/daizhigev20"]:
    if k not in html:
        print("FAIL 页面缺少：", k); fail += 1

print("\n结果：", "全部通过" if fail == 0 else f"{fail} 处失败")
sys.exit(1 if fail else 0)
