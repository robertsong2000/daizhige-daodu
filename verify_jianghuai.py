#!/usr/bin/env python3
"""江淮异人录导读页核验：引文逐字比对（前半卷上下本 / 后半正统道藏本分源）+ 双本分岔跨本断言 + 排版规则 + 结构计数。"""
import re
import sys
import unicodedata
from html.parser import HTMLParser

PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/jianghuai-yirenlu.html"
SRC = "/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/江淮异人录.txt"


def norm(s: str) -> str:
    return "".join(
        ch for ch in s
        if not ch.isspace() and not unicodedata.category(ch).startswith("P")
    )


class QCollector(HTMLParser):
    """收集所有 class 含 q 的最外层节点文本与其 data-v。"""

    def __init__(self):
        super().__init__()
        self.depth = 0
        self.buf = []
        self.quotes = []  # (text, data-v)

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        cls = (d.get("class") or "").split()
        if self.depth > 0 or "q" in cls:
            if self.depth == 0:
                self.cur_v = d.get("data-v")
            self.depth += 1

    def handle_endtag(self, tag):
        if self.depth > 0:
            self.depth -= 1
            if self.depth == 0 and self.buf:
                self.quotes.append(("".join(self.buf), getattr(self, "cur_v", None)))
                self.buf = []

    def handle_data(self, data):
        if self.depth > 0:
            self.buf.append(data)


def split_versions(src: str):
    mk = src.find("{正统道藏本}")
    assert mk > 0, "找不到道藏本标记"
    s_part = src[:mk]
    d_part = src[mk:]
    lines_s = s_part.split("\n")
    s_body = s_part
    # 目录题
    toc = [l.strip() for l in lines_s[3:30] if l.strip() and l.strip() not in ("卷上", "卷下")]
    assert len(toc) == 25, f"目录题数 {len(toc)} != 25"
    up, down = toc[:13], toc[13:]
    # 道藏本题
    d_titles = []
    for l in d_part.split("\n")[1:]:
        t = l.strip()
        if t and not t.startswith(("　", " ")) and len(t) <= 12 and "。" not in t and "[" not in t:
            d_titles.append(t)
    assert len(d_titles) == 25, f"道藏本题数 {len(d_titles)} != 25: {d_titles}"
    shared = sorted(set(toc) & set(d_titles))
    s_only = sorted(set(toc) - set(d_titles))
    d_only = sorted(set(d_titles) - set(toc))
    return norm(s_body), norm(d_part), up, down, d_titles, shared, s_only, d_only


def main() -> int:
    html = open(PAGE, encoding="utf-8").read()
    src = open(SRC, encoding="utf-8").read()
    fails = []

    s_norm, d_norm, up, down, d_titles, shared, s_only, d_only = split_versions(src)
    n_src = norm(src)
    print(f"[i] 卷上 {len(up)} 题 / 卷下 {len(down)} 题 / 道藏本 {len(d_titles)} 题")
    print(f"[i] 共享 {len(shared)}，前半独有 {s_only}，道藏独有 {d_only}")
    if len(shared) != 19 or len(s_only) != 6 or len(d_only) != 6:
        fails.append("两本题集分布 != 共享19/各独6")
    if s_only != sorted(["张标", "建康异人", "宣州军士", "唐宁王", "杭州野翁", "花姑"]):
        fails.append(f"前半独有题不符预期: {s_only}")
    if d_only != sorted(["洪州将校", "建康贫者", "魏王军士", "虔州少年", "闽中处士", "瞿童"]):
        fails.append(f"道藏独有题不符预期: {d_only}")

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
    for i, (q, v) in enumerate(p.quotes, 1):
        nq = norm(q)
        if not nq:
            fails.append(f"引文 {i} 为空")
            continue
        if nq not in n_src:
            fails.append(f"引文不在库内：{q[:40]}")
            continue
        if v == "s" and nq not in s_norm:
            fails.append(f"标前半却不在前半：{q[:40]}")
        if v == "d" and nq not in d_norm:
            fails.append(f"标道藏本却不在道藏本：{q[:40]}")
    print(f"[i] 页面 .q 引文 {len(p.quotes)} 处")

    # ---- 3. 双本分岔跨本断言 ----
    CROSS = [
        ("s", "临终命置一杖于棺中，及葬，棺空，发之，唯杖在焉。"),
        ("d", "临终令置一杖于棺中，及葬，觉棺空，发之，唯杖在焉。"),
        ("s", "旦来恶少子，吾不能容，断其首。"),
        ("d", "旦来恶子，吾不能容，已断其首。"),
        ("s", "或谓杨氏自称尊号至禅代二十五年，故髣髴倍之耳。"),
        ("d", "或谓杨氏自称尊至禅代二十年，故髣髴倍之耳。"),
        ("s", "二妾左右拥袂而哭。哭毕视之，汾已卒矣。"),
        ("s", "光如白虹，人触之，身首异处。"),
        ("s", "此犹公子孙鳞次而覇也。"),
        ("d", "训入厨，见甑中蒸一人头。"),
    ]
    for v, q in CROSS:
        nq = norm(q)
        other = d_norm if v == "s" else s_norm
        if v == "s" and nq not in s_norm:
            fails.append(f"分岔断言失败（不在前半）：{q[:30]}")
        if v == "s" and nq in other:
            fails.append(f"分岔断言失败（竟也在道藏本）：{q[:30]}")
        if v == "d" and nq not in d_norm:
            fails.append(f"分岔断言失败（不在道藏本）：{q[:30]}")
        if v == "d" and nq in other:
            fails.append(f"分岔断言失败（竟也在前半）：{q[:30]}")

    # ---- 4. 页脚引文计数 ----
    m = re.search(r"共 (\d+) 处引文", html)
    if not m:
        fails.append("页脚找不到引文计数")
    elif int(m.group(1)) != len(p.quotes):
        fails.append(f"页脚引文数 {m.group(1)} != 实际 {len(p.quotes)}")

    # ---- 5. 结构计数 ----
    for kw in ["去空白17681字", "二十五盏", "各二十五题", "共享十九题", "四十六年", "三十九年"]:
        if kw not in html:
            fails.append(f"页面缺关键声明：{kw}")
    for anchor in ["hu-geng", "hu-xia", "hu-daoshi", "hu-chen", "hu-ye", "hu-wenqing"]:
        if f'id="{anchor}"' not in html:
            fails.append(f"缺深读锚点 {anchor}")
    if len(up) != 13 or len(down) != 12:
        fails.append("卷上/卷下题数 != 13/12")

    if fails:
        print("\n".join("FAIL " + f for f in fails))
        return 1
    print("PASS 全部核验通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
