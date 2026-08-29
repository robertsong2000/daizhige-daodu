#!/usr/bin/env python3
"""铁围山丛谈导读页核验：引文逐字比对（按卷/附录分源）+ 排版规则 + 结构计数复核。"""
import re
import sys
import unicodedata
from html.parser import HTMLParser

PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/tieguishan-congtan.html"
SRC = "/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/铁围山丛谈.txt"


def norm(s: str) -> str:
    return "".join(
        ch for ch in s
        if not ch.isspace() and not unicodedata.category(ch).startswith("P")
    )


class QCollector(HTMLParser):
    """收集所有 class 含 q 的节点文本。"""

    def __init__(self):
        super().__init__()
        self.depth = 0
        self.buf = []
        self.quotes = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        cls = (d.get("class") or "").split()
        if self.depth > 0 or "q" in cls:
            self.depth += 1

    def handle_endtag(self, tag):
        if self.depth > 0:
            self.depth -= 1
            if self.depth == 0 and self.buf:
                self.quotes.append("".join(self.buf))
                self.buf = []

    def handle_data(self, data):
        if self.depth > 0:
            self.buf.append(data)


# (引文, 源范围: 1..6 主文卷 / 'ap' 附录 / None 任意)
QUOTES_SCOPE = [
    ("绦字约之，自号百纳居士", "ap"),
    ("官至徽猷阁待制。", "ap"),
    ("宣和六年京再起领三省，目昏眊不能视事，悉决于绦。", "ap"),
    ("凡京所判，皆绦为之，且代京入奏。", "ap"),
    ("由是恣为奸", "ap"),
    ("吾时在博白", 6),
    # 夜话一 玉柱斧子（卷一）
    ("故相位有阙，则中外侧耳耸听，一报供张小殿子，必知天子御内殿者，乃命相矣。", 1),
    ("及晚岁，虽倦万几，然命相每犹自择日", 1),
    ("在宣和殿亲札其姓名于小幅纸，缄封垂于玉柱斧子上，俾小珰持之导驾于前，自内中出至小殿子，见学士始启封焉。", 1),
    ("以姓名垂玉柱斧子，政与唐人金瓯覆之何异。", 1),
    # 夜话二 李超墨（卷五）
    ("昭陵晚岁开内宴", 5),
    ("一大臣得「李超墨」，而君谟伯父所得乃「廷珪」。", 5),
    ("大臣者但知「廷珪」为贵", 5),
    ("而不知有「超」也。", 5),
    ("既易，转欣然。", 5),
    ("君谟于马上始长揖曰：「还知廷珪是李超儿否？」", 5),
    # 夜话三 冢墓（卷四）
    ("及大观初，乃效公麟之考古，作宣和殿博古图。", 4),
    ("凡所藏者，为大小礼器，则已五百有几。", 4),
    ("故有得一器，其直为钱数十万", 4),
    ("于是天下冢墓，破伐殆尽矣。", 4),
    ("独政和间为最盛，尚方所贮至六千余数", 4),
    ("若岐阳宣王之石鼓，西蜀文翁礼殿之绘像，凡所知名，罔间巨细远近，悉索入九禁。", 4),
    ("俄遇僭乱，侧闻都邑方倾覆时，所谓先王之制作，古人之风烈，悉入金营。", 4),
    ("皆以食戎马，供炽烹，腥鳞湮灭，散落不存。", 4),
    ("文武之道，中国之耻，莫甚乎此，言之可为於邑。", 4),
    ("至于图录规模，则班班尚在，期流传以不朽云尔。", 4),
    # 夜话四 蜑户（卷五）
    ("合浦珠大抵四五所，皆居海洋中间。", 5),
    ("名断望者最，而断望池近交趾", 5),
    ("凡采珠必蜑人，号曰蜑户，丁为蜑丁，亦王民尔。", 5),
    ("特其状怪丑，能辛苦，常业捕鱼生，皆居海艇中，男女活计，世世未尝舍也。", 5),
    ("则别以小绳击诸蜑腰，", 5),
    ("曾未移时，然气已迫，则亟撼小绳。", 5),
    ("绳动，舶人觉，乃绞取。", 5),
    ("出辄大叫，因倒死，久之始苏。", 5),
    # 夜话五 橐驼（卷六）
    ("唐人说江东不识橐驼，谓是「庐山精」，况今南粤，宜未尝过五岭也。", 6),
    ("顷因云扰后，有北客驱一橐驼来。", 6),
    ("吾时在博白，博白人小大为鼓舞，争欲一识。", 6),
    ("客辄阖户蔽障，丐取十数金，即许一入。", 6),
    ("如是，徧历濒海诸郡，藉橐驼致富矣。", 6),
    ("后橐驼因瘴疠死，其家如丧其怙恃。", 6),
    # 夜话六 荔枝（卷六）
    ("自阳华门入，则夹道荔枝八十株，当前椰实一株。", 6),
    ("有太湖石曰「神运昭功」，高四十六尺，立其中，为亭以覆之。", 6),
    ("一小珰登梯，就摘而剖之，诸珰人荔枝二枚", 6),
    ("吾笑而顾之曰：「诸人久饫矣，且饶吾一路。」", 6),
    ("语此一梦，令人怆怅。", 6),
    # 终章（卷一）
    ("时因又赐阁下以小李将军唐明皇幸蜀图一横轴。", 1),
    ("今忽出此，何不祥耶。", 1),
    ("邈在炎陬而北望黄云，书此疾首。", 1),
    ("呼左右俾出市茴香。", 1),
    ("左右偶持一黄纸以包茴香来。", 1),
    ("太上就视之，乃中兴赦书也。", 1),
    ("夫茴香者，回乡也。岂非天乎？", 1),
    ("其后虽八骏忘返，然鸾舆竟还矣。", 1),
    # 众声（附录）
    ("蔡绦奸人，助其父为恶者也。", "ap"),
    ("至是犹不悟，真小人而无忌惮者哉。", "ap"),
    ("酿靖康之祸者，非伊父而谁哉！", "ap"),
    ("助父作奸，罪与攸等。", "ap"),
    ("京败，流白州以死。", "ap"),
    ("盖虽盗权怙势，而知博风雅之名者。", "ap"),
    ("观此书，乃知皆画院供奉代为染写，非真自作，尤历来赏鉴家所未言。", "ap"),
    ("上自干德，下及建炎，中间二百年轶事，无不详志备载，亹亹动听。", "ap"),
    # 校记
    ("铁围山丛淡六卷", "ap"),
    ("床蔡绦撰", "ap"),
    ("嘉靖庚戌孟冬，雁里草堂缮写。仲冬三日校毕。", 6),
    ("此则读书敏求记所谓雁里草堂旧写本也", "ap"),
    ("乾隆四十六年，岁在辛丑，十二月朔，歙西鲍廷博识。", "ap"),
    ("铁围山丛谈卷第一", None),
]

