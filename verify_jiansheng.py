#!/usr/bin/env python3
"""剪胜野闻导读页核验：引文逐字比对 + 排版规则 + 关键声明计数。"""
import re
import sys
import unicodedata
from html.parser import HTMLParser

PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/jiansheng-yewen.html"
SRC = "/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/剪胜野闻.txt"


def norm(s: str) -> str:
    return "".join(
        ch for ch in s
        if not ch.isspace() and not unicodedata.category(ch).startswith("P")
    )


class QCollector(HTMLParser):
    """收集所有 class 含 q 的最外层节点文本。"""

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


def main() -> int:
    html = open(PAGE, encoding="utf-8").read()
    src = open(SRC, encoding="utf-8").read()
    fails = []
    n_src = norm(src)
    print(f"[i] 库内去空白 {len(src.replace(' ','').replace(chr(10),'').replace('　',''))} 字")

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
    for i, q in enumerate(p.quotes, 1):
        nq = norm(q)
        if not nq:
            fails.append(f"引文 {i} 为空")
            continue
        if nq not in n_src:
            fails.append(f"引文不在库内：{q[:40]}")

    # ---- 3. 页面展示的碎片引语也须逐字（非 .q 的粗体短语白名单核对）----
    FRAGMENTS = ["是日诛夷盖寡", "倾朝无人色", "真齐东野人之语，祯卿似未必至是也",
                 "天下者天下之天下", "顺之未必其生，逆之未必其死", "政尚严猛"]
    for frag in FRAGMENTS:
        if norm(frag) not in n_src:
            fails.append(f"碎片引语不在库内：{frag}")

    # ---- 4. 关键声明 ----
    for kw in ["去空白9141字", "一卷", "四库存目", "徐祯卿", "蒸鹅",
               "「策」原作「岂」，据清胜朝遗事本改", "无标点原样照录"]:
        if kw not in html:
            fails.append(f"页面缺关键声明：{kw}")

    # ---- 5. 交互元素齐全 ----
    for anchor in ["cutTitle", "cutBtn", "belt", "beltUp", "beltDown",
                   "yuanBtn", "ystep3", "budaiFig", "gatha", "qcount"]:
        if f'id="{anchor}"' not in html:
            fails.append(f"缺交互锚点 {anchor}")

    print(f"[i] 页面 .q 引文 {len(p.quotes)} 处")
    if fails:
        print("\n".join("FAIL " + f for f in fails))
        return 1
    print("PASS 全部核验通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
