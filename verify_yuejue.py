#!/usr/bin/env python3
"""越绝书导读页核验：引文逐字比对 + 排版规则 + 计数复核。"""
import re
import sys
import unicodedata
from html.parser import HTMLParser

PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/yuejue-shu.html"
SRC = "/home/robertsong/workspace/claude/daizhige-simplified/史藏/载记/越绝书.txt"


def norm(s: str) -> str:
    return "".join(
        ch for ch in s
        if not ch.isspace() and not unicodedata.category(ch).startswith("P")
    )


class QCollector(HTMLParser):
    """收集所有 class="q" 节点的文本。"""

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
            fails.append("页面出现私有区字符（缺字应作 □）")
            break

    # ---- 2. 引文逐字比对：每个 .q 都必须能在库内文件找到 ----
    p = QCollector()
    p.feed(html)
    nsrc = norm(src)
    for i, q in enumerate(p.quotes, 1):
        nq = norm(q)
        if not nq:
            fails.append(f"引文 {i} 为空")
        elif nq not in nsrc:
            fails.append(f"引文 {i} 不在库内文件中：{q[:40]}")
    print(f"[i] 页面 .q 引文共 {len(p.quotes)} 处")

    # ---- 3. 页脚引文数与实际一致 ----
    m = re.search(r"(\d+) 处引文", html)
    if not m:
        fails.append("页脚找不到引文计数")
    elif int(m.group(1)) != len(p.quotes):
        fails.append(f"页脚引文数 {m.group(1)} != 实际 {len(p.quotes)}")

    # ---- 4. 库内结构计数（写作前实测，此处复核）----
    toc = src.split("越绝卷第一")[0]
    juan = len(re.findall(r"第[一二三四五六七八九十]+卷", toc))
    pian_lines = [ln for ln in toc.splitlines() if re.search(r"第[一二三四五六七八九十]+\s*$", ln)]
    if juan != 15:
        fails.append(f"目录卷数 {juan} != 15")
    if len(pian_lines) != 19:
        fails.append(f"目录篇数 {len(pian_lines)} != 19")
    nei = len(re.findall("内传", toc)) + len(re.findall("内经", toc))
    wai = len(re.findall("外传", toc))
    if nei != 6 or wai != 13:
        fails.append(f"内外篇计数 内{nei} 外{wai} != 6/13")
    if "内六 外十三" not in html:
        fails.append("页面缺「内六 外十三」结构声明")
    print(f"[i] 库本结构：卷 {juan}，篇 {len(pian_lines)}（内 {nei} 外 {wai}）")

    # ---- 5. 页面元素计数 ----
    if len(re.findall(r'class="gate[ "]', html)) != 5:
        fails.append("五门读法不等于 5 扇门")
    if html.count("<tr>") != 10:  # 表头 + 9 行货单
        fails.append(f"货单行数 {html.count('<tr>') - 1} != 9")
    if html.count("<rect") != 6:  # 1 底板 + 5 座城
        fails.append(f"城郭图 rect 数 {html.count('<rect')} != 6（5 座城）")
    if html.count('class="seal') != 8:  # 开门 4 + 尾声 4
        fails.append(f"印章数 {html.count(chr(34).join(['class=', 'seal']) )} != 8")
    if html.count('class="seal miss"') != 2:
        fails.append("缺字虚框印应为 2 处（开门 + 尾声）")
    if "邦贤以□为姓" not in html:
        fails.append("缺字谜面丢失")

    # ---- 6. 关键谜底字必须在库内署名行 ----
    if "袁康 吴平" not in src:
        fails.append("库本书首署名行异常")

    if fails:
        print(f"\n[FAIL] {len(fails)} 项：")
        for f in fails:
            print("  -", f)
        return 1
    print(f"[PASS] 排版规则、{len(p.quotes)} 处引文、结构计数全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
