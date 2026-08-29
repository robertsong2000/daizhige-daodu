#!/usr/bin/env python3
# 引文核验：wenxin-diaolong.html 中的所有引文与库内文件逐字比对
# 规则：去标点+去空白+异体字归一后做子串匹配
import re, sys, unicodedata

LIB = "/home/robertsong/workspace/claude/daizhige-simplified/集藏/文评/文心雕龙.txt"
PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/wenxin-diaolong.html"

VARIANTS = {
    "讱": "隐", "沉": "沈", "况": "況", "棄": "弃", "於": "于",
}

def normalize(s: str) -> str:
    s = unicodedata.normalize("NFC", s)
    s = "".join(VARIANTS.get(c, c) for c in s)
    return re.sub(r"[\s　，。；：、「」『』！？、（）【】《》『』“”‘’·…\-—–.,;:!?「」]+", "", s)

text = open(LIB, encoding="utf-8").read()
hay = normalize(text)

quotes = [
    # 原道第一
    "文之为德也大矣，与天地并生者何哉",
    "心生而言立，言立而文明，自然之道也",
    # 序志第五十
    "文心者，言为文之用心也",
    "余生七龄，乃梦彩云若锦，则攀而采之。",
    "形同草木之脆，名逾金石之坚",
    "盖文心之作也，本乎道，师乎圣，体乎《经》，酌乎《纬》，变乎《骚》",
    "位理定名，彰乎《大易》之数，其为文用，四十九篇而已。",
    "文果载心，余心有寄。",
    # 神思第二十六
    "登山则情满于山，观海则意溢于海",
    "寂然凝虑，思接千载；悄焉动容，视通万里",
    # 知音第四十八
    "知音其难哉！音实难知，知实难逢，逢其知音，千载其一乎！",
    "凡操千曲而后晓声，观千剑而后识器",
    "夫缀文者情动而辞发，观文者披文以入情，沿波讨源，虽幽必显。",
    "世远莫见其面，觇文辄见其心。",
    # 时序第四十五
    "文变染乎世情，兴废系乎时序，原始以要终，虽百世可知也。",
    # 序志（跨校勘括号的订正连读）
    "齿在逾立，则常夜梦执丹漆之礼器，随仲尼而南行",
    # 知音（六观）
    "一观位体，二观置辞，三观通变，四观奇正，五观事义，六观宫商",
]

# 五十篇篇名（库本用字）
titles = "原道第一 微圣第二 宗经第三 正纬第四 辩骚第五 明诗第六 乐府第七 铨赋第八 颂赞第九 祝盟第十 铭箴第十一 诔碑第十二 哀吊第十三 杂文第十四 谐讔第十五 史传第十六 诸子第十七 论说第十八 诏策第十九 檄移第二十 封禅第二十一 章表第二十二 奏启第二十三 议对第二十四 书记第二十五 神思第二十六 体性第二十七 风骨第二十八 通变第二十九 定势第三十 情采第三十一 镕裁第三十二 声律第三十三 章句第三十四 丽辞第三十五 比兴第三十六 夸饰第三十七 事类第三十八 练字第三十九 隐秀第四十 指瑕第四十一 养气第四十二 附会第四十三 总术第四十四 时序第四十五 物色第四十六 才略第四十七 知音第四十八 程器第四十九 序志第五十".split()

fails = 0
for q in quotes:
    if normalize(q) in hay:
        print(f"OK   {q}")
    else:
        fails += 1
        print(f"FAIL {q}")

for t in titles:
    if t in text:
        pass
    else:
        fails += 1
        print(f"TITLE FAIL {t}")
print(f"titles: {len(titles)} checked")

# 页面渲染后的引文抽查：页面里的所有「」引文（书名号除外）也要在库内
page = open(PAGE, encoding="utf-8").read() if len(sys.argv) > 1 and sys.argv[1] == "page" else ""
if page:
    page = re.sub(r"<[^>]+>", "", page)
    in_page = re.findall(r"「([^」]{6,})」", page)
    for q in in_page:
        if normalize(q) in hay:
            print(f"PAGE OK   {q[:24]}")
        else:
            fails += 1
            print(f"PAGE FAIL {q[:40]}")

print("ALL PASS" if fails == 0 else f"{fails} FAILURES")
sys.exit(0 if fails == 0 else 1)