# 页面标注的条序（卷几之几） -> (行号, 卷, 期望序)
ORDINALS = {
    "卷一之八": (11, 1, 8),
    "卷一之三十四": (37, 1, 34),
    "卷一之四十一": (44, 1, 41),
    "卷四之三十七": (199, 4, 37),
    "卷五之十八": (232, 5, 18),
    "卷五之二十七": (241, 5, 27),
    "卷六之三十": (282, 6, 30),
    "卷六之三十四": (286, 6, 34),
}


def count_juan(lines, k, bounds):
    """按写作时同一规则实点：非空、非校勘记标题、非 [一] 式校记条。"""
    seg = lines[bounds[k] + 1: bounds[k + 1]]
    ents = []
    for l in seg:
        if not l.strip():
            continue
        s = l.strip().lstrip("　 ")
        if "校勘记" in s or re.match(r"^\[\w+\]", s):
            continue
        ents.append(l)
    return ents


def main() -> int:
    html = open(PAGE, encoding="utf-8").read()
    src = open(SRC, encoding="utf-8").read()
    lines = src.split("\n")
    fails = []

    # ---- 1. 排版规则 ----
    if "—" in html:
        fails.append("页面出现长划线 —")
    if "–" in html:
        fails.append("页面出现短划线 –")
    for i, line in enumerate(html.splitlines(), 1):
        if line.count("·") > 1:
            fails.append(f"第 {i} 行 · 超过 1 个")
    for ch in html:
        if 0xE000 <= ord(ch) <= 0xF8FF:
            fails.append("页面出现私有区字符")
            break

    # ---- 2. 引文逐字比对 ----
    p = QCollector()
    p.feed(html)
    n_src = norm(src)
    bounds = [3, 65, 105, 162, 214, 252, 298]
    ap_i = src.find("附录")
    juan_norm = {k: norm("\n".join(lines[bounds[k] + 1: bounds[k + 1]])) for k in range(6)}
    ap_norm = norm(src[ap_i:])

    for i, (q, scope) in enumerate(QUOTES_SCOPE, 1):
        nq = norm(q)
        if not nq:
            fails.append(f"核验清单 {i} 为空")
            continue
        if nq not in n_src:
            fails.append(f"引文不在库内：{q[:36]}")
            continue
        if scope in (None,):
            continue
        pool = ap_norm if scope == "ap" else juan_norm[scope - 1]
        if nq not in pool:
            fails.append(f"引文不在指定范围（{'附录' if scope=='ap' else f'卷{scope}'}）：{q[:36]}")

    # 页面实际 .q 数应与核验清单一一覆盖（页面可能多出未入清单的 .q）
    page_norms = [norm(q) for q in p.quotes]
    for nq in page_norms:
        if nq not in [norm(q) for q, _ in QUOTES_SCOPE]:
            fails.append(f"页面存在未入核验清单的 .q：{p.quotes[page_norms.index(nq)][:36]}")
    print(f"[i] 页面 .q 引文 {len(p.quotes)} 处，核验清单 {len(QUOTES_SCOPE)} 条")

    # ---- 3. 页脚引文计数 ----
    m = re.search(r"(\d+) 处引文", html)
    if not m:
        fails.append("页脚找不到引文计数")
    elif int(m.group(1)) != len(p.quotes):
        fails.append(f"页脚引文数 {m.group(1)} != 实际 {len(p.quotes)}")

    # ---- 4. 结构计数复核 ----
    for k, exp in enumerate([52, 34, 47, 37, 27, 39]):
        got = len(count_juan(lines, k, bounds))
        if got != exp:
            fails.append(f"卷{k+1} 实点 {got} 则 != 页面标注 {exp}")
        if f"{exp} 则" not in html:
            fails.append(f"页面缺卷{k+1}「{exp} 则」标注")
    total = sum(len(count_juan(lines, k, bounds)) for k in range(6))
    if total != 236:
        fails.append(f"正文总则 {total} != 236")
    if "236" not in html or "二百三十六" not in html:
        fails.append("页面缺总则数声明（236 / 二百三十六）")
    if "71,998" not in html:
        fails.append("页面缺总字数 71,998")
    if len(re.findall(r"铁围山丛谈卷第[一二三四五六]", src)) != 6:
        fails.append("库内卷标数异常")
    if src.count("附录") < 1:
        fails.append("库内缺附录区")
    print(f"[i] 六卷则数 {total}，全帙 {len(src)} 字")

    # ---- 5. 条序复核 ----
    cn = "〇一二三四五六七八九十"
    for label, (ln, juan, exp) in ORDINALS.items():
        ents = count_juan(lines, juan - 1, bounds)
        try:
            idx = ents.index(lines[ln]) + 1
        except ValueError:
            fails.append(f"{label}: 行 {ln} 不在卷{juan}实点序列中")
            continue
        if idx != exp:
            fails.append(f"{label}: 实点序 {idx} != 页面 {exp}")
        if label not in html:
            fails.append(f"页面缺条序标注 {label}")

    # ---- 6. 页脚三要素 ----
    for key in ["文本来源", "引文核验", "时代局限"]:
        if key not in html:
            fails.append(f"页脚缺「{key}」")

    if fails:
        print(f"\n[FAIL] {len(fails)} 项：")
        for f in fails:
            print("  -", f)
        return 1
    print(f"[PASS] 排版规则、{len(p.quotes)} 处引文（含分卷定位）、结构计数、条序全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
